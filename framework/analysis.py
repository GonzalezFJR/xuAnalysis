from ROOT import *
from ROOT.TMath import Sqrt as sqrt
from fileReader import *
from jobManager import *
from multiprocessing import Pool
from array import array
from copy import deepcopy
from functions import *

def loopAnal(listOfInputs): 
  ''' External function to run de loop... needed for the multiprocessing ''' 
  anal, i0, iN, k = listOfInputs
  analcopy = deepcopy(anal) 
  analcopy.SetIndex(k)
  analcopy.SetVerbose(0)
  analcopy.SetNSlots(1)
  analcopy.loop(i0, iN)

class analysis:

  #############################################################################################
  #############################################################################################
  ### Getting inputs

  def AddInput(self, name, Object):
    ''' Add an input to the dictionaty '''
    self.inputs[name] = Object

  def LoadHisto(self, name, fname, hname):
    ''' Open file "fname" and gets the histo "hname" '''
    if self.index <= 0: print ' >> Getting histogram "' + hname + '" in file "' + fname +'"'
    if not os.path.isfile(fname):
      print 'ERROR: file not found'
      return
    f = TFile.Open(fname)
    h = f.Get(hname)
    h.SetDirectory(0)
    self.AddInput(name, h)

  def GetSF(self, name, var1, var2 = ''):
    ''' Get SF from an input hitogram '''
    nx = self.inputs[name].GetNbinsX()
    maxx   = self.inputs[name].GetXaxis().GetBinUpEdge(nx)
    maxxm1 = self.inputs[name].GetXaxis().GetBinUpEdge(nx-1)
    if var1 > maxx: var1 = (maxx+maxxm1)/2
    if var2 != '':
      ny     = self.inputs[name].GetNbinsY()
      maxy   = self.inputs[name].GetYaxis().GetBinUpEdge(ny)
      maxym1 = self.inputs[name].GetYaxis().GetBinUpEdge(ny-1)
      if var2 > maxy: var2 = (maxy+maxym1)/2
    ibin = self.inputs[name].FindBin(var1) if var2 == '' else self.inputs[name].FindBin(var1, var2, 1)
    return self.inputs[name].GetBinContent(ibin)

  def GetSFerr(self, name, var1, var2 = ''):
    ''' Get SF error from an input hitogram '''
    nx = self.inputs[name].GetNbinsX()
    maxx   = self.inputs[name].GetXaxis().GetBinUpEdge(nx)
    maxxm1 = self.inputs[name].GetXaxis().GetBinUpEdge(nx-1)
    if var1 > maxx: var1 = (maxx+maxxm1)/2
    if var2 != '':
      ny     = self.inputs[name].GetNbinsY()
      maxy   = self.inputs[name].GetYaxis().GetBinUpEdge(ny)
      maxym1 = self.inputs[name].GetYaxis().GetBinUpEdge(ny-1)
      if var2 > maxy: var2 = (maxy+maxym1)/2
    ibin = self.inputs[name].FindBin(var1) if var2 == '' else self.inputs[name].FindBin(var1, var2, 1)
    return self.inputs[name].GetBinError(ibin)

  def GetSFandErr(self, name, var1, var2 = ''):
    ''' Get SF and SF error from an input hitogram '''
    if ',' in name: return self.GetSFandErr([x.replace(' ', '') for x in name.split(',')], var1, var2)
    if isinstance(name, list):
      s = 1; e = 0
      for n in name:
        sf, err = self.GetSFandErr(n, var1, var2)
        s *= sf; e += err*err
      return s, sqrt(e)
    nx = self.inputs[name].GetNbinsX()
    maxx   = self.inputs[name].GetXaxis().GetBinUpEdge(nx)
    maxxm1 = self.inputs[name].GetXaxis().GetBinUpEdge(nx-1)
    if var1 > maxx: var1 = (maxx+maxxm1)/2
    if var2 != '':
      ny     = self.inputs[name].GetNbinsY()
      maxy   = self.inputs[name].GetYaxis().GetBinUpEdge(ny)
      maxym1 = self.inputs[name].GetYaxis().GetBinUpEdge(ny-1)
      if var2 > maxy: var2 = (maxy+maxym1)/2
    ibin = self.inputs[name].FindBin(var1) if var2 == '' else self.inputs[name].FindBin(var1, var2, 1)
    sf    = self.inputs[name].GetBinContent(ibin)
    sferr = self.inputs[name].GetBinError(ibin)
    return sf, sferr



  #############################################################################################
  #############################################################################################
  ### Setting funcitons

  def SetFiles(self, path, fname = '', j = -1):
    ''' Search and store the files '''
    if fname == '':
      if isinstance(path, list):
        self.files = path
        return
      else: print '[ERROR] Wrong input'
    else:
      self.files = GetFiles(path, fname, self.verbose >= 2)# if j == -1 else [GetFiles(path, fname, self.verbose >= 2)[j]]
    if len(self.files) == 0: exit()
    ### Set sample name
    path, sample, n = guessPathAndName(self.files[0])
    self.sampleName = sample

  def SetOptions(self, op):
    ''' Set options '''
    self.options = op

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

  def AddToOutputs(self, name, a):
    ''' Add an object to the output list '''
    self.obj[name] = a

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

  def GetFiles(self):
    ''' Retuns the list of files '''
    return self.files

  def manageOutput(self):
    ''' Checks if output existis and creates output dir '''
    out = self.outpath + self.outname + '.root'
    if self.index >= 0: out = self.outpath + self.outname + '_' + str(self.index) + '.root'
    if not os.path.isdir(self.outpath):
      if self.index <= 0:
        print ' >> Creating output directory: ' + self.outpath
        os.mkdir(self.outpath)
    elif os.path.isfile(out):
      print ' >> WARNING: output \'%s\' already existis... it will be overwritten!!'%out

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

  def GetOptions(self):
    ''' Returns the options '''
    return self.options

  def CreateTH1F(self, name, title, nbins, b0, bN = -999):
    ''' Constructor for TH1F '''
    h = TH1F()
    h.Sumw2()
    if isinstance(b0, array): h = TH1F(name, title, nbins, b0)
    else:                     h = TH1F(name, title, nbins, b0, bN)
    self.AddToOutputs(name,h)
    return h

  def CreateTH1D(self, name, title, nbins, b0, bN = -999):
    ''' Constructor for TH1F '''
    h = TH1D()
    h.Sumw2()
    if isinstance(b0, array): h = TH1D(name, title, nbins, b0)
    else:                     h = TH1D(name, title, nbins, b0, bN)
    self.AddToOutputs(name,h)
    return h

  def CreateTH2F(self, name, title, nbinsX, b0X, bNX, nbinsY, b0Y, bNY):
    ''' Constructor for TH2F '''
    h = TH1F(name, title, nbinsX, b0X, bNX, nbinsY, b0Y, bNY)
    self.AddToOutputs(name,h)
    return h

  def CreateTH2F(self, name, title, nbinsX, binsX, nbinsY, binsY):
    ''' Constructor for TH2F '''
    h = TH1F(name, title, nbinsX, binsX, nbinsY, binsY)
    self.AddToOutputs(name,h)
    return h

  def CreateTTree(self, name, title):
    ''' Constructor for a TTree '''
    t = TTree(name, title)
    self.AddToOutputs(name,t)
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
    pycom += 'outpath = "' + outpath + '", nSlots = ' + str(nSlots) + ', eventRange = [' + '%7i,%7i'%(n0,nF) + '], '
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
    if nSlots != -1: self.SetNSlots(nSlots)
    if self.nSlots > 1: print '[INFO] Number of slots: ', self.nSlots
    elif self.index == -1: print '[INFO] Secuential mode!'
    print '[INFO] Cross section: ', self.xsec
    if self.options != '': print '[INFO] Options = ', self.options
    if self.verbose >= 1: GetProcessInfo(self.files)
    if self.nSlots == 1: self.loop(first, last)
    else:                self.multiloop(first, last)
    self.log()

  def loop(self, ev0 = -1, evN = -1):
    ''' Loop over the events and fill the histograms '''
    self.manageOutput()
    self.tchain = TChain(self.treeName,self.treeName)
    for f in self.files: self.tchain.Add(f)
    self.init()
    self.createHistos()
    if self.index <= 0:
      self.CreateTH1F("nGenEvents", "", 1, 0, 2)
      self.CreateTH1F("hxsec",       "", 1, 0, 2)
      self.obj['nGenEvents'].SetBinContent(1,self.nGenEvents)
      self.obj['hxsec'].SetBinContent(1,self.xsec)
    if isinstance(ev0, list): ev0, evN = ev0
    if ev0 >= 0: self.firstEvent = ev0
    if evN >  0: self.nRunEvents = evN - ev0
    first = self.firstEvent
    last  = self.firstEvent + self.nRunEvents
    if self.verbose >= 1: 
      print '[INFO] Loaded %i inputs'%len(self.inputs)
      print '[INFO] Created %i outputs'%len(self.obj)
    for iEv in range(first, last):
      self.printprocess(iEv)
      self.tchain.GetEntry(iEv)
      self.hRunEvents.Fill(1)
      if not self.isData: self.EventWeight = self.xsec*self.tchain.genWeight/self.nSumOfWeights
      else: self.EventWeight = 1

      ### Start the analysis here!
      self.insideLoop(self.tchain)

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
    for element in self.obj: self.obj[element].Write()
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
        You could use the init function to create the histos '''
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

  def __init__(self,fname, fileName = '', xsec = 1, outpath = './temp/', nSlots = 1, eventRange = [], run = False, sendJobs = False, verbose = 1, index = -1, options = '', chooseFile = -1):
    # Default values:
    self.inpath = fname
    self.out = ''
    self.outpath = './temp/'
    self.jobFolder = './jobs/'
    self.outname = ''
    self.files = []
    self.obj = {}
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
    self.inputs = {}
    self.SetOptions(options)
    if fileName != '': self.SetFiles(fname, fileName, chooseFile)
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
    

