import os, sys
from numpy import sqrt
from ROOT import *
gROOT.SetBatch(1)
from plotterconf import *
from plotter.Graphs import GetGraph
from array import array

outname = 'xsec_vs_mass'
mnom = 172.5
xsecnom = 60.87
xsecunc = 5.85
Lumi = 304.32

def DrawTLatex(x,y, tsize, align, text):
  tl = TLatex(x, y, text);
  tl.SetNDC      (True);
  tl.SetTextAlign( align);
  tl.SetTextFont (    42);
  tl.SetTextSize ( tsize);
  #tl.Draw("same");
  return tl

def DrawTopMassFit(mass, xsec, xsecerr=[], mode='lin'):
  n = len(mass)
  x = mass; xerr = [0]*n; y = xsec; yerr = xsecerr
  
  c = TCanvas("c", "Graph", 10, 10, 1200, 800);
  gr = GetGraph(x, y, xerr, yerr, markerStyle=20, markerSize=1, markerColor=1)
  gr.SetMarkerStyle(20);
  gr.GetXaxis().SetTitle('top quaark mass (GeV)')
  gr.GetYaxis().SetTitle('t#bar{t} cross section (pb)')
  gr.SetTitle('')#5.02 TeV, %1.1f pb^{-1}'%Lumi)
   
  gr.Draw("APEL");
  funlin = lambda x, parameters: xsecnom*(1+parameters[0]*(x[0]-mnom))
  tl = []
  

  tl.append(DrawTLatex(0.10, 0.93, 0.035, 11, "e#mu, #geq 2jets"))
  tl.append(DrawTLatex(0.94, 0.93, 0.035, 31, "%1.1f pb^{-1} (5.02 TeV)"%Lumi))

  if(mode == 'lin'):
    x = array('f', [0,0])
    fun = TF1("flin",funlin,165,180,1);
    f = gr.Fit(fun, "s")# "", 165, 180);
    p0 = f.Parameter(0); e0 = f.ParError(0);# "xs*(1+k(x-x0))" 
    ds  = xsecnom*0.5*p0
    dse = xsecnom*0.5*e0
    tl.append(DrawTLatex(0.85, 0.88, 0.035, 33, "m_{t}^{0} = %1.1f, #sigma_{t#bar{t}}(m_{t}^{0}) = %1.1f #pm %1.1f pb"%(mnom, xsecnom, xsecunc)))
    tl.append(DrawTLatex(0.85, 0.81, 0.035, 33, "#sigma_{t#bar{t}}(m_{t}) = #sigma_{t#bar{t}}(m_{t}^{0})*(1+k(m_{t}-m_{t}^{0}))"))
    tl.append(DrawTLatex(0.84, 0.73, 0.035, 33, "k = %2.5f #pm %1.5f (%1.2f %s)"%(p0, e0, abs(e0/p0*100), '%') ))
    tl.append(DrawTLatex(0.12, 0.17, 0.035, 13, "#Delta#sigma_{t#bar{t}}(0.5 GeV) = %1.5f #pm %1.5f pb"%(ds, dse) ))
  
  elif(mode == "pol"):
    f = gr.Fit("pol2", "s", "", 165, 180);
    p0 = f.Parameter(0); p1 = f.Parameter(1); p2 = f.Parameter(2);
    DrawTLatex(0.55, 0.88, 0.035, 33, "Fit: #sigma_{t#bar{t}}(13TeV,m_{top}) = a m_{top}^{2} + b m_{top} + c")
    DrawTLatex(0.75, 0.83, 0.035, 33, "a=%4.3f (pb/GeV)^{2}\n,  b=%4.3f (pb/GeV)\n,  c=%4.3f pb"%(p2,p1,p0) )

  elif(mode == "exp"):
    f = gr.Fit("expo", "s", "", 165, 180);
    p0 = f.Parameter(0); p1 = f.Parameter(1);
    DrawTLatex(0.65, 0.88, 0.035, 33, "Fit: exp(a+bm_{top})      a=%4.3f     b=%4.3f GeV^{-1}"%(p0, p1))

  fun.Draw("same")
  for t in tl: t.Draw()
  #gr.GetYaxis().SetLimits(740,860); gr.SetMinimum(740); gr.SetMaximum(860);
  #gr.GetXaxis().SetLimits(165,180);

  c.SetRightMargin(0.03)
  c.Update();
  for form in ['png', 'pdf']: c.Print(outpath+outname + '_' + mode + '.' + form)


ch = 'ElMu'
lev = '2jets'
level = {'dilepton':1, 'ZVeto':2, 'MET':3, '2jets':4, '1btag':5}

# Get acceptance numbers
from plotter.TopHistoReader import TopHistoReader
thr = TopHistoReader(path)
dic = {'tt':'TT', 'up':'TT_mtop178p5', 'down':'TT_mtop166p5'}
GetAcc = lambda samp, ch, lev : thr.GetNamedHisto('Lep0Eta_%s_%s'%(ch,lev), dic[samp]).Integral()
GetUnc = lambda samp, ch, lev : thr.GetNamedHisto('Yields_%s'%(ch), dic[samp]).GetBinError(level[lev])
nom = GetAcc('tt', ch, lev)
up  = GetAcc('up', ch, lev)
do  = GetAcc('down', ch, lev)

mass = [166.5, 172.5, 178.5]
xsec = [xsecnom*(nom/do), xsecnom, xsecnom*(nom/up)]
#= [xsecunc*(nom/do), xsecunc, xsecunc*(nom/up)]
xsecerr = [GetUnc(x, ch, lev) for x in ['down', 'tt', 'up']]
DrawTopMassFit(mass, xsec, xsecerr, 'lin')
