from rootpy.plotting import Hist
import os
import pickle

#yes, everything hardcoded
plots = {
   'pt' : Hist(200, 0, 1000),
   'pt_zoom' : Hist(10, 0, 50),
   'eta' : Hist(300, -3, 3),
   'njets' : Hist(20, 0, 20),
}

for name in ['CvsL', 'CvsB']:
   plots[name] = {}
   plots[name]['output'  ] = Hist(400, -2, 2)
   plots[name]['output_C'] = Hist(400, -2, 2)
   plots[name]['output_L'] = Hist(400, -2, 2)
   plots[name]['output_B'] = Hist(400, -2, 2)

plots['trainingvars'] = {}
with open('historanges.db') as infile:
   ranges = pickle.load(infile)
   for name, hrange in ranges.iteritems():
      if hrange[0] == hrange[1]:
         hrange = -1, 1
      plots['trainingvars'][name] = Hist(200, *hrange)
