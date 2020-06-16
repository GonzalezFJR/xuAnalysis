import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow, kMagenta

### Input and output
'''
pathBS = {
  2016 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2016/30mar_BS/',
  2017 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2017/30mar_BS/',
  2018 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2018/30mar_BS/',
}

path = {
  #2018 : '/nfs/fanae/user/juanr/test/PAFnanoAOD/5dec/2018/SR/',
  2016 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2016/30mar_SR/',
  2017 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2017/30mar_SR/',
  2018 : '/pool/phedex/userstorage/andrea/stop/Trees/ver6/2018/30mar_SR/',
  #2018 : '/pool/phedexrw/userstorage/andrea/stop/Trees/ver6/2018/26mar_testmt2lblb_testnongauss/SR_emu/',
  #2018 : '/mnt_pool/ciencias_users/user/juanr/test/PAFnanoAOD/temp2018_minitrees/',
}
'''

pathToTrees = lambda year, ch, region: '/pool/phedexrw/userstorage/andrea/stop/Trees/ver6/%s/15abr/%s/%s/'%(str(year), region, ch) if ch in ['mumu', 'ee'] else '/pool/phedex/userstorage/andrea/stop/Trees/ver6/%s/30mar_%s/'%(str(year), region if region in ['SR', 'BS'] else 'BS')

folder = '29apr'#'24may'#'29apr'#'stop_v629Mar'#'16apr'
#folder = '8jun'#'24may'#'29apr'#'stop_v629Mar'#'16apr'
baseoutpath = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/'+folder
webpath  = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/'+folder
model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'
#getpath = lambda folder, ch, year, region : baseoutpath+'%s/%s/%s/%s/'%(folder, region, ch, year)

### Definition of the processes
processDic = {
       2018 : {
          #'stop_m275_m100':'stop_275_100',
          #'stop_m275_m70':'stop_275_70',
          #'stop_m205_m1':'stop_205_1',
          #'stop_225_50':'stop_225_50',
          #'stop_245_100':'stop_245_100',
          #'stop_265_120':'stop_265_120',
          'tt_test'  : 'TTTo2L2Nu_test',
          'stop_test'      : 'stop_test',
          'ttnongauss'  : 'TTTo2L2Nu',
          'stop'      : 'stop',
          'tt'  : 'TTTo2L2Nu',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'DY' : 'DYJetsToLL_M_50_HT_70to100_MLM,DYJetsToLL_M_50_HT_100to200_MLM,DYJetsToLL_M_50_HT_200to400_MLM,DYJetsToLL_M_50_HT_400to600_MLM,DYJetsToLL_M_50_HT_600to800_MLM,DYJetsToLL_M_50_HT_800to1200_MLM,DYJetsToLL_M_50_HT_1200to2500_MLM,DYJetsToLL_M_50_HT_2500toInf_MLM',#DYJetsToLL_M_10to50_MLM',
          'ttW'     : 'TTWJetsToLNu, TTWJetsToQQ',
          'VV'     : 'WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          #'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
          #'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
          #'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
          #'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
          #'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
          #'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
          'data' : 'EGamma_2018, MuonEG_2018, SingleMuon_2018,DoubleMuon_2018',
          #'DY'     : 'DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a',
        },
        2017 : {
          #'stop_m275_m100':'stop_275_100',
          #'stop_m275_m70':'stop_275_70',
          #'stop_m205_m1':'stop_205_1',
          #'stop_225_50':'stop_225_50',
          #'stop_245_100':'stop_245_100',
          #'stop_265_120':'stop_265_120',
          'tt_test'  : 'TTTo2L2Nu_test',
          'stop_test'      : 'stop_test',
          'ttnongauss'  : 'TTTo2L2Nu',
          'tt'  : 'TTTo2L2Nu',
          'stop'      : 'stop',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'DY' : 'DYJetsToLL_M_50_HT_70to100_MLM,DYJetsToLL_M_50_HT_100to200_MLM,DYJetsToLL_M_50_HT_200to400_MLM,DYJetsToLL_M_50_HT_400to600_MLM,DYJetsToLL_M_50_HT_600to800_MLM,DYJetsToLL_M_50_HT_800to1200_MLM,DYJetsToLL_M_50_HT_1200to2500_MLM,DYJetsToLL_M_50_HT_2500toInf_MLM',#,DYJetsToLL_M_10to50_MLM',
          'VV'     : 'WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'ttW'     : 'TTWJetsToLNu, TTWJetsToQQ',
          #'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
          #'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
          #'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
          #'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
          #'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
          #'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
          'data' : 'MuonEG_2017,SingleElectron_2017,SingleMuon_2017,DoubleEG_2017,DoubleMuon_2017',
          #'DY'     : 'DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a',
        },
    		2016 : {
          #'stop_m275_m100':'stop_275_100',
          #'stop_m275_m70':'stop_275_70',
          #'stop_m205_m1':'stop_205_1',
          #'stop_225_50':'stop_225_50',
          #'stop_245_100':'stop_245_100',
          #'stop_265_120':'stop_265_120',
          'tt_test'  : 'TT_test',
          'stop_test'      : 'stop_test',
          'ttnongauss'  : 'TT',
          'tt'  : 'TT',
          'stop'      : 'stop',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'DY' : 'DYJetsToLL_M_50_HT_70to100_MLM,DYJetsToLL_M_50_HT_100to200_MLM,DYJetsToLL_M_50_HT_200to400_MLM,DYJetsToLL_M_50_HT_400to600_MLM,DYJetsToLL_M_50_HT_600to800_MLM,DYJetsToLL_M_50_HT_800to1200_MLM,DYJetsToLL_M_50_HT_1200to2500_MLM,DYJetsToLL_M_50_HT_2500toInf_MLM',#,DYJetsToLL_M_10to50',
          #'tWDS'  : 'tbarW_noFullHadDS, tW_noFullHadDS',
          'ttZ' : 'TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a,TTZToQQ',#, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM, TT, tbarW_noFullHad, tW_noFullHad, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ,DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'VV'     : 'WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'ttW'     : 'TTWJetsToLNu, TTWJetsToQQ',
          #'tt_hdampUp' : 'TT_hdampUp',
          #'tt_UEUp'  : 'TT_TuneCUETP8M2T4up',
          #'tt_hdampDown' : 'TT_hdampDown',
          #'tt_UEDown'  : 'TT_TuneCUETP8M2T4down',
          #'tt_mtopDown'  : 'TT_mtop1715',
          #'tt_mtopUp'  : 'TT_mtop1735',
          'data' : 'MuonEG_2016,SingleElectron_2016,SingleMuon_2016,DoubleEG_2016,DoubleMuon_2016',
          #'DY'     : 'DYJetsToLL_M_10to50, DYJetsToLL_M_50_a',
        },
}

processes= ['DY', 'ttW', 'VV', 'Nonprompt', 'ttZ', 'tW', 'tt', 'stop']
#processes= ['Others', 'Nonprompt', 'ttZ', 'tW', 'tt', 'stop']

### Definition of colors for the processes
colors ={
'stop'      : kTeal+2,
'Nonprompt' : kGray+1,
'VV + ttV'  : kYellow-4,
'ttV'       : kYellow-4,
'ttZ'       : kYellow-4,
'ttW'       : kYellow-2,
'VV'        : kMagenta-9,
'DY'        : kAzure-8,
'Others'    : kAzure-8,
'tW'        : kOrange+1,
'tt'  : kRed+1,
'tt_test'  : kRed+1,
'data': 1}

systematics=''

def GetName(var, chan, lev):
  return 'H_' + var + '_' + chan + '_' + lev

def GetAllCh(var, lev):
  return [GetName(var,'eee',lev), GetName(var,'emm',lev), GetName(var,'mee',lev), GetName(var,'mmm',lev)]

def GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10, mode=''):
  points = []
  for mStop in range(minStop, maxStop+dStop, dStop):
    for dif in range(mindif, maxdif+ddif, ddif):
      mChi = mStop-dif
      #if mChi <= 10: continue
      #if dif == 175 or (mStop == 175 and mChi <= 1): continue
      if mChi == 0: mChi = 1
      #if mChi == 1: continue
      if mStop+mChi > maxStop+(maxStop-maxdif): continue
      if mChi < 0: continue
      if mode == 'diag'   and dif != 175: continue
      if mode == 'nodiag' and dif == 175: continue
      #print '[%i, %i]'%(mStop, mChi)
      points.append([mStop, mChi])
  return points

