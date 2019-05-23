import os,sys
#import ROOT
from ROOT import TH1F, TH1, TFile, TCanvas, TPad, THStack, TLatex, TLegend, TGaxis
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack
from ROOT import gPad, gROOT
from ROOT.TMath import Sqrt as sqrt
average = lambda x: sum(x)/len(x)
gROOT.SetBatch(1)
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')

from ttbar.ttanalysis import ch, chan, lev, level, dataset, datasets, systematic, systlabel  

class TopHistoReader:
 ''' Reads histograms created with the ttanalysis '''
 def SetFileNamePrefix(self, p):
   self.fileprefix = p
 
 def SetHistoNamePrefix(self,p):
   self.histoprefix = p

 def SetPath(self, path):
   if not path[-1] == '/': path += '/'
   self.path = path

 def SetProcess(self, process):
   if isinstance(process, list):
     self.process= []
     for pr in process: 
       self.AddProcess(pr)
     return
   if process.endswith('.root'): process = process[:-5]
   self.process = process

 def AddProcess(self, pr):
   if not isinstance(self.process, list): self.process = []
   if pr.endswith('.root'): pr = process[:-5]
   self.process.append(pr)

 def SetVar(self, var):
   self.var = var

 def SetChan(self, chan):
   self.chan = chan
  
 def SetLevel(self, ilevel):
   self.level = ilevel

 def SetSystematic(self, syst):
   self.syst = syst

 def SetRebin(self, rebin):
   self.rebin = rebin

 def SetLumi(self, lumi):
   self.lumi = lumi

 def SetIsData(self, isData = True):
   self.IsData = isData

 def SetVerbose(self, verbose = True):
   self.verbose = verbose

 def GetHistoName(self):
   ''' Craft histo name from var, chan, level '''
   name = self.var + '_' + self.chan + '_' + self.level
   if len(self.syst) > 0: name += '_' + self.syst
   return name

 def IsHisto(self, pr, name, syst = ''):
   ''' Check if histo exists '''
   if pr    != '': self.SetProcess(pr)
   if ',' in self.process: self.process = self.process.replace(' ', '').split(',')
   if ',' in self.process: self.process = self.process.replace(' ', '').split(',')
   if isinstance(self.process, list):
     for p in self.process: 
       if not self.IsHisto(p, name, syst): return False
     return True
   if syst != '':
     if self.IsHisto(pr, name + '_' + syst) or self.IsHisto(pr, name + '_' + syst+'Up') or self.IsHisto(pr, name + '_' + syst+'Down'): return True
     return False
   filename = self.path + 'Tree_' + pr + '.root'
   f = TFile.Open(filename)
   if not hasattr(f, name): return False
   else: return True

 def GetNamedHisto(self, name, pr = '', rebin = -1):
   ''' Load an histo from process pr '''
   if pr    != '': self.SetProcess(pr)
   if rebin != -1: self.rebin = rebin
   pr = self.process
   if ',' in self.process: self.process = self.process.replace(' ', '').split(',')
   if isinstance(self.process, list):
     listOfProcess = self.process
     h = self.GetNamedHisto(name, listOfProcess[0], rebin)
     for p in listOfProcess[1:]: 
       while p[0]  == ' ': p = p[1:]
       while p[-1] == ' ': p = p[:-1]
       h.Add(self.GetNamedHisto(name, p, rebin))
     return h
   if ',' in name:
     listOfNames = name.replace(' ', '').split(',')
     h = self.GetNamedHisto(listOfNames[0], pr, rebin)
     for n in listOfNames[1:]:
       while n[0 ] == ' ': n = n[1:]
       while n[-1] == ' ': n = n[:-1]
       h.Add(self.GetNamedHisto(n, pr, rebin))
     return h

   filename = self.path + 'Tree_' + pr + '.root'
   if self.verbose: print ' >> Opening file: ' + filename
   f = TFile.Open(filename)
   if self.verbose: print ' >> Looking for histo: ' + name
   if not hasattr(f, name):
     if name == self.GetHistoName() and self.syst != '':
       hnosyst = self.var + '_' + self.chan + '_' + self.level
       if hasattr(f, hnosyst):
         #print 'WARNING: no systematic %s for histo %s in process %s!! Returning nominal...'%(self.syst, hnosyst, pr)
         return 
     else:
       print 'ERROR: not found histogram ' + name + ' in file: ' + filename
       return False
   if self.syst != '':
     hsyst = name + '_' + self.syst
     if hasattr(f, hsyst): name = hsyst
     #else: print 'WARNING: not found systematic %s for histogram %s in sample %s'%(self.syst, name, filename)
   h = f.Get(name)

   h.Rebin(self.rebin)
   nb = h.GetNbinsX()
   if self.doStackOverflow:
     h.SetBinContent(nb, h.GetBinContent(nb) + h.GetBinContent(nb+2))
     h.SetBinContent(nb+2, 0)
   if not self.IsData: h.Scale(self.lumi)
   h.SetLineColor(1); h.SetFillStyle(0)
   h.SetLineWidth(2); h.SetStats(0)
   h.SetTitle('');
   h.GetXaxis().SetTitle('')
   h.GetYaxis().SetTitle('')
   h.SetDirectory(0)
   ### This is a patch, the bin-by-bin stat unc are (whatever the reason) not well calculated...
   ### This is a temporary solution
   nbins = h.GetNbinsX()
   integral = h.Integral() if h.Integral() > 0 else 0
   entries  = h.GetEntries()
   if self.ReComputeStatUnc:
     for i in range(1,nbins+1):
       bc = h.GetBinContent(i) if h.GetBinContent(i) > 0 else 0
       h.SetBinError(i, sqrt(bc*integral/entries) if entries != 0 else 0)
   if self.doNormalize: h.Scale(1./(integral if integral != 0 else 1))
   return h

 def GetBinNumberForLevel(self, ilev = ''):
   ''' Returns the bin number for a given level for the yields histogram '''
   if ilev == '': ilev = self.level
   for lv in level.keys(): 
     if ilev == level[lv]: return lv+1
   return -1

 def GetYieldHisto(self, pr = '', ch = '', syst = '', SS = False):
   ''' Returns the histogram with yields '''
   if pr != '': self.SetProcess(pr)
   if ch != '': self.SetChan(ch)
   self.SetSystematic(syst)
   prename = 'Yields_' if not SS else 'YieldsSS_'
   name = prename + self.chan
   if self.syst != '': name += '_' + self.syst
   return self.GetNamedHisto(name)

 def GetYield(self, pr = '', ch = '', ilev = '', s = '', SS = False):
   ''' Returns a yield '''
   if ilev != '': self.SetLevel(ilev)
   self.SetSystematic(s)
   hyields = self.GetYieldHisto(pr, ch, s, SS)
   y = hyields.GetBinContent(self.GetBinNumberForLevel(self.level))
   return y

 def GetRunXsec(self, pr = ''):
   ''' Returns the used xsec during the processing, stored in histo hxsec '''
   h = self.GetNamedHisto("hxsec",pr)
   return h.GetBinContent(1)

 def GetNGenEvents(self, pr = ''):
   ''' Returns the number of gen events, stored in histogram hGenEvents '''
   self.SetIsData(True)
   h = self.GetNamedHisto("nGenEvents",pr)
   self.SetIsData(False)
   return h.GetBinContent(1)

 def GetFiduEvents(self, pr = '', ilev = ''):
   ''' Returns value for FiduEvents histogram '''
   if ilev != '': self.SetLevel(ilev)
   self.SetIsData(True)
   h = self.GetNamedHisto("FiduEvents",pr)
   self.SetIsData(False)
   y = h.GetBinContent(self.GetBinNumberForLevel(self.level))
   return y

 def GetUnc(self, pr = '', ch = '', ilev = '', s = ''):
   ''' Return a systematic uncertainty (relative) ''' 
   nom = self.GetYield(pr, ch, ilev)
   if isinstance(s, list):
     err = 0
     for u in s:
       e = self.GetUnc(pr, ch, ilev, u)
       err += e*e
     return sqrt(err)
   else:
     if not s.endswith('Up') and not s.endswith('Down'):
       varUp = self.GetYield(pr, ch, ilev, s+'Up')
       varDo = self.GetYield(pr, ch, ilev, s+'Down')
     return max(abs(nom-varUp)/nom if nom!=0 else 0, abs(nom-varDo)/nom if nom != 0 else 0)
 
 def GetYieldStatUnc(self, pr = '', ch = '', ilev = '', s = '', SS = False):
   ''' Return the stat unc of a process '''
   if ilev != '': self.SetLevel(ilev)
   if s  != '':   self.SetSystematic(s)
   hyields = self.GetYieldHisto(pr, ch, s, SS)
   y = hyields.GetBinError(self.GetBinNumberForLevel(self.level))
   if not y == y: y = 0
   return y

 def GetHisto(self, pr = '', v = '', ch = '', ilev = '', s = '', rb = -1):
   ''' Returns an histogram named var_chan_level_syst '''
   if pr != '': self.SetProcess(pr)
   if ch != '': self.SetChan(ch)
   if v  != '': self.SetVar(v)
   if ilev != '': self.SetLevel(ilev)
   if s  != '':   self.SetSystematic(s)
   return self.GetNamedHisto(self.GetHistoName(), self.process, rb)

 def GetHistoSystDif(self, pr = '', v = '', ch = '', ilev = '', s = '', rb = -1):
   if ',' in pr: pr = pr.replace(' ', '').split(',')
   if isinstance(pr, list):
     h = GetHistoSystDif(pr[0], v, ch, ilev, s, rb)
     for p in pr[1:]: h.Add(GetHistoSystDif(p,v,ch,ilev,s,rb))
     return
   n = GetHisto(self, pr, v, ch, ilev, '', rb)
   v = GetHisto(self, pr, v, ch, ilev,  s, rb)
   nbin = n.GetNbinsX()+1;
   for i in range(len(nbin)):
    nom = n.GetBinContent(i)
    var = v.GetBinContent(v)
    n.SetBinContent(i, var-nom)
   return n

 def __init__(self, path = './', process = '', var = '', chan = '', ilevel = '', syst = ''):
    self.doStackOverflow = False
    self.doNormalize = False
    self.IsData  = False
    self.verbose = False
    self.fname = ''
    self.rebin = 1
    self.lumi = 1
    self.ReComputeStatUnc = False

    self.SetPath(path)
    self.SetProcess(process)
    self.SetVar(var)
    self.SetChan(chan)
    self.SetLevel(ilevel)
    self.SetSystematic(syst)


###############################################################################################
###############################################################################################
###############################################################################################
class Process:
  ''' Simple class that stores preferred values for a process '''

  def SetColor(self, color):
    self.color = color

  def SetFiles(self, files):
    self.samples = files

  def SetYield(self, y):
    self.y = y

  def SetSystErr(self, name, var):
    self.syst[name] = var

  def SetSystName(self, systname):
    self.systName = systname

  def GetSystName(self):
    return self.systName
 
  def GetSamples(self):
    return self.samples
 
  def GetYield(self):
    return self.y

  def AddToFiles(self, f):
    self.samples.append(f)

  def SetHisto(self, h):
    self.h = h
    self.h.SetLineColor(self.color)
    self.h.SetFillColor(self.color)
    self.h.SetFillStyle(1001)
    #self.h.SetFillColorAlpha(self.color, 1)
    if self.IsSignal:
      self.h.SetFillStyle(0)
      self.h.SetLineStyle(1)
      self.h.SetLineWidth(2)
    if self.IsData:
      self.h.SetFillStyle(0)
      self.h.SetLineStyle(0)
      self.h.SetLineColor(kBlack)
      self.h.SetMarkerStyle(20)
      self.h.SetMarkerSize(2.5)

    self.SetValues()

  def SetValues(self):
    if not isinstance(self.h, TH1F): return
    self.Yield = self.h.Integral()
    self.nbins = self.h.GetNbinsX()

  def SetName(self, n):
    self.Name = n

  def SetDrawStyle(self, ds):
    self.DrawStyle = ds

  def SetIsData(self, isData):
    self.IsData = isData

  def SetIsSignal(self, isSignal):
    self.IsSignal = isSignal

  def SetLineStyle(self):
    pass

  def histo(self):
    return self.h

  def GetDrawStyle(self):
    return self.DrawStyle

  def GetName(self):
    return self.Name

  def SetStatUnc(self, s): # Absolute unc!!!
    self.StatUnc = s
  
  def SetNormUnc(self, s): # Relative unc!!!
    self.NormUnc = s
  
  def SetSystUnc(self, s): # Absolute unc!!!
    self.SystUnc = s

  def SetExpUnc(self, name, val):
    if not isinstance(self.ExpUnc, dict): self.ExpUnc = {}
    self.ExpUnc[name] = val

  def SetModUnc(self, name, val):
    if not isinstance(self.ModUnc, dict): self.ModUnc = {}
    self.ModUnc[name] = val

  def GetUnc(self, name = ''):
    if name == '':
      if self.SystUnc != -999: return self.SystUnc
      else:
        unc = 0
        y = self.GetYield()
        normUnc = self.GetNormUnc()
        for val in self.ModUnc.values(): unc += val*val
        for val in self.ExpUnc.values(): unc += val*val
        val += y*y*normUnc*normUnc
        return sqrt(unc)
    else:
      for key in self.ModUnc.keys(): 
        if key == name: return self.ModUnc[key]
      for key in self.ExpUnc.keys():
        if key == name: return self.ExpUnc[key]
      print 'WARNING: not found systematic uncertainty \'%d\'... returning 0'%name
      return 0

  def GetNormUnc(self):
    return self.NormUnc

  def GetStatUnc(self):
    return self.StatUnc

  def GetTotRelUnc(self):
    norm = self.GetNormUnc() # relative
    syst = self.GetUnc() # relative
    stat = self.GetStatUnc() # Absolute
    y = self.GetYield()
    stat = stat/y if y != 0 else 0
    e = norm*norm + syst*syst + stat*stat
    return sqrt(e)

  def GetSystAbsUnc(self):
    y = self.GetYield()
    norm = self.GetNormUnc()*y # relative
    syst = self.GetUnc()*y # relative
    e = norm*norm + syst*syst
    return sqrt(e)

  def __init__(self, name, color = 1, samples = '', isData = False, isSignal = False, Yield = 0, systName = '', NormUnc = 0, SystUnc = -999, StatUnc = 0, ExpUnc = {}, ModUnc = {}):
    self.SetColor(color)
    self.SetName(name)
    self.SetIsData(isData)
    self.SetIsSignal(isSignal)
    self.SetFiles(samples)
    ds = "psameE1X0" if isData else "f,hist,same"
    self.SetDrawStyle(ds)
    self.syst = {}
    self.SetYield(Yield)
    self.SetSystName('')
    self.SetNormUnc(NormUnc)
    self.SetSystUnc(SystUnc)
    self.SetStatUnc(StatUnc)
    self.ExpUnc = {}
    self.ModUnc = {}

###############################################################################################
###############################################################################################
###############################################################################################

class XuanPlot:

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
    return self.GetOutPath()+self.histoName

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
  def SetLegendPos(self, x0 = 0.70, y0 = 0.65, x1 = 0.93, y1 = 0.91, size = 0.065, ncol = 2):
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

  def SetTextChan(self, texch = '', x = 0.15, y = 0.87, s = 0.04):
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

  def SetTextLumi(self, texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.67, texlumiY = 0.97, texlumiS = 0.05, doinvfb = False):
    self.texlumi  = texlumi
    self.texlumiX = texlumiX
    self.texlumiY = texlumiY
    self.texlumiS = texlumiS
    self.doinvfb  = doinvfb

  def DrawTextLumi(self):
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
    c.Divide(1,2)
    plot  = c.GetPad(1)
    ratio = c.GetPad(2)
    #if self.doRatio: 
    plot.SetPad( self.hpadx0, self.hpady0, self.hpadx1, self.hpady1)
    plot.SetMargin(self.hpadMleft, self.hpadMright, self.hpadMbottom, self.hpadMtop)
    #else: plot = c.GetPad(0)
    
    if self.doRatio:
      ratio.SetPad(self.rpadx0, self.rpady0, self.rpadx1, self.rpady1)
      ratio.SetMargin(self.rpadMleft, self.rpadMright, self.rpadMbottom, self.rpadMtop)
    else:
      ratio.SetPad(0,0,0,0)
      plot.SetPad(0,0,1,1)

    # Draw the text
    texcms = self.DrawTextCMS()
    texmod = self.DrawTextCMSmode()
    texlum = self.DrawTextLumi()
    self.Tex.append(texcms)
    self.Tex.append(texmod)
    self.Tex.append(texlum)
    for r in self.Tex: r.Draw()

    TGaxis.SetMaxDigits(3)
    if self.doSetLogY: plot.SetLogy()

    # Legend
    self.legend = self.SetLegend()

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
    self.SetLogY()
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
class CompPlot(XuanPlot):
  ''' Example:
      cp = CompPlot('./temp/', doRatio = True, doNorm = True)
      cp.AddHisto(hdata, 'pe', 'e2', 'Data')
      cp.AddHisto(hMC,   'hist', '', 'MC')
      cp.autoRatio = True
      cp.Draw()
  '''

  def AddHisto(self, h, drawOpt = 'hist', drawErr = 0, addToLeng = 0):
    if self.doNorm: h.Scale(1/h.Integral())
    self.histos.append([h, drawOpt, drawErr, addToLeng])

  def AddRatioHisto(self, h, drawOpt = 'hist', drawErr = 0):
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
      h[0].Draw('same,'+h[1])
      # Draw errors
      if h[2] != 0 and h[2] != '': h[0].Draw('same,'+h[2])
      # Legend
      if h[3] != 0 and h[3] != '': self.legend.AddEntry(h[0], h[3], 'l' if 'hist' in h[1] else h[1])
    self.SetAxisPlot(self.histos[0][0])
    dmax = max(dmax)
    dmin = min(dmin)
    self.legend.Draw()

    # Set maximum and minimum
    if isinstance(self.PlotMaximum, float): self.histos[0][0].SetMaximum(self.PlotMaximum)
    else: self.histos[0][0].SetMaximum(dmax*self.PlotMaxScale)
    if isinstance(self.PlotMinimum, float): self.histos[0][0].SetMinimum(self.PlotMinimum)
    self.plot.SetLogy(doSetLogy)

    if self.doRatio: 
      if self.autoRatio:
        hRatio = self.histos[0][0].Clone('hratio')
        self.SetAxisRatio(hRatio)
        if len(self.binLabels) > 0: 
          for i in range(len(self.binLabels)):
            hRatio.GetXaxis().SetBinLabel(i+1,self.binLabels[i])
        nbins = hRatio.GetNbinsX()
        for h in self.histos[1:]: 
          htemp    = h[0].Clone(h[0].GetName()+'ratio')
          htempRat = hRatio.Clone(h[0].GetName()+'hratio')
          htempRat.Divide(htemp)
          self.AddRatioHisto(htempRat, h[1], h[2])
      self.ratio.cd()
      if len(self.ratioh) >= 1:
        self.ratioh[0][0].SetMaximum(self.PlotRatioMax)
        self.ratioh[0][0].SetMinimum(self.PlotRatioMin)
        for h in self.ratioh: 
          h[0].Draw(h[1] + ',same')
          if h[2] != 0 and h[2] != '': h[0].Draw('same,'+h[2])
        
    # Save
    gPad.SetTickx();
    gPad.SetTicky();
    self.Save()

  def __init__(self, outpath = './', outname = 'temp', doRatio = True, doNorm = False, autoRatio = True):
    self.Initialize(outpath, outname, doRatio)
    self.doNorm = doNorm
    self.autoRatio = autoRatio
    self.histos = []
    self.ratioh = []
    

##############################################################################
### Magane weights for PDF and Scale uncertainties
from OutText import OutText
class WeightReader:
 ''' Get uncertainties from 9 scale weights and 33 PDF weights  

     ### For PDF + alpha_S
     See https://arxiv.org/pdf/1510.03865.pdf
     Eq 20 and 27 for PDF and alpha_s
     PDF4LHC15_nlo_nf4_30_pdfas, 1+30+2 weights, see Table 6
 '''

 def SetPath(self, p):
   self.path = p

 def SetOutPath(self, p):
   self.outpath = p

 def SetSampleName(self, n):
   self.sampleName = n

 def SetPDFhistoName(self, n):
   self.PDFhistoName = n

 def SetScaleHistoName(self, n):
   self.scaleHistoName = n

 def SetNormScaleHistoName(self, n):
   self.normScaleHitstoName = n

 def SetNormPDFhistoName(self, n):
   self.normPDFhistoName = n

 def SetSampleName(self, n):
   self.sampleName = n

 def SetLumi(self, l):
   self.lumi = l

 def SetLevel(self, l):
   self.level = l

 def SetChan(self, c):
   self.chan = c

 def SetNgenEvents(self, n):
   self.nGenEvents = n

 def GetNgenEvents(self):
   return self.nGenEvents

 def GetLumi(self):
   return self.lumi

 def GetSampleName(self):
   return self.sampleName

 def GetLevel(self):
   return self.level

 def GetChan(self):
   return self.chan

 def loadHistos(self):
   ''' Load the PDF and Scale histos and norm histos '''
   t = TopHistoReader(self.path)
   t.SetIsData(1)
   n = self.GetSampleName()
   t.SetProcess(n)
   t.SetChan(self.GetChan())
   t.SetLevel(self.GetLevel())
   if self.GetNgenEvents() <= 0 : self.SetNgenEvents(t.GetNGenEvents())
   self.hpdf      = t.GetHisto(n,self.PDFhistoName)
   self.hscale    = t.GetHisto(n,self.scaleHistoName)
   self.hsumpdf   = t.GetNamedHisto(self.normPDFhistoName)
   self.hsumscale = t.GetNamedHisto(self.normScaleHitstoName)

 def GetPDFyield(self, i):
   ''' Return value of bin i for PDF weights '''
   return self.hpdf.GetBinContent(i)*self.GetLumi()/self.GetPDFnorm(i)*self.GetNgenEvents()

 def GetPDFnom(self):
   ''' Nominal PDF set '''
   return self.GetPDFyield(1)

 def GetPDFnorm(self, i):
   ''' Get sum of PDF weights for a given set i '''
   return self.hsumpdf.GetBinContent(i)

 def GetScaleNorm(self, i):
   ''' Get sum of Scale weights for a given set i '''
   return self.hsumscale.GetBinContent(i)

 def GetScaleYield(self, i):
   ''' Return value of bin i for scale weights '''
   return self.hscale.GetBinContent(i)*self.GetLumi()/self.GetScaleNorm(i)*self.GetNgenEvents()

 def GetScaleNom(self):
   ''' Nominal scale weights '''
   return self.GetScaleYield(1)

 def GetRelUncScale(self, i):
   ''' Returns the relative unc for a given scale set '''
   return abs(self.GetScaleYield(i)-self.GetScaleNom())/self.GetScaleNom()

 def GetRelUncPDF(self, i):
   ''' Returns the relative unc for a given PDF set i '''
   return abs(self.GetPDFyield(i)-self.GetPDFnom())/self.GetPDFnom()

 def GetMaxRelUncScale(self):
   ''' Returns the max scale unc (avoiding unphysical variations) '''
   var = []; 
   for i in range(1,10):
     if i == 3 or i == 7: continue
     var.append(self.GetRelUncScale(i))
   return max(var)

 def GetPDFunc(self):
   ''' 
     Eq [20] in:  https://arxiv.org/pdf/1510.03865.pdf
     Weights 2, to 31, using 1 as nominal
   '''
   delta = sum([self.GetRelUncPDF(i)*self.GetRelUncPDF(i) for i in range(2,32)])
   return sqrt(delta)

 def GetAlphaSunc(self):
   '''
    Eq [27] in:  https://arxiv.org/pdf/1510.03865.pdf
    Weights 32 and 33
   '''
   alphaDo = self.GetPDFyield(32)
   alphaUp = self.GetPDFyield(33)
   return abs(alphaUp - alphaDo)/2/self.GetPDFnom()

 def GetPDFandAlphaSunc(self):
   ''' Quadratic sum of both '''
   pdfunc = self.GetPDFunc()
   alphas = self.GetAlphaSunc()
   return sqrt(pdfunc*pdfunc + alphas*alphas)
    
 def PrintMEscale(self, name = 'ScaleMEvariations'):
   ''' Prints a table with the info of scale systematics '''
   t = OutText(self.outpath, name)
   s = lambda i,muF,muR: ' [%d] muF = %1.2f, muR = %1.2f  | %1.2f (%1.2f %s)' %(i,muF,muR,self.GetScaleYield(i),self.GetRelUncScale(i)*100,'%')
   nom = s(1,0.5,0.5) + ' (nominal)'
   t.SetSeparatorLength(len(nom))
   t.line(" Scale ME uncertainties on tt acceptance")
   t.bar()
   t.line(nom)
   t.line(s(2,0.5, 1.0))
   t.line(s(3,0.5, 2.0) + ' (unphysical)')
   t.line(s(4,1.0, 0.5))
   t.line(s(5,1.0, 1.0))
   t.line(s(6,1.0, 2.0))
   t.line(s(7,2.0, 0.5) + ' (unphysical)')
   t.line(s(8,2.0, 1.0))
   t.line(s(9,2.0, 2.0))
   t.sep()
   t.line(' Maximum variation: %1.2f %s '%(self.GetMaxRelUncScale()*100,'%'))
   t.bar()
   t.write()

 def PrintPDFyields(self, name = 'PDFvariations'):
   ''' Prints a table with the info of PDF systematics '''
   t = OutText(self.outpath, name)
   s = lambda i : ' '+t.fix('[%d]'%i,4,'l',False) + ' %1.2f (%1.2f %s)' %(self.GetPDFyield(i), self.GetRelUncPDF(i)*100,'%')
   c0 = s(1) + ' (nominal) '
   t.SetSeparatorLength(len(c0))
   t.line('### PDF and alpha_s uncertianties')
   t.line()
   t.line(' Using PDF4LHC15_nlo_nf4_30_pdfas, 1+30+2 weights, see Table 6 in ')
   t.line(' > https://arxiv.org/pdf/1510.03865.pdf')
   t.bar()
   t.line(c0)
   for i in range(2,34): t.line(s(i))
   t.sep()
   pdfunc = self.GetPDFunc()
   alphas = self.GetAlphaSunc()
   totunc = self.GetPDFandAlphaSunc()
   t.line(' See reference: ')
   t.line(' > https://arxiv.org/pdf/1510.03865.pdf')
   t.line(' Eq [20] for PDF unc:  %1.2f (%1.2f %s)' %(pdfunc*self.GetPDFnom(), pdfunc*100, '%'))
   t.line(' Eq [27] for alpha_S:  %1.2f (%1.2f %s)' %(alphas*self.GetPDFnom(), alphas*100, '%'))
   t.sep()
   t.line(' Total PDF + alpha_S uncertainty: ')
   t.line('  ## %1.2f (%1.2f %s)' %(totunc*self.GetPDFnom(), totunc*100, '%'))
   t.bar()
   t.write()

 def __init__(self, path = '', outpath = './temp/', chan = 'ElMu', level = '2jets', sampleName = 'TT', PDFname = 'PDFweights', ScaleName = 'ScaleWeights', PDFsumName= 'SumOfPDFweights', ScaleSumName = 'SumOfScaleWeights', lumi = 308.54, nGenEvents = -1):
   self.SetPath(path)
   self.SetOutPath(outpath)
   self.SetChan(chan)
   self.SetLevel(level)
   self.SetSampleName(sampleName)
   self.SetPDFhistoName(PDFname)
   self.SetScaleHistoName(ScaleName)
   self.SetNormPDFhistoName(PDFsumName)
   self.SetNormScaleHistoName(ScaleSumName)
   self.SetLumi(lumi)
   self.SetNgenEvents(nGenEvents)
   self.loadHistos()




class StackPlot(XuanPlot):

  #############################################################################################
  ### Pads
  def SetLumi(self, lumi):
    self.lumi = lumi
    self.t.SetLumi(self.lumi)

  def GetOutName(self):
    return self.GetOutPath()+self.histoName

  def SetStackOverflow(self, t = True):
    self.t.doStackOverflow = t

  #############################################################################################
  #############################################################################################
  # Select histograms

  def SetHistoName(self, histoName = ''):
    self.SetOutName(histoName)

  def CraftHistoName(self):
    name = self.var + '_' + self.chan + '_' + self.level
    if self.syst != '': name += '_' + self.syst
    return name

  def SetChan(self, ch):
    self.chan = ch

  def SetLevel(self, ilev):
    self.level = ilev

  def SetSyst(self, syst):
    self.syst = syst

  def SetVar(self, var):
    self.var = var

  def SetVarChanLev(self, var, ch, ilev):
    self.SetVar(var)
    self.SetChan(ch)
    self.SetLevel(ilev)

  #############################################################################################
  ### Add process
  
  def AddProcess(self, processName, samples, color):
    self.pr.append(Process(processName, color, samples))
    #self.t.GetNamedHisto(self.histoName)
    #self.t.SetProcess(samples)
 
  def GetProcess(self, name):
    for pr in self.pr:
      if pr.GetName() == name: return pr
    print 'WARNING: not found process \''+name+'\''
    return False

  def GetSystematicHisto(self, name, syst):
    for s in self.systSamples:
      if pr.GetName() == name and pr.GetSystName() == syst: return pr
    print 'WARNING: not found systematic \''+syst+'\' for process \''+name+'\''
    return False

  def AddSystematic(self, processName, samples, systname):
    print 'Adding Process %s, systematic %s and sample %s'%(processName,systname,samples)
    self.systSamples.append(Process(processName, 1, samples, systName = systname))

  def AddData(self, datasamples):
    self.data = Process('Data', 1, datasamples, isData = True)

  def SetHisto(self, histoName=''):
    if   histoName != '': 
      self.histoName = histoName
      bits = histoName.split('_')
      if len(bits) >= 3:
        self.SetVar(bits[0])
        self.SetChan(bits[1])
        self.SetLevel(bits[2])
        if len(bits) >= 4: self.SetSyst(bits[3])
    else:                 
      self.SetSyst('')
      self.SetHistoName(self.CraftHistoName())
    self.t.SetProcess(self.pr[0].GetSamples())
    htemp = self.t.GetNamedHisto(self.histoName)
    self.nbins = htemp.GetNbinsX()
    self.ResetSyst()
    self.t.SetIsData(False)
    # Nominal
    for pr in self.pr:
      self.t.SetProcess(pr.GetSamples())
      pr.SetHisto(self.t.GetNamedHisto(self.histoName))
    # Systematic samples
    for pr in self.systSamples:
      self.t.SetProcess(pr.GetSamples())
      pr.SetHisto(self.t.GetNamedHisto(self.histoName))
    if hasattr(self,'data'):
      self.t.SetIsData(True)
      self.t.SetProcess(self.data.GetSamples())
      self.data.SetHisto(self.t.GetNamedHisto(self.histoName))
      self.t.SetIsData(False)

  #############################################################################################
  ### Histograms and systematics
  
  def GetAllBkg(self, syst = ''):
    processes = [x.GetSamples() for x in self.pr]
    self.SetSyst(syst)
    histoName = self.CraftHistoName() if self.histoName == '' else self.histoName# + ('' if syst == '' else '_'+syst)
    self.t.SetSystematic(syst)
    return self.t.GetNamedHisto(histoName, processes)

  def AddToSyst(self, syst):
    self.expSyst = syst

  def GetExpSyst(self):
    return self.expSyst

  def SumExpSyst(self, syst = ''):
    if syst == '': syst = self.GetExpSyst()
    if self.verbose >= 2: print 'Including systematics: ', syst
    if ',' in syst: 
      self.SumExpSyst(syst.replace(' ', '').split(','))
      return
    if isinstance(syst, list):
      for s in syst: self.SumExpSyst(s)
      return
    print 'Adding exp systematic %s...'%syst
    hnom = self.GetAllBkg()
    self.SetSyst(syst)
    hvar = self.GetAllBkg(syst)
    nbins = hnom.GetNbinsX()
    if not hasattr(self, 'sysup'):
      self.sysup = [0]*nbins
      self.sysdo = [0]*nbins
    d = [hvar.GetBinContent(i) - hnom.GetBinContent(i) for i in range(1, nbins+1)]
    if average(d) >= 0: self.sysup = [sqrt(a*a+b*b) for a,b in zip(self.sysup, d)]
    else:               self.sysdo = [sqrt(a*a+b*b) for a,b in zip(self.sysdo, d)]

  def ResetSyst(self):
    nbins = self.nbins
    self.sysup = [0]*self.nbins
    self.sysdo = [0]*self.nbins
    
  def AddSystFromHistos(self):
    if not hasattr(self, 'sysup'): self.ResetSyst()
    for pr in self.systSamples:
      name = pr.GetName()
      hvar = pr.histo()
      print 'Adding to systematics histo %s, with bins %i'%(name, hvar.GetNbinsX())
      hnom = self.GetProcess(name).histo()
      nbins = hnom.GetNbinsX()
      d = [hvar.GetBinContent(i) - hnom.GetBinContent(i) for i in range(1, nbins+1)]
      if average(d) > 0: self.sysup = [sqrt(a*a+b*b) for a,b in zip(self.sysup, d)]
      else:              self.sysdo = [sqrt(a*a+b*b) for a,b in zip(self.sysdo, d)]

  def AddStatUnc(self):
    if self.verbose >= 2: print 'Setting MC stat uncertainties...'
    if self.IncludedStatUnc: return
    self.IncludedStatUnc = True
    hnom = self.GetAllBkg()
    nbins = hnom.GetNbinsX()
    if not hasattr(self, 'sysup'): self.ResetSyst()
    du = [hnom.GetBinError(i) for i in range(1, nbins+1)]
    dd = [-hnom.GetBinError(i) for i in range(1, nbins+1)]
    self.sysup = [sqrt(a*a+b*b) for a,b in zip(self.sysup, du)]
    self.sysdo = [sqrt(a*a+b*b) for a,b in zip(self.sysdo, dd)]
      
  #############################################################################################
  ### Draw stack

  def DrawStack(self, histo = '', xtit = '', ytit = '', rebin = 1):
    ''' Draws a stack plot '''
    # Set the canvas and pads
    self.t.SetRebin(rebin)
    if histo != '': self.SetHisto(histo)
    if xtit  != '': self.axisXtit = xtit
    if ytit  != '': self.axisYtit = ytit
    self.SetCanvas()

    # Stack processes and draw stack and data
    self.plot.cd()
    gPad.SetTickx();
    gPad.SetTicky();
    if not os.path.isdir(self.GetOutPath()): os.makedirs(self.GetOutPath())
    hStack = THStack('stack', '')
    for pr in self.pr: 
      hStack.Add(pr.histo())
    hStack.Draw('hist')

    datamax = -999
    if hasattr(self, 'data'):
      data = self.data.histo()
      data.SetBinErrorOption(TH1.kPoisson)
      data.Sumw2(False);
      data.Draw('psameE0X0')#self.data.GetDrawStyle())
      datamax = data.GetMaximum()
      #if self.doPoissonErrors:
    
    bkg = hStack.GetStack().Last().Clone('AllBkg')

    dmax = max(datamax, bkg.GetMaximum())
    if isinstance(self.PlotMaximum, float): hStack.SetMaximum(self.PlotMaximum)
    else: hStack.SetMaximum(dmax*self.PlotMaxScale)
    if isinstance(self.PlotMinimum, float): hStack.SetMinimum(self.PlotMinimum)

    hRatio = data.Clone() if hasattr(self, 'data') else bkg.Clone()
    nbins = hRatio.GetNbinsX()
    for i in range(nbins+1):
      b = bkg. GetBinContent(i)
      d = data.GetBinContent(i) if hasattr(self, 'data') else b
      if b == 0: b = 1
      e = 0 if d == 0 else d/b*(sqrt(d)/d)
      hRatio.SetBinContent(i, d/b)
      hRatio.SetBinError(i, e)
  
    # Set titles...
    TGaxis.SetMaxDigits(3)
    self.SetAxisPlot(hStack)

    self.SetAxisRatio(hRatio)

    if len(self.binLabels) > 0: 
      for i in range(len(self.binLabels)):
        if self.doRatio:
          hRatio.GetXaxis().SetBinLabel(i+1,self.binLabels[i])
        else:
          hStack.GetXaxis().SetBinLabel(i+1,self.binLabels[i])


    # Set syst histo
    self.AddStatUnc()
    self.AddSystFromHistos()
    self.SumExpSyst()
    bkg.SetFillStyle(3444); 
    bkg.SetFillColor(kGray+2);
    #bkg.SetFillColorAlpha(kGray+2, 1);
    nbins = bkg.GetNbinsX()
    for i in range(1, self.nbins+1):
      err = (abs(self.sysup[i-1]) + abs(self.sysdo[i-1]))/2
      #if not err == err: err = 0
      bkg.SetBinError(i, err)
    bkg.SetLineColor(0)
    bkg.Draw("same,e2")
    
    # Legend
    if hasattr(self, 'data'): self.legend.AddEntry(self.data.histo(), 'Data', 'pe')
    for pr in reversed(self.pr): self.legend.AddEntry(pr.histo(), pr.GetName(), 'f')
    if self.doSystInLeg: self.legend.AddEntry(bkg, 'Stat #oplus Syst', 'f')
    self.legend.Draw()

    # Ratio
    if self.doRatio:
      self.ratio.cd()
      hRatio.SetMaximum(self.PlotRatioMax)
      hRatio.SetMinimum(self.PlotRatioMin)
      if hasattr(self, 'data'): hRatio.Draw(self.data.GetDrawStyle())
      else:                     hRatio.Draw('lsame')
      hRatioErr = bkg.Clone("hratioerr")
      for i in range(1, self.nbins+2):
        hRatioErr.SetBinContent(i, 1)   
        val = bkg.GetBinContent(i)
        err = bkg.GetBinError(i)
        hRatioErr.SetBinError(i, err/val if val != 0 else 0)
      hRatioErr.Draw("same,e2")

    self.Save()
    # Save
    #if not os.path.isdir(self.GetOutPath()): os.makedirs(self.GetOutPath())
    #c.Print(self.GetOutName()+'.pdf', 'pdf')
    #c.Print(self.GetOutName()+'.png', 'png')

  #############################################################################################
  #############################################################################################
  # Init

  def __init__(self, path = '', histoName = '', outPath = './'):
    self.Initialize(outPath, histoName, True)
    self.t = TopHistoReader(path)
    self.SetHistoName(histoName)
    self.SetChan('')
    self.SetLevel('')
    self.SetVar('')
    self.SetSyst('')
    self.verbose = 1
    self.pr = []    # Simulated processes
    self.systSamples = []  # Samples for systematics 
    self.allpr   = ''
    self.allprUp = ''
    self.allprDo = ''
    self.IncludedStatUnc = False
    self.expSyst = ''
    self.doSystInLeg = False





















#################################################################################################
### Histo saver
#################################################################################################

class HistoSaver:
 ''' Class to save histograms from different process and prepare a .root file 
     to use with the Higgs Combine tool
 '''

 def SetPath(self, p):
  if not p.endswith('/'): p += '/'
  if p == '/': p = './'
  self.path = p
  self.t.SetPath(self.path)

 def SetOutputDir(self, d):
  self.outdir = d
  if not self.outdir.endswith('/'): self.outdir += '/'

 def SetOutName(self, n):
  if n == '': n = 'histos'
  self.outname = n

 def GetOutFileName(self):
  return self.outdir + self.outname + '.root'

 def AddSystematic(self, *s):
  if len(s) == 1: s = s[0] 
  if isinstance(s, list) or isinstance(s, tuple): 
    for e in s: self.AddSystematic(e)
  else:
    self.syst.append(s)

 def SetVar(self, var):
  self.var = var

 def SetChan(self, chan):
   self.chan = chan
  
 def SetLevel(self, ilevel):
   self.level = ilevel

 def SetHistoName(self, h = ''):
   self.histoName = h

 def SetLumi(self, lumi):
   self.lumi = lumi
   self.t.SetLumi(self.lumi)

 def SetVarChanLev(self, var, ch, ilev):
  self.SetVar(var)
  self.SetChan(ch)
  self.SetLevel(ilev)

 def SetRebin(self, r = 1):
  self.rebin = r
  self.t.SetRebin(self.rebin)

 def AddProcess(self, prName, files = ''):
  if isinstance(prName, dict):
    self.dpr = prName
  elif isinstance(prName, list):
    for pr,f in zip(prName, files): self.dpr[pr] = f
  else: self.dpr[prName] = files

 def AddData(self, files = ''):
  self.dataFiles = files

 def AddHisto(self, h, prName, systname = ''):
  hOut = prName if systname == '' else prName + '_' + systname
  h.SetName(hOut)
  self.histos.append(h)

 def LoadHisto(self, fname, process, syst = '',hname = '', ):
  if fname in self.dpr.keys(): fname = self.dpr[fname]
  if hname == '': hname = self.GetHistoName()
  if syst != '':
    if self.t.IsHisto(fname, hname+'_'+syst): 
      self.LoadHisto(fname, process+'_'+syst, hname = hname+'_'+syst)
      return
    else:
      if self.t.IsHisto(fname, hname+'_'+syst+'Up'):   self.LoadHisto(fname, process+'_'+syst+'Up', hname = hname+'_'+syst+'Up')
      if self.t.IsHisto(fname, hname+'_'+syst+'Down'): self.LoadHisto(fname, process+'_'+syst+'Down', hname = hname+'_'+syst+'Down')
      return
  h = self.t.GetNamedHisto(hname, fname, self.rebin)
  self.AddHisto(h, process, syst)
  
 def GetHistoName(self):
  if self.histoName != '': return self.histoName
  hname = var + ('_' + self.chan if self.chan != '' else '') + ('_' + self.level if self.level != '' else '')
  self.SetHistoName(hname)
  return hname

 def ReadHistos(self):
   for k in self.dpr.keys():
     self.LoadHisto(self.dpr[k], k, '')
     for s in self.syst:
       self.LoadHisto(self.dpr[k], k, s)
   self.LoadHisto(self.dataFiles,'data_obs','')

 def Write(self):
  fname = self.GetOutFileName()
  if not os.path.isdir(self.outdir): os.mkdir(self.outdir)
  if os.path.isfile(fname): os.rename(fname, fname+'.bak')
  f = TFile(fname, 'recreate')
  print ' >> Saving histograms in: ' + fname
  for h in self.histos: h.Write()
  f.Close()

 def __init__(self, path, hname = '', outpath = './temp/', outname = '', rebin = 1):
  self.t = TopHistoReader(path)
  self.SetPath(path)
  self.SetRebin(rebin)
  self.SetHistoName(hname)
  self.SetOutputDir(outpath)
  self.SetOutName(outname)
  self.histos = []
  self.syst = []
  self.dpr = {}
  self.AddData()


