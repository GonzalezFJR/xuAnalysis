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

  def GetFlav(self):
    return self.pdgid

  def GetIso(self):
    return self.iso

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
    t = obj if isinstance(obj, TLorentzVector) else TLorentzVector(obj.p)
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

  def __init__(self, pvec = TLorentzVector(), charge = 0, pdgid = -1, mcmatch=-1, passTightID = True):
    self.SetP(pvec)
    self.SetCharge(charge)
    self.SetFlav(pdgid)
    self.resetValues()
    self.mcmatch = mcmatch
    self.passTightID = passTightID
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

  def SetDeepJet(self, csv):
    self.DeepJet = csv

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

  def GetDeepJet(self):
    return self.DeepJet

  def IsBtag(self):
    return self.isbtag

  ###############################
  ### Initialize
  def resetValues(self):
    self.ptUp = self.Pt(); self.ptDo = self.Pt();
    self.isbtag = False

  def __init__(self, pvec = TLorentzVector(), csv = -1, mcId = -1, jid = 0, deepcsv = -1, deepjet = -1):
    self.SetP(pvec)
    self.SetCSVv2(csv)
    self.SetDeepCSV(deepcsv)
    self.SetDeepJet(deepjet)
    self.SetFlav(mcId)
    self.SetJetId(jid)
    self.resetValues()

def SortByPt(vec):
  pt = [v.Pt() for v in vec]
  vec = [j for _,j in sorted(zip(pt,vec))]
  return vec

def SortByIso(vec):
  iso = [v.iso for v in vec]
  vec = [j for _,j in sorted(zip(iso,vec))]
  return vec



########################################################################################
########################################################################################
### Kinematics

def InvMass(obj1, obj2 = 0, obj3 = 0):
  ''' Invariant mass of two objects '''
  if isinstance(obj1, list):
    ob = TLorentzVector(obj1[0].p)
    for o in obj1[1:]: ob+=o.p
    return ob.M()
  elif obj3 == 0: return (obj1.p+obj2.p).M()
  else:           return (obj1.p+obj2.p+obj3.p).M()

def DiPt(obj1, obj2):
  ''' Di-object pT '''
  return (obj1.p+obj2.p).Pt()

def DeltaPhi(obj1, obj2):
  ''' Delta phi between objects '''
  return obj1.DeltaPhi(obj2)

def MT(obj1, obj2):
  ''' Transverse mass of the diobject system '''
  return TMath.Sqrt(2*obj1.Pt()*obj2.Pt()*(1-TMath.Cos(obj1.DeltaPhi(obj2))))

def CheckZpair(lep1, lep2):
  ''' Returns: mZ if OSSF, 0 otherwise '''
  if not abs(lep1.GetPDGid()) == abs(lep2.GetPDGid()): return 0
  if not lep1.charge*lep2.charge < 0: return 0
  return InvMass(lep1,lep2)

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

def GetLumi(year, era = 'all'):
  lumi = {
    2016 : {
             'B' : 5.783,
             'C' : 2.5639,
             'D' : 4.248,
             'E' : 4.0089,
             'F' : 3.101,
             'G' : 3.1013,
             'H' : 7.54,
             'all': 35.92,
           },
    2017 : {
             'B' : 4.823,
             'C' : 9.664,
             'D' : 4.252,
             'E' : 9.278,
             'F' : 13.540,
             'G' : 0.297,
             'H' : 0.22,
            'all': 41.53,
           },
     2018 : {
              'A' :  14.00,
              'B' :   7.10,
              'C' :   6.94,
              'D' :  31.93,
              'all': 59.74,
            }
  }
  return lumi[year][era]

def GetValue(tree, var, syst = '', index = -1):
  if syst == '':
    if hasattr(tree, var): return (getattr(tree, var) if index == -1 else getattr(tree, var)[index])
    else:
      print 'ERROR: var %s not in tree!!'%var
      return 0
  else:
    vars = "%s_%s"%(var,syst)
    vart = "%s%s"%(var,syst)
    if    hasattr(tree, vars): return (getattr(tree, vars) if index == -1 else getattr(tree, vars)[index])
    elif  hasattr(tree, vart): return (getattr(tree, vart) if index == -1 else getattr(tree, vart)[index])
    elif  hasattr(tree, var ): return (getattr(tree, var ) if index == -1 else getattr(tree, var )[index])
    else:
      print 'ERROR: var %s not in tree!!'%var
      return 0

def replaceWords(string, word, newstring):
  import re
  return re.sub(r'\b%s\b'%word, newstring, string)

