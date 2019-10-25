from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

from scripts.DrellYanDataDriven import DYDD
from scripts.NonpromptDataDriven import NonpromptDD
from scripts.CrossSection import CrossSection

process = processDic
def xsec(chan = 'ElMu', lev = 'ww'):
  x = CrossSection(outpath, chan, lev)
  x.SetTextFormat("tex")
  bkg = []
  bkg.append(['top',           process['top'],  0.20])
  bkg.append(['DY',            process['DY'],   0.15])
  bkg.append(['Nonprompt lep', process['Nonprompt'], 0.50])
  bkg.append(['VZ',            process['VZ'],   0.30])
  signal   = ['WW',            process['WW']]
  data     = process['data']
  expunc = "MuonEff, ElecEff, PU, JES, JER, TrigEff, Prefire" # JER
  modunc = []#"pdf, scale"

  x.ReadHistos(path, chan, lev, bkg = bkg, signal = signal, data = data, expUnc = expunc, modUnc = modunc)
  #x.AddModUnc('Underlying Event','TT_TuneCP5up','TT_TuneCP5down')
  x.SetLumi(296.1)
  x.SetLumiUnc(0.035)
  #x.AddModUnc('hdamp','TT_hdampUP','TT_hdampDOWN')

  '''
  if doDD:
    d = DYDD(path,outpath,chan,lev)
    DYy, DYerr = d.GetDYDD()
    x.AddBkg('DYDD', DYy, 0, 0.15, DYerr)

    f = NonpromptDD(path, level = lev)
    fy, fe = f.GetNonpromptDD(chan)
    x.AddBkg('Nonprompt lep', fy, 0, 0.30, fe)
  '''
  suf = '_'+chan+'_'+lev+'_'+('DD' if doDD else 'MC')
  x.PrintYields('Yields'+suf)
  x.PrintSystTable('Systematics'+suf)
  x.PrintXsec('CrossSection'+suf)

xsec()
#xsec('MuMu',lev)
