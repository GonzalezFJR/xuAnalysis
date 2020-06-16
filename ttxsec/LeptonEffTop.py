import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader, OutText

class LeptonEffTop(TopHistoReader):

  def SetOutPath(self, p):
    self.outpath = p

  def SetProcessDic(self, d):
    self.processDic = d

  def SetProcesses(self, pr = ''):
    if pr == '':
      k = self.processDic.keys()
      if   'data' in k: k.pop(k.index('data'))
      elif 'Data' in k: k.pop(k.index('Data'))
    self.selprocess = k

  def SetDataProcess(self, pr = 'data'):
    self.datapr = pr

  def SetProcessFromDic(self, pr = ''):
    if pr == '': pr = self.selprocess
    if isinstance(pr,str): pr = pr.replace(' ', '').split(',')
    self.SetProcess([self.processDic[p] for p in pr])

  def GetHistoName(self, l1 = '', l2 = '', l3 = '', l4 = ''):
    if   l1 == ''                          : return ''
    elif l4 == '' and l3 == '' and l2 == '': hname = l1
    elif l4 == ''                          : 
      if l1 == 'All' or l1 == 'Total' or l1 == 'Den':
        hname = [self.GetHistoName('Pass', l2, l3), self.GetHistoName('Fail', l2, l3)]
      else: hname = self.var + '_' + l1 + '_' + l2 + '_' + l3
    else                                   : 
      self.SetVar(l1)
      if l2 == 'All' or l2 == 'Total' or l2 == 'Den':
        hname = [self.GetHistoName(l1, 'Pass', l3, l4), self.GetHistoName(l1, 'Fail', l3, l4)]
      else:
        hname = self.var + '_' + l2 + '_' + l3 + '_' + l4
    if self.histoprefix != '' and not isinstance(hname, list): hname = self.histoprefix + '_' + hname
    return hname

  def GetHisto(self, l1, l2 = '', l3 = '', l4 = '', pr = ''):
    self.SetProcessFromDic(pr)
    hname = self.GetHistoName(l1, l2, l3, l4)
    return self.GetNamedHisto(hname)

  ######################################
  ## Fake from SS data

  def GetR(self, tag = 'Pass'):
    hOS = self.GetHisto(tag, 'Fake', 'OS')
    hSS = self.GetHisto(tag, 'Fake', 'SS')
    hSS.Divide(hOS)
    return hSS

  def GetNonpromtpFromSSdata(self, tag = 'Total'):
    hR = self.GetR()
    hDataSS   = self.GetHisto(tag, 'Prompt', 'SS', pr = self.datapr)
    hPromptSS = self.GetHisto(tag, 'Prompt', 'SS', pr = '')
    h = hDataSS.Clone('ggh')
    nbins = h.GetNbinsX()
    for i in range(0, nbins+1):
      data   = hDataSS  .GetBinContent(i)
      prompt = hPromptSS.GetBinContent(i)
      R      = hR       .GetBinContent(i)
      h.SetBinContent(i, (data-prompt)*R)
    return h

  def GetEff(self):
    hDataNum = self.GetHisto('Pass',  'Prompt', 'OS', pr = self.datapr)
    hBkgNum  = self.GetNonpromtpFromSSdata('Pass')
    hBkgNum.Scale(-1)
    hDataNum.Add(hBkgNum)
    hDataDen = self.GetHisto('Total', 'Prompt', 'OS', pr = self.datapr)
    hBkgDen  = self.GetNonpromtpFromSSdata('Total')
    hBkgDen.Scale(-1)
    hDataDen.Add(hBkgDen)
    hDataNum.Divide(hDataDen)
    return hDataNum

  def GetEffTnP(self, sign = 'OS'):
    ''' Return eff from MC (with standard SF applied) '''
    #self.SetProcessFromDic()
    hpass = self.GetHisto('Pass', 'Prompt', sign)
    hden  = self.GetHisto('All', 'Prompt', sign)
    #hpass = self.GetHisto('Pass', 'Prompt', sign)
    #hfail = self.GetHisto('Fail', 'Prompt', sign)
    #hden  = hpass.Clone('hden')
    #hden.Add(hfail)
    hpass.Divide(hden)
    return hpass

  def InitTopHistoReader(self):
    self.doStackOverflow = False
    self.doNormalize = False
    self.IsData  = True
    self.verbose = False
    self.SetVar('')
    self.SetChan('')
    self.SetLevel('')
    self.SetSystematic('')
    self.SetYieldsSSname()
    self.SetFileNamePrefix('')
    self.fname = ''
    self.rebin = 1
    self.lumi = 1
    self.ReComputeStatUnc = False
      
  def __init__(self, path, out = './', processDic = {}, process = '', dataname = 'data', histoprefix = 'H'):
    self.InitTopHistoReader()
    self.SetPath(path) 
    self.SetOutPath(out)
    if processDic != {}: 
      self.SetProcessDic(processDic)
      self.SetDataProcess(dataname)
      self.SetProcesses(process)
    self.SetHistoNamePrefix(histoprefix)

 
