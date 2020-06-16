'''
 Analysis ttxsec, created by xuAnalysis
 https://github.com/GonzalezFJR/xuAnalysis
'''

import os,sys
sys.path.append(os.path.abspath(__file__).rsplit("/xuAnalysis/",1)[0]+"/xuAnalysis/")
from framework.analysis import analysis
import framework.functions as fun
from ROOT import TLorentzVector

class ttxsec(analysis):
  def init(self):
    # Create your histograms here
    self.CreateTH1F("InvMass", "m_{#mu#mu} (GeV)", 20, 0.00, 2000.00)


  def insideLoop(self,t):
    # WRITE YOU ANALYSIS HERE


    # Selection

    # As an example: select medium ID muons and fill an histogram with the invariant mass
    selMuon = [];
    for imu in range(t.nMuon):
      if t.Muon_mediumId[imu]:
        v = TLorentzVector()
        v.SetPtEtaPhiM(t.Muon_pt[imu], t.Muon_eta[imu], t.Muon_phi[imu], t.Muon_mass[imu])
        selMuon.append(fun.lepton(v, t.Muon_charge[imu], 13))

      # Invariant mass, using a predefined function 
      invmass = fun.InvMass(selMuon[0], selMuon[1]) if len(selMuon) >= 2 else 0
  
    # Requirements
    if not len(selMuon) >= 2: return

    # Filling the histograms
    self.obj['InvMass'].Fill(invmass)
