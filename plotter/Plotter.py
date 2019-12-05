import os,sys
#import ROOT
from ROOT import TH1F, TH1, TFile, TCanvas, TPad, THStack, TLatex, TLegend, TGaxis
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack
from ROOT import gPad, gROOT, gSystem
from ROOT.TMath import Sqrt as sqrt
average = lambda x: sum(x)/len(x)
gROOT.SetBatch(1)
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from TopHistoReader import TopHistoReader

class Plot:

  #############################################################################################
  ### Pads
  def SetOutPath(self, path):
    if not path[-1] == '/': path += '/'
    self.outpath = path

  def SetLumi(self, lumi):
    self.lumi = lumi

  def GetOutPath(self):
    return self.outpath

  def GetOutName(self):
    hname = self.histoName if not isinstance(self.histoName, list) else self.histoName[0]
    return self.GetOutPath()+hname

  def SetHistoPad(self, x0 = 0.0, y0 = 0.23, x1 = 1, y1 = 1):
    self.hpadx0 = x0
    self.hpady0 = y0
    self.hpadx1 = x1
    self.hpady1 = y1

  def SetRatioPad(self, x0 = 0, y0 = 0, x1 = 1, y1 = 0.29):
    self.rpadx0 = x0
    self.rpady0 = y0
    self.rpadx1 = x1
    self.rpady1 = y1

  def SetHistoPadMargins(self, top = 0.08, bottom = 0.10, right = 0.02, left = 0.10):
    self.hpadMtop    = top
    self.hpadMbottom = bottom
    self.hpadMright  = right
    self.hpadMleft   = left

  def SetRatioPadMargins(self, top = 0.03, bottom = 0.40, right = 0.02, left = 0.10):
    self.rpadMtop    = top
    self.rpadMbottom = bottom
    self.rpadMright  = right
    self.rpadMleft   = left

  #############################################################################################
  ### Legend
  def SetLegendPos(self, x0 = 0.50, y0 = 0.65, x1 = 0.93, y1 = 0.91, size = 0.045, ncol = 2):
    self.legx0 = x0
    self.legx1 = x1
    self.legy0 = y0
    self.legy1 = y1
    self.legTextSize = size
    self.legNcol = ncol

  def SetLegend(self):
    leg = TLegend(self.legx0, self.legy0, self.legx1, self.legy1)
    leg.SetTextSize(self.legTextSize)
    leg.SetBorderSize(0)
    leg.SetFillColor(10)
    leg.SetNColumns(self.legNcol)
    return leg

  def SetLegendRatioPos(self, x0 = 0.18, y0 = 0.85, x1 = 0.60, y1 = 0.91, size = 0.065, ncol = 2):
    self.legratx0 = x0
    self.legratx1 = x1
    self.legraty0 = y0
    self.legraty1 = y1
    self.legratTextSize = size
    self.legratNcol = ncol

  def SetLegendRatio(self):
    legr = TLegend(self.legratx0, self.legraty0, self.legratx1, self.legraty1)
    legr.SetTextSize(self.legratTextSize)
    legr.SetBorderSize(0)
    legr.SetFillColor(10)
    legr.SetNColumns(self.legratNcol)
    return legr

  #############################################################################################
  ### Labels
  def SetTextCMS(self, cmstex = 'CMS', x = 0.13, y = 0.90, s = 0.06): # 0.18, y = 0.89
    self.cmstex  = cmstex
    self.cmstexX = x
    self.cmstexY = y
    self.cmstexS = s

  def SetTextCMSmode(self, texcmsMode = 'Preliminary', x = 0.225, y = 0.895, s = 0.052): # x = 0.18, y = 0.83
    self.texcmsMode  = texcmsMode
    self.texcmsModeX = x
    self.texcmsModeY = y
    self.texcmsModeS = s

  def DrawTextCMS(self):
    texcms = TLatex(0,0,self.cmstex)
    texcms.SetNDC()
    texcms.SetX(self.cmstexX)
    texcms.SetY(self.cmstexY)
    texcms.SetTextAlign(12)
    texcms.SetTextSize(self.cmstexS)
    texcms.SetTextSizePixels(22)
    return texcms

  def DrawTextCMSmode(self):
    texpre = TLatex(0,0,self.texcmsMode)
    texpre.SetNDC()
    texpre.SetTextAlign(12)
    texpre.SetX(self.texcmsModeX)
    texpre.SetY(self.texcmsModeY)
    texpre.SetTextFont(52)
    texpre.SetTextSize(self.texcmsModeS)
    texpre.SetTextSizePixels(22)
    return texpre

  def SetTextChan(self, texch = '', x = 0.20, y = 0.96, s = 0.04):
    self.texch  = texch
    self.texchX = x
    self.texchY = y
    self.texchS = s

  def AddTex(self, t = '', x = 0.15, y = 0.87, s = 0.04):
    tl = TLatex(-20, 50, t)
    tl.SetNDC();
    tl.SetTextAlign(12);
    tl.SetX(x);
    tl.SetY(y);
    tl.SetTextFont(42);
    tl.SetTextSize(s);
    self.Tex.append(tl)

  def SetTextLumi(self, texlumi = '%2.1f fb^{-1} (13 TeV)', texlumiX = 0.67, texlumiY = 0.97, texlumiS = 0.05, doinvfb = False):
    self.texlumi  = texlumi
    self.texlumiX = texlumiX
    self.texlumiY = texlumiY
    self.texlumiS = texlumiS
    self.doinvfb  = doinvfb

  def DrawTextLumi(self):
    if not hasattr(self, 'lumi'): self.lumi = 0
    t = self.texlumi if not '%' in self.texlumi else (self.texlumi%self.lumi if not self.doinvfb else self.texlumi%(self.lumi/1000.))
    tlum = TLatex(-20., 50., t)
    tlum.SetNDC()
    tlum.SetTextAlign(12)
    tlum.SetTextFont(42)
    tlum.SetX(self.texlumiX)
    tlum.SetY(self.texlumiY)
    tlum.SetTextSize(self.texlumiS)
    tlum.SetTextSizePixels(22)
    return tlum

  #############################################################################################
  ### Axes
  def SetXtitle(self, tit = '', size = 0.16, offset = 1.2, nDiv = 510, labSize = 0.16):
    self.axisXtit     = tit
    self.axisXsize    = size
    self.axisXoffset  = offset
    self.axisXnDiv    = nDiv
    self.axisXlabSize = labSize

  def SetYtitle(self, tit = 'Events', size = 0.06, offset = 0.80, nDiv = 505, labSize = 0.05):
    self.axisYtit     = tit
    self.axisYsize    = size
    self.axisYoffset  = offset
    self.axisYnDiv    = nDiv
    self.axisYlabSize = labSize

  def SetYratioTitle(self, tit = 'Data/Pred.', size = 0.12, offset = 0.32, nDiv = 505, labSize = 0.12):
    self.axisRtit     = tit
    self.axisRsize    = size
    self.axisRoffset  = offset
    self.axisRnDiv    = nDiv
    self.axisRlabSize = labSize

  def SetBinLabels(self, labels = []):
    self.binLabels = labels

  #############################################################################################
  ### Other
  def SetErrorStyle(self, style = 3444, color = kGray+2):
    self.ErrorStyle = style
    self.ErrorColor = color

  def SetLogY(self, do = True):
    self.doSetLogY = do

  def SetPlotMinimum(self, m = ''):
    self.PlotMinimum = m

  def SetPlotMaximum(self, m = ''):
    self.PlotMaximum = m

  def SetPlotMaxScale(self, m = 1.15):
    self.PlotMaxScale = m

  def SetRatioMin(self, m = 0.5):
    self.PlotRatioMin = m

  def SetRatioMax(self, m = 1.5):
    self.PlotRatioMax = m
 
  def SetVerbose(self, v = 1):
    self.verbose = v

  #############################################################################################
  #############################################################################################
  # Select histograms

  def SetOutName(self, histoName = ''):
    self.histoName = histoName

  def SetCanvas(self):
    self.canvas  = None; self.plot    = None; self.ratio = None
    c = TCanvas('c', 'c', 10, 10, 1600, 1200)
    if self.doRatio:
      c.Divide(1,2)
      plot  = c.GetPad(1)
      ratio = c.GetPad(2)
    else:
      plot = c.GetPad(0)
    #if self.doRatio: 
    plot.SetPad( self.hpadx0, self.hpady0, self.hpadx1, self.hpady1)
    plot.SetMargin(self.hpadMleft, self.hpadMright, self.hpadMbottom, self.hpadMtop)
    #else: plot = c.GetPad(0)
    
    if self.doRatio:
      ratio.SetPad(self.rpadx0, self.rpady0, self.rpadx1, self.rpady1)
      ratio.SetMargin(self.rpadMleft, self.rpadMright, self.rpadMbottom, self.rpadMtop)
    else:
      #ratio.SetPad(0,0,0,0)
      plot.SetPad(0,0,1,1)

    # Draw the text
    texcms = self.DrawTextCMS()
    texmod = self.DrawTextCMSmode()
    texlum = self.DrawTextLumi()
    self.Tex.append(texcms)
    self.Tex.append(texmod)
    self.Tex.append(texlum)
    if hasattr(self, 'texch') and self.texch != '':
      tch = TLatex(-20, 50, self.texch)
      tch.SetNDC();
      tch.SetTextAlign(12);
      tch.SetX(self.texchX);
      tch.SetY(self.texchY);
      tch.SetTextFont(42);
      tch.SetTextSize(self.texchS);
      self.Tex.append(tch)
    for r in self.Tex: r.Draw()

    TGaxis.SetMaxDigits(3)
    if self.doSetLogY: plot.SetLogy()

    # Legend
    self.legend = self.SetLegend()
    self.legendRatio=self.SetLegendRatio()
    
    self.canvas = c
    self.plot = plot
    if self.doRatio: self.ratio = ratio

  def SetAxisPlot(self, h):
    h.GetYaxis().SetTitle(self.axisYtit)
    h.GetYaxis().SetTitleSize(self.axisYsize)
    h.GetYaxis().SetTitleOffset(self.axisYoffset)
    h.GetYaxis().SetLabelSize(self.axisYlabSize)
    h.GetYaxis().SetNdivisions(self.axisYnDiv)
    h.GetYaxis().CenterTitle()
    if self.doRatio:
      h.GetXaxis().SetTitle("")
      h.GetXaxis().SetLabelSize(0)
    else:
      h.GetXaxis().SetTitle(self.axisXtit)
      h.GetXaxis().SetTitleSize(self.axisXsize)
      h.GetXaxis().SetTitleOffset(self.axisXoffset)
      h.GetXaxis().SetLabelSize(self.axisXlabSize)
      h.GetXaxis().SetNdivisions(self.axisXnDiv)

  def SetAxisRatio(self, h):
    h.GetXaxis().SetTitle(self.axisXtit)
    h.GetXaxis().SetTitleSize(self.axisXsize)
    h.GetXaxis().SetTitleOffset(self.axisXoffset)
    h.GetXaxis().SetLabelSize(self.axisXlabSize)
    h.GetXaxis().SetNdivisions(self.axisXnDiv)
    h.GetYaxis().SetTitle(self.axisRtit)
    h.GetYaxis().SetTitleSize(self.axisRsize)
    h.GetYaxis().SetTitleOffset(self.axisRoffset)
    h.GetYaxis().SetLabelSize(self.axisRlabSize)
    h.GetYaxis().SetNdivisions(self.axisRnDiv)
    h.GetYaxis().CenterTitle()

  def Save(self):
    # Save
    #if not os.path.isdir(self.GetOutPath()): 
    #  print 'Creating directory: ', self.GetOutPath()
    gSystem.mkdir(self.GetOutPath(), True)
    self.canvas.Print(self.GetOutName()+'.pdf', 'pdf')
    self.canvas.Print(self.GetOutName()+'.png', 'png')

  def Initialize(self, outpath = './', outname = 'temp', doRatio = True):
    self.SetOutPath(outpath)
    self.SetOutName(outname)
    self.verbose = 1
    self.Tex = []
    self.doRatio = doRatio
 
    ### Pads
    self.SetHistoPad()
    self.SetRatioPad()
    self.SetRatioPadMargins()
    self.SetHistoPadMargins()

    ### Legend
    self.SetLegendPos()
    self.SetLegendRatioPos()
    ### Labels
    self.SetTextCMS()
    self.SetTextCMSmode()
    self.SetTextChan()
    self.SetTextLumi()

    ### Axes
    self.SetXtitle()
    self.SetYtitle()
    self.SetYratioTitle()
    self.SetXtitle()
    self.SetYtitle()
    self.SetYratioTitle()
    self.SetBinLabels()
 
    ### Other
    self.SetErrorStyle()
    self.SetLogY(False)
    self.SetPlotMinimum()
    self.SetPlotMaximum()
    self.SetPlotMaxScale()
    self.SetRatioMin()
    self.SetRatioMax()
 
  #############################################################################################
  #############################################################################################
  # Init

  def __init__(self, outPath = './', outname = 'temp', doRatio = True):
    self.Initialize(outpath, outname, doRatio)


###############################################################################################
### Comparison plot
class HistoComp(Plot):
  ''' Example:
      cp = HistoComp('./temp/', doRatio = True, doNorm = True)
      cp.AddHisto(hdata, 'pe', 'e2', 'Data')
      cp.AddHisto(hMC,   'hist', '', 'MC')
      cp.autoRatio = True
      cp.Draw()
  '''

  def AddHisto(self, h, drawOpt = 'hist', drawErr = 0, addToLeng = 0, color = '', lineStyle = 1):
    if self.doNorm: h.Scale(1/h.Integral())
    h.SetStats(0); h.SetLineWidth(2); h.SetTitle('')
    if isinstance(color, int):
      h.SetLineColor(color)
      h.SetLineStyle(lineStyle)
      #h.SetFillColor(color)
    self.histos.append([h, drawOpt, drawErr, addToLeng])

  def AddRatioHisto(self, h, drawOpt = 'hist', drawErr = 0):
    h.SetTitle('')
    self.ratioh.append([h, drawOpt, drawErr])

  def Draw(self, doSetLogy = False):
    self.SetCanvas()
    self.plot.cd()
    gPad.SetTickx();
    gPad.SetTicky();
    if not os.path.isdir(self.GetOutPath()): os.makedirs(self.GetOutPath())

    dmax = []; dmin = []
    for h in self.histos: 
      dmax.append(h[0].GetMaximum())
      dmin.append(h[0].GetMinimum())
      legsymbol = h[1] if h[1] != '' and h[1] != 0 else h[2]
      if   'hist' in legsymbol: legsymbol = 'l'
      elif 'e2'   in legsymbol: legsymbol = 'f'
      if h[1] != 0 and h[1] != '': h[0].Draw('same,'+h[1])
      # Draw errors
      if h[2] != 0 and h[2] != '': h[0].Draw('same,'+h[2])
      # Legend
      if h[3] != 0 and h[3] != '': self.legend.AddEntry(h[0], h[3], legsymbol)
    self.SetAxisPlot(self.histos[0][0])
    dmax = max(dmax)
    dmin = min(dmin)
    if self.legend.GetNRows() > 0: self.legend.Draw()

    # Set maximum and minimum
    if isinstance(self.PlotMaximum, float): self.histos[0][0].SetMaximum(self.PlotMaximum)
    else: self.histos[0][0].SetMaximum(dmax*self.PlotMaxScale)
    if isinstance(self.PlotMinimum, float): self.histos[0][0].SetMinimum(self.PlotMinimum)
    self.plot.SetLogy(doSetLogy)

    if self.doRatio: 
      if self.autoRatio:
        hratio = self.histos[0][0].Clone("hratio")
        self.SetAxisRatio(hratio)
        if len(self.binLabels) > 0: 
          for i in range(len(self.binLabels)):
            hratio.GetXaxis().SetBinLabel(i+1,self.binLabels[i])
        nbins = hratio.GetNbinsX()
        for h in self.histos[1:]: 
          htemp    = h[0].Clone(h[0].GetName()+'ratio')
          htempRat = hratio.Clone(h[0].GetName()+'hratio')
          htempRat.Divide(htemp)
          self.AddRatioHisto(htempRat, h[1], h[2])
      self.ratio.cd()
      if len(self.ratioh) >= 1:
        self.SetAxisRatio(self.ratioh[0][0])
        self.ratioh[0][0].SetMaximum(self.PlotRatioMax)
        self.ratioh[0][0].SetMinimum(self.PlotRatioMin)
        for h in self.ratioh: 
          h[0].Draw(h[1] + ',same')
          if h[2] != 0 and h[2] != '': 
            hrat = h[0].Clone()
            hrat.SetFillStyle(3244)
            hrat.Draw('same,'+h[2])
        
    # Save
    gPad.SetTickx();
    gPad.SetTicky();
    self.Save()

  def __init__(self, outpath = './', outname = 'temp', doRatio = True, doNorm = False, autoRatio = False):
    self.Initialize(outpath, outname, doRatio)
    self.doNorm = doNorm
    self.autoRatio = autoRatio
    self.histos = []
    self.ratioh = []

class Stack(Plot):

  def SetDataHisto(self, h):
    if h != None: self.hData = h

  def SetStack(self, h):
    self.hStack = h

  def SetTotMC(self, a):
    self.TotMC = a

  def SetMCstatUnc(self, h):
    self.MCstatUnc = h
 
  def SetMCunc(self, h):
    self.MCunc = h

  def SetRatio(self, h):
    self.hRatio = h

  def SetProcesses(self, p):
    if   isinstance(p, str) and ',' in p: p = p.replace(' ', '').split(',')
    elif isinstance(p, str): p = [p]
    self.processes = p

  def SetRatioStatUnc(self, h):
    self.hRatioStatUnc = h

  def SetRatioUnc(self, h):
    self.hRatioUnc = h

  def SetLegendHistos(self, histos, labels, style = []):
    #legend.AddEntry(self.data.histo(), 'Data', 'pe')    
    pass

  def SetRatioLegendHistos(self, histos = [], labels = [], style = []):
    pass

  def SetColors(self, col):
    self.colors = col
    if self.HM != '':
      self.SetStack(self.HM.GetStack(colors=self.colors))

  def DrawStack(self, xtit = '', ytit = ''):
    ''' Draws a stack plot '''
    # Set the canvas and pads
    if xtit  != '': self.axisXtit = xtit
    if ytit  != '': self.axisYtit = ytit
    self.SetCanvas()

    # Stack processes and draw stack and data
    self.plot.cd()
    gPad.SetTickx();
    gPad.SetTicky();
    if not os.path.isdir(self.GetOutPath()): os.makedirs(self.GetOutPath())
    self.hStack.Draw('hist')
    if hasattr(self, 'MCstatUnc'): self.MCstatUnc.Draw("e2,same")
    if hasattr(self, 'MCunc'):     self.MCunc    .Draw("e2,same")

    # Extra histograms
    for h in self.overlapHistos:
      h.Draw("hist,same")

    # Errors in data
    if hasattr(self, 'hData'):
      self.hData.SetBinErrorOption(TH1.kPoisson)
      self.hData.Sumw2(False);
      self.hData.Draw('psameE0X0')#self.data.GetDrawStyle())

    # Set Maximum
    datamax = self.hData.GetMaximum() if hasattr(self, 'hData') else -999
    bkgmax = self.TotMC.GetMaximum() if hasattr(self, 'TotMC') else self.hStack.GetStack().Last().GetMaximum()
    dmax = max(datamax, bkgmax)

    if isinstance(self.PlotMaximum, float): self.hStack.SetMaximum(self.PlotMaximum)
    else: self.hStack.SetMaximum(dmax*self.PlotMaxScale)
    if isinstance(self.PlotMinimum, float): self.hStack.SetMinimum(self.PlotMinimum)
  
    # Set titles...
    TGaxis.SetMaxDigits(3)
    self.SetAxisPlot(self.hStack)
    if self.doRatio: 
      self.SetAxisRatio(self.hRatio)
      self.SetAxisRatio(self.hRatioUnc)
      self.SetAxisRatio(self.hRatioStatUnc)
   
    # Legend
    if hasattr(self, 'processes'):
      self.hleg = []
      leg = self.SetLegend()
      for pr in self.processes:
        h = self.TotMC.Clone('leg%s'%pr); h.SetFillStyle(1000); h.SetLineColor(0); h.SetLineWidth(0); h.SetFillColor(self.colors[pr])
        self.hleg.append(h)
        leg.AddEntry(self.hleg[-1], pr, 'f')
      for h in self.overlapHistos: leg.AddEntry(h, h.GetName(), 'l')
      if hasattr(self, 'hData'): leg.AddEntry(self.hData, 'data', 'pe')
      leg.Draw()

    # Ratio
    if self.doRatio:
      self.ratio.cd()
      legr=self.SetLegendRatio()
      if hasattr(self, 'hRatioStatUnc'):
        self.hRatioStatUnc.Draw('e2same')
        self.hRatioStatUnc.SetLineWidth(0)
        self.hRatioStatUnc.SetMaximum(self.PlotRatioMax)
        self.hRatioStatUnc.SetMinimum(self.PlotRatioMin)
        legr.AddEntry(self.hRatioStatUnc, 'Stat', 'f')
      if hasattr(self, 'hRatioUnc'    ): 
        self.hRatioUnc.Draw('e2same')
        self.hRatioUnc.SetLineWidth(0)
        self.hRatioUnc.SetMinimum(self.PlotRatioMin)
        self.hRatioUnc.SetMaximum(self.PlotRatioMax)
        legr.AddEntry(self.hRatioUnc, 'Stat #oplus Syst', 'f')
      if hasattr(self, 'hRatio'):
        self.hRatio.Draw('pE0X0,same')
        self.hRatio.SetMaximum(self.PlotRatioMax)
        self.hRatio.SetMinimum(self.PlotRatioMin)
      for h in self.extraRatio: h.Draw("hist, same")
      legr.Draw()
    else: 
      for r in self.Tex: r.Draw()

    if len(self.binLabels) > 0: 
      for i in range(len(self.binLabels)):
        if self.doRatio:
          if hasattr(self, 'hRatio'       ): self.hRatio       .GetXaxis().SetBinLabel(i+1,self.binLabels[i])
          if hasattr(self, 'hRatioUnc'    ): self.hRatioUnc    .GetXaxis().SetBinLabel(i+1,self.binLabels[i])
          if hasattr(self, 'hRatioStatUnc'): self.hRatioStatUnc.GetXaxis().SetBinLabel(i+1,self.binLabels[i])
        else:
          self.hStack.GetXaxis().SetBinLabel(i+1,self.binLabels[i])

    self.Save()

  def SetHistosFromMH(self, HM, defaultStyle = True):
    self.HM = HM
    self.SetTotMC(HM.GetSumBkg())
    self.SetMCstatUnc(HM.GetUncHist('stat'))
    self.SetMCunc(HM.GetUncHist())
    self.SetDataHisto(HM.GetDataHisto())
    self.SetStack(HM.GetStack(colors=self.colors))
    self.SetRatio(HM.GetRatioHisto())
    self.SetRatioStatUnc(HM.GetRatioHistoUnc('stat'))
    self.SetRatioUnc(HM.GetRatioHistoUnc('', False))
    if defaultStyle:
      self.SetRatioUncStyle()
      self.SetRatioStatUncStyle()
      self.SetUncStyle()
      self.SetStatUncStyle()

  def SetRatioUncStyle(self, color = kAzure+2, alpha = 0.2, fill = 1000):
    self.hRatioUnc.SetFillColorAlpha(color, alpha)
    self.hRatioUnc.SetFillStyle(fill)

  def SetRatioStatUncStyle(self, color = kOrange+1, alpha = 0.8, fill = 1000):
    self.hRatioStatUnc.SetFillColorAlpha(color, alpha)
    self.hRatioStatUnc.SetFillStyle(fill)

  def SetUncStyle(self, color = kGray+2, alpha = 0.9, fill = 3444):
    self.MCunc.SetFillColorAlpha(color, alpha)
    self.MCunc.SetFillStyle(fill)

  def SetStatUncStyle(self, color = kAzure+7, alpha = 0.9, fill = 3444):
    self.MCstatUnc.SetFillColorAlpha(color, alpha)
    self.MCstatUnc.SetFillStyle(fill)

  def AddOverlapHisto(self, h):
    self.overlapHistos.append(h)

  def AddSignalHisto(self, h, color = 1, mode = 'overlap', ratioBkg = True):
    ''' mode = overlap, stack, ontop '''
    h.SetLineColor(color)
    h.SetLineWidth(2)
    if mode == 'overlap' or mode == 'ontop': h.SetFillStyle(0)
    hBkg = self.TotMC.Clone('ontop_%s'%h.GetName())
    if mode == 'ontop': h.Add(hBkg)
    if ratioBkg:
      hRatio = h.Clone('ratio_%s'%h.GetName())
      hRatio.Divide(hBkg)
      self.extraRatio.append(hRatio)
    h.SetDirectory(0)
    self.AddOverlapHisto(h)
     

  def __init__(self, outpath = './', outname = 'temp', doRatio = True, HM='', colors=''):
    self.Initialize(outpath, outname, doRatio)
    self.colors = colors
    self.HM = HM
    self.overlapHistos = []
    self.extraRatio = []
    if HM!= '': self.SetHistosFromMH(HM)



class HistoUnc(HistoComp):
  ''' Example:
      cp = HistoUnc('./temp/', doRatio = True, doNorm = True)
      cp.AddHisto(hdata, 'pe', 'e2', 'Data')
      cp.AddHisto(hMC,   'hist', '', 'MC')
      cp.autoRatio = True
      cp.Draw()
  '''

  def AddHistoNom(self, h):
    self.hNo = h
    self.AddHisto(h, 'hist', 'e2' if self.DrawStatUnc else 0, 0, 1, 1)
    self.rnom = self.hNo.Clone('rnom')
    for b in range(0, self.rnom.GetNbinsX()+2): 
      bc = self.rnom.GetBinContent(b)
      berr = self.rnom.GetBinError(b) / bc if bc != 0 else 0
      self.rnom.SetBinError(b, berr)
      self.rnom.SetBinContent(b, 1.)
      #print 'berr: ', berr
    self.rnom.SetLineStyle(2)
    self.rnom.SetLineWidth(2)
    self.rnom.SetLineColor(kGray+1)
    self.rnom.SetFillColor(kTeal-9)
    self.rnom.SetFillStyle(1)
    self.AddRatioHisto(self.rnom, 'hist', 'e2')

  def AddHistoUp(self, h):
    self.hUp = h
    self.hUp.SetLineWidth(2); self.hUp.SetTitle('');
    self.hUp.SetStats(0); self.hUp.SetLineColor(kAzure+2)
    self.AddHisto(self.hUp, 'hist', 0, 0, kAzure+2, 2)
    self.rUp = self.hUp.Clone('hUp')
    #self.rUp.Divide(self.hNo)
    for b in range(0, self.rUp.GetNbinsX()+1):
      bc = self.rUp.GetBinContent(b)
      d  = self.hNo.GetBinContent(b)
      self.rUp.SetBinContent(b, 1 if (bc==0 or d==0) else bc/d)
    self.AddRatioHisto(self.rUp, 'hist', 0)
    if self.rUp.GetMinimum()*0.80 < self.PlotRatioMin: self.SetRatioMin(self.rUp.GetMinimum()*0.80)
    if self.rUp.GetMaximum()*1.20 > self.PlotRatioMax: self.SetRatioMax(self.rUp.GetMaximum()*1.2)
    self.rUp.SetLineStyle(1)

  def AddHistoDown(self, h):
    self.hDo = h
    self.hDo.SetLineWidth(2); self.hDo.SetTitle('');
    self.hDo.SetStats(0); self.hDo.SetLineColor(kRed+1)
    self.AddHisto(self.hDo, 'hist', 0, 0, kRed+1, 2)
    self.rDo = self.hDo.Clone('hDo')
    #self.rDo.Divide(self.hNo)
    for b in range(0, self.rDo.GetNbinsX()+1):
      bc = self.rDo.GetBinContent(b)
      d  = self.hNo.GetBinContent(b)
      self.rDo.SetBinContent(b, 1 if (bc==0 or d==0) else bc/d)
    self.rDo.SetLineStyle(1)
    if self.rDo.GetMinimum()*0.80 < self.PlotRatioMin: self.SetRatioMin(self.rDo.GetMinimum()*0.80)
    if self.rDo.GetMaximum()*1.20 > self.PlotRatioMax: self.SetRatioMax(self.rDo.GetMaximum()*1.2)
    self.AddRatioHisto(self.rDo, 'hist', 0)

  def __init__(self, outpath = './', outname = 'temp', tag = '', doNorm = False, drawStatErr = True, xtit = '', ytit = 'Events'):
    self.Initialize(outpath, outname, True)
    self.doNorm = doNorm
    self.DrawStatUnc = drawStatErr
    self.autoRatio = False
    self.histos = []
    self.ratioh = []
    self.SetPlotMaxScale(1.3)
    self.AddTex(tag, 0.65, 0.88, 0.05)
    self.SetHistoPad(x0 = 0.0, y0 = 0.47, x1 = 1, y1 = 1)
    self.SetRatioPad(x0 = 0.0, y0 = 0.00, x1 = 1, y1 = 0.52)
    self.SetHistoPadMargins(top = 0.14, bottom = 0.10, right = 0.03, left = 0.10)
    self.SetRatioPadMargins(top = 0.08, bottom = 0.25, right = 0.03, left = 0.10)
    self.SetYratioTitle('Unc./Nom.', 0.10, 0.4, labSize = 0.08)
    self.SetXtitle(xtit, 0.12, 0.8, labSize = 0.09)
    self.SetYtitle(ytit, 0.12, 0.35, labSize = 0.08)
    self.SetTextLumi(texlumi = '%2.1f fb^{-1} (13 TeV)' if not doNorm else '', texlumiX = 0.67, texlumiY = 0.97, texlumiS = 0.05)
    self.SetRatioMin(0.95); self.SetRatioMax(1.05)

