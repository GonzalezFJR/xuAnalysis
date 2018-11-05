import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from framework.analysis import analysis
import framework.functions as fun
from ROOT import TLorentzVector

class testAnalysis(analysis):
  def init(self):
    self.CreateTH1F('InvMass', 'InvMass', 20, 0, 120)
    self.CreateTH1F('LepPt', 'LepPt', 20, 0, 120)

  def insideLoop(self,t):
    # Simple analysis: lets draw the invariant mass of two muons
    # Lets require medium Id for the muons
    selMuon = []; 
    for imu in range(t.nMuon):
      if t.Muon_mediumId[imu]:
        v = TLorentzVector()
        v.SetPtEtaPhiM(t.Muon_pt[imu], t.Muon_eta[imu], t.Muon_phi[imu], t.Muon_mass[imu])
        selMuon.append(fun.lepton(v, t.Muon_charge[imu], 13))
    
    # At least two muons
    if not len(selMuon) >= 2: return

    # Invariant mass, using a predefined function 
    invmass = (selMuon[0].p + selMuon[1].p).M() #fun.InvMass(selMuon[0], selMuon[1])

    # Fill the histogram
    self.obj['InvMass'].Fill(invmass)
    self.obj['LepPt'].Fill(selMuon[0].Pt())
