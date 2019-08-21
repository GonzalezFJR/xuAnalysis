from TopHistoReader import TopHistoReader
from OutText import OutText

from ROOT.TMath import Sqrt as sqrt
square  = lambda x : x*x
SumSquare = lambda x : sqrt(sum([square(i) for i in x]))

class DYDD:

 ### Set methods
 def SetPath(self, p):
   if not p.endswith('/'): p+='/'
   self.path = p

 def SetOutPath(self, p):
   self.outpath = p
 
 def SetMode(self, mode = 'OF'):
   self.doOF = True
   if mode == 'SF' or mode == 'ElEl' or mode == 'MuMu':
     self.doOF = False
   if   self.doOF: self.SetZhistoName('DYHistoElMu')
   else: self.SetZhistoName('DYHisto')

 def SetLumi(self, l):
   self.lumi = l
   self.t.SetLumi(self.lumi)

 def SetDYsamples(self, f):
   self.DYfiles = f

 def SetDataSamples(self,f):
   self.datafiles = f

 def SetChannel(self, c):
   self.chan = c

 def SetLevel(self, l):
   self.level = l

 def SetZhistoName(self, h):
   self.zhname = h

 def SetMassRange(self, minM = 91-15, maxM = 91+15):
   self.minMZ = minM
   self.maxMZ = maxM

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

 def GetZhistoName(self):
   return self.zhname

 def GetDYfiles(self):
   return self.DYfiles

 def GetDataFiles(self):
   return self.datafiles

 def GetLevel(self):
   return self.level

 def GetChan(self):
   return self.chan

 ### Calculate quantities...

 def GetDYhisto(self, chan = '', level = '', isData = True):
   # ARREGLAR PARA QUE COJA EL ADECUADO DEPENDIENDO DEL CANAL!! O HACER FUNCION PARA INDICAR CANAL EMU
   chan, level = self.SetChanAndLevel(chan, level)
   if isData:
     self.t.SetIsData(True)
     pr = self.GetDataFiles()
   else:
     self.t.SetIsData(False)
     pr = self.GetDYfiles()
   zname = self.GetZhistoName()
   if level == 'dilepton' and zname[-4:] == 'ElMu': zname = zname[:-4]
   h = self.t.GetHisto(pr,zname, chan, level)
   return h

 def GetHdata(self, chan, level):
   return self.GetDYhisto(chan, level, True)

 def GetHMC(self, chan, level):
   return self.GetDYhisto(chan, level, False)

 def DYyield(self, direc = 'in', isData = True, chan = '', level = ''):
   h = self.GetDYhisto(chan, level, isData)
   b0 = h.FindBin(self.minMZ); bN = h.FindBin(self.maxMZ)
   nbins = h.GetNbinsX()
   integral = h.Integral()
   y = 0; err = 0
   if direc == 'in' or direc == 'In' or direc == 'IN':
     y += h.Integral(b0, bN)
   else:
     y += h.Integral(0, b0-1)
     y += h.Integral(bN+1, nbins+1)
   if isData: err = sqrt(y)
   else:
     entries = h.GetEntries()
     err = sqrt((y*integral)/entries)
   if y<0:  # Avoid wierd numbers due to negative weights...
    y = 0; err = 0
   return y, err
 
 def GetDataIn(self, chan = '', level = ''):
   return self.DYyield('in', True, chan, level)
   
 def GetDataOut(self, chan = '', level = ''):
   return self.DYyield('out', True, chan, level)

 def GetMCin(self, chan = '', level = ''):
   return self.DYyield('in', False, chan, level)

 def GetMCout(self, chan ='', level = ''):
   return self.DYyield('out', False, chan, level)

 def GetRoutin(self, chan = '', level = ''):
   ''' Returns ratio Rout/in from MC '''
   rin, errin  = self.GetMCin(chan, level)
   out, errout = self.GetMCout(chan, level)
   r = out/rin if rin != 0 else 0
   err = r*SumSquare([errout/out if out != 0 else 0,errin/rin if rin != 0 else 0])
   return r, err

 def GetKfactor(self, chan = '', level = ''):
   ''' Calculate the k factor k_ee, k_mumu '''
   chan, level = self.SetChanAndLevel(chan, level)
   rinElec, errElec = self.GetDataIn('ElEl', level)
   rinMuon, errMuon  = self.GetDataIn('MuMu', level)
   k = (rinElec/rinMuon if rinMuon != 0 else 0) if self.GetChan() == 'ElEl' else (rinMuon/rinElec if rinElec != 0 else 0)
   kerr = k*SumSquare([errElec/(2*rinElec) if rinElec != 0 else 0,errMuon/(2*rinMuon) if rinMuon !=0 else 0])
   return k, kerr

 def GetDYDD(self, chan = '', level = '', mode = ''):
   ''' Returns the DY estimate from data '''
   chan, level = self.SetChanAndLevel(chan, level)
   if chan == 'ElMu': self.SetMode('ElMu')
   if mode != '': self.SetMode(mode)
   routin, routin_err = self.GetRoutin(chan, level) 
   NemuIn, NemuIn_err = self.GetDataIn('ElMu', level)
   kee,   keerr    = self.GetKfactor('ElEl', level)
   NeeIn, NeeInerr = self.GetDataIn( 'ElEl', level)
   kmm  , kmmrr    = self.GetKfactor('MuMu', level)
   NmmIn, NmmInerr = self.GetDataIn( 'MuMu', level)
   est    = lambda r, Nin, Nemu, k : r*(Nin-Nemu*k/2)
   esterr = lambda r, Nin, Nemu, k, er, eNin, eNemu, ek : SumSquare([est(r, Nin, Nemu, k)*er/r, r*eNin, r*k/2*eNemu, r*Nemu/2*ek])
   N = 0; Nerr = 0
   if chan == 'ElEl': 
     N    = est(routin, NeeIn, NemuIn, kee)
     Nerr = esterr(routin, NeeIn, NemuIn, kee, routin_err, NeeInerr, NemuIn_err, keerr)
   elif chan == 'MuMu': 
     N    = est(routin, NmmIn, NemuIn, kmm)
     Nerr = esterr(routin, NmmIn, NemuIn, kmm, routin_err, NmmInerr, NemuIn_err, kmmrr)
   else: # ElMu
     self.t.SetIsData(False)
     yDY  = self.t.GetYield(self.GetDYfiles(), 'ElMu')
     yDYe = self.t.GetYieldStatUnc(self.GetDYfiles(), 'ElMu')
     SF,err = self.GetScaleFactor('ElMu')
     N = yDY*SF
     Nerr = N*SumSquare([err/SF,yDYe/yDY])
   if N < 0:
     N = 0; Nerr = 0;
   if not Nerr == Nerr: Nerr = 0
   return N, Nerr

 def GetScaleFactor(self, chan = '', level = '', mode = ''):
   ''' Returns the data/MC ratio for the DY estimate '''
   chan, level = self.SetChanAndLevel(chan, level)
   if chan == 'ElMu': self.SetMode('ElMu')
   if mode != '': self.SetMode(mode)
   SF = 1; err = 0
   if chan == 'ElEl' or chan == 'MuMu':
     dd, dde = self.GetDYDD(chan)
     mo, moe = self.GetMCout(chan)
     SF = dd/mo if mo != 0 else 0
     err = SF*SumSquare([dde/dd if dd != 0 else 0, moe/mo if mo != 0 else 0])
   elif chan == 'ElMu':
     e, er = self.GetScaleFactor('ElEl')
     m, mr = self.GetScaleFactor('MuMu')
     SF = sqrt(e*m)
     err = SF*SumSquare([er/e, mr/m])
   return SF,err

 def PrintDYestimate(self, doSF = False, name = '', level = ''):
   self.SetChanAndLevel('', level)
   self.SetMode('SF' if doSF else 'OF')
   if name == '': name = 'DYDD_%s_%s'%('SF' if doSF else 'OF',self.GetLevel())
   t = OutText(self.GetOutPath(), name)
   t.SetSeparatorLength(20+(3+22)*3)
   t.SetDefaultFixOption(False)
   t.line('Drell-Yan estimate for %s and level \'%s\''%('SF channels' if doSF else 'all channels (no MET cut) ',self.GetLevel()))
   t.bar()
   s = lambda tit,vee,vmm,vem : t.line(t.fix(tit,20) + t.vsep() + t.fix(vee,22,'c') + t.vsep()+ t.fix(vmm,22,'c') + t.vsep() + t.fix(vem,22,'c'))
   v = lambda val, err : '%1.3f'%val + t.pm() + '%1.3f'%err
   d = lambda val, err : '%1.0f'%val + t.pm() + '%1.2f'%err
   s('','ElEl','MuMu','ElMu')
   t.sep()
   mie, miee = self.GetMCin( 'ElEl')
   moe, moee = self.GetMCout('ElEl')
   mim, mime = self.GetMCin( 'MuMu')
   mom, mome = self.GetMCout('MuMu')
   s(' N_in        (MC)',v(mie,miee),v(mim,mime),'')
   s(' N_out       (MC)',v(moe,moee),v(mom,mome),'')

   re, ree   = self.GetRoutin('ElEl')
   rm, rme   = self.GetRoutin('MuMu')
   s(' R_(out/in)  (MC)',v(re,ree),v(rm,rme),'')

   ke, kee   = self.GetKfactor('ElEl')
   km, kme   = self.GetKfactor('MuMu')
   s(' k_ll            ',v(ke,kee),v(km,kme),'')

   ie, ier   = self.GetDataIn('ElEl')
   im, imr   = self.GetDataIn('MuMu')
   iem, iemr = self.GetDataIn('ElMu')
   s(' N_in      (Data)',d(ie,ier),d(im,imr),d(iem,iemr))
   t.sep()
   dde, ddee = self.GetDYDD('ElEl')
   ddm, ddme = self.GetDYDD('MuMu')
   tmc   = ' DY estimate out (MC) ' if doSF else ' DY estimate (MC)'
   tdata = ' DY estimate out (DD) ' if doSF else ' DY estimate (DD)'
   if doSF:
     s(' DY estimate (MC)',v(moe, moee),v(mom, mome),'')
     s(' DY estimate (DD)',v(dde, ddee),v(ddm, ddme),'')
   else:
     ddem, ddeme = self.GetDYDD('ElMu')
     yDY  = self.t.GetYield(self.GetDYfiles(), 'ElMu')
     yDYe = self.t.GetYieldStatUnc(self.GetDYfiles(), 'ElMu')
     s(' DY estimate (MC)',v(moe, moee),v(mom, mome),v(yDY, yDYe))
     s(' DY estimate (DD)',v(dde, ddee),v(ddm, ddme),v(ddem, ddeme))
   t.sep()
   sfee, sfeee = self.GetScaleFactor('ElEl')
   sfmm, sfmme = self.GetScaleFactor('MuMu')
   if doSF:
     s(' DD/MC ratio     ',v(sfee,sfeee), v(sfmm,sfmme),'')
   else:
     sfem, sfeme = self.GetScaleFactor('ElMu')
     s(' DD/MC ratio     ',v(sfee,sfeee), v(sfmm,sfmme), v(sfem, sfeme))
   t.bar()
   t.write()
   
 def PrintDYSFnjets(self):
   t = OutText(self.GetOutPath(), 'DYSF_njets')
   t.SetSeparatorLength(22+(3+16)*3)
   t.SetDefaultFixOption(False)
   t.line('Drell-Yan data/MC scale factors for different jet multiplicities') 
   t.bar()
   s = lambda tit,vee,vmm,vem : t.line(t.fix(tit,22) + t.vsep() + t.fix(vee,16,'c') + t.vsep()+ t.fix(vmm,16,'c') + t.vsep() + t.fix(vem,16,'c'))
   v = lambda val, err : '%1.2f'%val + t.pm() + '%1.2f'%err
   s('','ElEl','MuMu','ElMu')
   t.sep()
   labels = ['Inclusive','== 1 jet', '== 2 jets', '>= 3 jets','>= 2 jets, >= 1 btag', '>= 2 btag']
   levels = ['dilepton', 'eq1jet', 'eq2jet', 'geq3jet','1btag', '2btag']
   for i in range(len(labels)):
     if i == 4: t.sep()
     lab = labels[i]
     lev = levels[i]
     sfe, sfee = self.GetScaleFactor('ElEl', lev, 'SF')
     sfm, sfme = self.GetScaleFactor('MuMu', lev, 'SF')
     sfo, sfoe = self.GetScaleFactor('ElMu', lev, 'OF')
     s(' '+lab, v(sfe,sfee) if sfe > 0 else '-', v(sfm,sfme) if sfm > 0 else '-', v(sfo,sfoe) if sfo > 0 else '-')
   t.bar()
   t.write()

 def __init__(self, path, outpath = './temp/', chan = 'ElMu', level = '2jets', DYsamples = 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50', DataSamples = 'HighEGJet,SingleMuon, DoubleMuon', histoName = 'DYHisto', lumi = 308.54, massRange = [91-15, 91+15], mode = ''):
   self.SetPath(path)
   self.SetOutPath(outpath)
   self.t = TopHistoReader(path)
   self.SetLumi(lumi)
   self.SetChanAndLevel(chan, level)
   self.SetDYsamples(DYsamples)
   self.SetDataSamples(DataSamples)
   self.SetZhistoName(histoName)
   self.SetMassRange(massRange[0], massRange[1])
   if chan == 'ElMu': self.SetMode('OF')
   else             : self.SetMode('SF')
   if mode != '': self.SetMode(mode)

