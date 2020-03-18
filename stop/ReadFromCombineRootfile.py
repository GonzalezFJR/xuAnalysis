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

doStack = True
doPlotSyst = False
year = 'comb'#2016
ms = 225
ml = 50
region = 'CR' #'ttmt2'
syst = 'MuonEff, ElecEff, Trig, JER, MuonES, Uncl, Btag, TopPt, hdamp, UE, PU, JESCor, JESUnCor, mtop, ISR, FSR' # MisTag, Pref
process = 'tt, stop'#, tW, ttZ, Others'
#path = '../stop_v6testPU/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
#path = '../stop_v6Mod/Unc/%s/%i/mass%i_%i/'%(region,year, ms, ml)
#outpath = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/unc/mass%i_%i/%s/%i/'%(ms, ml, region,year)
GetPath = lambda region, year, ms, ml : '../stop_v617Feb/Unc/%s/%s/mass%i_%i/'%(region, str(year), ms, ml) # v611Feb NewSyst
GetOutpath = lambda region, year, ms, ml : '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/18feb/mass%i_%i/%s/%s/'%(ms, ml, region,str(year))
path    = GetPath(region,year, ms, ml)
outpath = GetOutpath(region,year, ms, ml)
#outpath = '/nfs/fanae/user/juanr/www/stopLegacy/nanoAODv6/testMod/mass%i_%i/%s/%i/'%(ms, ml, region,year)


#for pr in process.replace(' ', '').split(','):
#  print '%s : %1.2f'%(pr, hm.GetCYield(pr))
#print 'y = ', hm.GetCYield('tt', syst)
#for s in syst.replace(' ', '').split(','):
#  n = hm.GetCYield('tt')
#  v = hm.GetCYield('tt', s)
#  print '%s : %1.2f'%(s, abs(n-v)/n*100)

#print 'y = ', hm.GetCYield('tt')

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
}

titdic = {
  'mt2' : 'm_{T2} (GeV)',
  #'mt2_2bins' : 'm_{T2} (GeV)',
  #'mt2_3bins' : 'm_{T2} (GeV)',
  #'mt2_4bins' : 'm_{T2} (GeV)',
  'met' : 'MET (GeV)',
  #'met_5bins' : 'MET (GeV)',
  'dnn' : 'DNN score',
  #'dnn_5bins' : 'DNN score',
  #'dnn_4bins' : 'DNN score',
  'mll' : 'm_{e#mu} (GeV)',
  'deltaeta' : '#Delta#eta(e#mu)',
  'deltaphi' : '#Delta#phi(e#mu) (rad/#pi)',
  'ht' : 'H_{T} (GeV)',
  'jet0pt' : 'Leading jet p_{T} (GeV)',
  'jet1pt' : 'Subeading jet p_{T} (GeV)',
  'lep0pt' : 'Leading lepton p_{T} (GeV)',
  'lep1pt' : 'Subleading lepton p_{T} (GeV)',
  'lep0eta': 'Leading lepton #eta',
  'lep1eta': 'Subleading lepton #eta',
  'jet0eta': 'Leading jet #eta',
  'jet1eta': 'Subleading jet #eta',
  'njets'  : 'Jet multiplicity',
  'nbtags' : 'b tag multiplicity',
  'dileppt': 'p_{T}(e#mu) (GeV)',
}

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

process = processes
def StackPlot(var = 'mt2', xtit = 'm_{T2} (GeV)'):
  pr = ['Others', 'Nonprompt', 'ttZ', 'tW', 'tt']
  if isinstance(year, str):
    hm   = HistoManager(pr, syst, path=GetPath(region, 2016, ms, ml), signalList = 'stop')
    hm.ReadHistosFromFile(var)
    hm17 = HistoManager(pr, syst, path=GetPath(region, 2017, ms, ml), signalList = 'stop')
    hm17.ReadHistosFromFile(var)
    hm18 = HistoManager(pr, syst, path=GetPath(region, 2018, ms, ml), signalList = 'stop')
    hm18.ReadHistosFromFile(var)
    hm.Add(hm17).Add(hm18)
  else: 
    hm = HistoManager(pr, syst, path=path, signalList = 'stop')
  hm.ReadHistosFromFile(var)
  hm.AddNormUnc({'tt':0.06, 'Nonprompt':0.3, 'Others':0.3,'ttZ':0.3,'tW':0.15})
  #hm.GetDataHisto()
  #hm.indic['data_obs']['data_obs'] = hm.GetSumBkg()
  #if var in ['mt2', 'met', 'dnn']: del hm.indic['data_obs'] # blind
  outdir = GetOutpath(region, year, ms, ml)
  s = Stack(outpath=outdir+'/stackplots/')
  s.SetColors(colors)
  s.SetProcesses(pr)
  s.SetLumi(GetLumi(year) if isinstance(year, int) else (GetLumi(2016) + GetLumi(2017) + GetLumi(2018)) )
  s.SetOutName('stack_'+var)
  s.SetHistosFromMH(hm)
  if (not var in ['mt2', 'met', 'dnn']) or (region != 'SR'): s.SetDataHisto(hm.indic['data_obs']['data_obs'])
  else                               : 
    #hData  = hm.GetSumBkg().Clone("Asimov")
    hData  = s.TotMC.Clone("Asimov")
    hData.SetLineWidth(0); hData.SetMarkerStyle(20); hData.SetMarkerColor(kGray)
    hData2 = hData.Clone("Asimov2")
    hData2.Divide(hData)
    s.SetDataHisto(hData)
    s.SetRatio(hData2)
  s.AddSignalHisto(hm.indic['stop']['stop'], color = kTeal+2, mode = 'ontop', ratioBkg = True)
  if   region == 'SR': s.SetTextChan('SR: BS + p_{T}^{miss} > 50, m_{T2} > 80')
  elif region == 'BS': s.SetTextChan('BS: e#mu, #geq 2 jets, #geq 1 btag')
  elif region == 'ttmt2': s.SetTextChan('BS + met < 50')
  elif region == 'ttmet': s.SetTextChan('BS + m_{T2} < 80')
  s.SetRatioMin(0.5); s.SetRatioMax(1.5)
  #s.SetYratioTitle('S/(S+B)')
  s.SetYratioTitle('Ratio')
  s.DrawStack(xtit, 'Events')


'''
process = processes
var = 'met'
pr = ['tt']
hm   = HistoManager(pr, syst, path=GetPath('BS', 2016, 225, 50), signalList = 'stop')
hm.ReadHistosFromFile(var)
hm.AddNormUnc({'tt':0.5})
c = TCanvas('c', 'c', 10, 10, 800, 600)
hnorm = hm.GetNormUnc()
hnorm2 = hm.GetNormUnc()
hnorm.Divide(hnorm2);
hnorm.Draw("e2");
c.SaveAs('testnorm.png')
'''
StackPlot('met', 'MET')

exit()
#PrintTableUnc(syst)
for var in titdic.keys():
  if doStack: StackPlot(var, titdic[var])
  if not doPlotSyst: continue
  for s in sysdic.keys(): 
    if s == 'Pref': continue # and year == 2018: continue
    #for samp in ['tt']: SavePlots(s,var, samp)
    for samp in ['tt', 'stop']: SavePlots(s,var, samp)

