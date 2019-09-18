from plotter.TopHistoReader import TopHistoReader, StackPlot, Process, WeightReader
from plotter.DrellYanDataDriven import DYDD
from plotter.NonpromptDataDriven import NonpromptDD
from plotter.CrossSection import CrossSection
from ROOT.TMath import Sqrt as sqrt
from ROOT import *

### Input and output
path = '../temp5TeV/'
outpath = './outputs/'

### Definition of the processes
process = {
'VV'  : 'WZTo3LNU,WWTo2L2Nu',
'fake': 'WJetsToLNu,TTsemilep',
'tW'  : 'tW_noFullHad,  tbarW_noFullHad',
'DY'  : 'DYJetsToLL_M_10to50,DYJetsToLL_MLL50',
'tt'  : 'TT',
'data': 'HighEGJet,SingleMuon, DoubleMuon'}
prk = ['VV', 'fake', 'DY', 'tt', 'tW']

### Definition of colors for the processes
colors ={
'VV'  : kTeal+5,
'fake': kGray+2,
'tW'  : kOrange+1,
'DY'  : kAzure+2,
'tt'  : kRed+1,
'data': 1}

######################################################################################
### Plots
def DrawStack(out, *listOfPlots):
  ''' Draw some stack plots 
      Example:
      DrawStack(['NJets_ElMu_dilepton', 'Jet multiplicity'], ['DYMass_MuMu_dilepton', 'M_{#mu#mu}'])
  '''
  s = StackPlot(path)
  s.SetVerbose(1)
  s.SetOutPath(out)
  s.SetLumi(296.08)
  for pr in prk: s.AddProcess(pr, process[pr], colors[pr])
  s.AddData(process['data'])
  s.AddToSyst('ElecEffUp, ElecEffDown, MuonEffUp,MuonEffDown,PUUp, PUDown,JESUp,JESDown')
  s.SetRatioMin(0.5); s.SetRatioMax(1.5)
  for p in listOfPlots:
    if not isinstance(p, list): p = [p]
    s.DrawStack(p[0], p[1] if len(p) >= 2 else '', p[2] if len(p) >= 3 else '', p[3] if len(p) >= 4 else 1)

def GetName(var, chan, lev):
  return var + '_' + chan + '_' + lev

######################################################################################
## Cross section
def xsec(chan = 'ElMu', lev = '2jets', doDD = True):
  x = CrossSection(outpath, chan, lev)
  x.SetTextFormat("tex")
  bkg = []
  bkg.append(['tW',            process['tW'],   0.30])
  if not doDD: 
    bkg.append(['DY',            process['DY'],   0.15])
    bkg.append(['Nonprompt lep', process['fake'], 0.50])
  bkg.append(['VV',            process['VV'],   0.30])
  signal   = ['tt',            process['tt']]
  data     = process['data']
  expunc = "MuonEff, ElecEff, PU, JES" # JER
  modunc = "pdf, scale"

  x.ReadHistos(path, chan, lev, bkg = bkg, signal = signal, data = data, expUnc = expunc, modUnc = modunc)
  x.AddModUnc('Underlying Event','TT_TuneCP5up','TT_TuneCP5down')
  x.SetLumi(296.1)
  x.SetLumiUnc(0.035)
  x.AddModUnc('hdamp','TT_hdampUP','TT_hdampDOWN')

  if doDD:
    d = DYDD(path,outpath,chan,lev) 
    DYy, DYerr = d.GetDYDD()
    x.AddBkg('DYDD', DYy, 0, 0.15, DYerr)

    f = NonpromptDD(path, level = lev)
    fy, fe = f.GetNonpromptDD(chan)
    x.AddBkg('Nonprompt lep', fy, 0, 0.30, fe)
  
  suf = '_'+chan+'_'+lev+'_'+('DD' if doDD else 'MC')
  x.PrintYields('Yields'+suf)
  x.PrintSystTable('Systematics'+suf)
  x.PrintXsec('CrossSection'+suf)

######################################################################################
## PDF and scale systematics
def DrawWeightSystematics(chan = 'ElMu', lev = '2jets'):
  w = WeightReader(path, outpath, chan, lev)
  w.PrintMEscale('ScaleMEuncertainty_'+chan+'_'+lev)
  w.PrintPDFyields('PDFuncertainty_'+chan+'_'+lev)

######################################################################################
## Drell-Yan estimate with Rout/in 
def DrawDYDD(lev = '2jets', doSF = False):
  if not doSF and lev == 'MET': return 
  d = DYDD(path,outpath,'ElMu',lev) 
  lab = 'SF' if doSF else 'OF'
  d.PrintDYestimate(doSF,  'DYDD_'+lev+'_'+lab)

def DrawDYDDnjets():
  d = DYDD(path,outpath)
  d.PrintDYSFnjets()

######################################################################################
## Nonprompt estimate
def DrawNonpromptDD(ch = 'ElMu', lev = '2jets'):
  s = NonpromptDD(path, outpath, chan = ch, level = lev)
  s.PrintNonpromptEstimate('',ch,lev)

def DrawSS(lev = '2jets'):
  s = NonpromptDD(path, outpath, level = lev)
  s.PrintSSyields('',lev)

#######################################################################################
#######################################################################################
#######################################################################################

levels   = ['dilepton', 'MET','2jets']
channels = ['ElMu','ElEl', 'MuMu']
# Plots
'''
for ch in channels:
  if   ch == 'MuMu': lepstr = '#mu#mu'
  elif ch == 'ElMu': lepstr = 'e#mu'
  elif ch == 'ElEl': lepstr = 'ee'
  for lev in levels:
    if lev == '1btag' and ch != 'ElMu': continue
    if ch != 'ElMu' and lev == 'dilepton': DrawStack(outpath+'leptons',[GetName('DYMass',ch,lev),  'M_{'+lepstr+'} (GeV)'])
    if lev == 'MET' and ch == 'ElMu': continue
    if lev == 'dilepton':
      DrawStack(outpath + 'global', 
      [GetName('NJets',ch,lev), 'Jet multiplicity'],
      [GetName('Vtx',ch,lev),  'Reconstructed primary verteces'])
    DrawStack(outpath + 'global',
      [GetName('HT',ch,lev),  'H_{T} (GeV)','Events / 40 GeV',8],
      [GetName('MET',ch,lev), 'Missing p_{T} (GeV)','Events / 15 GeV',3])
    DrawStack(outpath + 'leptons',
      [GetName('Lep0Pt',ch,lev),  'Leading lepton p_{T} (GeV)','Events / 10 GeV',2],
      [GetName('Lep1Pt',ch,lev),  'Subleading lepton p_{T} (GeV)','Events / 10 GeV',2],
      [GetName('Lep0Eta',ch,lev),  'Leading lepton #eta','',5],
      [GetName('Lep1Eta',ch,lev),  'Subleading lepton #eta','',5],
      [GetName('DilepPt',ch,lev),  'p_{T}^{'+lepstr+'} (GeV)','Events / 20 GeV',4],
      [GetName('InvMass',ch,lev),  'M_{'+lepstr+'} (GeV)','Events / 30 GeV',6],
      [GetName('DeltaPhi',ch,lev),  '#Delta#phi('+lepstr+')','',2])
    DrawStack(outpath + 'jets',
      [GetName('Jet0Pt',ch,lev),  'Leading Jet p_{T} (GeV)','Events / 30 GeV',6],
      [GetName('Jet1Pt',ch,lev),  'Subleading Jet p_{T} (GeV)','Evetns / 25 GeV',5],
      [GetName('Jet0Eta',ch,lev),  'Leading Jet #eta','',5],
      [GetName('Jet1Eta',ch,lev),  'Subleading Jet #eta','',5])
'''
    
# Cross section
for ch in channels:
  xsec(ch,'2jets', doDD = True)
  xsec(ch,'2jets', doDD = False)
xsec('ElMu','1btag', doDD = True)
xsec('ElMu','1btag', doDD = False)

# Systematics
for ch in channels: DrawWeightSystematics(ch, '2jets')
DrawWeightSystematics('ElMu', '1btag')

# Drell-Yan
DrawDYDDnjets()
for lev in levels: 
  DrawDYDD(lev, False)
  if lev != '1btag': DrawDYDD(lev, True)

# Nonprompt
for lev in levels:
  DrawSS(lev)
  for ch in channels:
    DrawNonpromptDD(ch, lev)
