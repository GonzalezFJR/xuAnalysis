import os,sys
mypath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(mypath)

def GetAnalysisTemplate(analysisName):
  body  = "'''\n Analysis %s, created by xuAnalysis\n https://github.com/GonzalezFJR/xuAnalysis\n'''\n\n"%analysisName
  body += 'import os,sys\nsys.path.append(os.path.abspath(__file__).rsplit("/xuAnalysis/",1)[0]+"/xuAnalysis/")\n'
  body += 'from framework.analysis import analysis\nimport framework.functions as fun\nfrom ROOT import TLorentzVector\n\n'
  body += 'class %s(analysis):\n'%analysisName
  body += '  def init(self):\n    # Create your histograms here\n    self.CreateTH1F("MuonInvMass", "m_{#mu#mu} (GeV)", 20, 0, 120)\n\n'
  body += '  def insideLoop(self,t):\n    # WRITE YOU ANALYSIS HERE\n'
  body += '    # As an example: select medium ID muons and fill an histogram with the invariant mass\n    selMuon = []; \n'
  body += '    for imu in range(t.nMuon):\n      if t.Muon_mediumId[imu]:\n'
  body += '        v = TLorentzVector()\n        v.SetPtEtaPhiM(t.Muon_pt[imu], t.Muon_eta[imu], t.Muon_phi[imu], t.Muon_mass[imu])\n'
  body += '        selMuon.append(fun.lepton(v, t.Muon_charge[imu], 13))\n\n'
  body += '    # At least two muons\n    if not len(selMuon) >= 2: return\n\n'
  body += '    # Invariant mass, using a predefined function \n    invmass = fun.InvMass(selMuon[0], selMuon[1])\n\n'
  body += '    # Fill the histogram\n    self.obj[\'InvMass\'].Fill(invmass)\n'
  return body

def CreateAnalysis(analysisName):
  if os.path.isdir(mypath+analysisName):
    print 'ERROR: analysis %s already exists!!!'%analysisName
    return
  os.mkdir(mypath + analysisName)
  f = open(mypath + analysisName + '/' + analysisName + '.py', 'w')
  body = GetAnalysisTemplate(analysisName)
  f.write(body)
  print 'Created analysis code in %s'%(mypath + analysisName)


import argparse
pr = argparse.ArgumentParser()
pr.add_argument('name', help='Name of the new analysis', type = str)
args = pr.parse_args()
analname = args.name
CreateAnalysis(analname)

