import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow

### Input and output
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

baseoutpath = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop_v629Mar/'
webpath  = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/29mar/'
model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'


### Definition of the processes
processDic = {
       2018 : {
          'tt_test'  : 'TTTo2L2Nu_test',
          'stop_test'      : 'stop_test',
          'stop'      : 'stop',
          'tt'  : 'TTTo2L2Nu',
          'ttnoHEM'  : 'TTTo2L2Nu',
          'ttnongauss'  : 'TTTo2L2Nu',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
          'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
          'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
          'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
          'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
          'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
          'data' : 'EGamma_2018, MuonEG_2018, SingleMuon_2018',
        },
        2017 : {
          'tt_test'  : 'TTTo2L2Nu_test',
          'stop_test'      : 'stop_test',
          'tt'  : 'TTTo2L2Nu',
          'ttnongauss'  : 'TTTo2L2Nu',
          'stop'      : 'stop',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM,TTTo2L2Nu,tbarW_noFullHad, tW_noFullHad,WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
          'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
          'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
          'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
          'tt_mtopDown'  : 'TTTo2L2Nu_mtop171p5',
          'tt_mtopUp'  : 'TTTo2L2Nu_mtop173p5',
          'data' : 'MuonEG_2017,SingleElectron_2017,SingleMuon_2017',#,DoubleEG_2017,DoubleMuon_2017',
        },
    		2016 : {
          'tt_test'  : 'TT_test',
          'stop_test'      : 'stop_test',
          'tt'  : 'TT',
          'ttnongauss'  : 'TT',
          'stop'      : 'stop',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a,TTZToQQ',#, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM, TT, tbarW_noFullHad, tW_noFullHad, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ,DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo4L',
          'tt_hdampUp' : 'TT_hdampUp',
          'tt_UEUp'  : 'TT_TuneCUETP8M2T4up',
          'tt_hdampDown' : 'TT_hdampDown',
          'tt_UEDown'  : 'TT_TuneCUETP8M2T4down',
          #'tt'  : 'TTTo2L2Nu',
          #'tt_isrUp': 'TT_isrUp',
          #'tt_isrDown': 'TT_isrDown',
          #'tt_fsrUp': 'TT_fsrUp',
          #'tt_fsrDown': 'TT_fsrDown',
          #'tt_erdON' : 'TT_erdON',
          #'tt_colourFlip' : 'TT_colourFlip',
          #'tt_TuneEE5C_herwigpp' : 'TT_TuneEE5C_herwigpp',
          #'tt_QCDbasedCRTune_erdON' :'TT_QCDbasedCRTune_erdON',
          #'tt_GluonMoveCRTune':'TT_GluonMoveCRTune',
          'tt_mtopDown'  : 'TT_mtop1715',
          'tt_mtopUp'  : 'TT_mtop1735',
          'data' : 'MuonEG_2016,SingleElectron_2016,SingleMuon_2016',#,DoubleEG_2017,DoubleMuon_2017',
        },
}

processes= ['Others', 'Nonprompt', 'ttZ', 'tW', 'tt', 'stop']

### Definition of colors for the processes
colors ={
'stop'      : kTeal+2,
'Nonprompt' : kGray+1,
'VV + ttV'  : kYellow-4,
'ttV'       : kYellow-4,
'ttZ'       : kYellow-4,
'DY'        : kTeal+5,
'Others'        : kAzure,
'tW'        : kOrange+1,
'tt'  : kRed+1,
'data': 1}

systematics=''

def GetName(var, chan, lev):
  return 'H_' + var + '_' + chan + '_' + lev

def GetAllCh(var, lev):
  return [GetName(var,'eee',lev), GetName(var,'emm',lev), GetName(var,'mee',lev), GetName(var,'mmm',lev)]

def GetAllStopNeutralinoPoints(minStop = 145, maxStop = 295, dStop = 10, mindif = 145, maxdif = 205, ddif = 10):
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
      if dif == 175: continue
      #print '[%i, %i]'%(mStop, mChi)
      points.append([mStop, mChi])
  return points

