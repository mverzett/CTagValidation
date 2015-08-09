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
from helpers import dict2tdir, Struct, ExtJet
log = rootpy.log["/analyze_pat"]
log.setLevel(rootpy.log.INFO)
from copy import deepcopy 

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
plots = diff_plots

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

   plots['njets'].fill(len(pat_jets) - len(flat_jets))
   for extjet in pat_jets:
      pat_jet = extjet.jet
      try:
         flat_jet = flat_jets[(pat_jet.pt(), pat_jet.eta())]
      except:
         set_trace()

      taginfos = extjet.CvsL
      for vname in plots:
         if vname == 'njets': continue
         fillval = taginfos[vname] - getattr(flat_jet, vname)
         ## if vname == 'trackEtaRel_0' and fillval < -3:
         ##    print evtid, 'jID', (pat_jet.pt(), pat_jet.eta())
         ##    print 'flat: ', getattr(flat_jet, vname), 'pat:', taginfos[vname]
         ##    set_trace()
         plots[vname].fill(fillval)
         

print 'saving histograms'
with io.root_open('analyzed/jet_by_jet_diff.root', 'recreate') as out:
   dict2tdir(plots, out)
