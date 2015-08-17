import ROOT
import pprint
import sys
from DataFormats.FWLite import Events, Handle
from rootpy.plotting import Hist #yes, needs rootpy, it is MUCH better
import rootpy.io as io
from RecoBTag.CTagging.helpers import get_vars
import os
ROOT.gROOT.SetBatch()
from pdb import set_trace
import array
from helpers import dict2tdir, FunctorFromMVA
import pickle
#yeah, everything is pretty much hadrcoded, but this is
#supposed to be a quick check 
inputFile = io.root_open('trees/CombinedSV_ALL.root')
flat_tree = inputFile.tree
tested_discriminators = [
   'CvsL', 
   'CvsB'
]

if not os.path.isdir('analyzed'):
   os.makedirs('analyzed')

#book plots
from plots import plots


mva = {
   'CvsL' : FunctorFromMVA('c_vs_l', '%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE']),
   'CvsB' : FunctorFromMVA('c_vs_b', '%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])
}
njets = {}
#import jets for flat trees
jet_maps = {}
with open('flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

mva_jetmap = {}
for entry in flat_tree:
   evtid = (entry.run, entry.lumi, entry.evt)
   if evtid not in jet_maps:
      continue
   if (entry.jetPt, entry.jetEta) not in jet_maps[evtid]:
      continue

   if evtid in njets:
      njets[evtid] += 1
   else:
      njets[evtid] = 1

   plots['pt'].fill(entry.jetPt)
   plots['pt_zoom'].fill(entry.jetPt)
   plots['eta'].fill(entry.jetEta)
   mva_info = {}
   for short, evaluator in mva.iteritems():
      bmva = evaluator(entry)
      mva_info[short] = bmva
      plots[short]['output'].fill(bmva)
      flav = abs(entry.flavour)
      if flav == 4:
         plots[short]['output_C'].fill(bmva)
      elif flav == 5:
         plots[short]['output_B'].fill(bmva)
      else:
         plots[short]['output_L'].fill(bmva)

   if evtid not in mva_jetmap:
      mva_jetmap[evtid] = {}
   mva_jetmap[evtid][(entry.jetPt, entry.jetEta)] = mva_info

   for vname in plots['trainingvars']:
      if hasattr(entry, vname):
         plots['trainingvars'][vname].fill(getattr(entry, vname))

for j, i in njets.iteritems():
   if i > 20:
      print j, i
   plots['njets'].fill(i)

print len(njets)
with io.root_open('analyzed/flat_tree_output.root', 'recreate') as out:
   dict2tdir(plots, out)

with open('analyzed/falt_tree_mva_jetmap.db', 'wb') as out:
   pickle.dump(mva_jetmap, out)

inputFile.Close()
