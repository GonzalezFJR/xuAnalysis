import os, sys
from ROOT import TFile
'''
 Usage:
  sfr = SFreader()
  sfr.LoadHisto(path, filename1, histoname1, 'mynum')
  sfr.LoadHisto(path, filename2, histoname2, 'myden')
  sfr.SetNum('mynum')
  sfr.SetDen('myden')
  SF, SFerr = GetSF(pt, eta)
  SF, SFerr = GetSF2(pt1, eta1, pt2, eta2)
'''
class SFreader:

  def LoadHisto(self, path, fname, hname, name=''):
    if not path.endswith('/'): path += '/'
    if not fname.endswith('.root'): fname += '.root'
    if not os.path.isfile(path+fname):
      print 'ERROR: file %s not found'%(path+fname)
      return
    f = TFile.Open(path+fname)
    if not hasattr(f, hname):
      print 'ERROR: object %s not found in %s'%(hname, path+fname)
      return
    h = getattr(f, hname)
    h.SetDirectory(0)
    f.Close()
    if name == '': name = hname
    self.histos[name] = h
    if self.verbose: print '[SFreader::INFO] Loaded histo %s'%name

  def GetHisto(self, name):
    if not name in self.histos.keys():
      print '[SFreader::ERROR] Object %s not found'%name
      return None
    else: return self.histos[name]

  def GetValFromHisto(self, h, x, y, var=0):
    if y <= 25: y = 25.001 # Extend bin to 20 GeV
    if x >= 2.4 : x = 2.39 # Extend bin to 2.5
    if isinstance(h, str): h = self.GetHisto(h)
    b = h.FindBin(x,y,1)
    val = h.GetBinContent(b)
    err = h.GetBinError(b)
    return val
    if   var >= 1: return val+err
    elif var <=-1: return val-err
    else         : return val

  def GetNumDen(self, x, y, hname, var=0):
    name = lambda tip, dat, s: '%s%s%s'%(tip, dat, ('Up' if s == 1 else ('Do' if s == -1 else '')))
    num = self.GetValFromHisto(name(hname, 'Data', 0), x, y, 0)
    den = self.GetValFromHisto(name(hname, 'MC',   0), x, y, 0)
    if var != 0:
      num = num+self.GetValFromHisto(name(hname, 'Data', var), x, y, var)*var
      den = den+self.GetValFromHisto(name(hname, 'MC',   var), x, y, var)*var
    return num, den

  def GetSF(self, x, y, hname, var=0):
    num, den = self.GetNumDen(x, y, hname, var)
    return num/den if den != 0 else 1

  def GetSF2(self, x1, y1, x2, y2, hname, hname2='', var=0):
    if hname2 == '': hname2 = hname
    geteff = lambda e1,e2 : e1+e2-e1*e2
    n1, d1 = self.GetNumDen(x1, y1, hname,  var)
    n2, d2 = self.GetNumDen(x2, y2, hname2, var)
    neff = geteff(n1, n2)
    deff = geteff(d1, d2)
    SF    = neff/deff if deff != 0 else 1
    return SF

  def __init__(self, verbose=False):
    self.verbose = verbose
    self.histos = {}
