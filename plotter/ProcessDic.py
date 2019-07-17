'''
 Get a dictionary with histograms and compute all the uncertainties
 # dic['process']['histoname']
 h = HistoMerger(dic, ListOfProcesses, ListOfUncertainties, NameOfHistogram)
 h.SumHistos()
 hstat = h.GetUncHist('stat')
 hsyst = h.GetUncHist()
'''

class HistoMerger:
  def SetProcessList(self, listOfProcesses):
    if isinstance(listOfProcesses, str): listOfProcesses = listOfProcesses.split(',')
    self.processList = listOfProcesses

  def SetHistoName(self, hname):
    self.histoname = hname

  def SetSystList(self, listOfSyst):
    if isinstance(listOfSyst, str): listOfSyst = listOfSyst.split(',')
    self.systname = systList
    self.systlabels = []
    for s in systList:
      self.SearchSystHisto(self.hname, s)

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

  def SumHistos(self, hname, syst = ''):
    self.SetHistoName(hname)
    if syst == '':
      h = self.indic[self.processList[0]][hname].Clone("sum0")
      h.SetDirectory(0)
      if len(self.processList) > 1:
        for pr in self.processList[1:]: h.Add(self.indic[pr][hname])
      self.sumdic[syst] = h
    else:
      for s in self.GetListOfCandNames(syst):
        if not s in self.systlabels: return
        pr0 = self.processList[0]
        hs = "%s_%s"%(hname, s)
        if not hs in self.indic[pr0].keys(): hs = hname
        h = self.indic[pr0][hs].Clone("sum0")
        if len(self.processList) > 1:
          for pr in self.processList[1:]:
            hs = "%s_%s"%(hname, s)
            if not hs in self.indic[pr].keys(): hs = hname
            h.Add(self.indic[pr][hname])
        self.sumdic[s] = h

  def GetDifUnc(self, hnom, hsyst):
    ''' Get a nom histo and a list of histos and returns the mean per-bin error in a list 
        hsyst is a list of labels, not name of uncertainty
    '''
    nb = hnom.GetNbinsX()
    n = [hnom.GetBinContent(i) for i in range(0, nb+2)]
    if not isinstance(hsyst, list): hsyst = [hsyst]
    var  = [ [abs(h.GetBinContent(i)-n[i]) for i in range(0, nb+2)] for h in hsyst]
    nsyst = len(var)
    meansyst = []
    for i in range(0, nb+2):
      l = 0.
      for j in range(nsyst):
        l += var[j][i]
      l = l/nsyst
      meansyst.append(l)
    return meansyst

  def GetStatUnc(self):
    ''' List with stat unc from nominal histo '''
    hnom = self.sumdic['']
    nb = hnom.GetNbinsX()
    statunc = [hnom.GetBinError(i) for i in range(0, nb+2)]
    return statunc

  def GetSum2Unc(self, lsyst = '', includeStat = False):
    ''' From a list of uncertainties, get a list of per-bin unc w.r.t. nominal histo 
        lsyst is a list of uncertainty names, not labels
    '''
    if   lsyst == '': lsyst = self.systname
    elif isinstance(lsyst, str) and ',' in lsyst: lsyst = lsyst.split(',')
    elif not isinstance(lsyst, list): lsyst = [syst]
    unc = []
    systExist = labmda x : x in self.systlabels
    for s in lsyst:
      listOfGoodSyst = filter(systExist, self.GetListOfCandNames(s))
      unc.append(syst, GetDifUnc(self.sumdic[''], [sumdic[s] for s in listOfGoodSyst]))
    sum2 = []
    if includeStat: sum2.append(self.GetStatUnc())
    for iunc in unc:
      val = 0
      for v in iunc: val += v*v
      v = sqrt(v)
      sum2.append(v)
    return sum2

  def GetUncHist(self, syst = ''):
    ''' syst is a name, not a label... returns nominal histo with nice uncertainties '''
    if   syst == '': syst = self.systname
    elif isinstance(syst, str) and ',' in syst: syst = syst.split(',')
    elif not isinstance(syst, list): syst = [syst]
    sumdic = self.sumdic.copy() # To keep the original
    hnom = sumdic[''].Clone('hnom')
    if syst == 'stat': return hnom
    unc = self.GetSum2Unc(syst)
    nbins = hnom.GetNbinsX()
    for i in range(0,nbins+2)
      hnom.SetBinError(unc[i])
    hnom.SetDirectory(0)
    return hnom
      
  def __init__(self, indic, prlist = [], syslist = [], hname = ''):
    self.indic = indic
    self.SetProcessList(prlist)
    self.SetHistoName(hname)
    self.SetSystList(syslist)
    self.sumdic = {}
    self.systlabels = []
