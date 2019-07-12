'''
  How it works:
    l.AddCut('len(selMuon) >= 2')
    l.AddHisto('invmass', 'InvMass', 20, 0, 2000, tit = 'm_{#mu#mu} (GeV)')
    l.AddSample('TTTo2L2Nu', 'TTTo2L2Nu_TuneCP5_PSweights')
    l.AddSelection(selection)
    out = l.Run()
    out['TTTo2L2Nu']['invmass']
'''
import os,sys
mypath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(mypath)

from framework.AnalysisCreator import AnalysisCreator
from run import main as run

class looper(AnalysisCreator):

  def Run(self):
    self.CreateAnalysis()
    cfgpath = '%s/%s.cfg'%(self.outpath, self.cfgname)
    print 'Executing analysis \'%s\' using cfg file \'%s\' in \'%s\'...'%(self.analysisName, self.cfgname, self.outpath)
    # run(cfgpath)

  def AutoRemove(self):
    command = 'rm -r %s/%s'%(self.outpath, self.analysisName)
    os.system(command)

  def AddToOutput(self, sampleName, histodic):
    self.out[sampleName] = histodic

  def __init__(self, path = '', nSlots = 1, cut = '', weight = '', nEvents = 0, year = 0, verbose = 1, options = ''):
    self.analysisName = GetAnalysisName()
    self.SetCfgname('testcfg')
    self.SetOutpath('./.looper/')
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
    if cut != '': self.AddCut(cut)



