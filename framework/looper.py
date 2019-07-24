'''
  How it works:
    l.AddCut('len(selMuon) >= 2')
    l.AddHisto('invmass', 'InvMass', 20, 0, 2000, tit = 'm_{#mu#mu} (GeV)')
    l.AddSample('TTTo2L2Nu', 'TTTo2L2Nu_TuneCP5_PSweights')
    l.AddSelection(selection)
    out = l.Run()
    out['TTTo2L2Nu']['invmass']
'''
import os,sys,time
mypath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(mypath)

from framework.AnalysisCreator import AnalysisCreator
from run import main as run

class looper(AnalysisCreator):

  def AddRunFolder(self, fname):
    sys.path.append(fname)

  def Run(self):
    self.CreateAnalysis()
    #cfgpath = '%s/%s.cfg'%(self.outpath, self.cfgname)
    cfgpath = self.cfgname
    print 'Executing analysis \'%s\' using cfg file \'%s\' in \'%s/%s/\'...'%(self.analysisName, cfgpath, self.outpath, self.analysisName)
    return run('%s/%s/%s'%(self.outpath,self.analysisName,cfgpath))

  def AutoRemove(self):
    command = 'rm -r %s/%s'%(self.outpath, self.analysisName)
    os.system(command)

  def AddToOutput(self, sampleName, histodic):
    self.out[sampleName] = histodic

  def GetAnalysisName(self):
    return 'analysis_%i'%(int(time.time()*1e6)%1e12)

  def __init__(self, path = '', nSlots = 1, cut = '', weight = '', nEvents = 0, year = 0, verbose = 0, options = 'merge', treeName = 'Events', processdic = {}):
    self.analysisName = self.GetAnalysisName()
    self.SetTreeName(treeName)
    self.SetCfgname('testcfg')
    self.SetOutpath('./.looper/')
    self.SetBasePath('./.looper/')
    self.AddRunFolder('.looper')
    self.SetPath(path)
    self.SetNEvents(nEvents)
    self.SetYear(year)
    self.SetVerbose(verbose)
    self.SetOptions(options)
    self.SetNSlots(nSlots)
    self.SetWeight(weight)
    self.selection = ''
    self.cuts = []
    self.histos = []
    self.samples = {}
    self.vars = {}
    self.out = {}
    self.fillLine = []
    self.weights = {}
    self.histocuts = {}
    if cut != '': self.AddCut(cut)
    if processdic != {}:
      for pr in processdic:
        self.AddSample(pr, processdic[pr])



