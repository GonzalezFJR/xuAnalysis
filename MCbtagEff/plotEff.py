from ROOT import TFile, TH1F, TH2F, TLatex, TCanvas, gROOT, gStyle, TGraph, TLegend, TLine, TMultiGraph
from ROOT import kAzure, kRed, kOrange, kTeal, kViolet, kSpring, kGray, kBlack

gROOT.SetBatch(1)

path = {
  2017 : 'Efficiencies/TTTo2L2Nu.root',
  2018 : 'Efficiencies/TTTo2L2Nu.root',
  }
outpath = './plots/'

def GetTLatex(t, x, y, s = 0.04):
  t = TLatex(-20, 50, t);
  t.SetNDC();
  t.SetTextAlign(12);
  t.SetX(x);
  t.SetY(y);
  t.SetTextFont(42);
  t.SetTextSize(s);
  t.Draw()
  return t

def GetHisto(fname, hname, col = 1, lst = 1):
  f = TFile.Open(fname)
  h = f.Get(hname)
  #print 'Getting histogram %s in file %s'%(hname, fname)
  h.SetStats(0)
  h.SetLineWidth(2)
  h.SetDirectory(0)
  h.SetMarkerColor(col)
  h.SetLineColor(col)
  h.SetLineStyle(lst)
  f.Close()
  return h

def Get2D(fname, hname):
  #print 'Opening file %s, histo %s'%(fname, hname)
  f = TFile.Open(fname)
  h = f.Get(hname)
  h.SetStats(0)
  h.SetDirectory(0)
  f.Close()
  return h

def GetAcu(fname, hname, col = 1, lst = 1):
  h = GetHisto(fname,hname,col,lst)
  nb = h.GetNbinsX()
  #h2 = h.Clone('%s2'%hname)
  s = h.GetBinContent(nb+1)
  for i in range(1,nb+1):
    ti = nb+1-i
    bc  = h.GetBinContent(ti)
    s += bc
    h.SetBinContent(ti, s)
  norm = h.GetBinContent(1)
  h.Scale(1/norm)
  return h

def GetRatioCurve(fname, hname, hname2, col = 1, lst = 1):
  h = GetAcu(fname,hname,col,lst)
  m = GetAcu(fname,hname2,col,lst)
  nb = h.GetNbinsX()
  g = TGraph(nb+1)
  for i in range(1, nb+1):
    bh = h.GetBinContent(i)
    bm = m.GetBinContent(i)
    g.SetPoint(i-1, bh, bm)
  #g.SetPoint(nb, 0, 1)
  g.SetLineWidth(2)
  g.SetLineColor(col)
  g.SetLineStyle(lst)
  g.SetTitle('')
  g.GetXaxis().SetTitle('b jet efficiency')
  g.GetYaxis().SetTitle('Mistag probability')
  return g

def GetAcuGraph(fname, hname, col = 1, lst = 1):
  h = GetAcu(fname, hname, col, lst)
  nb = h.GetNbinsX()
  g = TGraph(nb+1)
  for i in range(1, nb+1):
    y = h.GetBinContent(i)
    x = h.GetBinLowEdge(i)
    g.SetPoint(i-1, x, y)
  g.SetPoint(nb, 1, 0)
  g.SetLineWidth(2)
  g.SetLineStyle(lst)
  g.SetLineColor(col)
  return g


def DrawCurves(year):
  fname = path[year]
  tit  = 'MC b-tag efficiencies for year %i'%year

  c = TCanvas('c', 'c', 10, 10, 1600, 1200)
  c.DrawFrame(0,0,1,1.1)
  hcsv = GetAcuGraph(fname, 'CSVv2B_%i'%year, kAzure+2)
  hdee = GetAcuGraph(fname, 'DeepCSVB_%i'%year, kSpring-9)
  hdfl = GetAcuGraph(fname, 'DFlavB_%i'%year, kRed+1)
  Bforleg = GetAcuGraph(fname, 'DFlavB_%i'%year, 1)

  mcsv = GetAcuGraph(fname, 'CSVv2L_%i'%year, kAzure+2, 3)
  mdee = GetAcuGraph(fname, 'DeepCSVL_%i'%year, kSpring-9, 3)
  mdfl = GetAcuGraph(fname, 'DFlavL_%i'%year, kRed+1, 3)
  Lforleg = GetAcuGraph(fname, 'DFlavL_%i'%year, 1, 3)

  ccsv = GetAcuGraph(fname, 'CSVv2C_%i'%year, kAzure+2, 2)
  cdee = GetAcuGraph(fname, 'DeepCSVC_%i'%year, kSpring-9, 2)
  cdfl = GetAcuGraph(fname, 'DFlavC_%i'%year, kRed+1, 2)
  Cforleg = GetAcuGraph(fname, 'DFlavC_%i'%year, 1, 2)

  hcsv.Draw('xl')
  hdee.Draw('xlsame')
  hdfl.Draw('xlsame')
  mcsv.Draw('xlsame')
  mdee.Draw('xlsame')
  mdfl.Draw('xlsame')
  ccsv.Draw('xlsame')
  cdee.Draw('xlsame')
  cdfl.Draw('xlsame')
  hcsv.SetTitle('')
  hcsv.GetXaxis().SetTitle('Tagger value')
  hcsv.GetYaxis().SetTitle('Efficiency')
  #hcsv.SetMinimum(0)
  #hcsv.SetMaximum(1)

  leg = TLegend(0.28, 0.84, 0.88, 0.90)
  leg.AddEntry(hcsv, 'CSVv2', 'l')
  leg.AddEntry(hdee, 'Deep CSV', 'l')
  leg.AddEntry(hdfl, 'Deep Flavour', 'l')
  leg.SetBorderSize(0)
  leg.SetNColumns(3)
  leg.SetFillStyle(0)
  leg.Draw()

  leg2 = TLegend(0.50, 0.76, 0.88, 0.83)
  leg2.AddEntry(Bforleg, 'b', 'l')
  leg2.AddEntry(Cforleg, 'c', 'l')
  leg2.AddEntry(Lforleg, 'udsg', 'l')
  leg2.SetBorderSize(0)
  leg2.SetFillStyle(0)
  leg2.SetNColumns(3)
  leg2.Draw()

  xax = GetTLatex("Tagger value", 0.67, 0.03, 0.05)
  yax = GetTLatex("b tag probability", 0.02, 0.55, 0.05)
  yax.SetTextAngle(90)

  t = GetTLatex(tit, 0.12, 0.93)
  c.SaveAs(outpath+'BtagEff%i.png'%year)
  c.SaveAs(outpath+'BtagEff%i.pdf'%year)

def DrawRatios(year):
  fname = path[year]

  xmin = 0.1
  c = TCanvas('c', 'c', 10, 10, 1600, 1200)
  c.DrawFrame(xmin,1e-4, 1, 1)
  hcsv = GetRatioCurve(fname, 'CSVv2B_%i'%year,   'CSVv2C_%i'%year,   kAzure+2)
  hdee = GetRatioCurve(fname, 'DeepCSVB_%i'%year, 'DeepCSVC_%i'%year, kSpring-8)
  hdfl = GetRatioCurve(fname, 'DFlavB_%i'%year,   'DFlavC_%i'%year,   kRed+1)
  lcsv = GetRatioCurve(fname, 'CSVv2B_%i'%year,   'CSVv2L_%i'%year,   kAzure+2, 2)
  ldee = GetRatioCurve(fname, 'DeepCSVB_%i'%year, 'DeepCSVL_%i'%year, kSpring-8, 2)
  ldfl = GetRatioCurve(fname, 'DFlavB_%i'%year,   'DFlavL_%i'%year,   kRed+1, 2)
  hforleg = GetRatioCurve(fname, 'CSVv2B_%i'%year,   'CSVv2C_%i'%year,   1, 1)
  lforleg = GetRatioCurve(fname, 'CSVv2B_%i'%year,   'CSVv2L_%i'%year,   1, 2)

  hcsv.Draw('xl')
  hdee.Draw('xlsame')
  hdfl.Draw('xlsame')
  lcsv.Draw('xlsame')
  ldee.Draw('xlsame')
  ldfl.Draw('xlsame')

  #hcsv.SetMaximum(1)
  #hcsv.SetMinimum(1e-3)
  leg = TLegend(0.13, 0.78, 0.72, 0.87)
  leg.AddEntry(hcsv, 'CSVv2', 'l')
  leg.AddEntry(hdee, 'Deep CSV', 'l')
  leg.AddEntry(hdfl, 'Deep Flavour', 'l')
  leg.SetBorderSize(0)
  leg.SetNColumns(3)
  leg.SetFillStyle(0)
  leg.Draw()

  leg2 = TLegend(0.75, 0.12, 0.87, 0.28)
  leg2.AddEntry(hforleg, 'c', 'l')
  leg2.AddEntry(lforleg, 'udsg', 'l')
  leg2.SetBorderSize(0)
  leg2.SetFillStyle(0)
  leg2.Draw()

  lL = TLine(xmin, 0.1, 1, 0.1)
  lM = TLine(xmin, 0.01, 1, 0.01)
  lT = TLine(xmin, 0.001, 1, 0.001)
  lL.SetLineColor(kGray)
  lM.SetLineColor(kGray+2)
  lT.SetLineColor(kBlack)
  lL.SetLineWidth(2); lM.SetLineWidth(2); lT.SetLineWidth(2)
  lL.SetLineStyle(2); lM.SetLineStyle(2); lT.SetLineStyle(2);
  lL.Draw(); lM.Draw(); lT.Draw()

  xax = GetTLatex("b-tagging efficiency", 0.67, 0.03, 0.05)
  yax = GetTLatex("Mistag probability", 0.02, 0.55, 0.05)
  yax.SetTextAngle(90)
  t = GetTLatex("MC efficiencies, %i"%year, 0.12, 0.93)
  p = c.GetPad(0)
  p.SetLogy()
  p.SetRightMargin(0.02)
  p.SetTickx()
  p.SetTicky()
  c.SaveAs(outpath+'BtagCurves%i.png'%year)
  c.SaveAs(outpath+'BtagCurves%i.pdf'%year)

def plot2D(year, tagger, wp, tipo = 'B'):
  c = TCanvas('c', 'c', 10, 10, 1600, 1200)
  fname = path[year]
  if isinstance(year, int): year = "%i"%year
  hnameN = "BtagSF%s_%s%s_%s"%(tipo, tagger, wp, year);
  hnameD = "BtagSF%s_%s%s_%s"%(tipo, tagger, 'D', year);
  hnum = Get2D(fname, hnameN)
  hden = Get2D(fname, hnameD)
  h = hnum.Clone()
  h.Divide(hden)
  h.Draw("colz,text")
  h.SetTitle('')
  h.GetXaxis().SetTitle("Jet p_{T} (GeV)")
  h.GetYaxis().SetTitle("Jet |#eta|")
  gStyle.SetOptStat(0);
  gStyle.SetPalette(1);
  gStyle.SetPaintTextFormat("1.2f");

  #mg = TMultiGraph()
  #mg.Add()
  t = GetTLatex("%s %s b tag MC efficiencies for %s jets, %s"%(tagger, wp, tipo, year), 0.12, 0.93)

  c.SaveAs(outpath+hnameN+'.png')
  c.SaveAs(outpath+hnameN+'.pdf')
  h.SetDirectory(0)
  return h

def DrawAll():
  fout = TFile(outpath + "BtagMCSF.root", "RECREATE")
  for y in [2017,2018]:
    for t in ['CSVv2', 'DeepCSV', 'DFlav']:
      for w in ['L', 'M', 'T']:
        for tip in ['B', 'C', 'L']:
          h = TH2F()
          h = plot2D(y, t, w, tip)
          fout.cd()
          h.Write()

  fout.Close()


DrawCurves(2018)
DrawRatios(2018)
#DrawAll()
