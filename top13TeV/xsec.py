from conf_andrea import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

from ttxsec.DrellYanDataDriven import DYDD
from ttxsec.NonpromptDataDriven import NonpromptDD
from tt5TeV.scripts.CrossSection import CrossSection
from framework.functions import GetLumi
year=2016
process = processDic

#outpath='/nfs/fanae/user/andreatf/PAFnanoAOD/temp%s_new/ver5/xsec/'%year
outpath='./temp%s'%year


pathToTrees = '/pool/cienciasrw/userstorage/juanr/nanoAODv4/22jul2019/%s/'%year
motherfname = 'TTTo2L2Nu_TuneCP5'#'TT_TuneCUETP8M2T4'#
sampleName='TTTo2L2Nu'
if year == 2016:
  #sample='TTTo2L2Nu'
  #motherfname = 'TTTo2L2Nu_TuneCP5_PSweights'
  sampleName = 'TT'
  motherfname = 'TT_TuneCUETP8M2T4'
  #tname = 'TT_TuneCUETP8M2T4'


DYsamples   = processDic[year]['DY']
datasamples = processDic[year]['data']
def xsec(chan = 'ElMu', lev = '2jets', doDD = False):
  x = CrossSection(outpath, chan, lev)
  x.SetPathToTrees(pathToTrees)
  x.SetMotherName(motherfname)
  x.SetTextFormat("tex")
  bkg = []
  bkg.append(['tW',            process[year]['tW'],   0.30])
  if not doDD:
    bkg.append(['DY',            process[year]['DY'],   0.15])
    bkg.append(['Nonprompt lep', process[year]['Nonprompt'], 0.50])
  bkg.append(['VV',            process[year]['VV'],   0.30])
  signal   = ['tt',            process[year]['t#bar{t}']]
  data     = process[year]['data']
  expunc = "MuonEff, ElecEff, PU, Btag, Mistag, Trig" # JER
  modunc = "pdf, scale, isr, fsr"

  x.ReadHistos(path[year], chan, lev, bkg = bkg,lumi=GetLumi(year)*1000, signal = signal, data = data, expUnc = expunc, modUnc = modunc, histoPrefix = 'H')
  x.SetBR(0.03263)
  x.SetLumi(GetLumi(year)*1000)
  x.SetLumiUnc(0.9*1000)  #0.9,  1 ,   1.5  , 
 # x.AddModUnc('Underlying Event','TT_TuneCUETP8M2T4down','TT_TuneCUETP8M2T4up')
 # x.AddModUnc('hdamp','TT_hdampUp','TT_hdampDown')

  if doDD:
    d = DYDD(path[year],outpath,chan,lev, DYsamples=DYsamples, DataSamples=datasamples, lumi=GetLumi(year)*1000)
    DYy, DYerr = d.GetDYDD()
    x.AddBkg('DYDD', DYy, 0, 0.15, DYerr)

    f = NonpromptDD(path[year], chan=chan, level=lev, process=processDic[year] , lumi=GetLumi(year)*1000)
    fy, fe = f.GetNonpromptDD(chan)
    x.AddBkg('Nonprompt lep', fy, 0, 0.30, fe)

  suf = '_'+chan+'_'+lev+'_'+('DD' if doDD else 'MC')
  x.PrintYields('Yields'+suf)
  x.PrintSystTable('Systematics'+suf)
  #x.PrintXsec('CrossSection'+suf)

  print(x.ComputeXsec(), x.GetXsecStatUnc()*100)

lev = '1btag'
xsec('ElMu',lev,0)
#xsec('MuMu',lev)
