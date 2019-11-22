import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis_all/',1)[0]+'/xuAnalysis_all/')
from plotter.TopHistoReader import TopHistoReader, OutText

from ROOT.TMath import Sqrt as sqrt
square  = lambda x : x*x
SumSquare = lambda x : sqrt(sum([square(i) for i in x]))

elname = 'ElEl' #Elec
muname = 'MuMu' #Muon
class DYDD:

 ### Set methods
 def SetPath(self, p):
   if not p.endswith('/'): p+='/'
   self.path = p

 def SetOutPath(self, p):
   self.outpath = p
 
 def SetMode(self, mode = 'OF', hname = ''):
   self.doOF = True
   if mode in ['SF', 'Elec', 'ElEl', 'Muon', 'MuMu']:
     self.doOF = False
   if   self.doOF: 
     if hname != '': self.SetHistoNameOF(hname)
     self.SetZhistoName(self.hnameOF)
   else:
     if hname != '': self.SetHistoNameSF(hname)
     self.SetZhistoName(self.hnameSF)

 def SetLumi(self, l):
   self.lumi = l
   self.t.SetLumi(self.lumi)

 def SetHistoNameOF(self, h = 'DY_InvMass'):
   self.hnameOF = h

 def SetHistoNameSF(self, h = 'DY_SF_InvMass'):
   self.hnameSF = h

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
   h.SetDirectory(0)
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
   rinElec, errElec = self.GetDataIn(elname, level)
   rinMuon, errMuon  = self.GetDataIn(muname, level)
   k = (rinElec/rinMuon if rinMuon != 0 else 0) if chan == elname else (rinMuon/rinElec if rinElec != 0 else 0)
   kerr = k*SumSquare([errElec/(2*rinElec) if rinElec != 0 else 0,errMuon/(2*rinMuon) if rinMuon !=0 else 0])
   return k, kerr

 def GetDYDD(self, chan = '', level = '', mode = ''):
   ''' Returns the DY estimate from data '''
   chan, level = self.SetChanAndLevel(chan, level)
   if chan == 'ElMu': self.SetMode('ElMu')
   if mode != '': self.SetMode(mode)
   routin, routin_err = self.GetRoutin(chan, level) 
   NemuIn, NemuIn_err = self.GetDataIn('ElMu', level)
   kee,   keerr    = self.GetKfactor(elname, level)
   NeeIn, NeeInerr = self.GetDataIn( elname, level)
   kmm  , kmmrr    = self.GetKfactor(muname, level)
   NmmIn, NmmInerr = self.GetDataIn( muname, level)
   est    = lambda r, Nin, Nemu, k : r*(Nin-Nemu*k/2)
   esterr = lambda r, Nin, Nemu, k, er, eNin, eNemu, ek : SumSquare([est(r, Nin, Nemu, k)*(er/r if r != 0 else 0), r*eNin, r*k/2*eNemu, r*Nemu/2*ek])
   N = 0; Nerr = 0
   if chan == elname: 
     N    = est(routin, NeeIn, NemuIn, kee)
     Nerr = esterr(routin, NeeIn, NemuIn, kee, routin_err, NeeInerr, NemuIn_err, keerr)
   elif chan == muname: 
     N    = est(routin, NmmIn, NemuIn, kmm)
     Nerr = esterr(routin, NmmIn, NemuIn, kmm, routin_err, NmmInerr, NemuIn_err, kmmrr)
   else: # ElMu
     self.t.SetIsData(False)
     yDY  = self.t.GetYield(self.GetDYfiles(), 'ElMu')
     yDYe = self.t.GetYieldStatUnc(self.GetDYfiles(), 'ElMu')
     SF,err = self.GetScaleFactor('ElMu')
     N = yDY*SF
     Nerr = N*SumSquare([err/SF if SF!=0 else err, yDYe/yDY if yDY != 0 else yDYe])
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
   if chan == muname or chan == elname:
     dd, dde = self.GetDYDD(chan)
     mo, moe = self.GetMCout(chan)
     SF = dd/mo if mo != 0 else 0
     err = SF*SumSquare([dde/dd if dd != 0 else 0, moe/mo if mo != 0 else 0])
   elif chan == 'ElMu':
     e, er = self.GetScaleFactor(elname)
     m, mr = self.GetScaleFactor(muname)
     SF = sqrt(e*m)
     err = SF*SumSquare([er/e if e!= 0 else 0, mr/m if m != 0 else 0])
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
   s('',elname,muname,'ElMu')
   t.sep()
   mie, miee = self.GetMCin( elname)
   moe, moee = self.GetMCout(elname)
   mim, mime = self.GetMCin( muname)
   mom, mome = self.GetMCout(muname)
   s(' N_in        (MC)',v(mie,miee),v(mim,mime),'')
   s(' N_out       (MC)',v(moe,moee),v(mom,mome),'')

   re, ree   = self.GetRoutin(elname)
   rm, rme   = self.GetRoutin(muname)
   s(' R_(out/in)  (MC)',v(re,ree),v(rm,rme),'')

   ke, kee   = self.GetKfactor(elname)
   km, kme   = self.GetKfactor(muname)
   s(' k_ll            ',v(ke,kee),v(km,kme),'')

   ie, ier   = self.GetDataIn(elname)
   im, imr   = self.GetDataIn(muname)
   iem, iemr = self.GetDataIn('ElMu')
   s(' N_in      (Data)',d(ie,ier),d(im,imr),d(iem,iemr))
   t.sep()
   dde, ddee = self.GetDYDD(elname)
   ddm, ddme = self.GetDYDD(muname)
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
   sfee, sfeee = self.GetScaleFactor(elname)
   sfmm, sfmme = self.GetScaleFactor(muname)
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
   s('',elname,muname,'ElMu')
   t.sep()
   #labels = ['Inclusive','== 1 jet', '== 2 jets', '>= 3 jets','>= 2 jets, >= 1 btag', '>= 2 btag']
   #levels = ['dilepton', 'eq1jet', 'eq2jet', 'geq3jet','1btag', '2btag']
   labels = ['Inclusive','>= 2 jets',' >= 1 btag']
   levels = ['dilepton', '2jets', '1btag']
   for i in range(len(labels)):
     if i == 4: t.sep()
     lab = labels[i]
     lev = levels[i]
     sfe, sfee = self.GetScaleFactor(elname, lev, 'SF')
     sfm, sfme = self.GetScaleFactor(muname, lev, 'SF')
     sfo, sfoe = self.GetScaleFactor('ElMu', lev, 'OF')
     s(' '+lab, v(sfe,sfee) if sfe > 0 else '-', v(sfm,sfme) if sfm > 0 else '-', v(sfo,sfoe) if sfo > 0 else '-')
   t.bar()
   t.write()

 def __init__(self, path, outpath = './temp/', chan = 'ElMu', level = '2jets', DYsamples = 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50', DataSamples = 'HighEGJet,SingleMuon, DoubleMuon', lumi = 308.54, massRange = [91-15, 91+15], mode = '', histonameprefix = 'H', hname = 'DY_InvMass'):
   self.SetPath(path)
   self.SetOutPath(outpath)
   self.t = TopHistoReader(path)
   self.t.SetHistoNamePrefix(histonameprefix)
   self.SetLumi(lumi)
   self.SetChanAndLevel(chan, level)
   self.SetDYsamples(DYsamples)
   self.SetDataSamples(DataSamples)
   self.SetMassRange(massRange[0], massRange[1])
   self.SetHistoNameOF(); self.SetHistoNameSF()
   if chan == 'ElMu': 
     if hname != '': self.SetHistoNameOF(hname)
     self.SetMode('OF')
   else             : 
     if hname != '': self.SetHistoNameSF(hname)
     self.SetMode('SF')
   if mode != '': self.SetMode(mode)

