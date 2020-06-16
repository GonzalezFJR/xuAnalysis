import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)
from framework.fileReader import GetNGenEvents, GetFiles
from plotter.OutText import OutText

pathToTrees = '/pool/phedexrw/userstorage/juanr/5TeV24apr2020/'
sdic = {
  'tt'        : 'TT_TuneCP5_5p02TeV',
  'hdampUp'   : 'TT_hdampDOWN_TuneCP5_5p02TeV',
  'hdampDown' : 'TT_hdampUP_TuneCP5_5p02TeV',
  'UEUp'      : 'TT_TuneCP5up_5p02TeV',
  'UEDown'    : 'TT_TuneCP5down_5p02TeV',
}
snames = ['tt', 'hdampUp', 'hdampDown', 'UEUp', 'UEDown']

lev = {'dilepton':1, 'ZVeto':2, 'MET':3, '2jets':4, '1btag':5}

GetGenEv = lambda name : GetNGenEvents(GetFiles(pathToTrees, sdic[name]))
path = '/mnt_pool/ciencias_users/user/juanr/dev/xuAnalysis/tt5TeV/temp5TeV/'
Lumi = 304.32

printRecoAndGen = False
printGenAndStatUnc = True

# tt_hdampDown
nom  = 'tt'
syst = ['hdamp', 'UE']
thr = TopHistoReader(path)

GetAcc = lambda sample, chan, level : thr.GetNamedHisto('FiduEvents_%s'%chan, processDic[('tt_'if sample !='tt' else '') +sample]).GetBinContent(lev[level])/float(GetGenEv(sample))
RecoY  = lambda sample, chan, level : thr.GetNamedHisto('Lep0Eta_%s_%s'%(chan, level), processDic[('tt_'if sample !='tt' else '') +sample]).Integral()*Lumi

def GetAccWithUnc(sample, chan, level):
  h = thr.GetNamedHisto('FiduEvents_%s'%chan, processDic[('tt_'if sample !='tt' else '') +sample])
  nEv = h.GetBinContent(lev[level])
  genEv = GetGenEv(sample)
  nEvUnc = sqrt(nEv)
  acc = nEv/genEv
  unc = abs(acc - (nEv+nEvUnc)/genEv)
  return acc, unc


chan = 'ElMu'
l = 'dilepton'
GA = lambda v,c : [GetAcc(v, c, l), (GetAcc(v,c,l)-GetAcc('tt',c,l))/GetAcc('tt',c,l)*100]
RS = lambda v,c : [RecoY(v, c, l), (RecoY(v, c, l)-RecoY('tt', c,l))/RecoY('tt', c,l)*100]

def GetGAandUnc(sname, chan):
  nom, uncnom = GetAccWithUnc('tt', chan, l)
  var, uncvar = GetAccWithUnc(sname, chan, l)
  syst = (var - nom)/nom
  nomup = nom+uncnom
  varup = var+uncvar
  systup1 = (var-nomup)/nomup
  systup2 = (varup-nom)/nom
  systunc = sqrt( (syst-systup1)*(syst-systup1) + (syst-systup2)*(syst-systup2)  )
  return [nom, uncnom, var, uncvar, syst, systunc]

GetValAndUncString = lambda n,s : '%g \pm %1.2f%s'%(n, s/n*100, '%')

'''
def PrintLine(sample, chan):
  print "Nominal - Variation %s - uncertainty"%sample
  nom, uncnom, var, uncvar, syst, systunc = GetGAandUnc(sample, chan)
  print "%s - %s - %s"%(GetValAndUncString(nom, uncnom), GetValAndUncString(var, uncvar), GetValAndUncString(syst, systunc))

PrintLine('hdampUp', 'ElMu')
'''

if printRecoAndGen:
  t = OutText(outpath+'/genSyst/', 'genSyst_'+l, "new", textformat='tex')
  t.SetTexAlign("l c c c c c")
  nsem = 12
  t.SetSeparatorLength(nsem)
  #t.line('Underlying event and hdamp uncertainties at reco and gen level (%s)'%l)
  t.bar()
  firstline = ''
  for lab in snames: 
    firstline += t.vsep() + t.fix(lab,20)
  t.line(firstline)
  t.sep()
  for ch in ['ElEl', 'MuMu', 'ElMu']:
    for mode in ['Reco', 'Gen']:
      name = ('ee' if ch=='ElEl' else ('$\mu\mu$' if ch =='MuMu' else 'e$\mu$')) +' '+ mode
      name = t.fix(name, 10)
      for lab in snames:
        val, unc = GA(lab, ch) if mode == 'Gen' else RS(lab, ch)
        name += t.vsep() + (t.fix("%1.2f %s"%(unc, '\%'), 20) if lab!='tt' else t.fix("%g"%(val), 20))
        #name += t.vsep() + t.fix("%1.1f (%1.2f %s)"%(val, unc, '%'), 20)
      t.line(name)
  t.bar()
  t.write()

if printGenAndStatUnc:
  t = OutText(outpath+'/genSyst/', 'genSystWithUnc_'+l, "new", textformat='tex')
  t.SetTexAlign("l c c")
  t.SetSeparatorLength(12)
  t.bar()
  t.line('Variation' + t.vsep() + 'Acceptance' + t.vsep() + 'Uncertainty')
  t.sep()
  for ch in ['ElEl', 'MuMu', 'ElMu']:
    name = ('ee' if ch=='ElEl' else ('$\mu\mu$' if ch =='MuMu' else 'e$\mu$'))
    name = t.fix(name, 10)
    nom, uncnom, var, uncvar, syst, systunc = GetGAandUnc('tt', ch)
    t.line('Nominal %s'%name + t.vsep() + '%g (%1.2f%s)'%(nom, uncnom/nom*100, '\%') + t.vsep())
    for lab in snames[1:]:
      nom, uncnom, var, uncvar, syst, systunc = GetGAandUnc(lab, ch)
      t.line(lab +' '+ name + t.vsep() + '%g (%1.2f%s)'%(var, uncvar/var*100, '\%') + t.vsep() + '%1.2f%s %s %1.2f%s'%(syst*100, '\%', t.pm(), systunc*100, '\%')  )
    t.bar()
  t.bar()
  t.write()


