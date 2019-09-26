import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

######################################################################################
### Plots

hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi = Lumi)
doParallel = True

def Draw(name = 'Lep0Pt_eee_lep', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 2, tag = False):
  if doParallel:
    return "Draw(%s, %i, \'%s\', \'%s\', %s, \'%s\', %s, %i, %s)"%("\'" + name + "\'" if type(name) == str else "[\'"+ "\',\'".join(name) + "\']" , rebin, xtit, ytit, "True" if doStackOverflow else "False", binlabels, "True" if setLogY else "False", maxscale, "False" if not(tag) else tag)

  s = Stack(outpath=outpath, doRatio = False)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.61, texlumiY = 0.96, texlumiS = 0.05)
  s.SetTextCMSmode(y = 0.865, s = 0.052)
  s.SetTextCMS(y = 0.87, s = 0.06)
  hm.SetStackOverflow(doStackOverflow)
  hm.SetHisto(name, rebin)
  s.SetHistosFromMH(hm)
  if tag == False:
    tag = name if type(name) == str else name[0]
    if type(name) == type([]):
      tag = tag.replace("eee","all").replace("emm","all").replace("mee","all").replace("mmm","all")
  s.SetOutName(tag)
  s.SetBinLabels(binlabels)
  s.SetTextChan('')
  s.SetRatioMin(2-maxscale)
  s.SetRatioMax(maxscale)
  s.SetTextChan('')
  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.SetXtitle(size = 0.05, offset = 0.8, nDiv = 510, labSize = 0.04)
  s.SetYtitle(labSize = 0.04)
  s.DrawStack(xtit, ytit)
  return 1

joblist = []
#lev = 'met' #lep, met
for lev in ['lep', 'wpt','m3l']:
  for ch in ['eee','mee','emm','mmm','All']:
 #joblist.append(Draw(GetAllCh('htmiss', lev), 1, 'H_{T}^{miss} (GeV)', 'Events / 5 GeV')
    if ch == 'All':
      joblist.append(Draw(GetAllCh('MET', lev), 1, 'p_{T}^{miss} (GeV)', 'Events / 5 GeV'))
      joblist.append(Draw(GetAllCh('m3l', lev), 1, 'm_{3l} (GeV)',      'Events / 10 GeV'))
      joblist.append(Draw(GetAllCh('mtw',lev), 1, 'm_{T}^{W} (GeV)',    'Events / 10 GeV'))
      joblist.append(Draw(GetAllCh('mz', lev), 1, 'm_{Z} (GeV)',        'Events / 10 GeV'))
      joblist.append(Draw(GetAllCh('LepWPt', lev), 1, 'p_{T}(lepW)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetAllCh('LepWEta', lev), 1, '#eta (lepW)', 'Events'))
      joblist.append(Draw(GetAllCh('LepWPhi', lev), 1, '#phi (lepW) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetAllCh('LepZ0Pt', lev), 1, 'p_{T}(lep0Z)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetAllCh('LepZ0Eta', lev), 1, '#eta (lep0Z)', 'Events'))
      joblist.append(Draw(GetAllCh('LepZ0Phi', lev), 1, '#phi (lep0Z) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetAllCh('LepZ1Pt', lev), 1, 'p_{T}(lep1Z)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetAllCh('LepZ1Eta', lev), 1, '#eta (lep1Z)', 'Events'))
      joblist.append(Draw(GetAllCh('LepZ1Phi', lev), 1, '#phi (lep1Z) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetAllCh('TrilepPt', lev), 1, 'Trilep p_{T} (GeV)', 'Events'))
      joblist.append(Draw(GetAllCh('ZPt', lev),  1, 'Z p_{T} (GeV)', 'Events'))
      joblist.append(Draw(GetAllCh('MaxDeltaPhi', lev), 1, 'max(#Delta#phi (ll)) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetAllCh('NJets', lev), 1, 'Jet multiplicity', 'Events', True))
    else:
      joblist.append(Draw(GetName('MET',ch, lev), 1, 'p_{T}^{miss} (GeV)', 'Events / 5 GeV'))
      joblist.append(Draw(GetName('m3l',ch, lev), 1, 'm_{3l} (GeV)',      'Events / 10 GeV'))
      joblist.append(Draw(GetName('mtw',ch, lev), 1, 'm_{T}^{W} (GeV)',    'Events'))
      joblist.append(Draw(GetName('mz',ch, lev), 1, 'm_{Z} (GeV)',        'Events / 10 GeV'))
      joblist.append(Draw(GetName('LepWPt',ch, lev), 1, 'p_{T}(lepW)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetName('LepWEta',ch, lev), 1, '#eta (lepW)', 'Events'))
      joblist.append(Draw(GetName('LepWPhi',ch, lev), 1, '#phi (lepW) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetName('LepZ0Pt',ch, lev), 1, 'p_{T}(lep0Z)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetName('LepZ0Eta',ch, lev), 1, '#eta (lep0Z)', 'Events'))
      joblist.append(Draw(GetName('LepZ0Phi',ch, lev), 1, '#phi (lep0Z) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetName('LepZ1Pt',ch, lev), 1, 'p_{T}(lep1Z)  (GeV)', 'Events / 40 GeV'))
      joblist.append(Draw(GetName('LepZ1Eta',ch, lev), 1, '#eta (lep1Z)', 'Events'))
      joblist.append(Draw(GetName('LepZ1Phi',ch, lev), 1, '#phi (lep1Z) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetName('TrilepPt',ch, lev), 1, 'Trilep p_{T} (GeV)', 'Events'))
      joblist.append(Draw(GetName('ZPt',ch, lev),  1, 'Z p_{T} (GeV)', 'Events'))
      joblist.append(Draw(GetName('MaxDeltaPhi',ch, lev), 1, 'max(#Delta#phi (ll)) (rad/#pi)', 'Events'))
      joblist.append(Draw(GetName('NJets',ch, lev), 1, 'Jet multiplicity', 'Events', True))

if doParallel:
  from multiprocessing import Pool
  from contextlib import closing
  import time
  doParallel = False
  def execute(com):
    eval(com)

  with closing(Pool(8)) as p:
    print "Now running " + str(len(joblist)) + " commands using: " + str(8) + " processes. Please wait" 
    retlist1 = p.map_async(execute, joblist, 1)
    while not retlist1.ready():
      print("Plots left: {}".format(retlist1._number_left ))
      time.sleep(1)
    retlist1 = retlist1.get()
    p.close()
    p.join()
    p.terminate()
