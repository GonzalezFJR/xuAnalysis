from plotter.TopHistoReader import TopHistoReader, Process, SampleSums
from plotter.WeightReader import WeightReader
from framework.fileReader import GetFiles
from ROOT.TMath import Sqrt as sqrt
from plotter.OutText import OutText

from tt5TeV import lev, level, invlevel

class CrossSection:
  
  ### Add background, signal and data numbers
  def AddBkg(self, name, val, normunc = 0, systunc = 0, statunc = 0, samples = ''):
    ''' Add a bkg process (must include yield, name, uncertainties...) '''
    self.bkg.append(Process(name, Yield = val, NormUnc = normunc, SystUnc = systunc, StatUnc = statunc, samples = samples))

  def SetSignal(self, name, val, statunc = 0, samples = ''):
    ''' Set the signal process (must include yield, name, uncertainties...) '''
    self.signal = Process(name, Yield = val, StatUnc = statunc, samples = samples)

  def SetData(self, n):
    ''' Number of observed events '''
    self.data = n
    self.dataunc = sqrt(n)

  ### Add uncertainties... experimental and modeling
  def AddExpUnc(self, name, val):
    ''' Add the uncertainty 'name' with value 'val' to the experimental uncertainties '''
    self.effUnc[name] = val

  def AddModUnc(self, name, val = 0., do = ''):
    ''' Add the uncertainty 'name' with value 'val' to the modeling uncertainties (on acceptance) 
        if sample names are given (up/down) the uncertainty is read from the histos in that samples 
    '''
    if isinstance(val, float):
      self.accUnc[name] = val
    else:
      nom = self.GetSignalYield()
      up = self.t.GetYield(val)
      do = self.t.GetYield(do)
      var = max(abs(up-nom),abs(do-nom))/nom
      self.AddModUnc(name, var)

  ### Setting methods
  def SetTextFormat(self, textformat):
    ''' Set the format of the output tables (txt, tex) '''
    self.textformat = textformat

  def SetChan(self, ch):
    ''' Set the channel '''
    self.chan = ch

  def SetLevel(self, lev):
    ''' Set level '''
    self.lev = lev
 
  def SetThXsec(self,t):
    ''' Set the theoretical cross section using to normalize signal events '''
    self.thxsec = t

  def SetDoFiducial(self, val = True):
    ''' Boolean to activate printing the fiducial cross section '''
    self.doFiducial = val

  def SetLumi(self, l):
    ''' Set the luminosity '''
    self.lumi = l

  def SetLumiUnc(self, l):
    ''' Set relative lumi unc '''
    self.lumiunc = l

  def SetFiduEvents(self,f):
    ''' Number of fiducual (unweighted) events ''' 
    self.nfidu = f
 
  def SetGenEvents(self, g):
    ''' Number of generated events in the sample '''
    self.ngen = g

  def SetBR(self, b): # Use relative unc
    ''' The branching ratio to what we consider signal '''
    self.BR = b

  def SetOutPath(self, p):
    ''' Set the output path '''
    self.outpath = p

  ### Get parameters...
  def GetThXsec(self):
    return self.thxsec

  def GetLumi(self):
    return self.lumi

  def GetLumiUnc(self):
    return self.lumiunc

  def GetFiduEvents(self, sys = ''):
    return self.nfidu

  def GetGenEvents(self):
    return self.ngen

  def GetBR(self):
    return self.BR

  def GetLevel(self):
    return self.lev
 
  def GetChan(self):
    return self.chan

  def GetBkg(self, name):
    for b in self.bkg:
      if b.GetName() == name: return b
    print 'WARNING: not found background ' + name

  def GetBkgTotRelUnc(self,name):
    return self.GetBkg(name).GetTotRelUnc()

  def GetBkgTotAbsUnc(self,name):
    return self.GetBkgYield(name) * self.GetBkgTotRelUnc(name)

  def GetBkgYield(self, name, sys = ''):
    pr = self.GetBkg(name)
    if   sys == '':       return pr.GetYield()
    elif IsUpSyst(sys):   return pr.GetYield()*(1+pr.GetTotRelUnc())
    elif IsDownSyst(sys): return pr.GetYield()*(1-pr.GetTotRelUnc())
    else                : return pr.GetYield()*(1+pr.GetTotRelUnc())

  def GetData(self):
    return self.data

  def GetDataUnc(self):
    return self.dataunc

  def GetSignal(self):
    return self.signal

  def GetSignalYield(self,sys='',d=''):
    y = self.signal.GetYield()
    if sys == '': return y
    u = self.GetUnc(sys)
    if IsDownSyst(d): return y*(1-u)
    return y*(1+u)

  def GetExpUnc(self, name = ''):
    if name == '':  return self.effUnc
    else         :  return self.effUnc[name]

  def GetModUnc(self, name = ''):
    if name == '':  return self.accUnc
    else         :  return self.accUnc[name]
 
  def GetUnc(self, name):
    if   name in self.modUnc.keys(): return self.GetModUnc(name)
    elif name in self.effUnc.keys(): return self.GetEffUnc(name)
    else: print 'WARNING: not found uncertainty \'%d\''%name
    return 0

  def GetTotBkg(self, sys = '', d = ''):
    ''' Returns the total expected bkg '''
    if sys != '' and sys in [x.GetName() for x in self.bkg]:
      y = self.GetTotBkg()
      var = self.GetBkgTotAbsUnc(sys)
      y = y-var if IsDownSyst(sys+d) else y+var
    else: y = sum([x.GetYield() for x in self.bkg])
    return y

  def GetTotBkgStatUnc(self):
    ''' Returns the total stat unc on bkg '''
    b = 0;
    for pr in self.bkg: b += pr.GetStatUnc()*pr.GetStatUnc()
    return sqrt(b)

  def GetTotBkgSystUnc(self):
    ''' Returns the total syst unc on bkg '''
    b = 0;
    for pr in self.bkg: b += pr.GetSystAbsUnc()*pr.GetSystAbsUnc()
    return sqrt(b)

  def GetXsec(self, sys = '', d = ''):
    ''' Returns the measured cross section '''
    data = self.GetData()
    bkg  = self.GetTotBkg(sys,d) if sys in [x.GetName() for x in self.bkg] else self.GetTotBkg()
    y    = self.GetSignalYield(sys,d)
    thxsec = self.GetThXsec()
    return self.ComputeXsec(data, bkg, y)
 
  def GetFiduXsec(self):
    ''' Returns the fiducial cross section '''
    # fidu = inclusive*(A)
    return self.ComputeXsec()*self.GetAcc()

  def GetAcc(self, sys = ''):
    ''' Returns the measured acceptance '''
    return self.GetFiduEvents(sys)/(self.GetGenEvents()*self.GetBR())

  def GetAccUnc(self):
    ''' Return the syst unc on acceptance '''
    err = 0
    for a in self.accUnc.values(): err += a*a
    return sqrt(err)

  def GetEff(self, sys = ''):
    ''' Returns the measured efficiency '''
    y = self.GetSignalYield(sys)
    A = self.GetAcc()
    BR = self.GetBR()
    lum = self.GetLumi()
    xth = self.GetThXsec()
    return (y)/(A*lum*xth*BR)

  def GetEffUnc(self):
    ''' Return the syst unc on efficiency '''
    err = 0
    for a in self.effUnc.values(): err += a*a
    return sqrt(err)

  def GetXsecSystUnc(self):
    ''' Returns the xsec syst unc on cross section '''
    effunc = self.GetEffUnc()
    accunc = self.GetAccUnc()
    return sqrt(effunc*effunc + accunc*accunc)
 
  def GetXsecLumiUnc(self):
    ''' Returns the xsec lumi uncertainty on cross section '''
    #return self.GetXsec()*(1/self.GetLumi() - 1/(self.GetLumi() * (1+self.GetLumiUnc()) ))
    r = self.GetLumiUnc()
    return (abs(r/(1-r)) + abs(r/(1+r)))/2

  def GetXsecStatUnc(self):
    ''' Returns the stat unc on cross section '''
    xsec = self.ComputeXsec()
    varUp  = self.ComputeXsec(self.GetData() + self.GetDataUnc(), self.GetTotBkg(), self.GetSignalYield())
    varDo  = self.ComputeXsec(self.GetData() - self.GetDataUnc(), self.GetTotBkg(), self.GetSignalYield())
    return max([abs(xsec - varDo)/xsec, abs(xsec - varUp)/xsec])

  def GetXsecBkgRelUnc(self, bkgname):
    ''' Returns the relative unc on the xsec due to the total unc on a bkg estimation '''
    nom = self.ComputeXsec()
    varUp = self.ComputeXsec(self.GetData(), self.GetTotBkg(bkgname,'Up'),   self.GetSignalYield())
    varDo = self.ComputeXsec(self.GetData(), self.GetTotBkg(bkgname,'Down'), self.GetSignalYield())
    return max([abs(nom-varUp)/nom, abs(nom-varDo)/nom])

  ### Several printing methods!
  def PrintYields(self, name = 'yields', doStat = True, doSyst = True):
    t = OutText(self.outpath, name, "new", textformat = self.textformat)
    t.SetTexAlign("l c")
    nsem = 16+3+8 + (5+8 if doStat else 0) + (5+8 if doSyst else 0)
    t.SetSeparatorLength(nsem)
    t.line('%'+'Yields for channel \'%s\' and level \'%s\''%(self.GetChan(), self.GetLevel()))
    t.bar()
    for pr in self.bkg:
      name = t.fix(" %s"%pr.GetName(), 16, 'l',0)
      y    = t.fix("%1.3f"%pr.GetYield(),   8,0)
      stat = t.fix("%1.3f"%pr.GetStatUnc(), 8,0)
      syst = t.fix("%1.3f"%pr.GetSystAbsUnc(), 8,0)
      t.line(name + t.vsep() + y + ((t.pm() + stat) if doStat else '') + ((t.pm() + syst) if doSyst else ''))
    t.sep()
    totbkg     = t.fix("%1.3f"%self.GetTotBkg(), 8,0)
    totbkgstat = t.fix("%1.3f"%self.GetTotBkgStatUnc(), 8,0)
    totbkgsyst = t.fix("%1.3f"%self.GetTotBkgSystUnc(), 8,0)
    t.line(t.fix(" Total bkg", 16, 'l',0) + t.vsep() + totbkg + ((t.pm() + totbkgstat) if doStat else '') + ((t.pm() + totbkgsyst) if doSyst else ''))
    t.sep()
    y = self.GetSignalYield()
    signal = t.fix(" %s"%(self.GetSignal().GetName()), 16, 'l',0)
    ysig   = t.fix("%1.3f"%y,8,0)
    sigunc = t.fix("%1.3f"%(self.GetXsecSystUnc()*y),8,0)
    sigsta = t.fix("%1.3f"%self.GetSignal().GetStatUnc(),8,0)
    t.line(signal + t.vsep() + ysig + ((t.pm() + sigsta) if doStat else '') + ((t.pm() + sigunc) if doSyst else ''))
    t.sep()
    t.line(t.fix(" Data", 16,'l',0) + t.vsep() + t.fix("%i"%self.GetData(),8,0))
    t.bar()
    t.write()

  def PrintXsec(self, name = 'xsec'):
    t = OutText(self.outpath, name, "new", textformat = self.textformat)
    t.SetTexAlign("l c")
    t.SetSeparatorLength(26 + 3 + 20 + 5)
    t.SetDefaultFixOption(False)
    t.line('%'+'tt cross section for channel \'%s\' and level \'%s\''%(self.GetChan(), self.GetLevel()))
    acc = self.GetAcc()
    eff = self.GetEff()
    t.bar()
    t.line(t.fix(' Acceptance', 16, 'r') + t.vsep() + t.fix("%1.4f"%acc, 6) + t.pm() + t.fix("%1.3f"%(acc*self.GetAccUnc()),8))
    t.line(t.fix(' Efficiency', 16, 'r') + t.vsep() + t.fix("%1.4f"%eff, 6) + t.pm() + t.fix("%1.3f"%(eff*self.GetEffUnc()),8))
    t.sep()
    t.line(t.fix(' Branching ratio', 16, 'r') + t.vsep() + t.fix("%1.4f"%self.GetBR(), 6))
    t.line(t.fix(' Gen events', 16, 'r') + t.vsep() + t.fix("%d"%self.GetGenEvents(), 9))
    t.line(t.fix(' Fiducial events', 16, 'r') + t.vsep() + t.fix("%d"%self.GetFiduEvents(), 9))
    if self.doFiducial:
      t.sep()
      xsec = self.GetFiduXsec()
      stat = self.GetXsecStatUnc()
      syst = self.GetEffUnc()
      lumi = self.GetXsecLumiUnc()
      t.line(t.fix(' Fiducial cross section', 26, 'r') + t.vsep() + t.fix("%1.3f"%xsec,6))
      t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(stat*xsec,stat*100) + ' %) (stat)',20, 'l'))
      t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(syst*xsec,syst*100) + ' %) (syst)',20, 'l'))
      t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(lumi*xsec,lumi*100) + ' %) (lumi)',20, 'l'))
    t.sep()
    xsec = self.GetXsec()
    stat = self.GetXsecStatUnc()
    syst = self.GetXsecSystUnc()
    lumi = self.GetXsecLumiUnc()
    t.line(t.fix(' Inclusive cross section', 26, 'r') + t.vsep() + t.fix("%1.3f"%xsec,6))
    t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(stat*xsec,stat*100) + ' %) (stat)',20, 'l'))
    t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(syst*xsec,syst*100) + ' %) (syst)',20, 'l'))
    t.line(t.fix(' +\- ', 26, 'r')            + '   ' + t.fix('%1.3f (%1.3f'%(lumi*xsec,lumi*100) + ' %) (lumi)',20, 'l'))
    t.bar()
    t.write()

  def PrintSystTable(self, name = 'uncertainties'):
    t = OutText(self.outpath, name, "new", textformat = self.textformat)
    t.SetTexAlign("l c")
    t.SetSeparatorLength(30)
    t.SetDefaultFixOption(False)
    t.line('%Uncertainties on tt inclusive cross section \n% '+'for channel \'%s\' and level \'%s\''%(self.GetChan(), self.GetLevel()))
    exp = self.GetExpUnc()
    mod = self.GetModUnc()
    stat = self.GetXsecStatUnc()
    lum  = self.GetXsecLumiUnc()
    syst = self.GetXsecSystUnc()
    xsec = self.GetXsec()
    t.bar()
    t.line(t.fix(' Source', 18, 'l') + t.vsep() + fix("value (%)", 6))
    t.sep()
    for b in [x.GetName() for x in self.bkg]: t.line(fix(' '+b,18,'r') + t.vsep() + fix('%1.3f'%(self.GetXsecBkgRelUnc(b)*100), 6))
    t.sep()
    for e in exp.keys(): t.line(fix(' '+e,18,'l') + t.vsep() + fix('%1.3f'%(exp[e]*100), 6))
    t.sep()
    for e in mod.keys(): t.line(fix(' '+e,18,'l') + t.vsep() + fix('%1.3f'%(mod[e]*100), 6))
    t.sep()
    t.line(fix(' Total systematic',18,'l')+t.vsep()+fix('%1.3f'%(syst*100), 6))
    t.sep()
    t.line(fix(' Statistics',18,'l')+t.vsep()+fix('%1.3f'%(stat*100), 6))
    t.sep()
    t.line(fix(' Luminosity',18,'l')+t.vsep()+fix('%1.3f'%(lum*100), 6))
    t.bar()
    t.write()

  ### Other
  def ComputeXsec(self, data = '', bkg = '', y = ''):
    ''' Computes the xsec from data, bkg and expected yield '''
    if data == '': data = self.data
    if bkg  == '': bkg  = self.GetTotBkg()
    if y    == '': y    = self.GetSignalYield()
    return (data - bkg)/y * self.GetThXsec()

  def SetPathToTrees(self, ptt):
    self.pathToTrees = ptt

  def SetMotherName(self, mn):
    self.motherfname = mn

  def GetNGenEvents(self):
    self.treesow = TChain('Runs', 'Runs')
    files = GetFiles(self.pathToTrees, self.motherfname)
    for f in files: self.treesow.Add(f)

  def ReadHistos(self, path, chan = 'ElMu', level = '2jets', lumi = 308.54, lumiunc = 0.04, bkg = [], signal = [], data = '', expUnc = [], modUnc = [], histoPrefix = ''):
    ''' Set the xsec from histos '''
    if isinstance(expUnc, str): expUnc = expUnc.replace(' ', '').split(',')
    if isinstance(modUnc, str): modUnc = modUnc.replace(' ', '').split(',')
    self.SetChan(chan); self.SetLevel(level)
    self.t = TopHistoReader(path)
    self.t.SetHistoNamePrefix(histoPrefix)
    self.t.SetLumi(lumi)
    self.t.SetChan(chan); self.t.SetLevel(level)
    self.ss = SampleSums(self.pathToTrees, self.motherfname, 'Runs')
    signalName = signal[0]
    signalSample = signal[1]

    # GetFiduEvents
    hfiduname = 'FiduEvents'#_%s'%chan
    fiduEvents = self.t.GetNamedHisto(hfiduname,signalSample).GetBinContent(invlevel[level])
    nGenEvents = self.ss.GetCount('Count') #self.GetNGenEvents(signalSample)
    self.SetLumiUnc(lumiunc)
    self.SetFiduEvents(fiduEvents)
    self.SetGenEvents(nGenEvents)
    for l in bkg:
      if len(l) == 3:
        name, pr, unc = l
        expunc = expUnc
      elif len(l) == 4:
        name, pr, unc, expunc = l
      self.AddBkg(name, self.t.GetYield(pr), unc, self.t.GetUnc(pr, chan, level, expUnc), self.t.GetYieldStatUnc(pr))
    self.SetSignal(signalName, self.t.GetYield(signalSample), self.t.GetYieldStatUnc(signalSample))
    self.t.SetIsData(True)
    self.SetData(self.t.GetYield(data))
    self.t.SetIsData(False)
    for e in expUnc: self.AddExpUnc(e, self.t.GetUnc(signal[1], chan, level, e))
    # Modeling uncertainties
    if 'pdf' in modUnc or 'PDF' in modUnc or 'Scale' in modUnc or 'ME' in modUnc or 'scale' in modUnc:
      pathToTrees = self.pathToTrees #'/pool/ciencias/userstorage/juanr/nanoAODv4/5TeV/5TeV_5sept/'
      motherfname = self.motherfname #'TT_TuneCP5_PSweights_5p02TeV'
      w = WeightReader(path, '',chan, level, sampleName='TT', pathToTrees=pathToTrees, motherfname=motherfname, PDFname='PDFweights', ScaleName='ScaleWeights', lumi=296.1, histoprefix=histoPrefix)
      #w.SetSampleName(signalName)
      if 'pdf' in modUnc or 'PDF' in modUnc: self.AddModUnc('PDF + alpha_S',w.GetPDFandAlphaSunc())
      if 'scale' in modUnc or 'ME' in modUnc: self.AddModUnc('Scale ME',w.GetMaxRelUncScale())
    if 'ISR' in modUnc or 'isr' in modUnc: self.AddModUnc('ISR', self.t.GetUnc(signalSample, chan, level, 'ISR'))
    if 'FSR' in modUnc or 'fsr' in modUnc: self.AddModUnc('FSR', self.t.GetUnc(signalSample, chan, level, 'FSR'))


  def __init__(self, outpath = './temp/', lev = '', chan = '', genEvents = 1, fiduEvents = 1, textformat = "txt"):
    self.SetTextFormat(textformat)
    self.SetThXsec(68.9)
    self.SetLumi(296.1)
    self.SetLumiUnc(0.035) # Relative
    self.SetChan(chan); self.SetLevel(lev)
    self.SetGenEvents(genEvents)   
    self.SetFiduEvents(fiduEvents) 
    self.SetBR((0.108*3)*(0.108*3)) # By default, tt dilepton
    self.bkg    = [] # List of 'Process'
    self.data   = 0  # This is just an integer
    self.signal = '' # Process
    self.accUnc = {} # 'Name' : value
    self.effUnc = {} # 'Name' : value
    self.SetOutPath(outpath)
    self.doFiducial = True
    self.SetMotherName("TT_TuneCP5_5p02TeV")
    self.SetPathToTrees("")

######################################################################################
### Auxiliar functions
def IsUpSyst(sys):
  return sys.endswith('Up') or sys.endswith('up') or sys.endswith('UP')

def IsDownSyst(sys):
  return sys.endswith('Down') or sys.endswith('down') or sys.endswith('DOWN')

def fix(s, n, align = 'l'):
  v = 0
  while len(s) < n:
    if   align == 'l': s += ' '
    elif align == 'r': s = ' ' + s
    elif align == 'c': 
      if   v%2 == 0: s = ' ' + s
      else         : s += ' '
      v += 1
    else: return s
  return s

