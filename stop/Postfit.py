import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp, HistoUnc, GetRatioHistoUncFromHisto
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas, TFile
gROOT.SetBatch(1)

# if ch == 'all', if year == 'comb'
doStack = True
doPlotSyst = False
ch= 'emu' #'mumu'
year ='comb'#2016
ms = 245
ml =  100
region = 'SR' #'ttmt2'
syst = 'ElecES, MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, hdamp, UE, PU, JESCor, JESUnCor, mtop, ISR, FSR, MisTag, nongauss, PDF, Scale, ISR, FSR' # MisTag, Pref

#path[year] = pathToTrees(year, chan, region)

if region == 'BS': 
  syst = 'MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, PU, JESCor, JESUnCor, MisTag'#, ISR, FSR' # MisTag, Pref
  if year != 2016 and year != 'comb': syst += ',ISR, FSR'
if year != 2018 and year != 'comb': syst += ', Pref'
#bkg = ['Nonprompt', 'ttZ', 'Others', 'tW']
bkg = ['VV', 'ttW', 'Nonprompt', 'ttZ', 'DY', 'tW']
#path = '../stop_v6testPU/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
#path = '../stop_v6Mod/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
folder = '15jun/'
GetPath = lambda region, year, ms, ml, ch : baseoutpath+'/Unc/%s/%s/%s/mass%i_%i/'%(region, ch, str(year), ms, ml)
webpath  = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/unblind/15jun/'
GetOutpath = lambda region, year, ms, ml, ch : webpath+'/PostFit/'+folder#%(region, ch, str(year))#, ms, ml)
path    = GetPath(region,year, ms, ml,ch)
outpath = GetOutpath(region,year, ms, ml,ch)

chdic = {
  2016 : {'ee':'ch1', 'mumu':'ch2', 'emu':'ch3'},
  2017 : {'ee':'ch4', 'mumu':'ch5', 'emu':'ch6'},
  2018 : {'ee':'ch7', 'mumu':'ch8', 'emu':'ch9'},
}


pathToPostFit = '/nfs/fanae/user/juanr/CMSSW_10_2_13/src/stoplimits/results/'+folder
def DrawPostFit(ms=235, ml=60, htype='fit_s', var='dnn', ch='', year=''):
  getdir = lambda dirtype, ch : 'shapes_%s/%s/'%(dirtype, ch)
  getfname = lambda ms, ml : 'postfit_%s_%s_%s'%(var, str(ms), str(ml))

  # Get channels
  if not isinstance(ch, list):
    if ch == '': ch = ['ee', 'mumu', 'emu'] 
    elif ',' in ch: ch = ch.replace(' ', '').split(',')
    else: ch = [ch]
  if not isinstance(year, list):
    if year == '': year = [2016, 2017, 2018]
    elif isinstance(year, str) and ',' in year: year = year.replace(' ', '').split(',')
    else: year = [year]
  pch = [];
  for y in year:
    for c in ch:
      pch.append(chdic[y][c])

  if len(year) == 3: yearname = 'comb'
  else             : yearname = str(year[0])
  if len(ch  ) == 3: chname   = 'all'
  else             : chname   = ch[0]

  # test or not depending on var
  ttname = 'tt' if not 'dnn' in var else 'tt_test'
  pr = bkg + [ttname]
  sig = ('stop' if not 'dnn' in var else 'stop_test') if htype!='fit_b' else []

  hm = HistoManager(pr, '', path=pathToPostFit, signalList = sig)
  pathInTree = [getdir(htype, x) for x in pch]
  hm.SetPathInTree(pathInTree)
  hm.ReadHistosFromFile(getfname(ms,ml), dataname='data',rebin=1)
  hm.ReArrangeDic({'Others' : ['ttW', 'ttZ', 'Nonprompt', 'VV'], 't#bar{t}+tW':['tW', ttname], 'Drell-Yan':['DY']})
  hm.GetDataHisto()
  #hm.indic['data_obs']['data_obs'] = hm.GetSumBkg()
  outdir = GetOutpath(region, year, ms, ml, ch)
  fprocess = ['Others', 'Drell-Yan', 't#bar{t}+tW'] 
  s = Stack(outpath=outdir+'/postfit/')
  colors['Others'] = kTeal+2
  colors['t#bar{t}+tW'] = colors['tt']
  colors['Drell-Yan'] = colors['DY']
  s.SetColors(colors)
  s.SetProcesses(fprocess)
  s.SetLumi(GetLumi(year[0]) if len(year)==1 else (GetLumi(2016) + GetLumi(2017) + GetLumi(2018)) )
  outname = htype+'_'+var+'%s_%s_%i_%i'%(yearname, chname, ms,ml)
  s.SetOutName(outname)
  s.SetHistosFromMH(hm)
  #s.Set
  t = TopHistoReader(pathToPostFit)
  t.ReComputeStatUnc = False
  t.SetPathInTree(pathInTree)
  hbkg = t.GetNamedHisto('total_background', getfname(ms,ml))
  hbkg.SetLineStyle(0); hbkg.SetLineWidth(0); hbkg.SetMarkerSize(0);

  s.SetTotMC(hbkg)
  s.SetMCunc(hbkg)
  s.SetMCstatUnc(None)
  s.SetMCnormUnc(None)

  s.SetRatioStatUnc(None)
  s.SetRatioNormUnc(None)
  s.SetRatioUnc(GetRatioHistoUncFromHisto(hbkg))

  s.SetRatioUncStyle()
  s.SetUncStyle()

  if sig!=[]: s.AddSignalHisto(hm.indic[sig][sig], color = kViolet+2, mode = 'ontop', ratioBkg = True, name='stop')
  s.SetTextChan('SR: BS + p_{T}^{miss} #geq 50, m_{T2} #geq 80')
  s.SetRatioMin(0.5); s.SetRatioMax(1.5)
  s.SetPlotMaxScale(1.8)
  xtit = 'DNN score (%i, %i)'%(ms, ml)
  chlab = ''
  if   chname == 'ee'  : chlab = 'ee'
  elif chname == 'mumu': chlab = '#mu#mu'
  elif chname == 'emu' : chlab = 'e#mu'
  flab = 'Prefit' 
  if   htype == 'fit_b': flab = 'Fit background only'
  elif htype == 'fit_s': flab = 'Fit S+B'
  mlab = '#splitline{m_{#tilde{t}_{1}} = %1.0f GeV}{m_{#tilde{#chi}_{1}^{0}} = %1.0f GeV}'%(ms, ml)
  s.AddTex(flab,  x=0.15, y=0.77, s=0.05)
  s.AddTex(mlab,  x=0.15, y=0.62, s=0.04)
  s.AddTex(chlab, x=0.15, y=0.84, s=0.04)
  s.DrawStack(xtit, 'Events')
  s.SetLogY()
  s.SetOutName('log_'+outname)
  s.SetPlotMinimum(1)
  s.SetPlotMaxScale(1200)
  s.SetYratioTitle('Ratio')
  #s.DrawStack(xtit, 'Events')

DrawPostFit(275, 100, 'prefit', 'dnn', ['ee', 'emu', 'mumu'], [2016, 2017, 2018])
exit()

ch = 'emu'
year = 2018
for c in ['ee', 'emu', 'mumu', ['ee', 'emu', 'mumu']]:
  for y in [2016, 2017, 2018, [2016,2017,2018]]:
    #for ms, ml in [[225,50],[235,60],[275,100],[275,70],[245,100]]:
    for ms, ml in [[205,40]]:
      for tag in ['prefit','fit_b', 'fit_s']:
        for var in ['dnn']:#, 'met']:
          DrawPostFit(ms, ml, tag, var, c, y)

