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

inputs = {
   'pat' : io.root_open('analyzed/pat_validation_output.root'),
   'flat_tree' : io.root_open('analyzed/flat_tree_output.root'),
   'varex_tree' : io.root_open('analyzed/varex_output.root'),
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
 'varex_tree' : dict((i, {}) for i in flavors),
}

colors = ['#ab5555', '#FFCC66', '#2aa198']
plotdir = 'plots_%s' % os.environ['tag']
mkdir(plotdir)

for prefix, infile in inputs.iteritems():
   mkdir('%s/%s' % (plotdir, prefix))

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
      canvas.SaveAs("%s/%s/%s_output.png" % (plotdir, prefix, name))
      canvas.SaveAs("%s/%s/%s_output.pdf" % (plotdir, prefix, name))
      
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

      canvas.SaveAs("%s/%s/%s_shape.png" % (plotdir, prefix, name))
      canvas.SaveAs("%s/%s/%s_shape.pdf" % (plotdir, prefix, name))

      disc_shapes[prefix]['c'][name] = cshape
      disc_shapes[prefix]['b'][name] = bshape
      disc_shapes[prefix]['l'][name] = lshape
      disc_shapes[prefix]['sum'][name] = cjets + bjets + ljets
      disc_shapes[prefix]['sum'][name].fillstyle = 'hollow'      
      disc_shapes[prefix]['sum'][name].linewidth = 2
      disc_shapes[prefix]['sum'][name].drawstyle = 'hist'
      disc_shapes[prefix]['sum'][name].legendstyle = 'l'


mkdir('%s/comparison' % plotdir)
train_var_out = {
   -1 : '%s/comparison/single_value' % plotdir,
    0 : '%s/comparison/vectorial/0th' % plotdir,
    1 : '%s/comparison/vectorial/1st' % plotdir,
    2 : '%s/comparison/vectorial/2nd' % plotdir,
    3 : '%s/comparison/vectorial/3rd+' % plotdir
}
for i in train_var_out.values():
   mkdir(i)

comparison_inputs = [
   views.TitleView(
      views.StyleView(
         inputs['pat'], 
         fillstyle = 'hollow',
         linewidth = 2,
         markerstyle= 0,
         drawstyle='hist',
         legendstyle='l',
         linecolor = colors[0]
         ),
      'from PAT' 
      ),
   views.TitleView(
      views.StyleView(
         inputs['flat_tree'], 
         fillstyle = 'hollow',
         linewidth = 2,
         markerstyle= 0,
         drawstyle='hist',
         legendstyle='l',
         linecolor = colors[1]
         ),
      'from flat tree'
      ),
   views.TitleView(
      views.StyleView(
         inputs['varex_tree'], 
         fillstyle = 'hollow',
         linewidth = 2,
         markerstyle= 0,
         drawstyle='hist',
         legendstyle='l',
         linecolor = colors[2]
         ),
      'from VarExtractor'
      )
   ]

to_compare = [
   {'rbin' : 8, 'png' : 'CvsL_MVA_B', 'path' : 'CvsL/output_B', 'norm' : False, 'title' : 'CvsL, B jets',     'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsL_MVA_C', 'path' : 'CvsL/output_C', 'norm' : False, 'title' : 'CvsL, charm jets', 'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsL_MVA_L', 'path' : 'CvsL/output_L', 'norm' : False, 'title' : 'CvsL, light jets', 'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsL_MVA'  , 'path' : 'CvsL/output'  , 'norm' : False, 'title' : 'CvsL, all jets',  'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsB_MVA_B', 'path' : 'CvsB/output_B', 'norm' : False, 'title' : 'CvsB, B jets',     'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsB_MVA_C', 'path' : 'CvsB/output_C', 'norm' : False, 'title' : 'CvsB, charm jets', 'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsB_MVA_L', 'path' : 'CvsB/output_L', 'norm' : False, 'title' : 'CvsB, light jets', 'xtitle' : 'MVA output'},
   {'rbin' : 8, 'png' : 'CvsB_MVA'  , 'path' : 'CvsB/output'  , 'norm' : False, 'title' : 'CvsB, all jets',  'xtitle' : 'MVA output'},
   {'rbin' : 4, 'png' : 'jet_pt'    , 'path' : 'pt'      , 'norm' : False, 'title' : 'jet p_{T}',       'xtitle' : 'jet p_{T}'},
   {'rbin' : 4, 'png' : 'jet_eta'   , 'path' : 'eta'     , 'norm' : False, 'title' : 'jet #eta',        'xtitle' : 'jet #eta'},
   {'rbin' : 1, 'png' : 'jet_pt_zoom', 'path': 'pt_zoom', 'norm' : False, 'title' : 'jet p_{T}', 'xtitle' : 'jet p_{T}'},
   {'rbin' : 1, 'png' : 'njets'     , 'path' : 'njets'  , 'norm' : False, 'title' : '# jets', 'xtitle' : '# jets'},
]
mva_vars = [i.name.value() for i in get_vars('%s/src/RecoBTag/CTagging/data/c_vs_udsg.weight.xml' % os.environ['CMSSW_BASE'])]
for name in mva_vars:
   to_compare.append(
      {'rbin' : 4, 'png' : '%s' % name, 'path' : 'trainingvars/%s' % name, 'norm' : False, 'title' : '%s' % name, 'xtitle' : '%s' % name}
      )
## mva_vars = [i.name.value() for i in get_vars('%s/src/RecoBTag/CTagging/data/c_vs_b.weight.xml' % os.environ['CMSSW_BASE'])]
## for name in mva_vars:
##    to_compare.append(
##       {'rbin' : 1, 'png' : 'name', 'path' : 'CvsB/%s' % name, 'norm' : False, 'title' : '%s' % name, 'xtitle' : '%s' % name}
##       )

for info in to_compare:
   #infer output dir
   plot_dir = '%s/comparison' % plotdir
   if info['path'].startswith('trainingvars'):
      if info['path'][-1].isdigit():
         idx = int(info['path'].split('_')[-1])
         plot_dir = train_var_out.get(idx, train_var_out[3])
      else:
         plot_dir = train_var_out[-1]

   canvas = plotting.Canvas(600, 800)
   pad1 = plotting.Pad(0,0.33,1,1)
   pad1.Draw()
   pad1.cd()

   legend = plotting.Legend(len(comparison_inputs), rightmargin=0.07, topmargin=0.05, leftmargin=0.45)
   legend.SetHeader(info['title'])
   legend.SetBorderSize(0)
   #print  flavor, name
   #set_trace()

   histos = [i.Get(info['path']) for i in comparison_inputs]

   for h in histos:
      h.Rebin(info['rbin']) 
      h.xaxis.title = info['xtitle']   
      if info['norm']: 
         h.yaxis.title =  'Entries (normalized)'
         h.Scale(1./pat.Integral())
      else:
         h.yaxis.title =  'Entries'

   #set range
   ymax = max(
      max(i.value for i in h) for h in histos
      )
   ymin = min(
      min(i.value for i in h) for h in histos
      )
   ymin = min(ymin, 0.)

   first = True
   for h in histos:
      h.yaxis.range_user = (ymin, ymax*1.2)
      legend.AddEntry(h)   
      dopts = '' if first else 'same'
      first = False
      h.Draw(dopts)
   legend.Draw()

   canvas.cd()
   pad2 = plotting.Pad(0,0,1,0.33)
   pad2.Draw()
   pad2.cd()
   
   ratios = [i.Clone() for i in histos]
   first = True
   for ratio in ratios:
      ratio.Divide(histos[0])
      ratio.yaxis.title = 'ratio (/PAT)'
      ratio.yaxis.range_user = (0.5, 1.5)
      opts = '' if first else 'same'
      ratio.Draw(opts)
   
   ## one = plotting.F1('1', *ratio.xaxis.range_user)
   ## one.Draw('same')
   ## one.linecolor = colors[0]
   
   canvas.SaveAs('%s/%s.png' % (plot_dir, info['png']))
   canvas.SaveAs('%s/%s.pdf' % (plot_dir, info['png']))

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
