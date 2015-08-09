from plots import plots
from RecoBTag.CTagging.helpers import get_vars
import ROOT
from rootpy.plotting import Hist #yes, needs rootpy, it is MUCH better
import rootpy.io as io
import os
ROOT.gROOT.SetBatch()
from pdb import set_trace
from helpers import dict2tdir, FunctorFromMVA, Struct
import pickle
from glob import glob
from RecoBTag.CTagging.trainingvars import get_var_pset
#yeah, everything is pretty much hadrcoded, but this is
#supposed to be a quick check 
tested_discriminators = [
   'CvsL', 
   'CvsB'
]

if not os.path.isdir('analyzed'):
   os.makedirs('analyzed')

mva = {
   'CvsL' : FunctorFromMVA('c_vs_l', '%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE']),
   'CvsB' : FunctorFromMVA('c_vs_b', '%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])
}
njets = {}
def get_info(pset):
   ret = {
      'entry_name' : pset.taggingVarName.value(),
      'default' : pset.default.value(),
      }
   if hasattr(pset, 'idx'):
      ret['idx'] = pset.idx.value()
   return ret

mva_vars_info = dict((i.name.value(), get_info(i)) for i in get_vars('%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE']))

#import jets for flat trees
jet_maps = {}
with open('flat_jet_map') as infile:
   jet_maps = pickle.load(infile)

infile_names = glob('training_trees/CombinedSV*.root')
for fname in infile_names:
   infile = io.root_open(fname)
   tname = os.path.basename(fname).split('_')[0]
   ttree = infile.Get(tname)
   flavor = os.path.basename(fname).split('_')[1].replace('.root','')
   for entry in ttree:
      evtid = (entry.run, entry.lumi, entry.evt)
      if (entry.jetPt, entry.jetEta) not in jet_maps[evtid]:
         continue

      if evtid in njets:
         njets[evtid] += 1
      else:
         njets[evtid] = 1

      plots['pt'].fill(entry.jetPt)
      plots['pt_zoom'].fill(entry.jetPt)
      plots['eta'].fill(entry.jetEta)

      mva_input = Struct()
      for vname in plots['trainingvars']:
         info = mva_vars_info[vname]
         var = info['default']
         if hasattr(entry, info['entry_name']):
            full_var = getattr(entry, info['entry_name'])
            if 'idx' in info and len(full_var) > info['idx']:
               var = full_var[info['idx']] 
            elif 'idx' not in info:
               var = full_var

         plots['trainingvars'][vname].fill(var)
         setattr(mva_input, vname, var)

      for short, evaluator in mva.iteritems():
         bmva = evaluator(mva_input)
         plots[short]['output'].fill(bmva)
         if flavor == 'C':
            plots[short]['output_C'].fill(bmva)
         elif flavor == 'B':
            plots[short]['output_B'].fill(bmva)
         else:
            plots[short]['output_L'].fill(bmva)
      
for j, i in njets.iteritems():
   if i > 20:
      print j, i
   plots['njets'].fill(i)

with io.root_open('analyzed/varex_output.root', 'recreate') as out:
   dict2tdir(plots, out)
