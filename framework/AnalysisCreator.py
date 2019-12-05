import os,sys, re
mypath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(mypath)
import functions as fun

class AnalysisCreator:
  def AddSelection(self, selection):
    selection = selection.replace('\t', '  ')
    lines = selection.split('\n')
    for l in lines:
      ltemp = "%s"%l
      lorig = "%s"%l
      ltemp = ltemp.replace(' ', '')
      if ltemp != '': break
    nspaces = 0
    while len(lorig) >0 and lorig[0] == ' ':
      nspaces += 1
      lorig = lorig[1:]
    addNSpaces = 4-nspaces
    self.selection =  ''
    for l in lines:
      self.selection += '%s%s\n'%(' '*addNSpaces, l)

  def AddSyst(self, syst):
    if isinstance(syst, list): self.syst += syst
    elif syst == '': return
    elif ',' in syst: self.AddSyst(syst.replace(' ', '').split(','))
    else: self.syst.append(syst)

  def AddHeader(self, h):
    self.header += h

  def AddInit(self, t):
    self.init += t

  def AddCut(self, cut, variables = ''):
    if not isinstance(variables, list): variables = [variables]
    for v in variables: cut = fun.replaceWords(cut, v, 'fun.GetValue(t, "%s",syst)'%v)
    #cut = self.CraftCut(cut)
    self.cuts.append(cut)

  def AddHisto(self, var, hname, nbins, b0 = 0, bN = 0, bins = [], weight = '', sys = '', cut = '', tit = '', write = True):
    if sys != '': hname += '_' + sys
    if weight == '': weight = self.weight
    self.weights[hname] = weight
    self.vars[hname] = var
    self.histocuts[hname] = cut
    if tit == '': tit = hname
    for syst in self.syst:
      hline = 'self.CreateTH1F("%s%s", "%s", %i, %1.2f, %1.2f)\n'%(hname, '' if syst == '' else '_'+syst, tit, nbins, b0, bN)
      self.histos.append(hline)
    var = self.vars[hname]
    weight = self.weights[hname]
    cut = '' if self.histocuts[hname] == '' else ' if %s:'%self.histocuts[hname]
    if var    in self.expr.keys()  : varstring = var
    else                           : varstring = 'fun.GetValue(t, "%s",syst)'%var
    if   weight == ''              : weistring = ''
    elif weight in self.expr.keys(): weistring = ', ' + weight
    else                           : weistring = ', fun.GetValue(t, "%s",syst)'%weight
    fillLine = '   %s self.obj[%s].Fill(%s%s)\n'%(cut, "'"+hname+"' + '_%s'%syst if syst != '' else '"+hname+"'", varstring, weistring)
    if write: self.fillLine.append(fillLine)
    else    : return fillLine

  def AddExpr(self, ename, var, expr):
    if not isinstance(var, list): var = [var]
    for v in var: 
      if v == '': continue
      st = 'fun.GetValue(t, "%s", syst)'%v
      expr = re.sub(r'\b%s\b'%v, st, expr)
    self.expr[ename] = expr

  def CraftCut(self, cut):
    return cut

  def AddSample(self, sampleName, sampleList):
    self.samples[sampleName] = sampleList

  def SetCfgname(self, cfgname):
    if not '.' in cfgname: cfgname += '.cfg'
    self.cfgname = cfgname

  def SetPath(self, path):
    self.path = path

  def SetBasePath(self, basepath):
    self.basepath = basepath

  def SetOutpath(self, outpath):
    self.outpath = outpath

  def SetOptions(self, options):
    self.options = options

  def SetNEvents(self, nEvents):
    self.nEvents = nEvents

  def SetYear(self, year = 0):
    if year not in [2016, 2017, 2018]: year = 0
    self.year = year

  def SetTreeName(self, treeName = ''):
    self.treeName = treeName

  def SetVerbose(self, verbose = 1):
    self.verbose = verbose

  def SetOptions(self, options = ''):
    self.options = options

  def SetWeight(self, weight = ''):
    self.weight = weight

  def SetNSlots(self, nSlots = 1):
    self.nSlots = nSlots

  def GetAnalysisTemplate(self):
    body  = "'''\n Analysis %s, created by xuAnalysis\n https://github.com/GonzalezFJR/xuAnalysis\n'''\n\n"%self.analysisName
    body += 'import os,sys\nsys.path.append(os.path.abspath(__file__).rsplit("/xuAnalysis/",1)[0]+"/xuAnalysis/")\n'
    body += 'from framework.analysis import analysis\nimport framework.functions as fun\nfrom ROOT import TLorentzVector\n\n'
    body += self.header
    body += '\nsystematics = ' + str(self.syst) + '\n'
    body += 'class %s(analysis):\n'%self.analysisName
    body += '  def init(self):\n'
    body += self.init
    body +='    # Create your histograms here\n'
    #if len(self.syst) > 0: body +='    for syst in systematics:\n'     
    for line in self.histos: body += '    %s%s'%('  ' if len(self.syst) > 0 else '', line)
    body += '\n  def insideLoop(self,t):\n    # WRITE YOU ANALYSIS HERE\n\n'

    if self.selection != '': 
      body += '\n    # Selection\n'
      body += self.selection

    if len(self.cuts) > 0 and len(self.syst) == 0:
      body += '\n    # Requirements\n'
      for cut in self.cuts: body += '    if not %s: return\n'%cut


    hnames = self.vars.keys()
    if len(hnames) > 0:
      body += '\n    # Filling the histograms\n'
      if len(self.syst) > 0: 
        body += '\n    for syst in systematics:\n'
        body += '\n      # Requirements\n'
        for cut in self.cuts: body += '      if not %s: return\n'%cut
      for expr in self.expr.keys(): body += '      %s = %s\n'%(expr, self.expr[expr])
    #  for h in hnames:
    #    var = self.vars[h]
    #    cut = ' ' if self.histocuts[h] == '' else ' if %s:'%self.histocuts[h]
    #    body += '  %s self.obj[\'%s\'].Fill(%s%s)\n'%(cut, h, var, (','+self.weights[h]) if self.weights[h] != '' else '')
    for line in self.fillLine: body += '%s%s\n'%('  ' if len(self.syst) > 0 else '', line)
    return body

  def GetConfigFileTemplate(self):
    path = self.path
    print 'PATH : ', path
    if path == '': path = '/Insert/path/to/trees/here/'
    cfg  = '# cfg file to run xuAnalysis\n'
    cfg += '# To execute: \n'
    cfg += '# >> python run.py %s -s SampleName -n nSlots\n\n'%self.cfgname
    cfg += 'path : %s\n'%path
    cfg += 'outpath: temp/\n' if self.outpath == '' else 'outpath : %s\n'%self.outpath
    cfg += '#options : \n' if self.options == '' else 'options : %s\n'%self.options
    cfg += '#nEvents : 1000\n' if self.nEvents == 0 else 'nEvents : %i\n'%self.nEvents
    cfg += '#year : 2016\n' if not self.year in [2016,2017,2018] else 'year : %i\n'%self.year
    cfg += 'verbose : %i\n'%self.verbose
    cfg += 'nSlots : %i\n'%self.nSlots
    cfg += 'selection : %s\n'%self.analysisName
    cfg += 'treeName : %s\n\n'%self.treeName if self.treeName != '' else '#treeName : \n\n'
    cfg += '# Introduce your samples here following the example of the form:\n'
    cfg += '# SampleName : Filename1, Filename2, Filename2_ext\n'
    samples = self.samples.keys()
    if len(samples) > 0:
      for s in samples:
        files = self.samples[s]
        cfg += '%s : %s\n'%(s, files)
    return cfg

  def CreateAnalysis(self):
    analysisName = self.analysisName
    mpath = mypath if self.basepath == '' else mypath + self.basepath + '/'
    if not os.path.isdir(mpath): os.mkdir(mpath)
    if os.path.isdir(mpath+analysisName):
      print 'ERROR: analysis %s already exists!!!'%analysisName
      return
    os.mkdir(mpath + analysisName)

    # Analysis code
    f = open('%s%s/%s.py'%(mpath,analysisName,analysisName), 'w')
    body = self.GetAnalysisTemplate()
    f.write(body)
    f.close()
    print 'Created analysis code in %s%s'%(mpath,analysisName)

    # cfg file
    f2 = open('%s%s/%s'%(mpath,analysisName,self.cfgname), 'w')
    cfg = self.GetConfigFileTemplate()
    f2.write(cfg)
    f2.close()
    print 'Created cfg file \'%s\' in %s%s'%(self.cfgname, mpath, analysisName)
    f3 = open(mpath + analysisName + '/__init__.py', 'w')
    f3.write(' ')
    f3.close()

  def __init__(self, analysisName, cfgname = 'testcfg', path = '', weight = '', outpath = '', nSlots = 1, nEvents = 0, year = 0, verbose = 1, options = '', basepath = '', treeName = 'Events'):
    self.analysisName = analysisName
    self.SetCfgname(cfgname)
    self.SetPath(path)
    self.SetOutpath(outpath)
    self.SetNEvents(nEvents)
    self.SetYear(year)
    self.SetTreeName(treeName)
    self.SetVerbose(verbose)
    self.SetOptions(options)
    self.SetNSlots(nSlots)
    self.SetWeight(weight)
    self.SetBasePath(basepath)
    self.header = ''
    self.init = ''
    self.selection = ''
    self.cuts = []
    self.histos = []
    self.fillLine = []
    self.samples = {}
    self.vars = {}
    self.weights = {}
    self.histocuts = {}
    self.syst = ['']
    self.expr = {}


def main():
  import argparse
  pr = argparse.ArgumentParser()
  pr.add_argument('name', help='Name of the new analysis', type = str)
  pr.add_argument('--cfg', '-c', help='Name of the new cfg file', type = str, default = 'testcfg.cfg')
  pr.add_argument('--path', '-p', help='Path where the trees are stored', type = str, default = '')
  args = pr.parse_args()
  analname = args.name
  cfgname  = args.cfg
  path     = args.path

  na = AnalysisCreator(analname, cfgname,  path)

  selection  = '''
    # As an example: select medium ID muons and fill an histogram with the invariant mass
    selMuon = [];
    for imu in range(t.nMuon):
      if t.Muon_mediumId[imu]:
        v = TLorentzVector()
        v.SetPtEtaPhiM(t.Muon_pt[imu], t.Muon_eta[imu], t.Muon_phi[imu], t.Muon_mass[imu])
        selMuon.append(fun.lepton(v, t.Muon_charge[imu], 13))\n
      # Invariant mass, using a predefined function 
      invmass = fun.InvMass(selMuon[0], selMuon[1]) if len(selMuon) >= 2 else 0
  '''

  na.AddSelection(selection)
  na.AddCut('len(selMuon) >= 2')
  na.AddHisto('invmass', 'InvMass', 20, 0, 2000, tit = 'm_{#mu#mu} (GeV)', weight = 'self.EventWeight', cut = 'self.nJet > 2')
  na.AddSample('TTTo2L2Nu', 'TTTo2L2Nu_TuneCP5_PSweights')
  na.CreateAnalysis()

if __name__ == '__main__': main()
