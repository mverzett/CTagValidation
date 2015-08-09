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

   canvas = plotting.Canvas(800, 600)
   canvas.set_logy(True)
   #print  flavor, name
   #set_trace()

   histo = inview.Get(path)
   histo.title = histo.name
   m = max(i.value for i in histo)
   histo.yaxis.range_user = (0.1, 3*m)
   histo.Draw()
   
   canvas.SaveAs('%s/%s.png' % (plot_dir, path))
   canvas.SaveAs('%s/%s.pdf' % (plot_dir, path))

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
