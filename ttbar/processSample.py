import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ttanalysis import *
from framework.fileReader import getDicFiles, GetAllInfoFromFile

path = '/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/'

xsecdic = {
 'DYJetsToLL_MLL50' : 2055,
 'DYJetsToLL_M_10to50' : 1506,
 'WJetsToLNu' : 21159,
 'ZZTo2L2Nu' : 1,
 'ZZTo4L' : 1,
 'WZTo3LNU' : 0.1258,
 'WWTo2L2Nu' : 0.1858,
 'tW_noFullHad' : 1.629072,
 'tW_noFullHad_ext1' : 1.629072,
 'tbarW_noFullHad' : 1.629072,
 'TT' : 68.9,
 'TTsemilep' : 68.9,
 'TT_hdampUP' : 68.9,
 'TT_hdampDOWN' : 68.9,
 'TT_mtop166p5' : 68.9,
 'TT_mtop178p5' : 68.9,
 'TT_TuneCP5up' : 68.9,
 'TT_TuneCP5down' : 68.9
}

nSlots = 8
doAll = False; doSendJobs = False;
def runSample(sample, dosend,options):
  if not sample in dic:
    print ' << Process \''+sample+'\' not found!'
    exit()

  #for sample in dic:
  nEvents, nGenEvents, nSumOfWeights, isData = GetAllInfoFromFile([path + x for x in dic[sample]])
  thexsec = xsecdic[sample] if not isData else 1
  a = ttanalysis(path, sample, xsec = thexsec)
  a.SetOptions(options)
  a.SetNSlots(nSlots)
  a.SetOutDir('temp')
  if dosend: a.sendJobs()
  else: a.run()

# Get files
dic = getDicFiles(path)
arg = sys.argv[1:]
if len(arg) == 0:
  print ' >> Usage:   python processSample.py [sample] [nSlots (8)] [options]'
  print ' >> Example: python processSample.py TT 6'
  print ' >> Options: --all, --sendJobs, --options'
  exit()

samp = arg[0]
i = 1; options = ''
if len(arg) >= 2: nSlots = int(arg[1])
if len(arg) >= 3:
  for a in arg[2:]:
    i+=1
    if not a[:2] == '--': continue
    if a[2:] == 'all': doAll = True
    if a[2:] == 'sendJobs': doSendJobs = True
    if a[2:] == 'options': options = arg[i+1]
if doAll: 
  for s in xsecdic.keys(): print s #runSample(s,doSendJobs)
else: runSample(samp,doSendJobs,options)

