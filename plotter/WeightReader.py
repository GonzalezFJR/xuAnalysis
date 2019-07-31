import os,sys
#import ROOT
from ROOT import TH1F, TH1, TFile, TCanvas, TPad, THStack, TLatex, TLegend, TGaxis, TChain
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack
from ROOT import gPad, gROOT
from ROOT.TMath import Sqrt as sqrt
average = lambda x: sum(x)/len(x)
gROOT.SetBatch(1)
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')

from framework.fileReader import GetFiles
from plotter.TopHistoReader import TopHistoReader #ch, chan, lev, level, dataset, datasets, systematic, systlabel  
from plotter.OutText import OutText

class WeightReader:
 ''' Get uncertainties from 9 scale weights, 33 PDF weights and 100 NNPDF30 weights

     ### For PDF + alpha_S (33 weights)
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

 def SetPShistoName(self, n):
   self.PShistoName = n

 def SetNormScaleHistoName(self, n):
   self.normScaleHitstoName = n

 def SetNormPDFhistoName(self, n):
   self.normPDFhistoName = n

 def SetMotherFileName(self, f):
   self.motherfname = f

 def SetPathToTrees(self, p):
   self.pathToTrees = p

 def SetSampleName(self, n):
   self.sampleName = n

 def SetLumi(self, l):
   self.lumi = l

 def SetLevel(self, l):
   self.level = l

 def SetChan(self, c):
   self.chan = c

 def SetHistoPrefix(self, p):
   self.histoprefix = p

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

 def LoadTreeSumOfWeights(self, path, fname):
   ''' Load the trees with the sum of weights and returns the corresponding TChain '''
   self.treesow = TChain('Runs', 'Runs')
   files = GetFiles(path, fname)
   for f in files: self.treesow.Add(f)
   print ' >> Loaded %i mother files!'%len(files)

 def GetSumPDFhistoFromSumWTree(self):
   if not hasattr(self, 'treesow'):
     print 'WARNING: tree with sum of weights has not been loaded!!'
     return 
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
     print 'WARNING: tree with sum of weights has not been loaded!!'
     return 
   self.treesow.GetEntry(1)
   nScaleWeights = self.treesow.nLHEScaleSumw
   h = TH1F('SumOfWeightsPS', '', nScaleWeights, 0.5, nScaleWeights+0.5)
   print 'GetEntries: ', self.treesow.GetEntries()
   for event in self.treesow:
     for i in range(nScaleWeights):
       h.Fill(i+1, event.LHEScaleSumw[i])
   h.SetDirectory(0)
   #for i in range(h.GetNbinsX()): print '[%i] %1.2f'%(i, h.GetBinContent(i+1))
   return h

 def loadHistos(self):
   ''' Load the PDF and Scale histos and norm histos '''
   t = TopHistoReader(self.path)
   t.SetHistoNamePrefix(self.histoprefix)
   t.SetIsData(1)
   n = self.GetSampleName()
   t.SetProcess(n)
   t.SetChan(self.GetChan())
   t.SetLevel(self.GetLevel())
   #if self.GetNgenEvents() <= 0 : self.SetNgenEvents(t.GetNGenEvents())
   self.hpdf      = t.GetHisto(n,self.PDFhistoName)
   self.hscale    = t.GetHisto(n,self.scaleHistoName)
   self.hPS       = t.GetHisto(n,self.PShistoName)
   if self.pathToTrees != '' and self.motherfname != '': self.LoadTreeSumOfWeights(self.pathToTrees, self.motherfname)
   self.hsumpdf   = t.GetNamedHisto(self.normPDFhistoName)    if self.normPDFhistoName    != '' else self.GetSumPDFhistoFromSumWTree()
   self.hsumscale = t.GetNamedHisto(self.normScaleHitstoName) if self.normScaleHitstoName != '' else self.GetSumScaleHistoFromSumWTree()
   self.SetNgenEvents(self.count)
   self.nPDFweights = self.hsumpdf.GetNbinsX()
   self.nScaleWeighs = self.hsumscale.GetNbinsX()
   print '>> Count        : ', self.count
   print '>> SumOfWeights : ', self.sow

 def GetPDFyield(self, i):
   ''' Return value of bin i for PDF weights '''
   return self.hpdf.GetBinContent(i)*self.GetLumi()/self.GetPDFnorm(i)#(self.GetNgenEvents())

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
   return self.hscale.GetBinContent(i)*self.GetLumi()/self.GetScaleNorm(i)#(self.GetNgenEvents())

 def GetScaleNom(self):
   ''' Nominal scale weights '''
   return self.GetScaleYield(5)

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
   nom = s(1,0.5,0.5)
   t.SetSeparatorLength(len(nom))
   t.line(" Scale ME uncertainties on tt acceptance")
   t.bar()
   t.line(nom)
   t.line(s(2,0.5, 1.0))
   t.line(s(3,0.5, 2.0) + ' (unphysical)')
   t.line(s(4,1.0, 0.5))
   t.line(s(5,1.0, 1.0) + ' (nominal)')
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

 def __init__(self, path = '', outpath = './temp/', chan = 'ElMu', level = '2jets', sampleName = 'TT', PDFname = 'PDFweights', ScaleName = 'ScaleWeights', PSname = 'PSweights', PDFsumName= '', ScaleSumName = '', lumi = 308.54, nGenEvents = -1, pathToTrees='', motherfname='', histoprefix='H_'):
   self.SetPath(path)
   self.SetOutPath(outpath)
   self.SetChan(chan)
   self.SetLevel(level)
   self.SetSampleName(sampleName)
   self.SetPDFhistoName(PDFname)
   self.SetScaleHistoName(ScaleName)
   self.SetPShistoName(PSname)
   self.SetNormPDFhistoName(PDFsumName)
   self.SetNormScaleHistoName(ScaleSumName)
   self.SetPathToTrees(pathToTrees)
   self.SetMotherFileName(motherfname)
   self.SetLumi(lumi)
   self.SetNgenEvents(nGenEvents)
   self.SetHistoPrefix(histoprefix)
   self.loadHistos()

def GetBranchInfo(fname, branchname, treeName = 'Events', verbose = 1):
  '''
  Obtain info of PS, PDF and ME weights from a nanoAOD file
  Usage: 
    GetBranchInfo(fname, "PSWeight, LHEScaleWeight, LHEPdfWeight")
  '''
  f = TFile.Open(fname)
  t = f.Get(treeName)
  t.GetEntry(1) # Explore first event:
  out = "Looking for branch/branches '%s' in tree '%s'\nin file '%s'...\n"%(branchname, treeName, fname)
  if isinstance(branchname, str) and ',' in branchname: branchname = branchname.replace(' ', '').split(',')
  elif isinstance(branchname, str): branchname = [branchname]
  for brname in branchname:
    nbranch = 'n'+brname
    info    = t.GetBranch(brname) .GetTitle()
    ninfo   = t.GetBranch(nbranch).GetTitle()
    out    += " %s : %s\n"%(brname,  info)
    out    += " %s : %s\n"%(nbranch, ninfo)
    nbr     = getattr(t, nbranch)
    lbr     = getattr(t, brname)
    out    += "Priting values for one event...\n %s : %i\n %s :"%(nbranch, nbr, brname)
    for i in range(nbr): 
      out += " %1.2f,"%lbr[i]
    if out.endswith(','): out = out[:-1] + '\n'
    out += '\n'
  out += '\n'
  f.Close()
  if verbose: print out
  return out


if __name__ == '__main__':
  fname = {
   #2016 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2016/Tree_TTTo2L2Nu_TuneCP5_PSweights_0.root',
   2016 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2016/Tree_TTTo2L2Nu_TuneCP5_PSweights_0.root',
   2017 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2017/Tree_TTTo2L2Nu_0.root',
   2018 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2018/Tree_TTTo2L2Nu_0.root',
  }
  GetBranchInfo(fname[2016], "PSWeight, LHEScaleWeight, LHEPdfWeight")
  GetBranchInfo(fname[2017], "PSWeight, LHEScaleWeight, LHEPdfWeight")
  GetBranchInfo(fname[2018], "PSWeight, LHEScaleWeight, LHEPdfWeight")
