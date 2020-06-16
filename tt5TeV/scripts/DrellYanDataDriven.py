import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis_all/',1)[0]+'/xuAnalysis_all/')
from plotter.TopHistoReader import TopHistoReader, OutText
from plotter.Plotter import Stack, HistoComp

from ROOT.TMath import Sqrt as sqrt
from ROOT import THStack, TH1F, kGray, kAzure, TLine
from ROOT import  kRed, kAzure
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
   k = sqrt(k)
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

 def DrawHisto(self, doSF = False, name = '', chan = '', level = '', rebin = 1, log = True):
   self.SetChanAndLevel('', level)
   self.SetMode('SF' if doSF else 'OF')
   if name == '': name = 'DYDD_%s_%s'%('SF' if doSF else 'OF',self.GetLevel())
   hData = self.GetDYhisto(chan, level, True)
   hMC   = self.GetDYhisto(chan, level, False)
   hemu  = self.GetDYhisto('ElMu', level, True)
   hData.SetMarkerStyle(20); hData.SetMarkerColor(1); hData.SetLineColor(1); hData.SetMarkerSize(1.3)
   hMC.SetFillStyle(1000); hMC.SetLineColor(kAzure-8); hMC.SetFillColor(kAzure-8);
   hemu.SetFillStyle(1000); hemu.SetLineColor(kGray); hemu.SetFillColor(kGray)
   hData.Rebin(rebin); hemu.Rebin(rebin); hMC.Rebin(rebin)
   ke, kee   = self.GetKfactor(elname)
   km, kme   = self.GetKfactor(muname)
   hemu.Scale(0.5 * (ke if chan == 'ElE' else km))
   hs = THStack()
   hs.Add(hemu)
   hs.Add(hMC)
   lab = 'e^{#pm}e^{#mp}' if chan == 'ElEl' else '#mu^{#pm}#mu^{#mp}'
   rlab = 'ee' if chan == 'ElEl' else '#mu#mu'
   processes = ['Z/#gamma*#rightarrow %s'%(lab), '0.5 k_{%s} #times Data(e#mu)'%rlab]
   colors = {processes[0] : kAzure-9, processes[1] : kGray}
   s = Stack(doRatio=False)
   s.SetXtitle(size = 0.06, offset = 0.8, nDiv = 510, labSize = 0.05)
   s.SetTextCMS(cmstex = 'CMS', x = 0.13, y = 0.88, s = 0.06)
   s.SetTextCMSmode(texcmsMode = 'Preliminary', x = 0.225, y = 0.875, s = 0.052)
   s.SetLumi(304.32)
   s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.68, texlumiY = 0.95, texlumiS = 0.045)
   s.SetDataHisto(hData)
   s.SetColors(colors)
   s.SetStack(hs)
   s.SetOutName('DYestimate_%s%s'%(chan, level) + ('_log' if log else ''))
   s.SetOutPath(self.outpath)
   plotMinimum = 0.5 if log else 0
   plotMaxScale = 10 if log else 1.3
   s.SetLogY(log)
   s.SetPlotMaxScale(plotMaxScale)
   s.SetPlotMinimum(plotMinimum)
   maximum = hData.GetMaximum()*(5 if log else 1.2)
   s.AddLine(76, 0.5, 76, maximum)
   s.AddLine(106, 0.5, 106, maximum)
   s.processes = processes
   s.SetLegendPos(x0=0.60, y0=0.55, x1=0.93, y1=0.91, size=0.042, ncol=1)
   s.DrawStack('m_{%s} (GeV)'%rlab)

 def DrawClosureMCeff(self, level='dilepton', outpath='~/www/temp/', ratio=[0.9,1.1]):
   self.SetMode('OF')
   self.SetChanAndLevel('', level)
   ke, kee   = self.GetKfactor(elname)
   km, kme   = self.GetKfactor(muname)
   print 'ke = %1.2f +/- %1.2f'%(ke, kee)
   print 'km = %1.2f +/- %1.2f'%(km, kme)

   hdata = TH1F('d1', 'd1', 2, 0, 2)
   hpred = TH1F('h1', 'h1', 2, 0, 2)
   err = lambda l : sqrt(sum([x*x for x in l]))
   '''
   hee1   = self.GetDYhisto(elname, level, False)
   hmm1   = self.GetDYhisto(muname, level, False)
   ee1 = hee1.Integral(); mm1 = hmm1.Integral()

   hdata.SetBinContent(1, ee1); hdata.SetBinError(1, sqrt(ee1));
   hdata.SetBinContent(2, mm1); hdata.SetBinError(2, sqrt(mm1));
   hpred.SetBinContent(1, mm1*ke1); hpred.SetBinError(1, mm1*ke1*( err([sqrt(mm1)/mm1, kee1/ke1]) ))
   hpred.SetBinContent(2, ee1*km1); hpred.SetBinError(2, ee1*km1*( err([sqrt(ee1)/ee1, kme1/km1]) ))
   '''
   sampName = 'TT'
   hname = 'Lep0Eta'
   h_emu = self.t.GetNamedHisto('%s_%s_%s'%(hname, 'ElMu', level), sampName)
   h_ee  = self.t.GetNamedHisto('%s_%s_%s'%(hname, 'ElEl', '2jetsnomet' if level == '2jets' else level), sampName)
   h_mu  = self.t.GetNamedHisto('%s_%s_%s'%(hname, 'MuMu', '2jetsnomet' if level == '2jets' else level), sampName)
   y_emu = h_emu.Integral()*304.32
   y_mu  = h_mu .Integral()*304.32
   y_ee  = h_ee .Integral()*304.32
   d_ee = 0.5*y_emu*ke; d_ee_err = d_ee*(kee/ke)
   d_mu = 0.5*y_emu*km; d_mu_err = d_mu*(kme/km)
   hdata.SetBinContent(1, y_ee); hdata.SetBinError(1, y_ee/sqrt(h_ee.GetEntries()));
   hdata.SetBinContent(2, y_mu); hdata.SetBinError(2, y_mu/sqrt(h_mu.GetEntries()));
   hpred.SetBinContent(1, d_ee); hpred.SetBinError(1, d_ee_err)
   hpred.SetBinContent(2, d_mu); hpred.SetBinError(2, d_mu_err)

   p = HistoComp(outpath, doRatio = True, doNorm = False)
   hdata .SetLineWidth(1); hdata .SetMarkerSize(1.2); hdata .SetMarkerColor(1); hdata .SetMarkerStyle(20)
   hdata.SetFillColor(0); hdata.SetFillStyle(0)
   hpred.SetFillStyle(3144); hpred.SetFillColor(kAzure-8)
   p.SetPlotMaxScale(1.5)
   p.SetLumi(304.32)
   p.AddHisto(hpred, 'l', 'e2', '0.5 x k_{ll} x t#bar{t} e#mu MC', kAzure+2, 2)
   p.AddHisto(hdata, 'pe', '','Same-flavor t#bar{t} MC', 1)
   p.SetBinLabels(['ee','#mu#mu'])
   p.SetYratioTitle('Ratio')
   p.SetYtitle('t#bar{t} events')
   rmin, rmax = ratio
   p.SetLegendPos(0.15, 0.6, 0.5, 0.8, ncol=1)
   p.SetRatioMin(rmin); p.SetRatioMax(rmax)
   p.SetOutName('DYDDeffClosure_'+level)
   p.autoRatio = True
   p.PlotWithData = True
   p.Draw(0)

 def PrintDYestimate(self, doSF = False, name = '', level = ''):
   hee   = self.GetDYhisto(elname, level, False)
   hmm   = self.GetDYhisto(muname, level, False)
   self.SetChanAndLevel('', level)
   self.SetMode('SF' if doSF else 'OF')
   if name == '': name = 'DYDD_%s_%s'%('SF' if doSF else 'OF',self.GetLevel())
   t = OutText(self.GetOutPath(), name, textformat='tex')
   t.SetTexAlign("l c c c")
   t.SetSeparatorLength(20+(3+22)*3)
   t.SetDefaultFixOption(False)
   t.line('%'+'Drell-Yan estimate for %s and level \'%s\''%('SF channels' if doSF else 'all channels (no MET cut) ',self.GetLevel()))
   t.bar()
   s = lambda tit,vee,vmm,vem : t.line(t.fix(tit,20) + t.vsep() + t.fix(vee,22,'c') + t.vsep()+ t.fix(vmm,22,'c') + t.vsep() + t.fix(vem,22,'c'))
   v = lambda val, err : '%1.2f'%val + t.pm() + '%1.2f'%err
   d = lambda val, err : '%1.0f'%val + t.pm() + '%1.2f'%err
   s('','ee','$\mu\mu$','e$\mu$')
   t.sep()
   mie, miee = self.GetMCin( elname)
   moe, moee = self.GetMCout(elname)
   mim, mime = self.GetMCin( muname)
   mom, mome = self.GetMCout(muname)
   s(' $N_{in}$        (MC)',v(mie,miee),v(mim,mime),'')
   s(' $N_{out}$       (MC)',v(moe,moee),v(mom,mome),'')

   re, ree   = self.GetRoutin(elname)
   rm, rme   = self.GetRoutin(muname)
   s(' $R_{out/in}$  (MC)',v(re,ree),v(rm,rme),'')

   ke, kee   = self.GetKfactor(elname)
   km, kme   = self.GetKfactor(muname)
   s(' $k_{ll}$            ',v(ke,kee),v(km,kme),'')

   ie, ier   = self.GetDataIn(elname)
   im, imr   = self.GetDataIn(muname)
   iem, iemr = self.GetDataIn('ElMu')
   s(' $N_{in}$      (Data)',d(ie,ier),d(im,imr),d(iem,iemr))
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

 def __init__(self, path, outpath = './temp/', chan = 'ElMu', level = '2jets', DYsamples = 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50', DataSamples = 'HighEGJet,SingleMuon, DoubleMuon', lumi = 304.32, massRange = [91-15, 91+15], mode = '', histonameprefix = 'H', hname = 'DY_InvMass'):
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

