import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow

### Input and output
path = {
  2016 : '/nfs/fanae/user/andreatf/PAFnanoAOD/temp2018_new/ver5/minitrees_minis_v5/',
  2017 : '/nfs/fanae/user/andreatf/PAFnanoAOD/temp2017_new/ver5/minitrees_minis_v5/',
  2018 : '/nfs/fanae/user/andreatf/PAFnanoAOD/temp2018_new/ver5/minitrees_minis_v5/',
}

path = {
  #2018 : '/nfs/fanae/user/juanr/test/PAFnanoAOD/5dec/2018/SR/',
  2016 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016_new/ver5/minitrees_minis_cutMETandMT2_v6/',
  2017 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2017_new/ver5/minitrees_minis_cutMETandMT2_v6/',
  2018 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2018_new/ver5/minitrees_minis_cutMETandMT2_v6/',
}

### Definition of the processes
processDic = {
       2018 : {
          'stop'      : 'stop',
          'tt'  : 'TTTo2L2Nu',
          #'ttDilep' : 'TTJets_DiLept',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo2Q2Nu, ZZTo4L',
          'tt_hdampUp' : 'TTTo2L2Nu_hdampUp',
          'tt_UEUp'  : 'TTTo2L2Nu_TuneCP5Up',
          'tt_hdampDown' : 'TTTo2L2Nu_hdampDown',
          'tt_UEDown'  : 'TTTo2L2Nu_TuneCP5Down',
        },
        2017 : {
          'tt'  : 'TTTo2L2Nu',
          #'ttDilep' : 'TTJets_DiLept',
          'stop'      : 'stop',
          'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          'ttZ' : 'TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
          'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu_MLM',
          'Others'     : 'TTWJetsToLNu, TTWJetsToQQ, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo2Q2Nu, ZZTo4L',
        },
    		2016 : {
          'tt'  : 'TT',
          #'ttDilep' : 'TTJets_DiLept',
          'stop'      : 'stop',
          #'tW'  : 'tbarW_noFullHad, tW_noFullHad',
          #'ttZ' : 'TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a',#, TTZToQQ',
          #'Nonprompt' : 'TTToSemiLeptonic, WJetsToLNu',
          #'Others'     : 'TTWJetsToLNu, DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, WZTo3LNu, ZZTo2L2Nu, ZZTo2L2Q, ZZTo2Q2Nu, ZZTo4L',#TTWJetsToQQ
        },
}
processes= ['Others', 'Nonprompt', 'ttZ', 'tW', 'tt']
#processes = ['tt']

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

model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'
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
      if mChi <= 10: continue
      if dif != 175: continue
      if mChi == 0: mChi = 1
      if mStop+mChi > maxStop+(maxStop-maxdif): continue
      #print '[%i, %i]'%(mStop, mChi)
      points.append([mStop, mChi])
  return points

