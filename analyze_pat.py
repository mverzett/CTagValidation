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
plots['CvsB']['mva_assert'] = Hist(2, 0, 2)
plots['CvsL']['mva_assert'] = Hist(2, 0, 2)

#import jets for flat trees
jet_maps = {}
with open('flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

## mva_map = {}
## with open('analyzed/falt_tree_mva_jetmap.db') as infile:
##    mva_map = pickle.load(infile)

handle = Handle('std::vector<pat::Jet>')
vtx_handle = Handle('vector<reco::Vertex>')
#global_jet_ID = 0
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

   jets = sjets

   ## evt.getByLabel('goodOfflinePrimaryVertices', vtx_handle)
   ## if not vtx_handle.product().size():
   ##    continue

   plots['njets'].fill(len(jets))
   for extjet in jets:
      jet = extjet.jet
      plots['pt'].fill(jet.pt())
      plots['pt_zoom'].fill(jet.pt())
      plots['eta'].fill(jet.eta())
      for full, short in tested_discriminators.iteritems():
         bmva = jet.bDiscriminator(full)
         plots[short]['mva_assert'].fill(
            0.
            ## int(mva_map[evtid][(jet.pt(), jet.eta())][short] == bmva)
            )
         plots[short]['output'].fill(bmva)
         flav = abs(jet.jetFlavourInfo().getPartonFlavour())
         if flav == 4:
            plots[short]['output_C'].fill(bmva)
         elif flav == 5:
            plots[short]['output_B'].fill(bmva)
         else:
            plots[short]['output_L'].fill(bmva)

      taginfos = extjet.CvsL
      for vname in plots['trainingvars']:
         if vname in taginfos:
            plots['trainingvars'][vname].fill(taginfos[vname])


with io.root_open('analyzed/pat_validation_output.root', 'recreate') as out:
   dict2tdir(plots, out)
