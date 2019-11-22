import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis_all/',1)[0]+'/xuAnalysis_all/')
from plotter.TopHistoReader import TopHistoReader, OutText
from ROOT.TMath import Sqrt as sqrt
square  = lambda x : x*x
SumSquare = lambda x : sqrt(sum([square(i) for i in x]))

elecName = 'ElEl' #Elec
muName   = 'MuMu' #Muon

class NonpromptDD:

 ### Set methods
 def SetPath(self, p):
   if not p.endswith('/'): p+='/'
   self.path = p

 def SetOutPath(self, p):
   self.outpath = p
 
 def SetLumi(self, l):
   self.lumi = l
   self.t.SetLumi(self.lumi)

 def SetChannel(self, c):
   self.chan = c

 def SetLevel(self, l):
   self.level = l

 def SetChanAndLevel(self, chan = '', level = ''):
   ''' Manages to set chan and leve to the class and the TopHistoReader '''
   if chan  != '': self.SetChannel(chan)
   if level != '': self.SetLevel(level)
   self.t.SetChan(self.GetChan())
   self.t.SetLevel(self.GetLevel())
   return self.GetChan(), self.GetLevel()

 ### Get methods
 def GetPath(self):
   return self.path

 def GetOutPath(self):
   return self.outpath

 def GetLevel(self):
   return self.level

 def GetChan(self):
   return self.chan

 ### Calculate quantities...

 def GetYield(self, process, chan = '', level = '', SS = False):
   if process == 'Data' or process == 'data': self.t.SetIsData(True)
   if process in self.process.keys(): process = self.process[process]
   chan, lev = self.SetChanAndLevel(chan, level)
   y   = self.t.GetYield(process, chan, level, SS = SS)
   err = self.t.GetYieldStatUnc(process, chan, level, SS = SS)
   self.t.SetIsData(False)
   if y < 0: # Negative weights...
     y = 0; err = 0;
   return y, err

 def GetSS(self, process, chan = '', level = ''):
   return self.GetYield(process, chan, level, True)

 def GetROSSS(self, process, chan = '', level = ''):
   ''' Returns the OS to SS ratio for process '''
   OS, OSe = self.GetYield(process, chan, level)
   SS, SSe = self.GetSS(process, chan, level)
   R = OS/SS if SS != 0 else 1
   e = R*SumSquare([OSe/OS if OS != 0 else 0, SSe/SS if SS != 0 else 0])
   return R, e

 def GetNonpromptDD(self, chan = '', level = ''):
   chan, lev = self.SetChanAndLevel(chan, level)
   R, Re = self.GetROSSS([self.process[lab] for lab in self.nonpromptProcess])
   BkgSS, BkgSSe = self.GetSS([self.process[lab] for lab in self.promptProcess])
   DataSS, DataSSe = self.GetSS('data')
   y = R*(DataSS-BkgSS)
   e = y*SumSquare([Re/R if R != 0 else 0, (DataSSe+BkgSSe)/(DataSS-BkgSS) if (DataSS-BkgSS != 0) else 0])
   return y, e

 ## Print tables
 def PrintSSyields(self, name = '', level = ''):
   self.SetChanAndLevel('', level)
   if name == '': name = 'SameSign_%s'%(self.GetLevel())
   t = OutText(self.GetOutPath(), name)
   t.SetSeparatorLength(12+(3+16)*3)
   t.SetDefaultFixOption(False)
   t.line('Same-sign yields for level of selection \'%s\''%(self.GetLevel()))
   t.bar()
   s = lambda tit,vee,vmm,vem : t.line(t.fix(tit,10) + t.vsep() + t.fix(vee,16,'c') + t.vsep()+ t.fix(vmm,16,'c') + t.vsep() + t.fix(vem,16,'c'))
   v = lambda L : '%1.2f'%L[0] + t.pm() + '%1.2f'%L[1]
   d = lambda L : '%1.0f'%L[0] + t.pm() + '%1.2f'%L[1]
   S = lambda tit, pr : s(tit, v(self.GetSS(pr,elecName)), v(self.GetSS(pr, muName)), v(self.GetSS(pr, 'ElMu')))
   D = lambda tit, pr : s(tit, d(self.GetSS(pr,elecName)), d(self.GetSS(pr, muName)), d(self.GetSS(pr, 'ElMu')))
   s('',elecName,muName,'ElMu')
   t.sep()
   for pr in self.promptProcess:
     S(pr, pr)
   #S('tt signal', 'tt')
   #S('tW','tW')
   #S('Drell-Yan','DY')
   #S('Dibosons','VV')
   t.sep()
   for pr in self.nonpromptProcess:
     S(pr, pr)
   #S('W+Jets', 'WJets')
   #S('tt semilep', 'ttsemilep')
   t.sep()
   S('Total MC', [self.process[lab] for lab in self.promptProcess + self.nonpromptProcess])
   t.sep()
   D('Data', 'data')
   t.bar()
   t.write()

 def PrintNonpromptEstimate(self, name = '', chan = '', level = ''):
   chan, lev = self.SetChanAndLevel(chan, level)
   if name == '': name = 'NonpromptDD_%s_%s'%(self.GetChan(),self.GetLevel())
   t = OutText(self.GetOutPath(), name)
   t.SetSeparatorLength(55+20)
   t.SetDefaultFixOption(False)
   t.line(' Nonpromt estimate from a same-sign control retion\nfor channel \'%s\' and level of selection \'%s\''%(chan, lev))
   t.bar()
   s = lambda tit,vee,vmm,vem : t.line(t.fix(tit,10) + t.vsep() + t.fix(vee,16,'c') + t.vsep()+ t.fix(vmm,16,'c') + t.vsep() + t.fix(vem,16,'c'))
   v = lambda L : '%1.2f'%L[0] + t.pm() + '%1.2f'%L[1]
   d = lambda L : '%1.0f'%L[0] + t.pm() + '%1.2f'%L[1]
   pr = [self.process[p] for p in self.nonpromptProcess]
   sr = [self.process[p] for p in self.promptProcess]
   t.line(t.fix(' MC nonprompt estimate (OS W+Jets and semilpetonic tt)',55) + t.vsep() + v(self.GetYield(pr)))
   t.sep()
   t.line(t.fix(' MC nonprompt SS (W+Jets and semilpetonic tt)',55) + t.vsep() + v(self.GetSS(pr)))
   t.line(t.fix(' R = nonpromt(OS)/nonprompt(SS)',55) + t.vsep() + v(self.GetROSSS(pr)))
   t.line(t.fix(' BkgSS = MC prompt SS (other sources)',55) + t.vsep() + v(self.GetSS(sr)))
   t.line(t.fix(' DataSS = Obseved data SS',55) + t.vsep() + v(self.GetSS('data')))
   t.sep()
   t.line(t.fix(' Nonprompt data-driven estimate = R(DataSS-BkgSS)',55) + t.vsep() + v(self.GetNonpromptDD()))
   t.bar()
   t.write()

 ### Init
 def __init__(self, path, outpath = './temp/', chan = 'ElMu', level = '2jets', process = {}, prompt = [], nonprompt = [], lumi = 308.54, histonameprefix = 'H', yieldsSSname = 'SSYields'):
   self.SetPath(path)
   self.t = TopHistoReader(self.GetPath())
   self.t.SetHistoNamePrefix(histonameprefix)
   self.t.SetYieldsSSname(yieldsSSname)
   self.SetLumi(lumi)
   self.SetOutPath(outpath)
   self.SetChanAndLevel(chan, level)
   self.process = process
   self.nonpromptProcess = []; self.promptProcess = []
   if prompt == [] or nonprompt == []:
     for pr in process.keys():
       if pr in ['data', 'Data', 'DATA']: continue
       elif pr in ['fake', 'nonprompt', 'Nonprompt', 'NonPrompt', 'Fake', 'fakes', 'Fakes']:
         self.nonpromptProcess.append(pr)
       else: self.promptProcess.append(pr)
   else:
     self.promptProcess = prompt
     self.nonpromptProcess = nonprompt
