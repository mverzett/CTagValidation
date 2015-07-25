import ROOT
import pprint
import sys
from DataFormats.FWLite import Events, Handle
from rootpy.plotting import Hist #yes, needs rootpy, it is MUCH better
import rootpy.io as io
ROOT.gROOT.SetBatch()
from pdb import set_trace

#yeah, everything is pretty much hadrcoded, but this is
#supposed to be a quick check 
events = Events('trees/validate_ctag_pat.root')
tested_discriminators = {
   'pfCombinedCvsLJetTags' : 'CvsL', 
   'pfCombinedCvsBJetTags' : 'CvsB'
}

#book plots
plots = {}
for name in tested_discriminators.values():
   plots[name] = {}
   #discriminator output
   plots[name]['output']   = Hist(400, -2, 2)
   plots[name]['output_C'] = Hist(400, -2, 2)
   plots[name]['output_L'] = Hist(400, -2, 2)
   plots[name]['output_B'] = Hist(400, -2, 2)
   plots[name]['pt'] = Hist(200, 0, 1000)
   plots[name]['eta'] = Hist(300, -3, 3)

handle = Handle('std::vector<pat::Jet>')
vtx_handle = Handle('vector<reco::Vertex>')

for evt in events:
   evt.getByLabel('selectedPatJets', handle)
   jets = handle.product()

   evt.getByLabel('goodOfflinePrimaryVertices', vtx_handle)
   if not vtx_handle.product().size():
      continue

   for jet in jets:
      if jet.pt() < 15 or abs(jet.eta()) > 2.5:
         continue
      if jet.jetFlavourInfo().getPartonFlavour() == 0:
         continue

      for full, short in tested_discriminators.iteritems():
         bmva = jet.bDiscriminator(full)
         plots[short]['output'].fill(bmva)
         plots[short]['pt'].fill(jet.pt())
         plots[short]['eta'].fill(jet.eta())
         flav = abs(jet.jetFlavourInfo().getPartonFlavour())
         if flav == 4:
            plots[short]['output_C'].fill(bmva)
         elif flav == 5:
            plots[short]['output_B'].fill(bmva)
         else:
            plots[short]['output_L'].fill(bmva)

if not os.path.isdir('analyzed'):
   os.makedirs('analyzed')

with io.root_open('analyzed/pat_validation_output.root', 'recreate') as out:
   for dname, dplots in plots.iteritems():
      tdir = out.mkdir(dname)
      for name, plot in dplots.iteritems():
         tdir.WriteTObject(plot, name)
