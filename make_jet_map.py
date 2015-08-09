import rootpy.io as io
from DataFormats.FWLite import Events, Handle
import pickle

flat_map = {}
inputFile = io.root_open('trees/CombinedSV_ALL.root')
flat_tree = inputFile.tree

for entry in flat_tree:
   evtid = (entry.run, entry.lumi, entry.evt)
   if evtid not in flat_map: flat_map[evtid] = set()      
   flat_map[evtid].add(
      (entry.jetPt, entry.jetEta)
      )

events = Events('trees/validate_ctag_pat.root')
handle = Handle('std::vector<pat::Jet>')
pat_map = {}

for evt in events:
   evtid = (evt.eventAuxiliary().run(), evt.eventAuxiliary().luminosityBlock(), evt.eventAuxiliary().event())
   evt.getByLabel('selectedPatJets', handle)
   jets = handle.product()
   pat_map[evtid] = set(
      (i.pt(), i.eta()) for i in jets
      )

#take intersection
pat_evts = set(pat_map.keys())
flat_evts = set(flat_map.keys())

both = pat_evts.intersection(flat_evts)
final_map = {}
for evtid in both:
   final_map[evtid] = pat_map[evtid].intersection(
      flat_map[evtid]
      )

with open('flat_jet_map', 'wb') as db:
   pickle.dump(final_map, db)
