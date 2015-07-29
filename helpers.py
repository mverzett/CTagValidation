
def dict2tdir(hdict, tdir):
   for name, val in hdict.iteritems():
      if isinstance(val, dict):
         subdir = tdir.mkdir(name)
         dict2tdir(val, subdir)
      else:
         tdir.WriteTObject(val, name)

