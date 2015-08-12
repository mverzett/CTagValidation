import rootpy.io as io
import rootpy.plotting as plotting
import rootpy.plotting.views as views
from rootpy.plotting.style import set_style
#set_style('cmstdr')
import os
import ROOT
from pdb import set_trace
from RecoBTag.CTagging.helpers import get_vars
from helpers import mkdir

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


plotdir = 'diff_%s' % os.environ['tag']
train_var_out = {
   -1 : '%s/single_value' % plotdir,
    0 : '%s/vectorial/0th' % plotdir,
    1 : '%s/vectorial/1st' % plotdir,
    2 : '%s/vectorial/2nd' % plotdir,
    3 : '%s/vectorial/3rd+' % plotdir
}
for i in train_var_out.values():
   mkdir(i)

infile = io.root_open('analyzed/jet_by_jet_diff.root')
inview = views.StyleView(
   infile,
   fillstyle = 'hollow',
   linewidth = 2,
   markerstyle= 0,
   drawstyle='hist',
   legendstyle='l',
   linecolor = 'black'
   )
histos = [i.name for i in infile.keys()]

for path in histos:
   plot_dir = ''
   if path[-1].isdigit():
      idx = int(path.split('_')[-1])
      plot_dir = train_var_out.get(idx, train_var_out[3])
   else:
      plot_dir = train_var_out[-1]

   if path == 'SameValRate' or path == 'DiffAndDefaulted':      
      canvas = plotting.Canvas(1500, 900)
      canvas.set_top_margin(0.001)
      canvas.set_bottom_margin(0.5)
   else:
      canvas = plotting.Canvas(800, 600)
      
   #print  flavor, name
   #set_trace()

   histo = inview.Get(path)
   histo.title = histo.name
   m = max(i.value for i in histo)
   if path == 'SameValRate' or path == 'DiffAndDefaulted':
      histo.yaxis.range_user = (0.8, 1.3)
   else:
      canvas.set_logy(True)
      histo.yaxis.range_user = (0.1, 3*m)

   histo.Draw()
   
   canvas.SaveAs('%s/%s.png' % (plot_dir, path))
   canvas.SaveAs('%s/%s.pdf' % (plot_dir, path))

with open('%s/same_value_rate.raw_txt' % plot_dir, 'w') as table:
   histo = inview.Get('SameValRate')
   labels = [histo.xaxis.get_bin_label(i) for i, _ in enumerate(histo)]
   mlen = max(len(i) for i in labels)
   format = '%-'+str(mlen)+'s %.2f\n'
   for bin, label in zip(histo, labels):
      table.write(format % (label, bin.value))

##    to_keep = []
##    first = True
##    for info, color in zip(shapes.iteritems(), colors):
##       dname, shape = info
##       shape.title = dname
##       shape.linecolor = color
##       opts = '' if first else 'same'
##       shape.Draw(opts)
##       first = False
##       legend.AddEntry(shape)
##       to_keep.append(shape)
##    legend.Draw()
##    canvas.SaveAs("plots/%sjet_shapes.png" % name)
##    canvas.SaveAs("plots/%sjet_shapes.pdf" % name)   
## pat_input.close()
