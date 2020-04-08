import os, sys
from conf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)

year = 2018

#hm.SetHisto(hname, 1)
#hm16 = HistoManager(processes, systematics, '', path = path[2016], processDic = processDic[2016], lumi = GetLumi(2016)*1000)
#hm17 = HistoManager(processes, systematics, '', path = path[2017], processDic = processDic[2017], lumi = GetLumi(2017)*1000)
hm18 = HistoManager(processes, systematics, '', path = path[2018], processDic = processDic[2018], lumi = GetLumi(2018)*1000)

s = Stack(outpath = '/nfs/fanae/user/juanr/www/temp/%s/'%year)
s.SetColors(colors)
s.SetProcesses(processes)
s.SetLumi(GetLumi(year))# if not isinstance(year, str) else GetLumi(2016)+GetLumi(2017)+GetLumi(2018))

def Draw(var = 'H_Lep0Pt_ElMu_2jets', ch = 'ElMu', lev = 'dilepton', rebin = 1, xtit = '', ytit = 'Events', doStackOverflow = False, binlabels = '', setLogY = False, maxscale = 1.15):
  name = 'H_%s_%s_%s'%(var, ch, lev)
  #hm16.SetStackOverflow(doStackOverflow)
  #hm17.SetStackOverflow(doStackOverflow)
  hm18.SetStackOverflow(doStackOverflow)
  hm18.SetHisto(name, rebin)
  hm = hm18#hm16.Add(hm17).Add(hm18)
  s.SetHistosFromMH(hm)
  s.SetOutName(name)
  s.SetBinLabels(binlabels)
 
  ch  = name.split('_')[-2]
  lev = name.split('_')[-1]
  tch = '#mu#mu' if ch == 'Muon' else 'ee' 
  if   ch == 'ElMu': tch = 'e#mu'
  if   lev == '2jets': ch += ', #geq 2 jets'
  elif lev == '1btag': ch += ', #geq 2 jets, #geq 1 btag'
  s.SetTextChan(tch)

  s.SetLogY(setLogY)
  s.SetPlotMaxScale(maxscale)
  s.DrawStack(xtit, ytit)
  #hm16.Clear()
  #hm17.Clear()
  hm18.Clear()

lev = 'dilepton'
ch = 'ElMu'
for ch in ['Muon', 'Elec', 'ElMu']:
 for lev in ['dilepton', '2jets', '1btag']:
   chtag = '#mu#mu'
   if ch == 'Elec': chtag = 'ee'
   elif ch == 'ElMu': chtag = 'e#mu'
   #Draw('NBtagsNJets', ch, lev, 1, 'nJets,nbtags', 'Events', True, ['[0,0]', '[1,0]', '[1,1]', '[2,1]', '[2,0]', '[2,1]', '[2,2]', '[3,0]', '[3,1]', '[3,2]', '[3,3]', '[4,0]', '[4,1]', '[4,2]', '[4,3]'])
   Draw('NJets', ch, lev,  1  , 'Jet multiplicity', 'Events', True)
   Draw('MET',   ch, lev,  100, 'Missing E_{T} (GeV)', 'Events / 10 GeV', True)
   #Draw('MT2',   ch, lev,  100, 'm_{T2} (GeV)', 'Events / 10 GeV', True, setLogY = True)
   Draw('Lep0Eta',  ch, lev,  5, 'Leading lepton #eta', 'Events', True, maxscale = 1.5)
   #Draw('Lep1Eta',  ch, lev,  5, 'Subleading lepton #eta', 'Events', True, maxscale = 1.5)
   Draw('Jet0Eta',  ch, lev,  5, 'Leading jet #eta', 'Events', True, maxscale = 1.5)
   #Draw('Jet1Eta',  ch, lev,  5, 'Subleading jet #eta', 'Events', True, maxscale = 1.5)
   #Draw('DelLepPhi',  ch, lev, 10, '#Delta#phi (%s)'%chtag, 'Events', True)
   #Draw('DelLepEta',  ch, lev,  6, '#Delta#eta (%s)'%chtag, 'Events', True)
   #Draw('InvMass',  ch, lev, 10, 'm(%s)'%chtag, 'Events / 10 GeV', True)
   Draw('InvMass2', ch, lev, 10, 'm(%s)'%chtag, 'Events / 1 GeV', False, maxscale = 1.4)
   Draw('NBtagJets', ch, lev, 1, 'b tag multiplicity', 'Events', True)
   Draw('Lep0Pt',  ch, lev,  100, 'Leading lepton p_{T} (GeV)', 'Events / 10 GeV', True)
   #Draw('Lep1Pt',  ch, lev,  100, 'Subleading lepton p_{T} (GeV)', 'Events / 10 GeV', True)
   Draw('Jet0Pt',  ch, lev,  100, 'Leading jet p_{T} (GeV)', 'Events / 10 GeV', True)
   #Draw('Jet1Pt',  ch, lev,  100, 'Subleading jet p_{T} (GeV)', 'Events / 10 GeV', True)
   #Draw('DiLepPt', ch, lev,  100, 'p_{T}(%s) (GeV)'%(chtag), 'Events / 10 GeV', True)
   Draw('Vtx',    ch, lev,  1,   'Number of vertices', 'Events', True)
   #Draw('HT',        ch, lev,235, 'H_{T} (GeV)', 'Events / 20 GeV', True)
   #if ch != 'Muon':
   #  Draw('ElecPt',  ch, lev,  100, 'Electron p_{T} (GeV)', 'Events / 10 GeV', True)
   #  Draw('ElecEta',  ch, lev,  5, 'Electron #eta', 'Events', True, maxscale = 1.5)
   #if ch != 'Elec':
   #  Draw('MuonPt',  ch, lev,  100, 'Muon p_{T} (GeV)', 'Events / 10 GeV', True)
   #  Draw('MuonEta',  ch, lev,  5, 'Muon #eta', 'Events', True, maxscale = 1.5)
