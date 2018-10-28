from ROOT import *
from fileReader import *
from jobManager import *
from multiprocessing import Pool
from array import array
from copy import deepcopy

def loopAnal(listOfInputs): 
  ''' External function to run de loop... needed for the multiprocessing ''' 
  anal, i0, iN, k = listOfInputs
  analcopy = deepcopy(anal) 
  analcopy.SetIndex(k)
  analcopy.SetNSlots(1)
  analcopy.loop(i0, iN)

class analysis:

  #############################################################################################
  #############################################################################################
  ### Setting funcitons

  def SetFiles(self, path, fname = ''):
    ''' Search and store the files '''
    if fname == '':
      if isinstance(path, list):
        self.files = path
        return
      else: print '[ERROR] Wrong input'
    else:
      self.files = GetFiles(path, fname, self.verbose >= 2)

  def SetOutDir(self, _outpath):
    ''' Sets the output directory '''
    self.outpath = _outpath
    if not self.outpath[-1] == '/': self.outpath = self.outpath + '/'
    
  def SetOutName(self, _outname):
    ''' Sets the name of the output rootfile '''
    self.outname = _outname  
    if self.outname[-5:] == '.root': self.outname = self.outname[:-5]

  def SetJobFolder(self, folder):
    ''' Sets the name of the folder where the job outputs will be stored '''
    if len(folder) > 0 and not folder[-1] == '/': folder += '/'
    self.jobFolder = folder

  def AddToOutputs(self, obj):
    ''' Add an object to the output list '''
    self.outputList.append(obj)

  def SetXsec(self, _xsec):
    self.xsec = _xsec

  def SetNSlots(self, _nSlots):
    self.nSlots = _nSlots

  def SetIndex(self, _index):
    self.index = _index

  def SetVerbose(self, verbose = 1):
    self.verbose = verbose

  def SetTreeName(self, name):
    ''' Sets the name of the input tree '''
    self.treeName = name

  def SetParams(self):
    ''' Once the input files are set, calculate all the needed parameters '''
    if len(self.files) == 0: return
    _nEvents, _nGenEvents, _nSumOfWeights, _isData = GetAllInfoFromFile(self.files)
    self.nEvents       = _nEvents
    self.nGenEvents    = _nGenEvents
    self.nSumOfWeights = _nSumOfWeights
    self.isData        = _isData 
    self.nRunEvents    = self.nEvents
    if self.outname == '': self.SetOutName(guessProcessName(self.files))

  def manageOutput(self):
    ''' Checks if output existis and creates output dir '''
    out = self.outpath + self.outname + '.root'
    if self.index >= 0: out = self.outpath + self.outname + '_' + str(self.index) + '.root'
    if not os.path.isdir(self.outpath):
      print ' >> Creating output directory: ' + self.outpath
      os.mkdir(self.outpath)
    elif os.path.isfile(out):
      print ' >> WARNING: output already existis... it will be overwritten!!'

  def printprocess(self, i):
    ''' Prints some output from time to time... '''
    nevents = self.nRunEvents
    i0 = self.firstEvent
    if int(i) % int(self.nEventsPrintOut) == 0:
      if   self.index == -1: print 'Processing... %i / %i (%1.2f'%(i,nevents, (float(i)-i0)/nevents*100) + '%)'
      elif self.index == 0:  print 'Processing... %1.2f'%((float(i)-i0)/nevents*100) + ' %'

  def getInputs(self,first = -1, last = -1):
    ''' Returns a list with [firstEvent, lastEvent] for paralel processing '''
    inputs = []
    if first >= 0: self.firstEvent = first
    if last  >  0: self.nRunEvents = last - self.firstEvent
    i0 = self.firstEvent; iN = i0 + self.nRunEvents; n = self.nSlots
    eventsPerChunk = float(iN-i0)/n
    for k in range(n):
      inputs.append([i0+int(eventsPerChunk*(k)), i0+int(eventsPerChunk*(k+1))])
    if self.verbose >= 2:
      print ' >> Intervals: '
      for i in inputs: print '    ' + i
    return inputs

  def CreateTH1F(self, name, title, nbins, b0, bN = -999):
    ''' Constructor for TH1F '''
    h = TH1F()
    if isinstance(b0, array): h = TH1F(name, title, nbins, b0)
    else:                     h = TH1F(name, title, nbins, b0, bN)
    self.AddToOutputs(h)
    return h

  def CreateTH2F(self, name, title, nbinsX, b0X, bNX, nbinsY, b0Y, bNY):
    ''' Constructor for TH2F '''
    h = TH1F(name, title, nbinsX, b0X, bNX, nbinsY, b0Y, bNY)
    self.AddToOutputs(h)
    return h

  def CreateTH2F(self, name, title, nbinsX, binsX, nbinsY, binsY):
    ''' Constructor for TH2F '''
    h = TH1F(name, title, nbinsX, binsX, nbinsY, binsY)
    self.AddToOutputs(h)
    return h

  def CreateTTree(self, name, title):
    ''' Constructor for a TTree '''
    t = TTree(name, title)
    self.AddToOutputs(t)
    return t

  #############################################################################################
  #############################################################################################
  ### Create and send jobs

  def divideFiles(self): 
    ''' Get a list with initial and final event numbers '''
    listEvents = []
    eventsPerChunk = float(iN)/n
    i0 = 0; iN = self.nEvents; n = self.nSlots
    listEvents.append(int(eventsPerChunk*(k)))
    for k in range(n): listEvents.append(int(eventsPerChunk*(k+1)))
    print listEvents
    return listEvents

  def craftJob(self, n0, nF, index = -1):
    ''' Returns a string with all the info for creating a job '''
    localPath  = os.getcwd() + '/'
    modulname  = self.__class__.__name__
    path       = self.inpath
    filename   = self.fileName
    outpath    = self.outpath
    xsec       = self.xsec
    nSlots     = 1  # One slot per job
    verbose    = 10 # why not
    eventRange = [n0, nF]
    t = 'cd ' + localPath + '\n'
    if 'CMSSW' in localPath: t += 'eval `scramv1 runtime -sh` \n'
    pycom =  'python -c \''
    pycom += 'from ' + modulname + ' import *; '
    pycom += modulname + '(' + '"' + path + '", "' + filename + '", xsec = ' + str(xsec) + ', '
    pycom += 'outpath = "' + outpath + '", nSlots = ' + str(nSlots) + ', eventRange = ' + str(eventRange) + ', '
    pycom += 'run = True, verbose = ' + str(verbose) + ', index = ' + str(index) + ')\''
    return t + pycom

  def sendJobs(self, nJobs = -1, folder = '', queue = '8nm', pretend = False, autorm = False):
    ''' Send jobs '''
    if nJobs != -1: self.SetNSlots(nJobs)
    if folder != '': self.jobFolder = folder
    jm = jobManager(self.outname, self.jobFolder, queue, 1, pretend, autorm)
    inputs = self.getInputs()
    index = 0
    for i in inputs:
      a,z = i
      jm.AddJob(self.craftJob(a,z,index))
      index += 1
    jm.run()


  #############################################################################################
  #############################################################################################
  ### Functions to run the analysis

  def run(self, first = -1, last = -1, nSlots = -1):
    ''' Run the analysis, taking into account the number of slots '''
    if nSlots > 1: print ' Number of slots: ', nSlots
    else: print ' Secuential mode!'
    print ' Cross section: ', self.xsec
    if self.verbose >= 1: GetProcessInfo(self.files)
    if nSlots != -1: self.SetNSlots(nSlots)
    if self.nSlots == 1: self.loop(first, last)
    else:                self.multiloop(first, last)
    self.log()

  def loop(self, ev0 = -1, evN = -1):
    ''' Loop over the events and fill the histograms '''
    self.manageOutput()
    self.createHistos()
    self.init()
    tchain = TChain(self.treeName,self.treeName)
    for f in self.files: tchain.Add(f)
    if isinstance(ev0, list): ev0, evN = ev0
    if ev0 >= 0: self.firstEvent = ev0
    if evN >  0: self.nRunEvents = evN - ev0
    first = self.firstEvent
    last  = self.firstEvent + self.nRunEvents
    for iEv in range(first, last):
      self.printprocess(iEv)
      tchain.GetEntry(iEv)
      self.hRunEvents.Fill(1)
      self.weight = self.xsec*tchain.genWeight/self.nSumOfWeights

      ### Start the analysis here!
      self.insideLoop(tchain)

    self.saveOutput()
    return

  def multiloop(self, first = -1, last = -1):
    ''' Executes the loop with several cores '''
    pass
    inputs = self.getInputs(first, last)
    pool = Pool(self.nSlots)
    for i in range(len(inputs)):
      inputs[i].insert(0, self)
      inputs[i].append(i)
    pool.map(loopAnal, inputs)
    pool.close()
    pool.join()
    return

  def saveOutput(self):
    ''' Creates the out file and save the histos '''
    out = self.outpath + self.outname + '.root'
    if self.index >= 0: out = self.outpath + self.outname + '_' + str(self.index) + '.root'
    if self.verbose >= 1: print ' >> Saving output in: ' + out
    self.out = out
    fout = TFile.Open(out, "recreate")
    for element in self.outputList: element.Write()
    fout.Close()
    return

  #############################################################################################
  #############################################################################################
  ### Functions to be overriden

  def init(self):
    ''' [Override this method!] Executes once, before looping... '''
    pass

  def createHistos(self):
    ''' [Override this method] Create the histos to be filled. 
        You could use the inif function to create the histos '''
    pass

  def insideLoop(self, t):
    ''' [Override this method!] Implement your analysis here. It's executed one per event. '''
    pass
 
  def log(self):
    ''' [Override this method!] Prints a logfile at the end of the loop '''
    pass

  #############################################################################################
  #############################################################################################
  ### Init method

  def __init__(self,fname, fileName = '', xsec = 1, outpath = './temp/', nSlots = 1, eventRange = [], run = False, sendJobs = False, verbose = 1, index = -1):
    # Default values:
    self.inpath = fname
    self.out = ''
    self.outpath = './temp/'
    self.jobFolder = './jobs/'
    self.outname = ''
    self.loadedSF = {}
    self.files = []
    self.outputList = []
    self.nEvents = -1
    self.nGenEvents = -1
    self.nSumOfWeights = -1
    self.isData = False
    self.xsec   = 0
    self.nSlots = 1
    self.index = index
    self.tree = 0
    self.firstEvent = 0
    self.nRunEvents = 0
    self.nEventsPrintOut = 10000
    self.verbose = 1
    self.treeName = 'Events'
    self.SetVerbose(verbose)
    self.fileName = fileName
    if fileName != '': self.SetFiles(fname, fileName)
    else:              self.SetFiles(fname)
    self.SetXsec(xsec)
    self.SetOutDir(outpath)
    self.SetNSlots(nSlots)
    self.SetParams()
    self.hRunEvents = self.CreateTH1F('RunEvents', 'RunEvents', 1, 0, 2)
    if len(eventRange) == 2: 
      n0,nf = eventRange
      self.firstEvent = n0
      self.nRunEvents = nf-n0
    if run: self.run(self.firstEvent, self.firstEvent+self.nRunEvents)
    elif sendJobs: self.sendJobs()

