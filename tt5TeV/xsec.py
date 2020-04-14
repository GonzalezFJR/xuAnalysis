from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

from scripts.DrellYanDataDriven import DYDD
from scripts.NonpromptDataDriven import NonpromptDD
from scripts.CrossSection import CrossSection

process = processDic
DYsamples   = processDic['DY']
datasamples = processDic['data']
labdic = {
  'ElMu' : 'e#mu',
  'ElEl' : 'ee',
  'MuMu' : '#mu#mu',
  'Elec' : 'ee',
  'Muon' : '#mu#mu'
}
def xsec(chan = 'ElMu', lev = '2jets', doDD = False):
  x = CrossSection(outpath, chan, lev)
  x.SetTextFormat("tex")
  x.SetPathToTrees('/pool/ciencias/nanoAODv4/5TeV/5TeV_21nov2019/')
  bkg = []
  bkg.append(['tW',            process['tW'],   0.20])
  bkg.append(['Nonprompt lep', process['Nonprompt'], 0.50])
  if not doDD:# or chan == 'MuMu' or chan == 'ElEl':
    bkg.append(['DY',            process['DY'],   0.30])
  bkg.append(['VV',            process['VV'],   0.30])
  signal   = ['tt',            process['tt']]
  data     = process['data']
  expunc = "MuonEff, ElecEff, TrigEff, Prefire, JES, JER, Prefire, PU"#, JES, JER, TrigEff, Prefire" # JER
  modunc = "pdf, scale"#, isr, fsr"

  x.ReadHistos(path, chan, lev, bkg = bkg, signal = signal, data = data, expUnc = expunc, modUnc = modunc)
  x.SetLumi(296.1)
  x.SetLumiUnc(0.013)
  x.AddModUnc('Underlying Event','TT_TuneCP5up','TT_TuneCP5down')
  x.AddModUnc('hdamp','TT_hdampUP','TT_hdampDOWN')

  thr = TopHistoReader(path)
  thr.SetLumi(296.1)
  hname = 'Lep0Eta_%s_%s'%(chan, lev)
  if os.path.isfile(path+'/TTPS.root'):
    nom   = thr.GetNamedHisto(hname, 'TTPS').Integral()
    isrup = thr.GetNamedHisto(hname+'_ISRUp', 'TTPS').Integral()
    isrdo = thr.GetNamedHisto(hname+'_ISRDown', 'TTPS').Integral()
    fsrup = thr.GetNamedHisto(hname+'_FSRUp', 'TTPS').Integral()
    fsrdo = thr.GetNamedHisto(hname+'_FSRDown', 'TTPS').Integral()
    isr = (abs(isrdo-nom)/nom + abs(isrup-nom)/nom)/2
    fsr = (abs(fsrdo-nom)/nom + abs(fsrup-nom)/nom)/2
    x.AddModUnc('FSR', fsr)
    x.AddModUnc('ISR', isr)

  if doDD:
    d = DYDD(path,outpath,chan,lev, DYsamples=DYsamples, DataSamples=datasamples, lumi=Lumi, histonameprefix='', hname = 'DYHistoElMu' if chan == 'ElMu' else 'DYHisto')
    DYy, DYerr = d.GetDYDD()
    x.AddBkg('DYDD', DYy, 0, 0.30, DYerr)
    '''
    d = DYDD(path,outpath,chan,lev, DYsamples=DYsamples, DataSamples=datasamples, lumi=Lumi, histonameprefix='', hname = 'DYHistoElMu')
    if chan == 'ElMu': 
      DYy, DYerr = d.GetDYDD()
      x.AddBkg('DYDD', DYy, 0, 0.15, DYerr)
    else:
      SF, SFerr = d.GetScaleFactor()
      dy = x.GetBkg('DY').GetYield()
      print 'dy = ', dy
      print 'dy = ', dy*SFerr
      x.GetBkg('DY').SetYield(dy*SF)
      x.GetBkg('DY').SetStatUnc(dy*SFerr)
    '''

    #f = NonpromptDD(path, chan=chan, level=lev, process=processDic , lumi=Lumi, histonameprefix='',yieldsSSname='YieldsSS')
    #fy, fe = f.GetNonpromptDD(chan)
    #x.AddBkg('Nonprompt lep', fy, 0, 0.30, fe)

  suf = '_'+chan+'_'+lev+'_'+('DD' if doDD else 'MC')
  x.PrintYields('Yields'+suf)
  x.PrintSystTable('Systematics'+suf)
  x.PrintXsec('CrossSection'+suf)
  x.AddToTxt('ttxsec', labdic[chan])

lev = '2jets'
xsec('ElMu',lev,1)
xsec('MuMu',lev,1)
xsec('ElEl',lev,1)
