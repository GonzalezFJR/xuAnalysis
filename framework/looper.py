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
from ROOT import TFile

class looper(AnalysisCreator):

  def AddRunFolder(self, fname):
    sys.path.append(fname)

  def Run(self):
    odir = {}
    if len(self.samples.keys()) != 0:
      self.CreateAnalysis()
      #cfgpath = '%s/%s.cfg'%(self.outpath, self.cfgname)
      cfgpath = self.cfgname
      print 'Executing analysis \'%s\' using cfg file \'%s\' in \'%s/%s/\'...'%(self.analysisName, cfgpath, mypath+self.basepath, self.analysisName)
      odir = run('%s/%s/%s'%(mypath+self.basepath,self.analysisName,cfgpath), self.sendJobs)
    if self.readOutput and self.loadDic != {}:
      for ksamp in self.loadDic.keys():
        odir[ksamp] = self.loadDic[ksamp]
    return odir

  def AutoRemove(self):
    command = 'rm -r %s/%s'%(self.outpath, self.analysisName)
    os.system(command)

  def AddToOutput(self, sampleName, histodic):
    self.out[sampleName] = histodic

  def GetAnalysisName(self):
    return 'analysis_%i'%(int(time.time()*1e6)%1e12)

  def AddSample(self, sampleName, sampleList):
    if self.readOutput:
      #print '[readOutput = True] Looking for files in %s...'%self.outpath
      if ' ' in sampleName: sampleName = sampleName.replace(' ', '')
      if os.path.isfile('%s/%s.root'%(self.outpath, sampleName)):
        if not sampleName in self.loadDic.keys(): self.loadDic[sampleName] = {}
        print 'Reading %s from %s...'%(sampleName, self.outpath)
        f = TFile.Open('%s/%s.root'%(self.outpath, sampleName))
        hlist = f.GetListOfKeys()        
        for l in hlist:
          hname = l.GetName()
          histo = getattr(f, hname)
          histo.SetDirectory(0)
          self.loadDic[sampleName][hname] = histo
      else: self.samples[sampleName] = sampleList
    else:
      self.samples[sampleName] = sampleList

  def SendJobs(self, do=True):
    self.sendJobs = do

  def __init__(self, path = '', nSlots = 1, cut = '', weight = '', nEvents = 0, year = 0, verbose = 0, options = 'merge', treeName = 'Events', processdic = {}, outpath='./.looper/', readOutput=False, basepath = './looper/', xsec = 'xsec', sendJobs = False):
    self.analysisName = self.GetAnalysisName()
    self.SetTreeName(treeName)
    self.SetCfgname('testcfg')
    self.SetOutpath(outpath)
    self.SetBasePath(basepath)
    self.AddRunFolder(outpath)
    self.SetPath(path)
    self.SetNEvents(nEvents)
    self.SetYear(year)
    self.SetVerbose(verbose)
    self.SetXsec(xsec)
    self.SetOptions(options)
    self.SetNSlots(nSlots)
    self.SetWeight(weight)
    self.readOutput = readOutput
    self.header = ''
    self.init = ''
    self.selection = ''
    self.loopcode = ''
    self.cuts = []
    self.histos = []
    self.samples = {}
    self.vars = {}
    self.out = {}
    self.loadDic = {}
    self.fillLine = []
    self.weights = {}
    self.histocuts = {}
    self.syst = ['']
    self.expr = {}
    self.exprorder = {}
    self.sampleOptions = ''
    self.sendJobs = sendJobs
    if cut != '': self.AddCut(cut)
    if processdic != {}:
      for pr in processdic:
        self.AddSample(pr, processdic[pr])



