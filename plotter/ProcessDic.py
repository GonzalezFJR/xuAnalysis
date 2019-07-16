'''
 Get a dictionary with histograms and compute all the uncertainties
 # dic['process']['histoname']
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
      
  def __init__(self, indic, prlist = [], syslist = [], hname = ''):
    self.indic = indic
    self.SetProcessList(prlist)
    self.SetHistoName(hname)
    self.SetSystList(syslist)
    self.sumdic = {}
    self.systlabels = []
