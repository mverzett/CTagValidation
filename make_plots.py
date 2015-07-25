import rootpy.io as io
import rootpy.plotting as plotting
import rootpy.plotting.views as views
from rootpy.plotting.style import set_style
#set_style('cmstdr')
import os
import ROOT
from pdb import set_trace

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

#utility functions
def make_shape(histo):
   'converts a histo into a shape only (normalizes and removes fill, add line color)'
   ret = histo.Clone()
   ret.Scale(1./ret.Integral())
   ret.linecolor = ret.fillcolor
   ret.fillstyle = 'hollow'
   ret.linewidth = 2
   ret.drawstyle = 'hist'
   ret.legendstyle = 'l'
   return ret

discrims = [
   'CvsL',
   'CvsB',   
]

pat_input = io.root_open('validation_output.root')
flat_input = io.root_open('flat_tree_output.root')
inputs = {
   'pat' : pat_input,
   'flat_tree' : flat_input
   }

flavors = ['c', 'b', 'l', 'sum']
nice_names = {
   'c' : 'charm', 
   'b' : 'b', 
   'l' : 'light', 
   'sum' : 'all'
}

disc_shapes = {
 'pat' : dict((i, {}) for i in flavors),
 'flat_tree' : dict((i, {}) for i in flavors),
}

colors = ['#ab5555', '#FFCC66', '#2aa198']
if not os.path.isdir('plots'):
   os.makedirs('plots')

for prefix, infile in inputs.iteritems():
   if not os.path.isdir('plots/%s' % prefix):
      os.makedirs('plots/%s' % prefix)

   for name in discrims:
      mva_out_view = views.StyleView(
         views.FunctorView(
            infile,
            lambda x: x.Rebin(4)
            ),
         fillstyle = 'solid',
         linewidth = 0,
         markerstyle= 0,
         drawstyle='hist',
         legendstyle='f'
         )

      cjets = mva_out_view.Get('%s/output_C' % name)
      cjets.xaxis.title = 'MVA output'
      cjets.yaxis.title = 'Entries'
      cjets.yaxis.SetTitleOffset(1.4)
      cjets.title = 'charm jets'
      cjets.fillcolor = '#ab5555'
      bjets = mva_out_view.Get('%s/output_B' % name)
      bjets.title = 'b jets'
      bjets.fillcolor = '#FFCC66'
      bjets.xaxis.title = 'MVA output'
      bjets.yaxis.title = 'Entries'
      bjets.yaxis.SetTitleOffset(1.4)
      ljets = mva_out_view.Get('%s/output_L' % name)
      ljets.title = 'light jets'
      ljets.fillcolor = '#2aa198'
      ljets.xaxis.title = 'MVA output'
      ljets.yaxis.title = 'Entries'
      ljets.yaxis.SetTitleOffset(1.4)

      stack = plotting.HistStack()
      stack.Add(cjets)
      stack.Add(ljets)
      stack.Add(bjets)

      canvas = plotting.Canvas()
      canvas.SetLogy(True)
      legend = plotting.Legend(3, rightmargin=0.07, topmargin=0.05, leftmargin=0.45)
      legend.AddEntry(stack)
      
      stack.Draw()
      legend.Draw()
      canvas.SaveAs("plots/%s/%s_output.png" % (prefix, name))
      canvas.SaveAs("plots/%s/%s_output.pdf" % (prefix, name))
      
      cshape = make_shape(cjets)
      bshape = make_shape(bjets)
      lshape = make_shape(ljets)
      cshape.yaxis.title = 'Entries (normalized)'
      bshape.yaxis.title = 'Entries (normalized)'
      lshape.yaxis.title = 'Entries (normalized)'
      cshape.Draw()
      bshape.Draw('same')
      lshape.Draw('same')

      legend = plotting.Legend(3, rightmargin=0.07, topmargin=0.05, leftmargin=0.45)
      legend.AddEntry(cshape)
      legend.AddEntry(bshape)
      legend.AddEntry(lshape)
      legend.Draw()

      canvas.SaveAs("plots/%s/%s_shape.png" % (prefix, name))
      canvas.SaveAs("plots/%s/%s_shape.pdf" % (prefix, name))

      disc_shapes[prefix]['c'][name] = cshape
      disc_shapes[prefix]['b'][name] = bshape
      disc_shapes[prefix]['l'][name] = lshape
      disc_shapes[prefix]['sum'][name] = cjets + bjets + ljets
      disc_shapes[prefix]['sum'][name].fillstyle = 'hollow'      
      disc_shapes[prefix]['sum'][name].linewidth = 2
      disc_shapes[prefix]['sum'][name].drawstyle = 'hist'
      disc_shapes[prefix]['sum'][name].legendstyle = 'l'


if not os.path.isdir('plots/comparison'):
   os.makedirs('plots/comparison')

for flavor in flavors:
   for name in discrims:
      canvas = plotting.Canvas(600, 800)
      pad1 = plotting.Pad(0,0.33,1,1)
      pad1.Draw()
      pad1.cd()

      legend = plotting.Legend(2, rightmargin=0.07, topmargin=0.05, leftmargin=0.45)
      legend.SetHeader('%s, %s jets' % (name, flavor))
      legend.SetBorderSize(0)
      #print  flavor, name
      #set_trace()
      pat = disc_shapes['pat'][flavor][name]
      flat = disc_shapes['flat_tree'][flavor][name]

      pat.title = 'from PAT'
      flat.title = 'from flat tree'
      
      pat.linecolor = colors[0]
      flat.linecolor = colors[1]
      
      legend.AddEntry(pat)
      legend.AddEntry(flat)
      
      pat.Draw()
      flat.Draw('same')
      legend.Draw()

      canvas.cd()
      pad2 = plotting.Pad(0,0,1,0.33)
      pad2.Draw()
      pad2.cd()
      
      ratio = pat.Clone()
      ratio.Divide(flat)
      ratio.drawstyle = 'p'
      ratio.linecolor = 'black'      
      ratio.yaxis.title = 'ratio (PAT/tree)'
      ratio.Draw()

      one = plotting.F1('1', *ratio.xaxis.range_user)
      one.Draw('same')
      one.linecolor = colors[0]
      
      canvas.SaveAs('plots/comparison/%s_%s.png' % (flavor, name))
      canvas.SaveAs('plots/comparison/%s_%s.pdf' % (flavor, name))

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
