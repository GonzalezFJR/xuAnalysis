import os, sys
from numpy import sqrt
from ROOT import *
gROOT.SetBatch(1)
from plotterconf import *

outname = 'xsec5TeV'

class xsecval:
 def __init__(self, lab, val, stat=0, syst=0, lum=0):
   self.lab = lab
   self.val  = float(val)
   self.stat = float(stat)
   self.syst = float(syst)
   self.lum  = float(lum)

 def SetRelUnc(self, stat=None, syst=None, lum=None, val=None):
   if val  != None: self.val = val
   if stat != None: self.stat = self.val*stat
   if syst != None: self.syst = self.val*syst
   if lum  != None: self.lum  = self.val*lum 

 def SystAndStat2(self):
   return self.stat*self.stat + self.syst*self.syst

 def SystAndStat(self):
   return sqrt(self.SystAndStat2())

 def Total2(self):
   return self.lum*self.lum + self.SystAndStat2()

 def Total(self):
   return sqrt(self.Total2())

def DrawTLatex(tfont, x, y, tsize, align, text, setndc=True):
  tl = TLatex(x, y, text);
  tl.SetNDC      (setndc);
  tl.SetTextAlign( align);
  tl.SetTextFont ( tfont);
  tl.SetTextSize ( tsize);
  tl.Draw("same");
  return tl

def DrawTLegend(x1, y1, x2, y2, hist, label, tsize=0.03, option = 'f'):
  legend = TLegend(x1, y1, x2, y2)
  legend.SetBorderSize(    0);
  legend.SetFillColor (    0);
  #legend.SetTextAlign (   12);
  #legend.SetTextFont  (   42);
  legend.SetTextSize  (tsize);
  legend.AddEntry(hist, label, option);
  legend.Draw();
  return legend;


 
# Theory
xsec    = 68.9
xsecunc = 0.06 # %

def DrawFig(xsecfile = '', values = ''):
  if not os.path.isfile(xsecfile) and xsecfile != '':
    print 'File does not exist!'
    return
  outdir = outpath
  measurements = []
  if os.path.isfile(xsecfile):
    f = open(xsecfile)
    for l in f.readlines():
      if l.replace(' ', '') in ['', '\\']: continue
      vals = l.split(' ')
      if len(vals) != 5: continue
      label, val, stat, syst, lum = vals
      measurements.append(xsecval(label, val, stat, syst, lum))
    outdir = xsecfile[:-xsecfile[::-1].index('/')]

  if ',' in values: values = values.split(',')
  if isinstance(values, list):
    for v in values:
      if len(v) != 5: continue
      label, val, stat, syst, lum = v
      measurements.append(xsecval(label, val, stat, syst, lum))

  nChannel = len(measurements)

  gstat = TGraphErrors(nChannel);
  gsyst = TGraphErrors(nChannel);
  glumi = TGraphErrors(nChannel);

  text = []
  for i in range(nChannel):
    m = measurements[i]
    gstat.SetPointError(i, m.stat, 0.25);
    gsyst.SetPointError(i, m.SystAndStat(), 0.25);
    glumi.SetPointError(i, m.Total(),  0.25);
    gstat.SetPoint(i, m.val, nChannel-i);
    gsyst.SetPoint(i, m.val, nChannel-i);
    glumi.SetPoint(i, m.val, nChannel-i);
    txt = "%1.2f #pm %1.2f pb"%(m.val, m.Total()) 
    tx2 = "(%1.1f %s)" %( m.Total()/m.val*100, '%')
    text.append(DrawTLatex(52, 15, nChannel-i+0.15,  0.045, 12, m.lab, False))
    text.append(DrawTLatex(52, 15, nChannel-i-0.03,  0.028, 12, txt, False))
    text.append(DrawTLatex(52, 15, nChannel-i-0.17, 0.026, 12, tx2, False))
      
  gstat.SetFillColorAlpha(kTeal+2, 0.8);
  gstat.SetLineWidth  (0);
  gstat.SetMarkerColor(kWhite);
  gstat.SetMarkerSize (0.8);
  gstat.SetMarkerStyle(kFullCircle);
  gsyst.SetFillColor(kCyan+2);
  gsyst.SetLineWidth(0);
  glumi.SetFillColor(kAzure+2);
  glumi.SetLineWidth(0);

  
  canvas = TCanvas('c', 'c')
  canvas.SetLeftMargin(canvas.GetRightMargin());
  margin = 0.9
  xmin = xsec*(1-margin); xmax = xsec*(1+margin)
  ymin = 0.2; ymax = nChannel + ymin + 0.6;
  
  h2 = TH2F("h2", "", 100, xmin, xmax, 100, ymin, ymax);
  h2.SetStats(0)
  h2.Draw();
  
  xsecbox = TBox(xsec*(1-xsecunc), ymin, xsec*(1+xsecunc), ymax);

  xsecbox.SetLineColor(0);
  xsecbox.SetFillColor(kGray+1);
  xsecbox.SetFillStyle(1001);
  xsecbox.Draw("e2,same");


  glumi.Draw("p2,same");
  gsyst.Draw("p2,same");
  gstat.Draw("p2,same");

  text.append(DrawTLatex(42, 0.65, 0.935, 0.04, 12, '296.1 pb^{-1} (5.02 TeV)'))
  text.append(DrawTLatex(61, 0.10, 0.93, 0.06, 11, "CMS"))
  text.append(DrawTLatex(52, 0.195, 0.925, 0.052, 11, "Preliminary"))

  h2.GetXaxis().CenterTitle();
  h2.GetXaxis().SetTitle("t#bar{t} cross section (pb)");
  h2.GetXaxis().SetTitleSize(0.05);
  h2.GetXaxis().SetTitleOffset(0.85);
  h2.GetYaxis().SetTitle("");
  yaxis = h2.GetYaxis();
  for i in range(1, h2.GetYaxis().GetNbins()): h2.GetYaxis().SetBinLabel(i, '')
  
  hempty = TH1F()
  legends = []
  legends.append(DrawTLegend(0.65, 0.6, 0.85, 0.66, xsecbox,  "#splitline{NNLO+NNLL}{prediction}"))
  legends.append(DrawTLegend(0.65, 0.7, 0.85, 0.76, gstat,   "Statistical"))
  legends.append(DrawTLegend(0.65, 0.8, 0.85, 0.86, gsyst,   "Systematic"))
  #legends.append(DrawTLegend(0.65, 0.5, 0.85, 0.56, glumi,   "Luminosity"))
  for l in legends: l.Draw()
  for t in text:    t.Draw()

  #canvas.Update();
  #canvas.GetFrame().DrawClone();
  canvas.RedrawAxis();
  canvas.SaveAs(outdir+outname+".pdf");
  canvas.SaveAs(outdir+outname+".png");

import argparse
parser = argparse.ArgumentParser(description='Plot cross sections')
parser.add_argument('--path','-p'       , default=''       , help = 'path')
parser.add_argument('--file','-f'       , default=''       , help = 'File name')
parser.add_argument('--values','-v'       , default=''       , help = 'values')
args = parser.parse_args()

if args.path == '': args.path = outpath
if args.file == '': args.file = 'ttxsec.txt'
if   os.path.isfile(args.path):  xsecfile = args.path
elif os.path.isdir(args.path):  xsecfile = args.path+args.file

if not os.path.isfile(xsecfile): xsecfile = ''
values = args.values

DrawFig(xsecfile, values)
