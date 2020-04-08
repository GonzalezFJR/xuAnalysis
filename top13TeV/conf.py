import os, sys
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from framework.functions import GetLumi
from plotter.TopHistoReader import TopHistoReader
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow

### Input and output
path = {
#  2016 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016/', #'/pool/ciencias/userstorage/juanr/top/2016/nov15/', #'/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016/',
#  2015 : '/pool/ciencias/userstorage/juanr/top/2016/nov15/',  #TOP-17-001
#  2017 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2017/',# '/nfs/fanae/user/juanr/legacy/PAFnanoAOD/histograms/2017',
#  2018 : '/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2018/' #'/nfs/fanae/user/juanr/legacy/PAFnanoAOD/histograms/2018/',
  2016 : '/nfs/fanae/user/juanr/test/PAFnanoAOD/temp2016/', #'/pool/ciencias/userstorage/juanr/top/2016/nov15/', #'/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016/',
  2017 : '/nfs/fanae/user/juanr/test/PAFnanoAOD/temp2017/', #'/pool/ciencias/userstorage/juanr/top/2016/nov15/', #'/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016/',
  2018 : '/nfs/fanae/user/juanr/test/PAFnanoAOD/temp2018/', #'/pool/ciencias/userstorage/juanr/top/2016/nov15/', #'/mnt_pool/ciencias_users/user/andreatf/PAFnanoAOD/temp2016/',
}

### Definition of the processes
processDic = {
       2018 : {
          'VV'        : 'WZTo3LNu, WZTo2L2Q, WZTo1L3Nu, ZZTo2L2Q, ZZTo2L2Nu, ZZTo4L, WWTo2L2Nu',#ZZTo2Q2Nu,
          'Nonprompt' : 'TTToSemiLeptonic',#'TTToSemiLeptonic, WJetsToLNu_MLM',
          'ttV'       : 'TTWJetsToLNu, TTZToLLNuNu_M_10_a',#'TTWJetsToLNu, TTWJetsToQQ, TTZToQQ, TTZToLL_M_1to10, TTZToLLNuNu_M_10_a',
          'DY'        : 'DYJetsToLL_M_50_a', #'DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a',
          'tW'        : 'tW_noFullHad,tbarW_noFullHad',
          't#bar{t}'  : 'TTTo2L2Nu',
          'data'      : 'DoubleMuon_2018,SingleMuon_2018,EGamma_2018,MuonEG_2018'},
        2017 : {
          'VV'        : 'WWTo2L2Nu,WZTo3LNu,WZTo2L2Q,ZZTo2L2Nu,ZZTo4L,ZZTo2L2Q',
          'Nonprompt' : 'TTToSemiLeptonic,WJetsToLNu_MLM',
          'ttV'       : 'TTWJetsToLNu,TTZToLLNuNu_M_10_a,TTZToQQ,TTWJetsToQQ,TTZToLL_M_1to10',
          'DY'        : 'DYJetsToLL_M_50_a,DYJetsToLL_M_10to50_MLM',
          'tW'        : 'tbarW_noFullHad,tW_noFullHad',
          't#bar{t}'  : 'TTTo2L2Nu',
          'data'      : 'MuonEG_2017,DoubleMuon_2017,DoubleEG_2017,SingleElectron_2017,SingleMuon_2017',
        },
		2016 : {
          'VV'        : 'WWTo2L2Nu,WZTo3LNu,WZTo2L2Q,ZZTo2L2Nu,ZZTo4L,ZZTo2L2Q', #andrea
          'Nonprompt' : 'WJetsToLNu_MLM,TTToSemiLeptonic',
	    	  'ttV'       : 'TTWJetsToLNu,TTZToLLNuNu_M_10_a,TTZToQQ,TTWJetsToQQ,TTZToLL_M_1to10',
          'DY'        : 'DYJetsToLL_M_10to50,DYJetsToLL_M_50_a',
          'tW'        : 'tbarW_noFullHad,tW_noFullHad',
		      't#bar{t}'  : 'TT',#'TTTo2L2Nu',
		      'data'      : 'DoubleMuon_2016,DoubleEG_2016,MuonEG_2016,SingleMuon_2016,SingleElectron_2016'
		},

		2015 : {
			'VV'        : 'WZ',#,WW, ZZ',
			'Nonprompt' : 'WJetsToLNu_MLM',#,TTbar_Powheg_Semilep',
			'ttV'       : 'TTWToLNu',#,TTZToLLNuNu,TTZToQQ,TTWToQQ',
			'DY'        : 'DYJetsToLL_M10to50_aMCatNLO',#,DYJetsToLL_M50_aMCatNLO', 
			'tW'        : 'TbarW',#,TW', 
			't#bar{t}'  : 'TTbar_Powheg',
			'data'      : 'DoubleMuon',#DoubleEG,MuonEG,SingleElec,SingleMuon'
		}
}

processes = ['VV', 'ttV', 'Nonprompt','DY', 'tW', 't#bar{t}']
#prk = ['t#bar{t}']
systdic = {
    't#bar{t}': {
      'hdampUp' : 'TTTo2L2Nu_hdampUp',
      'hdampDo' : 'TTTo2L2Nu_hdampDown',
      'TuneUp'  : 'TTTo2L2Nu_TuneCP5Up',
      'TuneDo'  : 'TTTo2L2Nu_TuneCP5Down',
    },
}

### Definition of colors for the processes
colors ={
'VV'        : kTeal+2,
'Nonprompt' : kGray+1,
'ttV'       : kYellow-4,
'DY'        : kAzure,
'tW'        : kOrange+1,
't#bar{t}'  : kRed+1,
'data': 1}

systematics = 'MuonEff, ElecEff, PU, Btag, Mistag'
