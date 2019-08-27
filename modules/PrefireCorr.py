import os,sys,re
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
import ROOT
from ROOT.TMath import Sqrt as sqrt
ROOT.PyConfig.IgnoreCommandLineOptions = True

class PrefCorr:
    def __init__(self, jetroot="L1prefiring_jetpt_2017BtoF.root", jetmapname="L1prefiring_jetpt_2017BtoF",
                 photonroot="L1prefiring_photonpt_2017BtoF.root", photonmapname="L1prefiring_photonpt_2017BtoF"):

        self.photon_file = self.open_root(basepath + "/inputs/prefire_maps/" + photonroot)
        self.photon_map = self.get_root_obj(self.photon_file, photonmapname)

        self.jet_file = self.open_root(basepath + "/inputs/prefire_maps/" + jetroot)
        self.jet_map = self.get_root_obj(self.jet_file, jetmapname)

        self.UseEMpT = ("jetempt" in jetroot)
        print 'Calculating prefire weights with the files: '
        print ' >> Jets   : %s'%jetroot
        print ' >> Photons: %s'%photonroot

    def open_root(self, path):
        r_file = ROOT.TFile.Open(path)
        if not r_file.__nonzero__() or not r_file.IsOpen(): raise NameError('File ' + path + ' not open')
        return r_file

    def get_root_obj(self, root_file, obj_name):
        r_obj = root_file.Get(obj_name)
        if not r_obj.__nonzero__(): raise NameError('Root Object ' + obj_name + ' not found')
        return r_obj

    def beginFile(self, intree, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        '''
        self.out = intree 
        self.branchnames = ["PrefireWeight", "PrefireWeight_Up", "PrefireWeight_Down"]
        for bname in self.branchnames:
          self.out.branch(bname, "F")
        '''

    def GetWeight(self, event, direc = 0):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #jets = Collection(event,"Jet")

        # Options
        self.JetMinPt = 20 # Min/Max Values may need to be fixed for new maps
        self.JetMaxPt = 500
        self.JetMinEta = 2.0
        self.JetMaxEta = 3.0
        self.PhotonMinPt = 20
        self.PhotonMaxPt = 500
        self.PhotonMinEta = 2.0
        self.PhotonMaxEta = 3.0

        #for i,bname in zip([0,1,-1], self.branchnames):
        #self.branchnames = ["PrefireWeight", "PrefireWeight_Up", "PrefireWeight_Down"]
        self.variation = direc
        prefw = 1.0

        for jid in range(event.nJet): 
          jetpf = 1.0
          PhotonInJet = []

          jetpt = event.Jet_pt[jid]
          if self.UseEMpT: jetpt *= (event.Jet_chEmEF[jid] + event.Jet_neEmEF[jid])

          if jetpt >= self.JetMinPt and abs(event.Jet_eta[jid]) <= self.JetMaxEta and abs(event.Jet_eta[jid]) >= self.JetMinEta:
            jetpf *= 1-self.GetPrefireProbability(self.jet_map, event.Jet_eta[jid], jetpt, self.JetMaxPt)

          phopf = self.EGvalue(event, jid)
          prefw *= min(jetpf,phopf) # The higher prefire-probablity between the jet and the lower-pt photon(s)/elecron(s) from the jet is chosen

        prefw *= self.EGvalue(event, -1) # Then loop over all photons/electrons not associated to jets
        '''
        self.out.fillBranch(bname, prefw)
        '''
        return prefw

    def GetWeightUp(self, event):
      return self.GetWeight(event, direc = 1)

    def GetWeightDown(self, event):
      return self.GetWeight(event, direc = -1)

    def EGvalue(self, event, jid):
      #photons = Collection(event,"Photon")
      #electrons = Collection(event,"Electron")
      phopf = 1.0
      PhotonInJet = []

      for pid in range(event.nPhoton): #,pho in enumerate(photons):
        if event.Photon_jetIdx[pid] == jid:
          if event.Photon_pt[pid] >= self.PhotonMinPt and abs(event.Photon_eta[pid]) <= self.PhotonMaxEta and abs(event.Photon_eta[pid]) >= self.PhotonMinEta:
            phopf_temp = 1-self.GetPrefireProbability(self.photon_map, event.Photon_eta[pid], event.Photon_pt[pid], self.PhotonMaxPt)

            elepf_temp = 1.0
            if event.Photon_electronIdx[pid] > -1: # What if the electron corresponding to the photon would return a different value?
              if event.Electron_pt[event.Photon_electronIdx[pid]] >= self.PhotonMinPt and abs(event.Electron_eta[event.Photon_electronIdx[pid]]) <= self.PhotonMaxEta and abs(event.Electron_eta[event.Photon_electronIdx[pid]]) >= self.PhotonMinEta:
                elepf_temp = 1-self.GetPrefireProbability(self.photon_map, event.Electron_eta[event.Photon_electronIdx[pid]], event.Electron_pt[event.Photon_electronIdx[pid]], self.PhotonMaxPt)

            phopf *= min(phopf_temp, elepf_temp) # The higher prefire-probablity between the photon and corresponding electron is chosen
            PhotonInJet.append(pid)

      for eleid in range(event.nElectron): #electrons:
        if event.Electron_jetIdx[eleid] == jid and (event.Electron_photonIdx[eleid] not in PhotonInJet):
          if event.Electron_pt[eleid] >= self.PhotonMinPt and abs(event.Electron_eta[eleid]) <= self.PhotonMaxEta and abs(event.Electron_eta[eleid]) >= self.PhotonMinEta:
            phopf *= 1-self.GetPrefireProbability(self.photon_map, event.Electron_eta[eleid], event.Electron_pt[eleid], self.PhotonMaxPt)

      return phopf

    def GetPrefireProbability(self, Map, eta, pt, maxpt):
      bin = Map.FindBin(eta, min(pt, maxpt-0.01))
      pref_prob = Map.GetBinContent(bin)

      stat = Map.GetBinError(bin) # bin statistical uncertainty
      syst = 0.2*pref_prob # 20% of prefire rate

      if self.variation == 1: 
        pref_prob = min(pref_prob + sqrt(stat*stat + syst*syst), 1.0)
      if self.variation == -1:
        pref_prob = max(pref_prob - sqrt(stat*stat + syst*syst), 0.0)
      return pref_prob

PrefCorr5TeV = lambda : PrefCorr(jetroot="L1prefiring_jetpt_2017BtoF.root", jetmapname="L1prefiring_jetpt_2017BtoF",
                 photonroot="L1prefiring_photonpt_2017BtoF.root", photonmapname="L1prefiring_photonpt_2017BtoF")
