import ROOT
import pprint
import sys
from DataFormats.FWLite import Events, Handle
from rootpy.plotting import Hist #yes, needs rootpy, it is MUCH better
import rootpy.io as io
ROOT.gROOT.SetBatch()
from pdb import set_trace
import os
import pickle
import rootpy
from helpers import dict2tdir, Struct, ExtJet, FunctorFromMVA
from RecoBTag.CTagging.trainingvars import training_vars
log = rootpy.log["/analyze_jetByjet"]
log.setLevel(rootpy.log.INFO)
from copy import deepcopy 
import math

def is_defaulted(vname, value):
   #wild approximation, but for now works
   varname = vname
   if varname[-2] == '_':
      varname = varname[:-2]
   return value == training_vars[varname]['default']

#yeah, everything is pretty much hadrcoded, but this is
#supposed to be a quick check 
events = Events('trees/validate_ctag_pat.root')

debug_CvsL_file = io.root_open('trees/ctag_debug_CvsL.root')
debug_CvsB_file = io.root_open('trees/ctag_debug_CvsB.root')
debug_CvsL = debug_CvsL_file.tree.__iter__()
debug_CvsB = debug_CvsB_file.tree.__iter__()

tested_discriminators = {
   'pfCombinedCvsLJetTags' : 'CvsL', 
   'pfCombinedCvsBJetTags' : 'CvsB'
}

if not os.path.isdir('analyzed'):
   os.makedirs('analyzed')

#book plots
from plots import plots
diff_plots = {}
diff_plots['njets'] = Hist(40, -20, 20)
for name, h in plots['trainingvars'].iteritems():
   delta = h[-1].x.high - h[0].x.low
   diff_plots[name] = Hist(100, -delta/2., delta/2)
ntrining = len(plots['trainingvars'])
diff_plots['nsame'] = Hist(ntrining+1, -0.5, ntrining+0.5)
diff_plots['LMVA'] = Hist(40, -2, 2)
diff_plots['BMVA'] = Hist(40, -2, 2)
diff_plots['SameValRate'] = Hist(ntrining+1, -0.5, ntrining+0.5)
diff_plots['DiffAndDefaulted'] = Hist(ntrining+1, -0.5, ntrining+0.5)
same_rate = dict((i, 0) for i in plots['trainingvars'])
diff_and_defaulted = dict((i, 0) for i in plots['trainingvars'])

plots = diff_plots
not_auto = set(['njets', 'nsame', 'LMVA', 'BMVA', 'SameValRate', 'DiffAndDefaulted'])

mva = {
   'CvsL' : FunctorFromMVA('c_vs_l', '%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE']),
   'CvsB' : FunctorFromMVA('c_vs_b', '%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])
}

#import jets for flat trees
jet_maps = {}
with open('flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

print 'build jet by jet map from flat tree'
flat_map = {}
inputFile = io.root_open('trees/CombinedSV_ALL.root')
flat_tree = inputFile.tree

for entry in flat_tree:
   evtid = (entry.run, entry.lumi, entry.evt)
   if (entry.jetPt, entry.jetEta) not in jet_maps[evtid]:
      continue

   if evtid not in flat_map: flat_map[evtid] = {}
   flat_map[evtid][(entry.jetPt, entry.jetEta)] = Struct.from_entry(entry)


handle = Handle('std::vector<pat::Jet>')
vtx_handle = Handle('vector<reco::Vertex>')
print 'analyzing pat output'
same_mva, same_inputs = 0, 0
n_analyzed_jets = 0
different_jets = {}
for evt in events:
   evtid = (evt.eventAuxiliary().run(), evt.eventAuxiliary().luminosityBlock(), evt.eventAuxiliary().event())

   evt.getByLabel('selectedPatJets', handle)
   jets = handle.product()
   ext_jets = []
   for jet in jets:
      ext_jets.append(
         ExtJet(
            jet,
            debug_CvsL.next(),
            debug_CvsB.next()
         )
         )
   jets = ext_jets

   if evtid not in jet_maps:
      log.warning("Event %s not found in the flat map!" % evtid.__repr__())
      continue
   
   #jet selection
   jets = [jet for jet in jets
           if jet.jet.pt() > 15 
           if abs(jet.jet.eta()) < 2.5
           #if jet.jetFlavourInfo().getPartonFlavour() != 0
           ]

   #apply flat jet mapping
   evt_jets = jet_maps[evtid]
   sjets = [i for i in jets
           if (i.jet.pt(), i.jet.eta()) in evt_jets]
   jdiff = len(evt_jets)-len(sjets)
   if jdiff:
      log.warning("I could not find %i jets in Event %s" % (jdiff, evtid.__repr__()))
      set_trace()

   pat_jets = sjets
   if not pat_jets:
      continue

   #get flat jets
   flat_jets = flat_map[evtid]

   diffjet_entry = set()
   plots['njets'].fill(len(pat_jets) - len(flat_jets))
   for extjet in pat_jets:
      n_analyzed_jets += 1
      pat_jet = extjet.jet
      try:
         flat_jet = flat_jets[(pat_jet.pt(), pat_jet.eta())]
      except:
         set_trace()

      taginfos = extjet.CvsL
      nsame = 0
      for vname in plots:
         if vname in not_auto: continue
         fillval = taginfos[vname] - getattr(flat_jet, vname)
         precision = abs(taginfos[vname])*0.001 #require precision of al least one per mil
         fillval = fillval if abs(fillval) > precision else 0
         if fillval == 0: 
            nsame += 1
            same_rate[vname] += 1
         else:
            if abs(fillval/taginfos[vname]) > 1:
               print 'BIG', vname, taginfos[vname], getattr(flat_jet, vname)
            else:
               print 'SMALL',vname, taginfos[vname], getattr(flat_jet, vname) #set_trace()
            if is_defaulted(vname, taginfos[vname]) or is_defaulted(vname, getattr(flat_jet, vname)):
               diff_and_defaulted[vname] += 1
         plots[vname].fill(fillval)
      plots['nsame'].fill(nsame)
      mva_diff = pat_jet.bDiscriminator('pfCombinedCvsLJetTags') - mva['CvsL'](flat_jet)
      if abs(mva_diff) < 10**-5:
         same_mva += 1
      if nsame == ntrining:
         same_inputs += 1
      else:
         diffjet_entry.add((pat_jet.pt(), pat_jet.eta()))
      plots['LMVA'].fill(
         mva_diff
         )
      plots['BMVA'].fill(
         pat_jet.bDiscriminator('pfCombinedCvsBJetTags') -
         mva['CvsB'](flat_jet)
         )
   different_jets[evtid] = diffjet_entry

for bin, label in zip(plots['SameValRate'][1:], same_rate):
   value = float(same_rate[label])/n_analyzed_jets
   bin.value = value
   blabel = label
   if value < 0.6:
      blabel = '#color[2]{%s}' % label
   elif value < 0.8:
      blabel = '#color[42]{%s}' % label      
   plots['SameValRate'].xaxis.SetBinLabel(bin.idx, blabel)


for bin, label in zip(plots['DiffAndDefaulted'][1:], same_rate):
   value = float(diff_and_defaulted[label])/(n_analyzed_jets-same_rate[label]) if (n_analyzed_jets-same_rate[label]) > 0 else 0.
   bin.value = value
   if value > 0.3:
      label = '#color[2]{%s}' % label
   ## elif value < 0.8:
   ##    label = '#color[42]{%s}' % label      
   plots['DiffAndDefaulted'].xaxis.SetBinLabel(bin.idx, label)


print 'total number of jets: ', n_analyzed_jets
print "with same mva", same_mva
print "with same inputs", same_inputs
print 'saving histograms'
with io.root_open('analyzed/jet_by_jet_diff.root', 'recreate') as out:
   dict2tdir(plots, out)

with open('analyzed/different_jets.db', 'wb') as out:
   pickle.dump(different_jets, out)
