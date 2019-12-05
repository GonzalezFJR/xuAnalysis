import os,sys
#import ROOT
from ROOT import TH1F, TH1, TFile, TCanvas, TPad, THStack, TLatex, TLegend, TGaxis, TChain
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack
from ROOT import gPad, gROOT
from ROOT.TMath import Sqrt as sqrt
from copy import deepcopy
from framework.fileReader import GetFiles
average = lambda x: sum(x)/len(x)
gROOT.SetBatch(1)
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')

#from ttbar.ttanalysis import ch, chan, lev, level, dataset, datasets, systematic, systlabel  
level = {0:'dilepton', 1:'ZVeto', 2:'MET', 3:'2jets', 4:'1btag'}

class TopHistoReader:
 ''' Reads histograms created with the ttanalysis '''
 def SetFileNamePrefix(self, p):
   self.fileprefix = p
 
 def SetHistoNamePrefix(self,p):
   self.histoprefix = p

 def SetPath(self, path):
   if path == '': path = '/'
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

 def SetYieldsSSname(self, n = "SSYields"):
   self.YieldsSSname = n

 def GetHistoName(self):
   ''' Craft histo name from var, chan, level '''
   name = (self.histoprefix + '_' if self.histoprefix != '' else '') + self.var + '_' + self.chan + '_' + self.level
   if len(self.syst) > 0: name += '_' + self.syst
   return name

 def IsHisto(self, pr, name, syst = ''):
   ''' Check if histo exists '''
   if pr    != '': self.SetProcess(pr)
   if ',' in self.process: self.process = self.process.replace(' ', '').split(',')
   if isinstance(self.process, list):
     for p in self.process: 
       if not self.IsHisto(p, name, syst): return False
     return True
   if syst != '':
     if self.IsHisto(pr, name + '_' + syst) or self.IsHisto(pr, name + '_' + syst+'Up') or self.IsHisto(pr, name + '_' + syst+'Down'): return True
     return False
   if not pr.endswith('.root'): pr += '.root'
   filename = self.path + self.fileprefix + pr
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
     return self.GetNamedHisto(listOfNames, pr, rebin)
   elif isinstance(name, list):
     listOfNames = name
     h = self.GetNamedHisto(listOfNames[0], pr, rebin)
     for n in listOfNames[1:]:
       while n[0 ] == ' ': n = n[1:]
       while n[-1] == ' ': n = n[:-1]
       h.Add(self.GetNamedHisto(n, pr, rebin))
     return h

   filename = self.path + self.fileprefix + pr
   if not filename.endswith('.root'): filename += '.root'
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
       h.SetBinError(i, bc/sqrt(bc/integral*entries) if (entries != 0 and bc!=0 and integral!=0) else 0)
   else:
     for i in range(1,nbins+1):
       bc = h.GetBinContent(i) if h.GetBinContent(i) > 0 else 0
       be = h.GetBinError(i)
       if bc == 0: h.SetBinContent(i, bc)
       if be > bc: h.SetBinError(i, bc)
       #h.SetBinError(i, sqrt(bc*integral/entries) if entries != 0 else 0)
   if self.doNormalize: h.Scale(1./(integral if integral != 0 else 1))
   return h

 def GetBinNumberForLevel(self, ilev = ''):
   ''' Returns the bin number for a given level for the yields histogram '''
   if ilev == '': ilev = self.level
   if isinstance(ilev,int): return ilev
   for lv in level.keys(): 
     if ilev == level[lv]: return lv+1
   return -1

 def GetYieldHisto(self, pr = '', ch = '', syst = '', SS = False):
   ''' Returns the histogram with yields '''
   if pr != '': self.SetProcess(pr)
   if ch != '': self.SetChan(ch)
   self.SetSystematic(syst)
   prename = 'Yields_' if not SS else self.YieldsSSname + '_'#'SSYelds_'
   if self.histoprefix != '': prename = self.histoprefix + '_' + prename
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

 def GetNGenEvents(self, pr = '', hname = 'nGenEvents'):
   ''' Returns the number of gen events, stored in histogram hGenEvents '''
   self.SetIsData(True)
   h = self.GetNamedHisto(hname,pr)
   self.SetIsData(False)
   return h.GetBinContent(1)

 def GetFiduEvents(self, pr = '', ilev = '', chan = ''):
   ''' Returns value for FiduEvents histogram '''
   if ilev != '': self.SetLevel(ilev)
   self.SetIsData(True)
   h = self.GetNamedHisto("H_FiduYields_%s"%chan,pr)
   self.SetIsData(False)
   y = h.GetBinContent(self.GetBinNumberForLevel(self.level))
   self.SetIsData(False)
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

 ### Histodic

 def AddProcessDic(self, process):
   if process in self.histodic.keys(): return
   else:
    d = {}
    self.histodic[process] = d

 def AddToHistoDic(self, h, process, hname, syst = ''):
   hist = TH1F()
   hist = h.Clone()
   if syst != '': hname = hname+'_'+syst
   self.AddProcessDic(process)
   self.histodic[process][hname] = hist

 def GetSystHistoNames(self, process, hname, syst):
   #print 'Looking for syst labes pr [%s] hname [%s] syst [%s]'%(process, hname, syst)
   hnames = []
   name = '%s_%s'%(hname, syst)
   if self.IsHisto(process, name): hnames.append(name)
   name = '%s_%s%s'%(hname, syst, 'Up')
   if self.IsHisto(process, name): hnames.append(name)
   name = '%s_%s%s'%(hname, syst, 'Do')
   if self.IsHisto(process, name): hnames.append(name)
   name = '%s_%s%s'%(hname, syst, 'Down')
   if self.IsHisto(process, name): hnames.append(name)
   return hnames
   
 def GetHistoDic(self, processDic, hname, systlist, systdic = {}):
   if isinstance(hname, str) and ',' in hname: hname = hname.replace(' ', '').split(',') 
   if isinstance(hname, list): 
     for histoname in hname:
       self.GetHistoDic(processDic, histoname, systlist, systdic)
     return self.histodic
   processes = processDic.keys()
   for pr in processes:
     h = TH1F()
     if hname == "%s": hname = hname%pr
     h = self.GetNamedHisto(hname, processDic[pr], rebin=self.rebin)
     self.AddToHistoDic(h, pr, hname)
     for syst in systlist:
       hnames = self.GetSystHistoNames(processDic[pr], hname, syst)
       for hsyst in hnames:
         h = TH1F()
         h = self.GetNamedHisto(hsyst, processDic[pr], rebin=self.rebin)
         self.AddToHistoDic(h, pr, hsyst)
   for pr in systdic:
     if not pr in processes: continue
     for syst in systdic[pr].keys():
       h = TH1F()
       h = self.GetNamedHisto(hname, systdic[pr][syst], rebin=self.rebin)
       hsystname = '%s_%s'%(hname, syst)
       self.AddToHistoDic(h, pr, hsystname)
   return self.histodic

 def __init__(self, path = './', process = '', var = '', chan = '', ilevel = '', syst = '', fileprefix = '', histoprefix = ''):
    self.doStackOverflow = False
    self.doNormalize = False
    self.IsData  = False
    self.verbose = False
    self.fname = ''
    self.rebin = 1
    self.lumi = 1
    self.ReComputeStatUnc = True 
    self.SetFileNamePrefix(fileprefix)
    self.SetHistoNamePrefix(histoprefix)
    self.histodic = {}

    self.SetPath(path)
    self.SetProcess(process)
    self.SetVar(var)
    self.SetChan(chan)
    self.SetLevel(ilevel)
    self.SetSystematic(syst)
    self.SetYieldsSSname()


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
  oname = self.outdir + self.outname
  if not oname.endswith('.root'): oname += '.root'
  return oname

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

####################################################################################################
####################################################################################################
'''
 Get a dictionary with histograms and compute all the uncertainties
 # dic['process']['histoname']
 h = HistoMerger(dic, ListOfProcesses, ListOfUncertainties, NameOfHistogram)
 h.SumHistos()
 hstat = h.GetUncHist('stat')
 hsyst = h.GetUncHist()
'''

class HistoManager:
  def SetProcessList(self, listOfProcesses):
    if isinstance(listOfProcesses, str): listOfProcesses = listOfProcesses.replace(' ', '').split(',')
    self.processList = listOfProcesses

  def AddToSignals(self, signals):
    if isinstance(signals, str):
      if ',' in signals: signals = signals.replace(' ', '').split(',')
      else             : signals = [signals]
      self.AddToSignals(signals)
      return
    else: self.signalProcess += signals
                     
  def SetHistoName(self, hname, rebin = 1):
    self.histoname = hname
    self.rebin = 1

  def SetSystList(self, listOfSyst):
    if isinstance(listOfSyst, str): listOfSyst = listOfSyst.replace(' ','').split(',')
    self.systname = listOfSyst

  def LookForSystLabels(self):
    self.systlabels = []
    for s in self.systname:
      #histoname = self.histoname[0] if isinstance(self.histoname, list) else self.histoname
      self.SearchSystHisto(self.histoname, s)

  def SetDataName(self, dname = 'data'):
    self.dataname = dname

  def SetProcessDic(self, pd):
    self.processDic = pd

  def SetSystDic(self, systdic):
    self.systdic = systdic

  def SetTopReader(self, path):
    self.path = path
    self.thr = TopHistoReader(path)
    self.thr.SetLumi(1)

  def SetStackOverflow(self, t = True):
    self.thr.doStackOverflow = t
 
  def SetRebin(self, rebin):
    self.thr.SetRebin(rebin)
    self.rebin = rebin

  def SetInputDicFromReader(self):
    hdic = self.thr.GetHistoDic(self.processDic, self.histoname, self.systname, self.systdic)
    self.indic = hdic
    return hdic

  def GetHistoName(self):
    return self.histoname

  def GetListOfCandNames(self, syst):
    systCand = ["%s"%syst, "%sUp"%syst, "%sDo"%syst, "%sDown"%syst]
    return systCand

  def SearchSystHisto(self, hname, syst = ''):
    systCand = self.GetListOfCandNames(syst)
    for syst in systCand:
      found = False
      name = "%s_%s"%(hname, syst) if syst != '' else hname
      for pr in self.processList:
        khist = self.indic[pr].keys()
        if name in khist: found = True
      if found: self.systlabels.append(syst)

  def SumHistos(self, syst = 'ALL'):
    #histoname = self.histoname[0] if isinstance(self.histoname, list) else self.histoname
    if syst == 'ALL':
      self.SumHistos('')
      for s in self.systname: self.SumHistos(s)
      return
    elif syst == '':
      if isinstance(self.histoname, list):
        h = self.indic[self.processList[0]][self.histoname[0]].Clone("sum0")
        for hname in self.histoname[1:]:
          h.Add(self.indic[self.processList[0]][hname])
      else: 
          hnam = self.histoname if self.histoname != '%s' else self.processList[0]
          h = self.indic[self.processList[0]][hnam].Clone("sum0")
      h.SetDirectory(0)
      if len(self.processList) > 1:
        for pr in self.processList[1:]: 
          hnam = self.histoname if self.histoname != '%s' else pr
          if isinstance(self.histoname, list):
            for hname in self.histoname:
              h.Add(self.indic[pr][hname])
          else: h.Add(self.indic[pr][hnam])
      self.sumdic[syst] = h
    else:
      for s in self.GetListOfCandNames(syst):
        if not s in self.systlabels: continue
        pr0 = self.processList[0]
        hname = self.histoname if not isinstance(self.histoname, list) else self.histoname[0]
        hnam  = hname if hname != "%s" else pr0
        hs = "%s_%s"%(hnam, s) if "%s_%s"%(hnam, s) in self.indic[pr0].keys() else hnam
        h = self.indic[pr0][hs].Clone("sum_%s"%s)
        if len(self.processList) > 1:
          for pr in self.processList[1:]:
            hnam  = hname if hname != "%s" else pr
            hs = "%s_%s"%(hnam, s) if "%s_%s"%(hnam, s) in self.indic[pr].keys() else hnam
            h.Add(self.indic[pr][hs])
        if isinstance(self.histoname, list):
          for hname in self.histoname[1:]:
            for pr in self.processList:
              hnam  = hname if hname != "%s" else pr
              hs = "%s_%s"%(hnam, s) if "%s_%s"%(hnam, s) in self.indic[pr].keys() else hnam
              h.Add(self.indic[pr][hs])
        self.sumdic[s] = h

  def GetDifUnc(self, hnom, hsyst):
    ''' Get a nom histo and a list of histos and returns the mean per-bin error in a list 
        hsyst is a list of labels, not name of uncertainty
    '''
    nb = hnom.GetNbinsX()
    n = [hnom.GetBinContent(i) for i in range(0, nb+2)]
    if not isinstance(hsyst, list): hsyst = [hsyst]
    var  = [ [(h.GetBinContent(i)-n[i]) for i in range(0, nb+2)] for h in hsyst]
    nsyst = len(var)
    meansyst = []
    if nsyst == 0:
      print 'ERROR: no systematics set...'
      return meansyst
    for i in range(0, nb+2):
      up = 0; do = 0
      for j in range(nsyst):
        up += abs(var[j][i]) if var[j][i] > 0 else 0
        do += abs(var[j][i]) if var[j][i] < 0 else 0
      l = (up+do)/2
      meansyst.append(l)
    return meansyst

  def GetStatHisto(self, direc = 'Up'):
    ''' Returns a histogram with the nominal values plus (minus) stat unc '''
    hnom = self.sumdic[''].Clone("stat"+direc)
    hnom.SetDirectory(0)
    nb = hnom.GetNbinsX()
    for i in range(0, nb+2):
      v = hnom.GetBinContent(i)
      e = hnom.GetBinError(i)
      nv = v+e if (direc == 'Up' or direc == 'UP' or direc == 'up') else v-e
      hnom.SetBinContent(i, nv)
    return hnom

  def GetStatUnc(self):
    ''' List with stat unc from nominal histo '''
    hnom = self.sumdic['']
    nb = hnom.GetNbinsX()
    statunc = [hnom.GetBinError(i) for i in range(0, nb+2)]
    return statunc

  def GetSum2Unc(self, lsyst = '', includeStat = True):
    ''' From a list of uncertainties, get a list of per-bin unc w.r.t. nominal histo 
        lsyst is a list of uncertainty names, not labels
    '''
    if   lsyst == '': lsyst = self.systname[:]
    elif isinstance(lsyst, str) and ',' in lsyst: lsyst = lsyst.replace(' ', '').split(',')
    elif not isinstance(lsyst, list): lsyst = [syst]
    if includeStat and not 'stat' in lsyst: lsyst.append('stat') #sum2.append(self.GetStatUnc())
    unc = []
    systExist = lambda x : x in self.systlabels
    for s in lsyst:
      listOfGoodSyst = filter(systExist, self.GetListOfCandNames(s))
      if s == 'stat':
        listOfHistos = [self.GetStatHisto()]
      elif len(listOfGoodSyst) == 0:
        print 'WARNING: no systematic found for label %s!'%s
        continue
      else: 
        listOfHistos = [self.sumdic[s] for s in listOfGoodSyst]
      unc.append(self.GetDifUnc(self.sumdic[''], listOfHistos))
    sum2 = []
    nlen = len(unc[0])
    for i in range(nlen):
      v = 0
      for iunc in unc: v += iunc[i]*iunc[i]
      v = sqrt(v)
      sum2.append(v)
    return sum2

  def ScaleByLumi(self):
    if self.IsScaled: return
    for pr in self.processList + self.signalProcess:
      for h in self.indic[pr]: 
        self.indic[pr][h].SetStats(0)
        self.indic[pr][h].SetTitle('')
        self.indic[pr][h].Scale(self.lumi)
    self.IsScaled = True

  def GetUncHist(self, syst = '', includeStat = True):
    ''' syst is a name, not a label... returns nominal histo with nice uncertainties '''
    if   syst == '': syst = self.systname
    elif isinstance(syst, str) and ',' in syst: syst = syst.replace(' ', '').split(',')
    elif not isinstance(syst, list): syst = [syst]
    sumdic = self.sumdic.copy() # To keep the original
    hnom = sumdic[''].Clone('hnom')
    unc = self.GetSum2Unc(syst, includeStat)
    nbins = hnom.GetNbinsX()
    for i in range(0,nbins+2): hnom.SetBinError(i, unc[i])
    hnom.SetDirectory(0)
    hnom.SetFillStyle(3444)
    hnom.SetFillColor(kGray+2)
    return hnom

  def GetDataHisto(self):
    if not self.dataname in self.indic.keys():
      #print 'WARNING: data histogram not found...'
      return None
    hname = self.histoname if not isinstance(self.histoname, list) else self.histoname[0]
    hnam  = hname if hname != '%s' else self.dataname
    h = self.indic[self.dataname][hnam].Clone("hdata")
    h.SetMarkerSize(1.2)
    h.SetMarkerStyle(20)
    h.SetDirectory(0)
    if isinstance(self.histoname, list):
      for hname in self.histoname[1:]: h.Add(self.indic[self.dataname][hname])
    return h

  def GetSumBkg(self):
    return self.GetUncHist('stat')

  def GetRatioHisto(self):
    # Data / All bkg
    hbkg  = self.GetSumBkg()
    h     = self.GetDataHisto().Clone("hratio") if self.dataname in self.indic.keys() else self.GetSumBkg().Clone("hratio")
    h.SetDirectory(0)
    h.Divide(hbkg)
    #hdata = self.GetDataHisto()
    #nb = h.GetNbinsX()
    #for i in range(0, nb+2):
    #  d = hdata.GetBinContent(i)
    #  b = hbkg. GetBinContent(i)
    return h
     
  def GetRatioHistoUnc(self, syst = '', includeStat = True): # syst = stat for stat unc
    hRatio = self.GetRatioHisto()
    hdata  = self.GetDataHisto()
    hUnc   = self.GetUncHist(syst, includeStat)
    nb     = hUnc.GetNbinsX()
    for i in range(0, nb+2):
      b    = hUnc.GetBinContent(i)
      bu   = hUnc.GetBinError(i)
      hUnc.SetBinContent(i, 1)
      hUnc.SetBinError(i, bu/b if b > 0 else 0)
    hUnc.SetFillColorAlpha(kAzure+2, 0.5)
    hUnc.SetFillStyle(1000)
    return hUnc

  def GetStack(self, colors = '', pr = ''):
    if pr == '': pr = self.processList
    elif isinstance(pr,str) and ',' in pr: pr = pr.replace(' ', '').split(',')
    npr = len(pr)
    if isinstance(colors, dict): colors = [colors[p] for p in pr]
    elif colors == '': colors = [1]*npr
    elif isinstance(colors,str) and ',' in colors: colors = colors.replace(' ', '').split(',')
    hStack = THStack('hStack', '')
    for p, col in zip(pr, colors):
      if isinstance(self.histoname, list):
        for hname in self.histoname:
          self.indic[p][hname].SetFillColor(col)
          self.indic[p][hname].SetFillStyle(1000)
          self.indic[p][hname].SetLineColor(0)
          self.indic[p][hname].SetLineStyle(0)
          self.indic[p][hname].SetLineWidth(0)
          hStack.Add(self.indic[p][hname])
      else:
        self.indic[p][self.histoname].SetFillColor(col)
        self.indic[p][self.histoname].SetFillStyle(1000)
        self.indic[p][self.histoname].SetLineColor(0)
        self.indic[p][self.histoname].SetLineStyle(0)
        self.indic[p][self.histoname].SetLineWidth(0)
        hStack.Add(self.indic[p][self.histoname])
    return hStack
      
  def __init__(self, prlist = [], syslist = [], hname = '', path = '', processDic = {}, systdic = {}, lumi = 1, rebin = 1, indic = {}):
    self.SetProcessList(prlist)
    self.SetHistoName(hname)
    self.SetSystList(syslist)
    self.sumdic = {}
    self.systlabels = []
    self.signalProcess = []
    self.SetProcessDic(processDic)
    self.SetSystDic(systdic)
    self.SetTopReader(path)
    self.SetRebin(rebin)
    self.indic = indic
    self.lumi = lumi
    self.readFromTrees = False
    self.IsScaled = False
    self.SetDataName()
    if(indic == {} and path != '' and processDic != {}): self.readFromTrees = True
    if self.readFromTrees and hname != '':
      self.SetHisto(hname, rebin)

  def Add(self, HM):
    if isinstance(HM, list):
      for hm in HM: self.Add(hm)
      return self
    if not self.histoname == HM.histoname or not self.rebin == HM.rebin:
      HM.lumi = 1
      HM.SetHisto(self.histoname, self.rebin)
    self.sumdic = {}
    self.lumi = 1
    for pr in self.indic.keys():
      #print '>>>> hadding process: %s'%pr
      for hname in self.indic[pr].keys():
        #print '   ---> hname = ', hname
        self.indic[pr][hname].Add(HM.indic[pr][hname])
    self.LookForSystLabels()
    self.SumHistos()
    return self

  def SetHisto(self, hname, rebin = 1):
    self.SetHistoName(hname)
    self.SetRebin(rebin)
    if self.readFromTrees:
      self.SetInputDicFromReader()
    self.LookForSystLabels()
    self.ScaleByLumi()
    self.SumHistos()

  def Clear(self):
    self.indic = {}

  def GetHisto(self, sname, hname, syst = ''):
    key = hname if syst == '' else hname + '_' + syst
    h = self.indic[sname][key] if key in self.indic[sname].keys() else self.indic[sname][hname]
    return h

  def GetYield(self, sname, hname, syst = ''):
    y = 0
    if isinstance(sname, str) and ',' in sname: sname = sname.replace(' ', '').split(',')
    if isinstance(syst,  str) and ',' in syst : syst  = syst .replace(' ', '').split(',')
    if isinstance(sname, list):
      for s in sname: y += self.GetYield(s, hname, syst)
      return y
    if isinstance(syst, list):
      nom = self.GetYield(sname, hname)
      m = 0
      for s in syst: 
        u = abs(self.GetYield(sname, hname, s) - nom)
        m += u*u
      return nom + sqrt(m)
    if syst != '' and not syst.endswith('Up') and not syst.endswith('Down'):
      nom = self.GetYield(sname, hname)
      up  = self.GetYield(sname, hname, syst+'Up')
      do  = self.GetYield(sname, hname, syst+'Down')
      return up if abs(nom-up) > abs(nom-do) else do
    h = self.GetHisto(sname, hname, syst)
    y = h.Integral() + h.GetBinContent(h.GetNbinsX()+2)  # Yields including overflow
    return y

  def GetCYield(self, pr, syst = ''):
    return self.GetYield(pr, pr, syst)

  def Save(self, outname = 'htemp', htag = ''):
    if not outname.endswith('.root'): outname+='.root'
    if os.path.isfile(outname): os.rename(outname, outname+'.old')
    fout = TFile.Open(outname,'recreate')
    if htag == '': htag = self.histoname
    prlist = self.indic.keys()
    for pr in prlist:
      hlist = self.indic[pr].keys()
      for h in hlist:
        if htag != '' and not h.startswith(htag): continue
        histo = self.indic[pr][h]
        if htag == h: # Nominal!
          histo.SetName(pr)
          histo.Write()
        else:
          term = h[len(htag):]
          if term.startswith('_'): term = term[1:]
          histo.SetName("%s_%s"%(pr, term))
          histo.Write()
    hdata = self.GetDataHisto()
    if hdata == None: hdata = self.GetSumBkg()
    hdata.SetName('data_obs')
    hdata.SetDirectory(0)
    hdata.Write()
    fout.Close()
          
  def ReadHistosFromFile(self, fname, path = 0, dataname = 'data_obs', rebin = 1):
    if path != 0:  self.SetTopReader(path)
    self.IsScaled = True
    self.readFromTrees = True
    self.SetRebin(rebin)
    self.SetHistoName('%s')
    self.SetDataName(dataname)
    for pr in self.processList+self.signalProcess:
      self.processDic = {}
      self.processDic[pr] = fname
      self.SetInputDicFromReader()
    if dataname != '': 
      self.processDic = {}
      self.processDic[dataname] = fname
      self.SetInputDicFromReader()
    self.LookForSystLabels()
    self.SumHistos()



class SampleSums:

  def GetFiles(self):
    self.files = GetFiles(self.path, self.sname)

  def LoadTree(self):
    self.tree = TChain(self.tname, self.tname)
    for f in self.files: self.tree.Add(f)

  def GetCountsFromSumWTree(self):
   if not hasattr(self, 'treesow'):
     #print 'WARNING: tree with sum of weights has not been loaded!!'
     self.LoadTree()
   count = 0
   sow   = 0
   for event in self.tree:
     count += event.genEventCount
     sow   += event.genEventSumw
   self.count = count
   self.sow   = sow

  def GetSumPDFhistoFromSumWTree(self):
   if not hasattr(self, 'treesow'):
     #print 'WARNING: tree with sum of weights has not been loaded!!'
     self.LoadTree()
   self.treesow.GetEntry(1)
   nPDFweights = self.treesow.nLHEPdfSumw
   h = TH1F('SumOfWeightsPDF', '', nPDFweights, 0.5, nPDFweights+0.5)
   count = 0
   sow   = 0
   for event in self.treesow:
     count += event.genEventCount
     sow   += event.genEventSumw
     for i in range(nPDFweights):
       h.Fill(i+1, event.LHEPdfSumw[i])
   h.SetDirectory(0)
   #for i in range(h.GetNbinsX()): print '[%i] %1.2f'%(i, h.GetBinContent(i+1))
   self.count = count
   self.sow   = sow
   return h

  def GetSumScaleHistoFromSumWTree(self):
   if not hasattr(self, 'treesow'):
     #print 'WARNING: tree with sum of weights has not been loaded!!'
     self.LoadTree()
     return 
   self.treesow.GetEntry(1)
   nScaleWeights = self.treesow.nLHEScaleSumw
   h = TH1F('SumOfWeightsScale', '', nScaleWeights, 0.5, nScaleWeights+0.5)
   print 'GetEntries: ', self.treesow.GetEntries()
   for event in self.treesow:
     for i in range(nScaleWeights):
       h.Fill(i+1, event.LHEScaleSumw[i])
   h.SetDirectory(0)
   #for i in range(h.GetNbinsX()): print '[%i] %1.2f'%(i, h.GetBinContent(i+1))
   return h

  def SetNormPDFhistoName(self, n):
    self.normPDFhistoName = n

  def SetNormScaleHistoName(self, n):
    self.normScaleHitstoName = n
    
  def SetCountHistoName(self, n = 'Count'):
    self.countName = n

  def SetSOWname(self, n = 'SumWeights'):
    self.SOWname = n

  def GetHsumPDF(self, hname = ''):
    if hname != '': self.SetNormPDFhistoName(hname)
    self.hsumpdf = t.GetNamedHisto(self.normPDFhistoName) if self.normPDFhistoName != '' else self.GetSumPDFhistoFromSumWTree()
    return self.hsumpdf

  def GetHsumPDF(self, hname = ''):
    if hname != '': self.SetNormPDFhistoName(hname)
    self.hsumscale = t.GetNamedHisto(self.normScaleHitstoName) if self.normScaleHitstoName != '' else self.GetSumScaleHistoFromSumWTree()
    return self.hsumscale

  def GetCount(self, hname):
    if hname!= '': self.SetCountHistoName(hname)
    if self.t.IsHisto(self.files[0], self.countName):
      h = t.GetNamedHisto(self.countName)
      count = h.GetBinContent(1)
      self.count = count
    else: 
      self.GetCountsFromSumWTree()
    return self.count

  def GetSOW(self, hname):
    if hname!= '': self.SetSOWname(hname)
    if self.t.IsHisto(self.files[0],self.SOWname):
      h = t.GetNamedHisto(self.SOWname)
      sow = h.GetBinContent(1)
      self.sow   = sow
    else:
      self.GetCountsFromSumWTree()
    return self.sow

  def __init__(self, pathToTrees, sname, tname = 'Runs', normPDFhistoName = '', normScaleHitstoName = ''):
    self.path = pathToTrees
    self.sname = sname
    self.tname = tname
    self.GetFiles()
    self.t = TopHistoReader('')#self.path)
    self.SetNormPDFhistoName(normPDFhistoName)
    self.SetNormScaleHistoName(normScaleHitstoName)
