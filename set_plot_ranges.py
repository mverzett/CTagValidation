from RecoBTag.CTagging.helpers import get_vars
import math
import rootpy.io as io
import pickle
import os

mva_vars_cl = set([i.name.value() for i in get_vars('%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE'])])
mva_vars_cb = set([i.name.value() for i in get_vars('%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])])
mva_vars_cl.update(mva_vars_cb)
mva_vars_cl.add('vertexCategory')
#automatic set mins and maxes
mms_vars = dict((i, (float('inf'), float('-inf'))) for i in mva_vars_cl)


debug_CvsL_file = io.root_open('trees/ctag_debug_CvsL.root')
debug_CvsL_tree = debug_CvsL_file.tree
for entry in debug_CvsL_tree:
   for name, minmax in mms_vars.iteritems():
      min_val, max_val = minmax
      val = getattr(entry, name)
      min_val = min(min_val, val)
      max_val = max(max_val, val)
      mms_vars[name] = (min_val, max_val)


flat_file = io.root_open('trees/CombinedSV_ALL.root')
flat_tree = flat_file.tree
for entry in debug_CvsL_tree:
   for name, minmax in mms_vars.iteritems():
      min_val, max_val = minmax
      val = getattr(entry, name)
      min_val = min(min_val, val)
      max_val = max(max_val, val)
      mms_vars[name] = (min_val, max_val)
      
with open('historanges.db', 'wb') as out:
   pickle.dump(mms_vars, out)
