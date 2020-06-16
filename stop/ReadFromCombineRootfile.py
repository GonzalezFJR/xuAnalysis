import os, sys
from config import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp, HistoUnc
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
gROOT.SetBatch(1)

# if ch == 'all', if year == 'comb'
doStack = True
doPlotSyst = False
ch= 'emu'
year = 2016#2016
ms = 235
ml =  60
region = 'SR' #'ttmt2'
#syst = 'ElecES, MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, hdamp, UE, PU, JESCor, JESUnCor, mtop, ISR, FSR, MisTag, nongauss, PDF, Scale' # MisTag, Pref
syst = 'ElecES, MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, hdamp, UE, PU, JESCor, JESUnCor, mtop, MisTag, nongauss, PDF, Scale' # MisTag, Pref

#path[year] = pathToTrees(year, chan, region)

if region == 'BS': 
  syst = 'MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, PU, JESCor, JESUnCor, MisTag'#, ISR, FSR' # MisTag, Pref
  if year != 2016 and year != 'comb': syst += ',ISR, FSR'
if year != 2018 and year != 'comb': syst += ', Pref'
#process = 'tt_test, tW, ttZ, Others, Nonprompt'
process = 'tt_test, tW, ttZ, DY, ttW, VV, Nonprompt'
#path = '../stop_v6testPU/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
#path = '../stop_v6Mod/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
GetPath = lambda region, year, ms, ml, ch : baseoutpath+'/Unc/%s/%s/%s/mass%i_%i/'%(region, ch, str(year), ms, ml)
GetOutpath = lambda region, year, ms, ml, ch : webpath+'/Unc/%s/%s/%s/mass%i_%i/'%(region, ch, str(year), ms, ml)
path    = GetPath(region,year, ms, ml,ch)
outpath = GetOutpath(region,year, ms, ml,ch)




sysdic = {
'MuonEff' : 'Muon efficiency',
'ElecEff' : 'Electron efficiency',
'Trig'    : 'Trigger efficiency',
'Pref'    : 'Prefire correction',
'JES'     : 'Jet energy scale',
'JESUnCor': 'JES (uncorrelated)',
'JESCor'  : 'JES (correlated)',
'JER'     : 'Jet energy resolution',
'MuonES'  : 'Muon energy scale',
'ElecES'  : 'Electron energy scale',
'Uncl'    : 'Unclustered energy',
'Btag'    : 'b-tag efficiency',
'MisTag'  : 'MisTag efficiency',
'TopPt'   : 'Top quark p_{T}',
'hdamp'   : 'h_{damp} variations',
'UE'      : 'UE Tune',
'PU'      : 'Pileup reweighting',
'ISR'     : 'Initial state radiation',
'FSR'     : 'Final state radiation',
'mtop'    : 'Top quark mass',
'PDF'     : 'PDF + #alpha_{S}',
'Scale'   : '#mu_{F} and #mu_{R} scales',
'nongauss': 'Non-gaussian JER tails',
}

'''
  #'mt2_2bins' : 'm_{T2} (GeV)',
  #'mt2_3bins' : 'm_{T2} (GeV)',
  #'mt2_4bins' : 'm_{T2} (GeV)',
  #'met_5bins' : 'MET (GeV)',
  #'dnn_5bins' : 'DNN score',
  #'dnn_4bins' : 'DNN score',
  'mt2_dnng80' : 'm_{T2} (GeV)',
  'met_dnng80' : 'MET (GeV)',
  'mt2lblb_dnng80' : 'm_{T2}(lblb) (GeV)',
  'mt2_dnng90' : 'm_{T2} (GeV)',
  'met_dnng90' : 'MET (GeV)',
  'mt2lblb_dnng90' : 'm_{T2}(lblb) (GeV)',
  'mt2_dnng95' : 'm_{T2} (GeV)',
  'met_dnng95' : 'MET (GeV)',
  'mt2lblb_dnng95' : 'm_{T2}(lblb) (GeV)',
  'mtwlblb' : 'm_{T2}(lblb) (GeV)',
}
'''

rebin = {
  'mt2lblb_dnng80':5,
  'mt2lblb_dnng90':5,
  'mt2lblb_dnng95':5,
}
titdic = {
  'dnnVIPS' : 'DNN score',
  'dnn' : 'DNN score',
  'mt2' : 'm_{T2} (GeV)',
  'met' : 'MET (GeV)',
  'njets'  : 'Jet multiplicity',
  'nbtags' : 'b tag multiplicity',
  'dileppt': 'p_{T}(e#mu) (GeV)',
  'mll' : 'm_{e#mu} (GeV)',
  'deltaeta' : '#Delta#eta(e#mu)',
  'deltaphi' : '#Delta#phi(e#mu) (rad/#pi)',
}
'''
  'mtwlblb' : 'm_{T2}(lblb) (GeV)',
  'ht' : 'H_{T} (GeV)',
  'jet0pt' : 'Leading jet p_{T} (GeV)',
  'jet1pt' : 'Subeading jet p_{T} (GeV)',
  'lep0pt' : 'Leading lepton p_{T} (GeV)',
  'lep1pt' : 'Subleading lepton p_{T} (GeV)',
  'lep0eta': 'Leading lepton #eta',
  'lep1eta': 'Subleading lepton #eta',
  'jet0eta': 'Leading jet #eta',
  'jet1eta': 'Subleading jet #eta',

titdic = {
  'mt2_dnng0p90' : 'm_{T2} (GeV)',
  'met_dnng0p90' : 'MET (GeV)',
  'mt2_dnng0p95' : 'm_{T2} (GeV)',
  'met_dnng0p95' : 'MET (GeV)',
}
  'njets_dnng0p90'  : 'Jet multiplicity',
  'nbtags_dnng0p90' : 'b tag multiplicity',
  'dileppt_dnng0p90': 'p_{T}(e#mu) (GeV)',
  'deltaeta_dnng0p90' : '#Delta#eta(e#mu)',
  'deltaphi_dnng0p90' : '#Delta#phi(e#mu) (rad/#pi)',
  'ht_dnng0p90' : 'H_{T} (GeV)',
  'jet0pt_dnng0p90' : 'Leading jet p_{T} (GeV)',
  'lep0pt_dnng0p90' : 'Leading lepton p_{T} (GeV)',
  'lep1pt_dnng0p90' : 'Subleading lepton p_{T} (GeV)',
  'lep0eta_dnng0p90': 'Leading lepton #eta',
  'lep1eta_dnng0p90': 'Subleading lepton #eta',
  'njets_dnng0p95'  : 'Jet multiplicity',
  'nbtags_dnng0p95' : 'b tag multiplicity',
  'dileppt_dnng0p95': 'p_{T}(e#mu) (GeV)',
  'deltaeta_dnng0p95' : '#Delta#eta(e#mu)',
  'deltaphi_dnng0p95' : '#Delta#phi(e#mu) (rad/#pi)',
  'ht_dnng0p95' : 'H_{T} (GeV)',
  'jet0pt_dnng0p95' : 'Leading jet p_{T} (GeV)',
  'lep0pt_dnng0p95' : 'Leading lepton p_{T} (GeV)',
  'lep1pt_dnng0p95' : 'Subleading lepton p_{T} (GeV)',
  'lep0eta_dnng0p95': 'Leading lepton #eta',
  'lep1eta_dnng0p95': 'Subleading lepton #eta',
'''


def SavePlots(syst, var = 'mt2', sampName = 'tt'):
  hm = HistoManager(process, syst, path=path)
  hm.ReadHistosFromFile(var)
  hm.GetDataHisto()
  a = HistoUnc(outpath+'/%s/'%sampName, var+sampName+s, tag=sysdic[s], xtit = titdic[var] if var in titdic.keys() else '')
  a.SetLumi(GetLumi(year))
  a.AddHistoNom(hm.GetHisto(sampName, sampName))
  a.AddHistoUp(hm.GetHisto(sampName, sampName, s+'Up'))
  a.AddHistoDown(hm.GetHisto(sampName, sampName, s+'Down'))
  a.Draw()

def GetTableOfUnc(syst, sampName='tt', var='dnn', dic = {}):
  if isinstance(sampName, str) and ',' in sampName: sampName = sampName.replace(' ', '').split(',')
  if isinstance(syst,     str) and ',' in syst    : syst     = syst    .replace(' ', '').split(',')
  if isinstance(sampName, list):
    for s in sampName: GetTableOfUnc(syst, s, var, dic)
    return
  if isinstance(syst, list):
    for s in syst: GetTableOfUnc(s, sampName, var, dic)
    return
  if not sampName in dic: dic[sampName] = {}
  if not syst in dic[sampName]: dic[sampName][syst] = {}
  hm = HistoManager(process, syst, path=path)
  hm.ReadHistosFromFile(var)
  hm.GetDataHisto()
  n = hm.GetHisto(sampName, sampName             ).Integral()
  u = hm.GetHisto(sampName, sampName, syst+'Up'  ).Integral()
  d = hm.GetHisto(sampName, sampName, syst+'Down').Integral()
  meanval = (abs(n-d) + abs(n-u))/(2*n)*100
  dic[sampName][syst] = meanval
  return dic

def PrintTableUnc(syst, process='tt', var='dnn'):
  dic = {}
  GetTableOfUnc(syst, process, var, dic)
  if   isinstance(syst, str) and ',' in syst    : syst     = syst    .replace(' ', '').split(',')
  elif isinstance(syst, str): syst = [syst]
  print '##################################################'
  print ' Process: %s'%process
  print '--------------------------------------------------'
  for s in syst: print ' %s : %1.2f %s'%(s, dic[process][s], '%')
  print '##################################################'

#process = processes
def StackPlot(var = 'mt2', xtit = 'm_{T2} (GeV)', rebin=1):
  pr = process.replace(' ', '').split(',')#['VV', 'ttW', 'DY', 'Nonprompt', 'ttZ', 'tW', 'tt']
  #pr = ['Others', 'Nonprompt', 'ttZ', 'tW', 'tt']
  if year == 'comb':
    hm   = HistoManager(pr, syst, path=GetPath(region, 2016, ms, ml, ch), signalList = 'stop'); hm.SetStackOverflow()
    hm.ReadHistosFromFile(var,rebin=rebin)
    hm17 = HistoManager(pr, syst, path=GetPath(region, 2017, ms, ml, ch), signalList = 'stop'); hm17.SetStackOverflow()
    hm17.ReadHistosFromFile(var,rebin=rebin)
    hm18 = HistoManager(pr, syst, path=GetPath(region, 2018, ms, ml, ch), signalList = 'stop'); hm18.SetStackOverflow()
    hm18.ReadHistosFromFile(var,rebin=rebin)
    hm.Add(hm17).Add(hm18)
  else: 
    hm = HistoManager(pr, syst, path=path, signalList = 'stop'); hm.SetStackOverflow()
  hm.ReadHistosFromFile(var, rebin=rebin)
  hm.AddNormUnc({'tt':0.06, 'Nonprompt':0.3, 'DY':0.3,'ttZ':0.3,'tW':0.15})
  hm.GetDataHisto()
  #if ('mt2' in var or 'met' in var or 'dnn' in var or 'lblb' in var) and region != 'CR':
  #  #del hm.indic['data_obs'] # blind
  #  hm.indic['data_obs']['data_obs'] = hm.GetSumBkg()
  outdir = GetOutpath(region, year, ms, ml, ch)
  s = Stack(outpath=outdir+'/stackplots/')
  s.SetColors(colors)
  s.SetProcesses(pr)
  s.SetLumi(GetLumi(year) if isinstance(year, int) else (GetLumi(2016) + GetLumi(2017) + GetLumi(2018)) )
  s.SetOutName('stack_'+var)
  s.SetHistosFromMH(hm)
  s.SetDataHisto(hm.indic['data_obs']['data_obs'])
  #if not ('mt2' in var or 'met' in var or 'dnn' in var or 'lblb' in var) or (region == 'CR'): s.SetDataHisto(hm.indic['data_obs']['data_obs'])
  #else                               : 
  #  #hData  = hm.GetSumBkg().Clone("Asimov")
  #  hData  = s.TotMC.Clone("Asimov")
  #  hData.SetLineWidth(0); hData.SetMarkerStyle(20); hData.SetMarkerColor(kGray)
  #  hData2 = hData.Clone("Asimov2")
  #  hData2.Divide(hData)
  #  s.SetDataHisto(hData)
  #  s.SetRatio(hData2)
  s.AddSignalHisto(hm.indic['stop']['stop'], color = kTeal+2, mode = 'ontop', ratioBkg = True)
  if   region == 'SR': s.SetTextChan('SR: BS + p_{T}^{miss} #geq 50, m_{T2} #geq 80')
  elif region == 'BS': s.SetTextChan('BS: e#mu, #geq 2 jets, #geq 1 btag')
  elif region == 'CR': s.SetTextChan('BS + met < 50, m_{T2} < 80 ')
  elif region == 'ttmt2': s.SetTextChan('BS + met < 50')
  elif region == 'ttmet': s.SetTextChan('BS + m_{T2} < 80')
  s.SetRatioMin(0.0); s.SetRatioMax(2.5)
  #s.SetYratioTitle('S/(S+B)')
  s.SetYratioTitle('Ratio')
  s.SetPlotMaxScale(2.5)
  s.DrawStack(xtit, 'Events')
  s.SetLogY()
  s.SetOutName('stack_log_'+var)
  s.SetPlotMinimum(0.1)
  s.SetPlotMaxScale(1200)
  s.DrawStack(xtit, 'Events')


#PrintTableUnc(syst, 'tt')
StackPlot('dnn', titdic['dnn'], 1)
exit()
for var in titdic.keys():
  print 'Drawing plots for variable: ', var
  if doStack: StackPlot(var, titdic[var], rebin[var] if var in rebin else 1)
  if not doPlotSyst or year=='comb': continue
  for s in sysdic.keys(): 
    #if s == 'Pref': continue # and year == 2018: continue
    for samp in ['tt']: SavePlots(s,var, samp)
    #for samp in ['tt', 'stop']: SavePlots(s,var, samp)

