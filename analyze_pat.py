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
log = rootpy.log["/URUnfolding"]
log.setLevel(rootpy.log.INFO)

#yeah, everything is pretty much hadrcoded, but this is
#supposed to be a quick check 
events = Events('trees/validate_ctag_pat.root')
tested_discriminators = {
   'pfCombinedCvsLJetTags' : 'CvsL', 
   'pfCombinedCvsBJetTags' : 'CvsB'
}

if not os.path.isdir('analyzed'):
   os.makedirs('analyzed')

#book plots
out_file = io.root_open('analyzed/pat_validation_output.root', 'recreate')
out_file.cd()
plots = {}
plots['pt'] = Hist(200, 0, 1000, name='pt')
plots['pt_zoom'] = Hist(10, 0, 50, name='pt_zoom')
plots['eta'] = Hist(300, -3, 3, name='eta')
plots['njets'] = Hist(20, 0, 20, name='njets')
for name in tested_discriminators.values():
   tdir = out_file.mkdir(name)
   tdir.cd()
   plots[name] = {}
   #discriminator output
   plots[name]['output'  ] = Hist(400, -2, 2, name='output'  )
   plots[name]['output_C'] = Hist(400, -2, 2, name='output_C')
   plots[name]['output_L'] = Hist(400, -2, 2, name='output_L')
   plots[name]['output_B'] = Hist(400, -2, 2, name='output_B')

handle = Handle('std::vector<pat::Jet>')
vtx_handle = Handle('vector<reco::Vertex>')

#import jets for flat trees
jet_maps = {}
with open('analyzed/flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

for evt in events:
   evtid = (evt.eventAuxiliary().run(), evt.eventAuxiliary().luminosityBlock(), evt.eventAuxiliary().event())
   if evtid not in jet_maps:
      log.warning("Event %s not found in the flat map!" % evtid.__repr__())
      continue

   evt.getByLabel('selectedPatJets', handle)
   jets = handle.product()

   #jet selection
   jets = [jet for jet in jets
           if jet.pt() > 15 
           if abs(jet.eta()) < 2.5
           #if jet.jetFlavourInfo().getPartonFlavour() != 0
           ]

   #apply flat jet mapping
   evt_jets = jet_maps[evtid]
   sjets = [i for i in jets
           if (i.pt(), i.eta()) in evt_jets]
   jdiff = len(evt_jets)-len(sjets)
   if jdiff:
      log.warning("I could not find %i jets in Event %s" % (jdiff, evtid.__repr__()))
      set_trace()

   jets = sjets

   evt.getByLabel('goodOfflinePrimaryVertices', vtx_handle)
   if not vtx_handle.product().size():
      continue

   plots['njets'].fill(len(jets))
   for jet in jets:
      plots['pt'].fill(jet.pt())
      plots['pt_zoom'].fill(jet.pt())
      plots['eta'].fill(jet.eta())
      for full, short in tested_discriminators.iteritems():
         bmva = jet.bDiscriminator(full)
         plots[short]['output'].fill(bmva)
         flav = abs(jet.jetFlavourInfo().getPartonFlavour())
         if flav == 4:
            plots[short]['output_C'].fill(bmva)
         elif flav == 5:
            plots[short]['output_B'].fill(bmva)
         else:
            plots[short]['output_L'].fill(bmva)


out_file.Write()
out_file.Close()
