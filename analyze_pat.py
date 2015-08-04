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
from helpers import dict2tdir
log = rootpy.log["/URUnfolding"]
log.setLevel(rootpy.log.INFO)
from copy import deepcopy 

class Struct:
   def __init__(self, **entries): 
       self.__dict__.update(entries)

   def clone(self, **subs):
       newd = deepcopy(self.__dict__)
       newd.update(subs)
       return Struct(**newd)

   def __len__(self):
       return len(self.__dict__)

   def __contains__(self, val):
       return val in self.__dict__

   def __hash__(self):
       return self.__dict__.__repr__().__hash__()

   def __getitem__(self, name):
     'x.__getitem__(i, y) <==> x[i]'
     return self.__dict__[name]

   def __setitem__(self, name, val):
     'x.__setitem__(i, y) <==> x[i]=y'
     self.__dict__[name] = val

   def iteritems(self):
       return self.__dict__.iteritems()

   def keys(self):
       return self.__dict__.keys()

class ExtJet(object):
   def __init__(self, patjet, l_entry, b_entry):
      self.jet = patjet
      assert(self.jet.pt() == l_entry.jetPt)
      assert(self.jet.eta() == l_entry.jetEta)
      self.CvsL = Struct(
         **dict(
            (i, deepcopy(getattr(l_entry, i))) for i in l_entry.iterkeys())
           )

      assert(self.jet.pt() == b_entry.jetPt)
      assert(self.jet.eta() == b_entry.jetEta)
      self.CvsB = Struct(
         **dict((i, deepcopy(getattr(b_entry, i))) for i in b_entry.iterkeys())
           )

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

#import jets for flat trees
jet_maps = {}
with open('analyzed/flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

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
