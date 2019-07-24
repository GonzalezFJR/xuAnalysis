import os,sys
mypath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(mypath)

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

  def AddCut(self, cut):
    cut = self.CraftCut(cut)
    self.cuts.append(cut)

  def AddHisto(self, var, hname, nbins, b0 = 0, bN = 0, bins = [], weight = '', sys = '', cut = '', tit = '', write = True):
    if sys != '': hname += '_' + sys
    if weight == '': weight = self.weight
    self.weights[hname] = weight
    self.vars[hname] = var
    self.histocuts[hname] = cut
    if tit == '': tit = hname
    hline = 'self.CreateTH1F("%s", "%s", %i, %1.2f, %1.2f)\n'%(hname, tit, nbins, b0, bN)
    var = self.vars[hname]
    cut = ' ' if self.histocuts[hname] == '' else ' if %s:'%self.histocuts[hname]
    fillLine = '  %s self.obj[\'%s\'].Fill(%s%s)\n'%(cut, hname, var, (','+self.weights[hname]) if self.weights[hname] != '' else '')
    self.histos.append(hline)
    if write: self.fillLine.append(fillLine)
    else    : return fillLine
           

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
    body += 'class %s(analysis):\n'%self.analysisName
    body += '  def init(self):\n    # Create your histograms here\n'
    for line in self.histos: body += '    %s\n'%line
    body += '\n  def insideLoop(self,t):\n    # WRITE YOU ANALYSIS HERE\n\n'

    if self.selection != '': 
      body += '\n    # Selection\n'
      body += self.selection

    if len(self.cuts) > 0:
      body += '\n    # Requirements\n'
      for cut in self.cuts: body += '    if not %s: return\n'%cut

    hnames = self.vars.keys()
    if len(hnames) > 0:
      body += '\n    # Filling the histograms\n'
    #  for h in hnames:
    #    var = self.vars[h]
    #    cut = ' ' if self.histocuts[h] == '' else ' if %s:'%self.histocuts[h]
    #    body += '  %s self.obj[\'%s\'].Fill(%s%s)\n'%(cut, h, var, (','+self.weights[h]) if self.weights[h] != '' else '')
    for line in self.fillLine: body += '%s\n'%line
    return body

  def GetConfigFileTemplate(self):
    path = self.path
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
    self.selection = ''
    self.cuts = []
    self.histos = []
    self.fillLine = []
    self.samples = {}
    self.vars = {}
    self.weights = {}
    self.histocuts = {}


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
  na.AddHisto('invmass', 'InvMass', 20, 0, 2000, tit = 'm_{#mu#mu} (GeV)', weight = 'EventWeigt', cut = 'nJets > 2')
  na.AddSample('TTTo2L2Nu', 'TTTo2L2Nu_TuneCP5_PSweights')
  na.CreateAnalysis()

if __name__ == '__main__': main()
