import os,sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class puWeightProducer:
  def __init__(self,intree, myfile,targetfile,myhist="pileup",targethist="pileup",name="puWeight",norm=True,verbose=False,nvtx_var="Pileup_nTrueInt",doSysVar=True):
    self.targeth = self.loadHisto(targetfile,targethist)
    if doSysVar:
        self.targeth_plus = self.loadHisto(targetfile,targethist+"_plus")
        self.targeth_minus = self.loadHisto(targetfile,targethist+"_minus")
        self.fixLargeWeights = True # temporary fix
    if myfile != "auto" :
      self.autoPU=False
      self.myh = self.loadHisto(myfile,myhist)
    else:
        self.fixLargeWeights = False #AR: it seems to crash with it, to be deugged
    self.autoPU=True
    ROOT.gROOT.cd()
    self.myh=self.targeth.Clone("autoPU")
    self.myh.Reset()
    self.name = name
    self.norm = norm
    self.verbose = verbose
    self.nvtxVar = nvtx_var
    self.doSysVar = doSysVar
    print 'Computing PU weights from: '
    print ' >> ' + myfile
    print ' >> ' + targetfile
      
    pathtolib = "%s/src/WeightCalculatorFromHistogram_cc.so"%basepath
    #if os.path.isfile(pathtolib): 
    ROOT.gSystem.Load(pathtolib)
    #else: #if "/WeightCalculatorFromHistogram_cc.so" not in ROOT.gSystem.GetLibraries():
    # ROOT.gROOT.ProcessLine(".L %s/src/WeightCalculatorFromHistogram.cc++" %basepath)
    dummy = ROOT.WeightCalculatorFromHistogram
    self.beginFile(intree)

  def loadHisto(self,filename,hname):
    tf = ROOT.TFile.Open(filename)
    hist = tf.Get(hname)
    hist.SetDirectory(None)
    tf.Close()
    return hist

  def beginFile(self, intree, outputFile = 0):
    if self.autoPU: self.myh.Reset()
    ROOT.gROOT.cd()
    intree.Project("autoPU",self.nvtxVar)#doitfrom inputFile
    if outputFile : 
      outputFile.cd()
      self.myh.Write()    
    self._worker = ROOT.WeightCalculatorFromHistogram(self.myh,self.targeth,self.norm,self.fixLargeWeights,self.verbose)
    self._worker_plus = ROOT.WeightCalculatorFromHistogram(self.myh,self.targeth_plus,self.norm,self.fixLargeWeights,self.verbose)
    self._worker_minus = ROOT.WeightCalculatorFromHistogram(self.myh,self.targeth_minus,self.norm,self.fixLargeWeights,self.verbose)
    '''
    self.out = intree
    self.out.Branch(self.name, "F")
    if self.doSysVar:
      self.out.Branch(self.name+"Up","F")
      self.out.Branch(self.name+"Down","F")
   '''

  def GetWeight(self, event, direc = 0):
    """process event, return True (go to next module) or False (fail, go to next event)"""
    if hasattr(event,self.nvtxVar):
      nvtx = int(getattr(event,self.nvtxVar))
      weight = self._worker.getWeight(nvtx) if nvtx < self.myh.GetNbinsX() else 1
      if direc ==  0: return weight
      if direc ==  1: return self._worker_plus.getWeight(nvtx) if nvtx < self.myh.GetNbinsX() else 1
      if direc == -1: return self._worker_minus.getWeight(nvtx) if nvtx < self.myh.GetNbinsX() else 1
    else: return 1
    '''
      self.out.GetBranch(self.name).Fill(weight)
      if self.doSysVar:
        self.out.GetBranch(self.name+"Up").Fill(weight_plus)
        self.out.GetBranch(self.name+"Down").Fill(weight_minus)
      return True
    '''
  def GetWeightUp(self, event):
    return self.GetWeight(event, 1)

  def GetWeightDown(self, event):
    return self.GetWeight(event, -1)

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

pufile_mc2016="%s/inputs/pileup/pileup_profile_Summer16.root" %basepath
pufile_data2016="%s/inputs/pileup/PileupData_GoldenJSON_Full2016.root" %basepath
puWeight_2016 = lambda intree : puWeightProducer(intree, pufile_mc2016,pufile_data2016,"pu_mc","pileup",verbose=False, doSysVar=True)
puAutoWeight_2016 = lambda intree : puWeightProducer(intree, "auto", pufile_data2016,"pu_mc","pileup",verbose=False)
'''
pufile_data2017="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/puData2017_withVar.root" % os.environ['CMSSW_BASE']
pufile_mc2017="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2017.root" % os.environ['CMSSW_BASE']
puWeight_2017 = lambda : puWeightProducer(pufile_mc2017,pufile_data2017,"pu_mc","pileup",verbose=False, doSysVar=True)
puAutoWeight_2017 = lambda : puWeightProducer("auto",pufile_data2017,"pu_mc","pileup",verbose=False)

pufile_data2018="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/puData2018_withVar.root" % os.environ['CMSSW_BASE']
pufile_mc2018="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2018.root" % os.environ['CMSSW_BASE']
puWeight_2018 = lambda : puWeightProducer(pufile_mc2018,pufile_data2018,"pu_mc","pileup",verbose=False, doSysVar=True)
puAutoWeight_2018 = lambda : puWeightProducer("auto",pufile_data2018,"pu_mc","pileup",verbose=False)
'''
