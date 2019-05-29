'''
 Runs on a mini tree to produce a histogram.
 Works with multiprocessing
 Example:

  fname = '/pool/ciencias/userstorage/juanr/stop/apr2018/Tree_TTbar_Powheg.root'
  myHisto = TH1F('h', '', 8, 0, 8)
  h = xLoop(fname, var = 'TNJets', cut = "TNJets >= 1", weight = "TWeight", treeName = 'tree', nSlots = 8, histo = myHisto)
 
'''

from ROOT import TChain, TH1F
from array import array
from multiprocessing import Pool
import re

def SearchForIndex(expr, words):
  for i in len(words):
    j = i+1
    if j < len(words):
      fir = words[i]
      sec = words[j]
      if sec.isdigit(): 
        cand = fir+'['+sec+']'
        if cand in expr: nw.append(cand)

def EvalExpForEvent(exp, ev):
  words = re.findall(r"[\w']+", exp)
  words = filter(lambda x : not x.isdigit(), words)
  num = [(getattr(ev, x) if hasattr(ev, x) else x) for x in words]
  expv = exp
  for i in range(len(words)):
    w = words[i]
    n = str(num[i])
    expv = expv.replace(w, n)
  return eval(expv)

def xLoop(fileName, var = '', cut = '', weight = '1', treeName = 'Events', nSlots = 1, nbins = 0, bin0 = -1, binN = -1, bins = [], e0 = 0, nEvents = -1, histo = None, iChunk = -1):

  # Read from dictionary
  if isinstance(fileName, dict):
    d = fileName
    fileName = d['fileName']
    var      = d['var']
    cut      = d['cut']
    weight   = d['weight']
    treeName = d['treeName']
    nSlots   = d['nSlots']
    nbins    = d['nbins']
    bin0     = d['bin0']
    binN     = d['binN']
    bins     = d['bins']
    e0       = d['e0']
    nEvents  = d['nEvents']
    histo    = d['histo']
    iChunk   = d['iChunk']

  # Load the TChain
  t = TChain(treeName)
  if ',' in fileName:
    files = fileName.replace(' ', '').split(',')
    for f in files: t.Add(f)
  else: t.Add(fileName)
  nEntries = t.GetEntries()
  if nEvents+e0 > nEntries: nEvents = nEntries-e0
  elif nEvents == -1: nEvents = nEntries
  nEv = -1

  # Multiprocess...
  iN = e0+nEvents
  eventsPerChunk = float(iN-e0)/nSlots
  if nSlots > 1:
    inputs = []
    pool = Pool(nSlots)
    for i in range(nSlots):
      first = e0+int(eventsPerChunk*(i))
      last  = e0+int(eventsPerChunk*(i+1))
      nEv   = last - first
      print 'Chunk %i: [first, last] = [%i, %i]... nEvents = %i'%(i, first, last, nEv)
      impi = {}
      impi['fileName'] = fileName
      impi['var']      = var
      impi['cut']      = cut
      impi['weight']   = weight
      impi['treeName'] = treeName
      impi['nSlots']   = 1
      impi['nbins']    = nbins
      impi['bin0']     = bin0
      impi['binN']     = binN
      impi['bins']     = bins
      impi['e0']       = first
      impi['nEvents']  = nEv
      impi['histo']    = None if histo == None else histo.Clone("histo%i"%i)
      impi['iChunk']   = i
      inputs.append(impi)
    print 'Starting the loop with %i nodes...'%nSlots
    pool.map(xLoop, inputs)
    pool.close()
    pool.join()
    return

  # Prepare the histogram
  if histo == None:
    if bins == []: 
      histo = TH1F('histo', '', nbins, bin0, binN)
    else        : 
      ba = array('f', bins)
      histo = TH1F('histo', '', bins, ba)

  # Print some information
  if iChunk == -1: print 'Starting the loop in event %i... runing on %i events of a total of %i'%(e0, nEvents, nEntries)
  theCut = cut; theVar = var; theWeight = weight
  if iChunk <= 0:
    print ' Variable: %s'%theVar
    print ' Cut     : %s'%theCut
    print ' Weight  : %s'%theWeight

  for iEv in range(e0, nEvents+e0):
    t.GetEntry(iEv)
    if not t.TNBtags >= 1: continue
    nEv += 1
    if iChunk == -1:
      if nEv % 10000 == 0: print "[%i/%i] (%1.2f %s), event %i in tree"%(nEv, nEvents, float(nEv)/float(nEvents), '%', e0+nEv)
    elif iChunk == 0:
      ns = float(nEntries)/float(nEvents)
      if nEv % 10000 == 0: print "[%i/%i] (%1.2f %s)"%(nEv*ns, nEntries, float(nEv)/float(nEvents), '%')
    passCut = EvalExpForEvent(theCut,    t)
    val     = EvalExpForEvent(theVar,    t)
    weight  = EvalExpForEvent(theWeight, t)
    if passCut: histo.Fill(val, weight)
    if nEv >= nEvents: break
  return histo

#fname = '/pool/ciencias/userstorage/juanr/stop/apr2018/Tree_TTbar_Powheg.root'
#histo = TH1F('h', '', 8, 0, 8)
#h = xLoop(fname, var = 'TNJets', cut = "TNJets >= 1", weight = "TWeight", treeName = 'tree', nSlots = 8, nEvents = -1, e0 = 0, histo = histo)
#h.Draw()


class Loop:
  ''' Class to obtain several histograms from files and miniTrees '''
  def SetPath(self, p):
    if not p.endswith('/'): p += '/'
    self.path = p

  def AddProcess(self, files, pr, color = 1):
    self.process[pr]['files'] = files
    self.process[pr]['histo'] = None
    self.process[pr]['color'] = color
    self.process[pr]['name']  = pr
  
  def SetNslots(self, n):
    self.nslots = n

  def SetVar(self, v):
    self.var = v

  def SetWeight(self, w):
    self.weight = w

  def SetCut(self, c):
    self.cut = c

  def SetTreeName(self, n):
    self.treeName = n

  def SetHisto(self, h, nbins = 0, b0 = 0, bN = 0, bins = []):
    if nibins != 0:
      if len(bins) > 0:
        ba = array('f', bins)
        h = TH1F(h, '', nbins, bins)
      else:
        h = TH1F(h, '', nbins, b0, bN)
    else:
      self.histo = h

  def GetHistoCopy(self, newName = 'copyhisto'):
    hn = self.histo.Clone(newName)
    return hn

  def Loop(self):
    for pr in self.process.values():
      print 'Looping on sample %s' pr['name']
      pr['histo'] = xLoop(pr['files'], self.var, self.cut, self.weight, self.treeName, self.nslots, histo = self.GetHistoCopy('h'+pr['name'])
      pr['histo'].SetFillColor(pr['color'])
      pr['histo'].SetFillStyle(1001)
      pr['histo'].SetStats(0)

  def GetProcess(self, pr):
    return self.process[pr]

  def GetHisto(self, pr):
    return GetProcess(pr)['histo']

  def __init__(self, path, var = '', cut = '', weight = '', treeName = 'Events', nSlots = 1, nbins = 1, bin0 = 0, bin1 = 1, bins = [], histo = None):
    self.SetPath(path)
    self.SetVar(var)
    self.SetCut(cut)
    self.SetWeight(weight)
    self.SetTreeName(treeName)
    self.SetNslots(nSlots)
    if histo != None: self.SetHisto(histo)
    else:             self.SetHisto('histo', nbins, bin0, binN, bins)

