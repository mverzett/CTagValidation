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

out_file = io.root_open('analyzed/flat_tree_output.root', 'recreate')

#book plots
plots = {}
out_file.cd()
plots['pt']  = Hist(200, 0, 1000, name='pt')
plots['pt_zoom'] = Hist(10, 0, 50, name='pt_zoom')
plots['eta'] = Hist(300, -3, 3, name='eta')
for name in tested_discriminators:
   tdir = out_file.mkdir(name)
   tdir.cd()
   plots[name] = {}
   #discriminator output
   plots[name]['output'  ] = Hist(400, -2, 2, name='output'  )
   plots[name]['output_C'] = Hist(400, -2, 2, name='output_C')
   plots[name]['output_L'] = Hist(400, -2, 2, name='output_L')
   plots[name]['output_B'] = Hist(400, -2, 2, name='output_B')


class FunctorFromMVA(object):
    def __init__(self, name, xml_filename, **kwargs):
       mva_vars = get_vars(xml_filename)
       variables = [i.name.value() for i in mva_vars]
       self.reader    = ROOT.TMVA.Reader( "!Color:Silent=%s:Verbose=%s" % (kwargs.get('silent','T'), kwargs.get('verbose','F')))
       self.var_map   = {}
       self.name      = name
       self.variables = variables
       self.xml_filename = xml_filename
       for var in variables:
          self.var_map[var] = array.array('f',[0]) 
          self.reader.AddVariable(var, self.var_map[var])
       self.reader.BookMVA(name, xml_filename)
          
    def evaluate_(self): #so I can profile the time needed
        return self.reader.EvaluateMVA(self.name)

    def __call__(self, entry):
        #kvars enforces that we use the proper vars
        if not ( 
                 all(hasattr(entry, name) for name in self.variables)
                ):
            raise Exception("Wrong variable names. Available variables: %s" % self.variables.__repr__())
        for name in self.variables:
            self.var_map[name][0] = float(getattr(entry, name))
        retval = self.evaluate_() #reader.EvaluateMVA(self.name)
        return retval


mva = {
   'CvsL' : FunctorFromMVA('c_vs_l', '%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE']),
   'CvsB' : FunctorFromMVA('c_vs_b', '%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])
}
njets = {}

for entry in flat_tree:
   evtid = (entry.run, entry.lumi, entry.evt)
## if evtid in njets:
##    njets[evtid] += 1
## else:
##    njets[evtid] = 1

   plots['pt'].fill(entry.jetPt)
   plots['pt_zoom'].fill(entry.jetPt)
   plots['eta'].fill(entry.jetEta)
   for short, evaluator in mva.iteritems():
      bmva = evaluator(entry)
      plots[short]['output'].fill(bmva)
      flav = abs(entry.flavour)
      if flav == 4:
         plots[short]['output_C'].fill(bmva)
      elif flav == 5:
         plots[short]['output_B'].fill(bmva)
      else:
         plots[short]['output_L'].fill(bmva)

out_file.Write()
inputFile.Close()
out_file.Close()
