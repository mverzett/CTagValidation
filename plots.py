from rootpy.plotting import Hist

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
