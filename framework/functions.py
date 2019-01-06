##############################################################################
# 
# Includes several classes (lepton, jet, ...)
# Several function to calculate kinematic observables, etc.
# 

from ROOT import TLorentzVector, TMath

#################################################################################    
### Class particle
#################################################################################    
class object:

  def SetP(self, pvec):
    self.p = pvec

  def SetCharge(self, c):
    self.charge = c

  def SetFlav(self, f):
    self.pdgid = f

  def SetPDGid(self, pdgid):
    self.pdgid = pdgid

  def SetSF(self, SF, error = 0):
    self.SF = SF
    self.SFerr = error

  def SetIso(self, iso):
    self.iso = iso

  def SetSFup(self, SFup):
    self.SFup = SFup

  def SetSFdo(self, SFdo):
    self.SFdo = SFdo

  def SetPtUp(self, ptup):
    self.ptUp = ptup

  def SetPtUp(self, ptup):
    self.ptUp = ptup

  ###############################
  ### Get methods

  def GetType(self):
    return self.pdgid

  def GetPDGid(self):
    return self.pdgid

  def Pt(self):
    return self.p.Pt()

  def Eta(self):
    return self.p.Eta()

  def Phi(self):
    return self.p.Phi()

  def M(self):
    return self.p.M()

  def P(self):
    return self.p

  def GetSF(self):
    return self.SF
  
  def GetSFUp(self):
    if self.SFerr != 0 and self.SFup == 1: return self.SF + self.SFerr
    else: return self.SFup

  def GetSFDown(self):
    if self.SFerr != 0 and self.SFdo == 1: return self.SF - self.SFerr
    else: return self.SFdo

  def GetPtUp(self):
    return self.ptUp

  def GetPtDown(self):
    return self.ptDo

  ###############################
  ### Kinematics

  def DeltaR(self, obj):
    return self.p.DeltaR(obj.p)

  def DeltaPhi(self, obj):
    t = obj if isinstance(obj, TLorentzVector) else obj.p
    return self.p.DeltaPhi(t)

  def MatchToParticle(self, listOfParticles, dRval = 0.4):
    ''' Return index of matched paricle in the list, or -1 if not matched. '''
    minDR = 999; index = -1; i = 0;
    for part in listOfParticles:
      dR = self.DeltaR(part)
      if dR < minDR: 
        minDR = dR
        index = i
        i += 1
    if minDR > dRval: index = -1
    return index

  def IsClean(self, listOfParticles, dRval = 0.4):
    ''' Returns True if it's clean from all particles in the list.  '''
    return self.MatchToParticle(listOfParticles, dRval) == -1

  ###############################
  ### Initialize
  def resetValues(self):
    self.SF    = 1; self.SFerr = 0; self.SFup = 1; self.SFdo = 1;
    self.ptUp = self.Pt(); self.ptDo = self.Pt();
    self.iso   = -1

  def __init__(self, pvec = TLorentzVector(), charge = 0, pdgid = -1):
    self.SetP(pvec)
    self.SetCharge(charge)
    self.SetFlav(pdgid)
    self.resetValues()


#################################################################################    
### Class lepton
#################################################################################    
class lepton(object):

  ###############################
  ### Set methods

  def SetMuon(self):
    self.pdgid = 13

  def SetElec(self):
    self.pdgid = 11

  ###############################
  ### Get methods

  def IsMuon(self):
    return self.pdgid == 13

  def IsElec(self):
    return self.pdgid == 11

#################################################################################    
### Class jet
#################################################################################    
class jet(object):

  ###############################
  ### Set methods

  def SetJetId(self, jid):
    self.jetid = id

  def SetCSVv2(self, csv):
    self.CSVv2 = csv

  def SetDeepCSV(self, csv):
    self.DeepCSV = csv

  def SetBtag(self, isbtag = True):
    self.isbtag = isbtag

  ###############################
  ### Get methods

  def GetJetId(self):
    return self.jetid

  def GetCSVv2(self):
    return self.CSVv2

  def GetDeepCSV(self):
    return self.DeepCSV

  def IsBtag(self):
    return self.isbtag

  ###############################
  ### Initialize
  def resetValues(self):
    self.ptUp = self.Pt(); self.ptDo = self.Pt();
    self.isbtag = False

  def __init__(self, pvec = TLorentzVector(), csv = -1, mcId = -1, jid = 0, deepcsv = -1):
    self.SetP(pvec)
    self.SetCSVv2(csv)
    self.SetDeepCSV(deepcsv)
    self.SetFlav(mcId)
    self.SetJetId(jid)
    self.resetValues()

def SortByPt(vec):
  pt = [v.Pt() for v in vec]
  vec = [j for _,j in sorted(zip(pt,vec))]
  return vec


########################################################################################
########################################################################################
### Kinematics

def InvMass(obj1, obj2):
  ''' Invariant mass of two objects '''
  return (obj1.p+obj2.p).M()

def DiPt(obj1, obj2):
  ''' Di-object pT '''
  return (obj1.p+obj2.p).Pt()

def DeltaPhi(obj1, obj2):
  ''' Delta phi between objects '''
  return obj1.DeltaPhi(obj2)

def MT(obj1, obj2):
  ''' Transverse mass of the diobject system '''
  return obj1.Pt()*obj2.Pt()*(1-TMath.Cos(obj1.DeltaPhi(obj2)))

def GetNBtags(listOfJets):
  ''' Returns the number of btag jets in the list of jets '''
  nbtags = 0
  for jet in listOfJets:
    if jet.IsBtag(): nbtags+=1
  return nbtags

def GetObjMinDR(list1, list2 = ''):
  ''' DR '''
  minDR = 999
  o1 = 0; o2 = 0
  if list2 == '':
    for obj1 in list1:
      for obj2 in list1:
        if obj1 == obj2: continue
        dr = obj1.DeltaR(obj2)
        if dr < minDR:
          minDR = dr
          o1 = obj1
          o2 = obj2
    return o1, o2
  else:
    l = list1
    for obj in list2:
      dr = l.DeltaR(obj)
      if dr < minDR:
        minDR = dr
        o1 = obj
    return o1
  return o1, o2


def GetLbMass(lep, jets, btags):
  ''' Returns the invariant mass of a b jet and lepton '''
  m = 0
  if len(btags) == 0:
    m = (lep.p + jets[0].p).M()
  elif len(btags) == 1:
    m = (lep.p + btags[0].p).M()
  elif len(btags) >= 2:
    m = (lep.p + GetObjMinDR(lep, btags).p).M()
  return m
