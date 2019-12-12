import os
from ROOT import TH2F, TCanvas, gROOT, TFile, TGraph, TLegend, TLatex
from ROOT import kOrange, kGreen, kRed, kAzure, kYellow, kGray
gROOT.SetBatch(1)
outputdir = './'

scalefact = 1 #1.15
lumi = 59.74 #137.2 #35.9 59.74

def GetDic(pname = 'limits.p', diag = -1):
  import pickle
  if not os.path.isfile(pname): return None
  results = pickle.load( open( pname, "rb" ) )
  limits = {}
  limits['mstop'] = []; limits['mlsp' ] = []
  limits['s+2'  ] = []; limits['s+1'  ] = []
  limits['exp'  ] = []; limits['obs'  ] = []
  limits['s-1'  ] = []; limits['s-2'  ] = []
  for  ms, ml, res in results:
    if diag != -1 and not (ms - ml == diag): continue
    limits['mstop'].append(ms); limits['mlsp'].append(ml)
    limits['s-2'].append(res[0])
    limits['s-1'].append(res[1])
    limits['exp'].append(res[2])
    limits['s+1'].append(res[3])
    limits['s+2'].append(res[4])
    if len(res) >= 6: limits['obs'].append(limits[5])
  return limits

def Get2Dhisto(pname = 'limits.p', tag = 'exp'):
  dic = GetDic(pname)
  mstop = dic['mstop']
  mlsp  = dic['mlsp']
  minstop = min(mstop)
  minlsp  = min(mlsp)
  maxstop = max(mstop)
  maxlsp  = max(mlsp)
  nbinsStop = (maxstop - minstop)/10 + 1
  nbinsLsp  = (maxlsp  - minlsp )/10 + 1
  h = TH2F('h', 'h', nbinsStop, minstop, maxstop+10, nbinsLsp, minlsp, maxlsp+10)
  for i in range(len(mstop)):
    ms = mstop[i]
    ml = mlsp[i]
    e  = dic[tag][i]
    h.SetBinContent(h.FindBin(ms, ml, 1), e)
  h.SetStats(0)
  h.SetTitle('')
  h.GetXaxis().SetTitle('Stop mass (GeV)')
  h.GetYaxis().SetTitle('Neutralino mass (GeV)')
  h.SetDirectory(0)
  return h

def SaveHistos(outname = 'hlimits.root', pname = 'limits.p'):
  f = TFile(outname, 'RECREATE') 
  tags = ['s+2', 's+1', 'exp', 's-1', 's-2']
  for tag in tags:
    h = Get2Dhisto(pname, tag)
    h.SetName(tag)
    h.Write()
  f.Close()

def Draw2Dhisto(tag = 'exp', pname = 'limits'):
  h = Get2Dhisto(pname+'.p', 'exp')
  c = TCanvas('c', 'c', 10, 10, 800, 600)
  h.Draw('colz')
  c.Print(pname+'.png')
  c.Print(pname+'.pdf')

def DrawBazil(diagonal = 175, doData = False, pname = 'limits'):
  import numpy as np
  # 'mstop','mlsp','sm2','sm1','central','sp1','sp2', 'data'
  d = GetDic(pname+'.p', diagonal)
  x = np.array(d['mstop']); e = np.array(d['exp']) 
  y1max = np.array(d['s+1']); y2max = np.array(d['s+2']) 
  y1min = np.array(d['s-1']); y2min = np.array(d['s-2']) 
  # observed
  if(doData): o = np.array(d['obs'])
  else:       o = np.array(d['exp'])

  c1 = TCanvas("c1","CL",10,10,800,600); #c1.SetGrid();

  ymax = 7.5; ymin = 0.3 
  if(  diagonal == 'down' or diagonal == 'Down' or diagonal == 'DOWN'): 
    ymax = 3.1; ymin = 0.30
  elif(diagonal == 'up'   or diagonal == 'Up'   or diagonal == 'UP'  ): 
    ymax = 2.5; ymin = 0.15

  #c1.DrawFrame(min(x)-2,min(d['sp2']+d['sm2'])-0.2,max(x)+2,max(d['sp2']+d['sm2'])+0.2);
  c1.DrawFrame(min(x), ymin, max(x),ymax);

  n = len(e)
  gr1min = TGraph(n,x,y1min); gr1max = TGraph(n,x,y1max);
  gr2min = TGraph(n,x,y2min); gr2max = TGraph(n,x,y2max);
  gro    = TGraph(n,x,o);  gre = TGraph(n,x,e);
  gh     = TGraph(n,x, np.linspace(0.999,1,n));
  gr1shade = TGraph(2*n);  gr2shade = TGraph(2*n);

  #color1shade = 3; color2shade = 5;
  color1shade = kOrange; color2shade = kGreen+1;
  for i in range(n):
    gr1shade.SetPoint(i,x[i],y1max[i]*scalefact);
    gr1shade.SetPoint(n+i,x[n-i-1],y1min[n-i-1]*scalefact);
    gr2shade.SetPoint(i,x[i],y2max[i]*scalefact);
    gr2shade.SetPoint(n+i,x[n-i-1],y2min[n-i-1]*scalefact);
    gre.SetPoint(i, x[i], e[i]*scalefact)
    gh. SetPoint(i, x[i], np.linspace(0.999,1,n)[i]*scalefact)
    gro.SetPoint(i, x[i], o[i]*scalefact if doData else e[i]*scalefact)

  gr2shade.SetFillColor(color2shade); gr2shade.Draw("f");
  gr1shade.SetFillColor(color1shade); gr1shade.Draw("f");
  gh.SetLineWidth( 2); gh. SetMarkerStyle(0 ); gh.SetLineColor(46); gh.SetLineStyle(2); gh.Draw("LP");
  gro.SetLineWidth(2); gro.SetMarkerStyle(20); gro.SetMarkerSize(0.7);  gro.SetLineColor(1); 
  if doData: gro.Draw("LP");
  gre.SetLineWidth(2); gre.SetMarkerStyle(0 ); gre.SetLineColor(1); gre.SetLineStyle(6); gre.Draw("LP");

  gre.SetTitle("Expected"); gro.SetTitle("Observed") 
  gr1shade.SetTitle("Expected 1#sigma"); gr2shade.SetTitle("Expected 2#sigma") 

  leg = TLegend(.1, .65, .4, .9)
  leg.AddEntry(gro);      leg.AddEntry(gre)
  leg.AddEntry(gr1shade,'','f'); leg.AddEntry(gr2shade, '', 'f')
  leg.SetFillColor(0)
  leg.Draw("same")

  gre.SetFillColor(0); gro.SetFillColor(0);
  gr1shade.SetLineColor(color1shade); gr2shade.SetLineColor(color2shade);

  tit  = "m_{#tilde{t}_{1}} - m_{#tilde{#chi}_{1}^{0}} = "
  dm = "0"; ymax = 4.1; ymin = 0.3 
  if(  diagonal == 'down' or diagonal == 'Down' or diagonal == 'DOWN'): 
    tit += "182.5 GeV" #" + 7.5 GeV" 
    dm   = "m7p5"
    ymax = 2.2; ymin = 0.15
    
  elif(diagonal == 'up'   or diagonal == 'Up'   or diagonal == 'UP'  ): 
    tit += "167.5 GeV"#" - 7.5 GeV"
    dm   = "7p5"
    ymax = 3.3; ymin = 0.30
  else:
    tit += "175 GeV"
  Title    = TLatex(); Title.SetTextSize(0.060); Title.DrawLatexNDC(.42, .84, tit)
  Xaxis    = TLatex(); Xaxis.SetTextFont(42); Xaxis.DrawLatexNDC(0.8, 0.03, "m_{#tilde{t}_{1}} (GeV)")
  Yaxis    = TLatex(); Yaxis.SetTextFont(42); Yaxis.SetTextAngle(90); Yaxis.DrawLatexNDC(0.05, 0.15, "95% CL limit on signal strength")
  textCMS  = TLatex(); textCMS.SetTextSize(0.06); textCMS.SetTextSizePixels(22); textCMS.SetTextAlign(12); textCMS.DrawLatexNDC(.12, .93, "CMS")
  textLumi = TLatex(); textLumi.SetTextFont(42); textLumi.SetTextSize(0.06); textLumi.SetTextSizePixels(22); textLumi.DrawLatexNDC(.58, .91, "%1.1f fb^{-1} (13 TeV)"%(lumi) )#35.9

  name = "brazil_%i"%diagonal
  name = "brazil_%s"%pname
  for form in ['pdf', 'png']: c1.Print(outputdir + name + '.%s'%form)


#SaveHistos()
for var in ['met50', 'met160', 'mt2', 'met', 'dnn']: Draw2Dhisto(pname='scan_'+var)

#for var in ['mt2', 'met', 'dnn']: DrawBazil(diagonal = 175, doData = False, pname = 'limits_'+var)
#for var in ['met50', 'met160']: DrawBazil(diagonal = 175, doData = False, pname = 'limits_'+var)
