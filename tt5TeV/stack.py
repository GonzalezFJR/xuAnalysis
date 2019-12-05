import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi = Lumi)

def Draw(var = 'H_Lep0Pt_ElMu_2jets', ch = '', lev = 'dilepton', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 1.6):
  s = Stack(outpath=outpath)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(Lumi)
  s.SetHistoPadMargins(top = 0.08, bottom = 0.10, right = 0.06, left = 0.10)
  s.SetRatioPadMargins(top = 0.03, bottom = 0.40, right = 0.06, left = 0.10)
  s.SetTextLumi(texlumi = '%2.1f pb^{-1} (5.02 TeV)', texlumiX = 0.62, texlumiY = 0.97, texlumiS = 0.05)
  s.SetBinLabels(binlabels)
  hm.SetStackOverflow(doStackOverflow)
  hm.IsScaled = False
  name = GetName(var, ch, lev)
  hm.SetHisto(name, rebin)
  s.SetHistosFromMH(hm)
  s.SetOutName(name)
  s.SetTextChan('')
  s.SetRatioMin(2-maxscale)
  s.SetRatioMax(maxscale)
  if ch == 'MuMu': tch = '#mu#mu'
  elif ch == 'ElEl': tch = 'ee'
  else: tch = 'e#mu'
  if   lev == '2jets': Tch = tch+', #geq 2 jets'
  elif lev == '1btag': Tch =tch+ ', #geq 2 jets, #geq 1 btag'
  else: Tch=tch
  s.SetTextChan(Tch)
  tch=''
  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.DrawStack(xtit, ytit)

lev = 'dilepton'
for chan in ['ElEl', 'MuMu']: 
  Draw('Jet0Pt', chan, lev, 2, 'Leading jet p_{T} (GeV)', 'Events', False, maxscale = 1.6 )
  Draw('NJets',  chan, lev, 1, 'Jet multiplicity', 'Events', True)
  Draw('MET', chan, lev, 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
  Draw('MET', chan, 'ZVeto', 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
  Draw('MET', chan, '2jetsnomet', 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
    
for chan in ['ElEl', 'MuMu']: 
  Draw('MET', chan, 'ZVeto', 1, 'MET (GeV)', 'Events', False, maxscale = 1.9)

lev = 'dilepton'
ch = 'ElMu'

Draw('Lep0Eta', 'MuMu', lev, 2, 'Lep #eta', 'Events', False, maxscale = 1.9)
Draw('Lep0Eta', 'ElEl', lev, 2, 'Lep #eta', 'Events', False, maxscale = 1.9)
Draw('DYMass', 'MuMu', lev, 10, 'm_{#mu#mu} (GeV)', 'Events', False, maxscale = 1.9)
Draw('DYMass', 'ElEl', lev, 10, 'm_{ee} ',          'Events', False, maxscale = 1.9)
for chan in ['ElEl', 'MuMu']: 
  Draw('MET', chan, 'ZVeto', 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
  Draw('MET', chan, '2jetsnomet', 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
for chan in ['ElEl', 'MuMu', 'ElMu']:
  Draw('NJets',  chan, 'dilepton', 1, 'Jet multiplicity', 'Events', True)
  Draw('Yields', chan, '', 1, 'Level', 'Events', False, maxscale = 1.2)
  Draw('YieldsSS', chan, '', 1, 'Level', 'Events', False, maxscale = 1.2)
  for lev in ['dilepton', '2jets']:
    if lev == '2jets' and chan != 'ElMu': continue
    Draw('Lep0Eta', chan, lev, 2, 'Lep #eta', 'Events', False, maxscale = 1.6)
    Draw('Lep0Pt', chan, lev, 2, 'Leading lep p_{T} (GeV)', 'Events', False, maxscale = 1.6)
    Draw('Lep1Pt', chan, lev, 2, 'Subeading lep p_{T} (GeV)', 'Events', False, maxscale = 1.6)
    Draw('DilepPt', chan, lev, 2, 'Dilepton p_{T} (GeV)', 'Events', False, maxscale = 1.6)
    Draw('DeltaPhi', chan, lev, 2, '#Delta#phi(ll) (GeV)', 'Events', False, maxscale = 1.6)
    Draw('MET', chan, lev, 2, 'MET (GeV)', 'Events', False, maxscale = 1.6)
    Draw('HT', chan, lev, 4, 'H_{T} (GeV)', 'Events', False, maxscale = 1.6)

  lev = 'dilepton'
  Draw('Btags', chan, lev, 1, 'b tag multiplicity', 'Events', True, maxscale = 1.6)
  Draw('NBtagNJets', chan, lev, 1, 'nJets,nbtags', 'Events', True,['[0,0]', '[1,0]', '[1,1]', '[2,0]', '[2,1]', '[2,2]', '[#geq 3,#geq 0]'],maxscale = 1.6 )
  Draw('Vtx', chan, lev, 1, 'Number of vertices', 'Events', False, maxscale = 1.6 )
  for lev in ['dilepton', '2jets']:
    Draw('InvMass', chan, lev, 20, 'm_{e#mu} (GeV)', 'Events', False, maxscale = 1.6 )
  for lev in ['2jets']:
    Draw('Jet0Pt', chan, lev, 4, 'Leading jet p_{T} (GeV)', 'Events', False, maxscale = 1.6 )
    Draw('Jet1Pt', chan, lev, 5, 'Subeading jet p_{T} (GeV)', 'Events', False, maxscale = 1.6 )
    Draw('Jet0Eta', chan, lev, 5, 'Leading jet #eta', 'Events', False, maxscale = 1.6 )
    Draw('Jet1Eta', chan, lev, 5, 'Subleading jet #eta', 'Events', False, maxscale = 1.6 )

'''
Draw('InvMass2', 'Muon', lev, 1, 'm(#mu#mu) (GeV)', 'Events', False, maxscale = 1.6)
Draw('InvMass2', 'Elec', lev, 1, 'm(ee) (GeV)', 'Events', False, maxscale = 1.6)
Draw('NJets', ch, lev,  1  , 'Jet multiplicity', 'Events', True)
Draw('NJets', 'Elec', lev,  1  , 'Jet multiplicity', 'Events', True)
Draw('NJets', 'Muon', lev,  1  , 'Jet multiplicity', 'Events', True)
Draw('NBtagJets', ch, '2jets', 1, 'b tag multiplicity', 'Events', maxscale = 1.6)
Draw('NBtagJets', 'Elec', '2jets', 1, 'b tag multiplicity', 'Events', maxscale = 1.6)
Draw('NBtagJets', 'Muon', '2jets', 1, 'b tag multiplicity', 'Events', maxscale = 1.6)
Draw('MuonEta',  'ElMu', '1btag',  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('ElecEta',  'ElMu', '1btag',  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('MuonPt',  'ElMu', '1btag',  50, 'Muon p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('ElecPt',  'ElMu', '1btag',  50, 'Electron p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('MuonEta',  'ElMu', lev,  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('ElecEta',  'ElMu', lev,  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('MuonPt',  'ElMu', lev,  50, 'Muon p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('ElecPt',  'ElMu', lev,  50, 'Electron p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('MuonPt',  'Muon', lev,  50, 'Muon p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('ElecPt',  'Elec', lev,  50, 'Electron p_{T} (GeV)', 'Events / 5 GeV', True)
Draw('MuonEta',  'Muon', lev,  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('ElecEta',  'Elec', lev,  1, 'Electron #eta', 'Events', True, maxscale = 1.5)
Draw('Jet0Eta',  ch, '1btag',  1, 'Leading jet #eta', 'Events', True, maxscale = 1.5)
Draw('Jet1Eta',  ch, '1btag',  1, 'Subleading jet #eta', 'Events', True, maxscale = 1.5)
Draw('Jet0Pt',  ch, '1btag',  50, 'Leading jet p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('Jet1Pt',  ch, '1btag',  50, 'Subleading jet p_{T} (GeV)', 'Events / 5 GeV', False)
Draw('Vtx',    'ElMu', lev,  1,   'Number of vertices', 'Events', True)
Draw('Vtx',    'Muon', lev,  1,   'Number of vertices', 'Events', True)
Draw('Vtx',    'Elec', lev,  1,   'Number of vertices', 'Events', True)
'''
'''
Draw('Lep0Eta',  ch, lev,  1, 'Leading lepton #eta', 'Events', True, maxscale = 1.5)
Draw('JetAllEta',  ch, lev,  1, 'All Jets #eta', 'Events', True, maxscale = 1.5)
Draw('JetAllPt',  ch, lev,  100, 'All Jets p_{T} (GeV)', 'Events / 10 GeV', True, maxscale = 1.5)
Draw('HT',  ch, lev,  1, 'HT p_{T} (GeV)', 'Events / 10 GeV', maxscale = 1.5) 
'''
'''
for lev in ['dilepton','2jets', '1btag']:
  for ch in ['Muon','Elec','ElMu']:
    chtag = '#mu#mu'
    if ch == 'Elec': chtag = 'ee'
    elif ch == 'ElMu': chtag = 'e#mu'

   Draw('DelLepPhi',  ch, lev, 10, '#Delta#phi (%s)'%chtag, 'Events', True,maxscale = 1.5)

   Draw('NJets', ch, lev,  1  , 'Jet multiplicity', 'Events', True)
   Draw('MET',   ch, lev,  100, 'Missing E_{T} (GeV)', 'Events / 10 GeV', True)
   Draw('MT2',   ch, lev,  100, 'm_{T2} (GeV)', 'Events / 10 GeV', True, setLogY = True)
   Draw('Lep0Eta',  ch, lev,  5, 'Leading lepton #eta', 'Events', True, maxscale = 1.5)
   Draw('Lep1Eta',  ch, lev,  5, 'Subleading lepton #eta', 'Events', True, maxscale = 1.5)
   Draw('Jet0Eta',  ch, lev,  5, 'Leading jet #eta', 'Events', True, maxscale = 1.5)
   Draw('Jet1Eta',  ch, lev,  5, 'Subleading jet #eta', 'Events', True, maxscale = 1.5)

   Draw('NBtagsNJets', ch, lev, 1, 'nJets,nbtags', 'Events', True,['[0,0]', '[1,0]', '[1,1]', '[2,1]', '[2,0]', '[2,1]', '[2,2]', '[3,0]', '[3,1]', '[3,2]', '[3,3]', '[4,0]', '[4,1]', '[4,2]', '[4,3]'],maxscale = 1.5 )

   Draw('DelLepEta',  ch, lev,  6, '#Delta#eta (%s)'%chtag, 'Events', True)
  
 #Draw('HT',        ch, lev,235, 'H_{T} (GeV)', 'Events / 20 GeV', True)
   Draw('InvMass',  ch, lev, 10, 'm(%s)'%chtag, 'Events / 10 GeV', True)
   Draw('InvMass2', ch, lev, 10, 'm(%s)'%chtag, 'Events / 1 GeV', False, maxscale = 1.4)
   Draw('NJets', ch, lev, 1, 'Jet multiplicity', 'Events', True)
   Draw('NBtagJets', ch, lev, 1, 'b tag multiplicity', 'Events', True,maxscale = 1.5)
   Draw('Lep0Pt',  ch, lev,  100, 'Leading lepton p_{T} (GeV)', 'Events / 10 GeV', True,)
   Draw('Lep1Pt',  ch, lev,  100, 'Subleading lepton p_{T} (GeV)', 'Events / 10 GeV', True)
   Draw('Jet0Pt',  ch, lev,  100, 'Leading jet p_{T} (GeV)', 'Events / 10 GeV', True)
   Draw('Jet1Pt',  ch, lev,  100, 'Subleading jet p_{T} (GeV)', 'Events / 10 GeV', True)
   Draw('DiLepPt', ch, lev,  100, 'p_{T}(%s) (GeV)'%(chtag), 'Events / 10 GeV', True)
  
   Draw('Vtx',    ch, lev,  1,   'Number of vertices', 'Events', True)
  
   if ch != 'Muon':
     Draw('ElecPt',  ch, lev,  100, 'Electron p_{T} (GeV)', 'Events / 10 GeV', True)
     Draw('ElecEta',  ch, lev,  5, 'Electron #eta', 'Events', True, maxscale = 1.5)
   if ch != 'Elec':
     Draw('MuonPt',  ch, lev,  100, 'Muon p_{T} (GeV)', 'Events / 10 GeV', True)
     Draw('MuonEta',  ch, lev,  5, 'Muon #eta', 'Events', True, maxscale = 1.5)
'''
