import FWCore.ParameterSet.Config as cms
from RecoBTag.CTagging.helpers import get_vars
import ROOT
import array
from copy import deepcopy
import os

def mkdir(path):
   if not os.path.isdir(path):
      os.makedirs(path)
      return True
   return False

def dict2tdir(hdict, tdir):
   for name, val in hdict.iteritems():
      if isinstance(val, dict):
         subdir = tdir.mkdir(name)
         dict2tdir(val, subdir)
      else:
         tdir.WriteTObject(val, name)

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
   
   @classmethod
   def from_entry(cls, entry):
      return cls(
         **dict(
            (i, deepcopy(getattr(entry, i))) for i in entry.iterkeys())
           )
      

class ExtJet(object):
   def __init__(self, patjet, l_entry, b_entry):
      self.jet = patjet
      assert(self.jet.pt() == l_entry.jetPt)
      assert(self.jet.eta() == l_entry.jetEta)
      self.CvsL = Struct.from_entry(l_entry)
      assert(self.jet.pt() == b_entry.jetPt)
      assert(self.jet.eta() == b_entry.jetEta)
      self.CvsB = Struct.from_entry(b_entry)
   
