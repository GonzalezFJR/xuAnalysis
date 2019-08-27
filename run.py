'''
  Example: 
  python run.py tt -p /pool/ciencias/userstorage/juanr/nanoAODv4/2017/ -s TTTo2L2Nu
  python run.py 2017.cfg
'''

doSendPath = True

# Check if ROOT and PAF is loaded...
import imp, os, sys, time
try:
    imp.find_module('ROOT')
    found = True
except ImportError:
  print 'Please, load ROOT... (typically by executing \'root6\')'
  exit()

from ROOT import gROOT
gROOT.SetBatch(1)

from framework.fileReader import getDicFiles, GetAllInfoFromFile, IsVarInTree, GuessIsData

def ex(command, verbose = False, pretend = False):
  if verbose:
    print 'Executing command: ', command
  if pretend: 
    print 'Pretending...'
    return
  os.system(command)

def loadxsecdic(fname, verbose):
  xsecdir = {}
  if not os.path.isfile('./'+fname):
    l = filter(lambda x: x[0] == fname, [x.split('.') for x in os.listdir('.')])
    if len(l) == 0:
      print 'ERROR: not found file %s with cross sections...'
      return
    else: l = l[0]
    fname = l[0] + '.' + l[1]
  if verbose: print ' >> Reading cross section from %s...'%fname
  f = open(fname)
  lines = f.readlines()
  for l in lines:
    l = l.replace(' ', '')
    l = l.replace('\n', '')
    if l.startswith('#'): continue
    if not ':' in l: continue
    if '#' in l: l = l.split('#')[0]
    if l == '': continue
    lst = l.split(':')
    key = lst[0]
    val = lst[1]
    if val == '': val = 1
    xsecdir[key] = float(val)
  return xsecdir 

def GetXsec(xsec, s, verbose, isdata):
  if isdata: return 1
  if isinstance(xsec, int): xsec = float(xsec)
  if isinstance(xsec, str):
    xsecdic = loadxsecdic(xsec, verbose)
    if not s in xsecdic.keys():
      print 'ERROR: not found xsec value for sample %s'%s
      xsec = 1
    else: xsec = xsecdic[s]
  return xsec

def GetSampleList(path, sample):
  dic = getDicFiles(path)
  nfileInPath = len(dic)
  if verbose: print 'Found %i files in path %s'%(nfileInPath, path)

  samples = []
  for s in sample:
    dk = dic.keys()
    if not s in dk: s = prefix+'_'+s
    if not s in dk:
      print 'WARNING: file %s not in path %s'%(s, path)
    else:
      samples += dic[s]
  return samples

def GetOptions(path, sample, options = ""):
  if not path.endswith('/'): path += '/'
  if not sample.endswith(".root"): sample += '.root'
  doPUweight  = 'PUweight,' if IsVarInTree(path+sample, 'puWeight') else ''
  doJECunc    = 'JECunc,'   if IsVarInTree(path+sample, 'Jet_pt_jesTotalUp') else ''
  useJetPtNom = 'JetPtNom,' if IsVarInTree(path+sample, 'Jet_pt_nom') else ''
  options += doPUweight + doJECunc + useJetPtNom + useLepGood + options
  if options.endswith(','): options = options[:-1]
  return options

def GetTStringVectorSamples(path, samples):
  from ROOT import vector, TString, gSystem
  # Add the input data files
  v = vector(TString)()
  for s in samples: 
    t = TString(path+s)
    v.push_back(t)
  return v
  v = GetTStringVector(samples)


def RunSample(selection, path, sample, year = 2018, xsec = 1, nSlots = 1, outname = '', outpath = '', options = '', nEvents = 0, FirstEvent = 0, prefix = 'Tree', verbose = 0, pretend = False, dotest = False, sendJobs = False, queu = 'short', treeName = 'Events'):

  if dotest:
    nEvents  = 1000
    nSlots   = 1
    sendJobs = False
  if isinstance(sample, str) and ',' in sample: sample = sample.replace(' ','').split(',')
  sap = sample if not isinstance(sample, list) else sample[0]
  gs = filter(lambda x : os.path.isfile(x), [path + sap + '_0.root', path + 'Tree_' + sap + '_0.root'])
  if len(gs) == 0: print 'ERROR: file %s not found in %s'%(sap, path)
  isData = GuessIsData(gs[0])
  
  xsec = GetXsec(xsec, outname, verbose, isData) if not dotest else 1

  selecModul = __import__('%s.%s'%(selection,selection))
  modul = getattr(selecModul, selection)
  analysis = getattr(modul, selection)
  evRang = []
  if nEvents != 0: evRang = [FirstEvent, nEvents]
  an = analysis(path, sample, eventRange = evRang, xsec = xsec, nSlots = nSlots, options = options, verbose=verbose, treeName = treeName)
  an.SetOutDir(outpath)
  an.SetOutName(outname)

  if sendJobs: 
    print '>> Sending jobs...'
    if pretend:
      print 'Pretending...'
      return
    out = an.sendJobs(queue=queue, pretend=pretend)
  else:
    print ' >> Running sample %s...'%sample
    if pretend:
      print 'Pretending...'
      return
    out = an.run()
  return out


def main(ocfgfile = ''): 
  selection = ocfgfile
  ################################################################################
  ### Execute
  ################################################################################
  import argparse
  out = {}
  parser = argparse.ArgumentParser(description='Run xuAnalysis')
  if ocfgfile == '':
    parser.add_argument('selection'         , default=''         , help = 'Name of the selector')
  parser.add_argument('--pretend','-p'    , action='store_true'  , help = 'Create the files but not send the jobs')
  parser.add_argument('--test','-t'       , action='store_true'  , help = 'Sends only one or two jobs, as a test')
  parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')
  parser.add_argument('--verbose','-v'    , default=0            , help = 'Activate the verbosing')
  parser.add_argument('--path'            , default=''           , help = 'Path to look for nanoAOD')
  parser.add_argument('--sample','-s'     , default=''           , help = 'Sample(s) to process')
  parser.add_argument('--xsec','-x'       , default='xsec'       , help = 'Cross section')
  parser.add_argument('--year','-y'       , default=-1           , help = 'Year')
  parser.add_argument('--conf','-c'       , default=''           , help = 'Config file (not yet implemented')
  parser.add_argument('--options','-o'    , default=''           , help = 'Options to pass to your analysis')
  parser.add_argument('--prefix'          , default='Tree'       , help = 'Prefix of the name...')
  parser.add_argument('--outname'         , default=''           , help = 'Name of the output file')
  parser.add_argument('--outpath'         , default=''           , help = 'Output path')
  parser.add_argument('--queue','-q'      , default='short'      , help = 'Queue to send jobs')
  parser.add_argument('--firstEvent'      , default=0            , help = 'First event')
  parser.add_argument('--nEvents'         , default=0            , help = 'Number of events')
  parser.add_argument('--nSlots','-n'     , default=-1           , help = 'Number of slots')
  parser.add_argument('--treeName'        , default='Events'     , help = 'Name of the tree')

  args = parser.parse_args()
  if hasattr(args, 'selection'): selection   = args.selection
  if selection == '': return
  verbose     = args.verbose
  pretend     = args.pretend
  dotest      = args.test
  sample      = args.sample
  path        = args.path
  options     = args.options
  xsec        = args.xsec
  year        = args.year
  prefix      = args.prefix
  outname     = args.outname
  outpath     = args.outpath
  nEvents     = int(args.nEvents)
  nSlots      = int(args.nSlots)
  FirstEvent  = int(args.firstEvent)
  sendJobs    = int(args.sendJobs)
  queue       = args.queue
  treeName    = args.treeName

  aarg = sys.argv
  ncores = nSlots
  
  # Check if a cfg file is given as first argument
  fname = selection
  if not os.path.isfile('./'+fname):
    l = filter(lambda x: x[0] == fname, [x.split('.') for x in os.listdir('.')])
    if len(l) != 0: 
      l = l[0]
      fname = l[0] + '.' + l[1]
  print '>> fname = ', fname
  if os.path.isfile(fname):
    if verbose: print ' >> Using config file \'%s\'...'%fname
    selection = ''
    spl = []
    samplefiles = {}
    nslots = {}
    f = open(fname)
    lines = f.readlines()
    for l in lines:
      l = l.replace(' ', '')
      l = l.replace('\n', '')
      if l.startswith('#'): continue
      if '#' in l: l = l.split('#')[0]
      if l == '': continue
      if l.endswith(':'): l = l[:-1]
      if not ':' in l: 
        #if   l == 'verbose': verbose = 1
        if   l == 'pretend': pretend = 1
        elif l == 'test'   : dotest  = 1
        elif l in ['path', 'sample', 'options', 'selection', 'xsec', 'prefix', 'outpath', 'year', 'nSlots', 'nEvents', 'firstEvent', 'queue']: continue
        else:
          spl.append(l)
          samplefiles[l]=l
          nslots[l]=nSlots
      else:
        lst = l.split(':')
        key = lst[0]
        val = lst[1] if lst[1] != '' else lst[0]
        if   key == 'pretend'   : pretend   = 1
        elif key == 'verbose'   : verbose   = int(val) if val.isdigit() else 1
        elif key == 'test'      : dotest    = 1
        elif key == 'path'      : path      = val
        elif key == 'sample'    : sample    = val
        elif key == 'options'   : options   = val
        elif key == 'selection' : selection = val
        elif key == 'xsec'      : xsec      = val
        elif key == 'prefix'    : prefix    = val
        elif key == 'outpath'   : outpath   = val
        elif key == 'queue'     : queue     = val
        elif key == 'year'      : year      = int(val)
        elif key == 'nSlots'    : nSlots    = int(val)
        elif key == 'nEvents'   : nEvents   = int(val)
        elif key == 'firstEvent': FirstEvent= int(val)
        elif key == 'treeName'  : treeName  = val
        else:
          ncor = nSlots if len(lst) < 3 else int(lst[2])
          spl.append(key)
          samplefiles[key] = val
          nslots[key] = ncor
  
    # Re-assign arguments...
    if '--pretend' in aarg or '-p' in aarg : pretend     = args.pretend
    if '--test'    in aarg or '-t' in aarg : dotest      = args.test
    if '--sendJobs'in aarg or '-j' in aarg : sendJobs    = args.sendJobs
    if args.path       != ''       : path        = args.path
    if args.options    != ''       : options     = args.options
    if args.xsec       != 'xsec'   : xsec        = args.xsec
    if args.year       != -1       : year        = args.year
    if args.prefix     != 'Tree'   : prefix      = args.prefix
    if args.outname    != ''       : outname     = args.outname
    if args.outpath    != ''       : outpath     = args.outpath
    if args.nEvents    != 0        : nEvents     = int(args.nEvents)
    if args.firstEvent != 0        : FirstEvent  = int(args.firstEvent)
    if args.queue      != 0        : queue       = args.queue
    if args.treeName   != 'Events' : treeName    = args.treeName
    if args.verbose    != 0        : verbose     = int(args.verbose)
  
    if args.nSlots     != -1: 
      nSlots      = int(args.nSlots)
      for k in nslots.keys(): nslots[k] = nSlots
    elif nSlots == -1: 
      nSlots = 1
  
    if args.sample     != '': 
      sample = args.sample
      if not sample in samplefiles.keys():
        print 'WARNING: Sample \'%s\' not found in cfg file!!'%sample
        samplefiles[sample] = sample
        nslots[sample] = nSlots
      spl = [sample]
  
    if dotest:
      nEvents = 1000
      queue = 'cpupower'
      spl = spl[0:1]
      nslots[spl[0]] = 1
      #samplefiles[spl[0]] = [samplefiles[spl[0]][0]]
      outname = 'test'
  
    for sname in spl:
      outname = sname
      sample  = samplefiles[sname]
      ncores  = nslots[sname]
      out[outname] = RunSample(selection, path, sample, year, xsec, ncores, outname, outpath, options, nEvents, FirstEvent, prefix, verbose, pretend, dotest, sendJobs, queue, treeName)
  
  else: # no config file...
    out[outname] = RunSample(selection, path, sample, year, xsec, nSlots, outname, outpath, options, nEvents, FirstEvent, prefix, verbose, pretend, dotest, sendJobs, queue, treeName)
  return out

if __name__ == '__main__':
  main()

