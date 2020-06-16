# python RunCombine.py -m impacts --var dnn --mStop 275 --mLSP 70 -c all --noDoCard
# python RunCombine.py -m FitDiagnostics --var dnn --mStop 235 --mLSP 60 -c all --noDoCard 

from GetLimits import * 

def execute(command, pretend=False):
  print command
  if pretend: return command
  os.system(command)

datacard = DoCard(mStop, mLSP, var, year, ch, not noDoCards, sufix)
outnamepref = lambda var, ms, ml, year, ch : '%s_%s_%s%s%s'%(var, str(ms), str(ml), '' if year not in [2016,2017,2018] else '_'+str(year), '' if ch not in ['emu', 'mumu', 'ee'] else '_'+ch)
outdir = 'results/15jun/'
if not os.path.isdir(outdir): execute('mkdir -p '+outdir)
pathToScripts = '../scripts/'

if mode=='FitDiagnostics':
  command = 'combine -M FitDiagnostics --saveShapes --saveWithUncertainties --robustFit 1 --rMin -20 ' + datacard
  execute(command, pretend)
  outname = 'postfit_' + outnamepref(var,mStop,mLSP,year,ch)
  execute('mv fitDiagnostics.root %s%s.root'%(outdir,outname),pretend)
  
elif mode=='impacts':
  scriptName = 'estimateImpact_Asimov.sh' if runblind else 'estimateImpact.sh'
  dataname = datacard[:-4]
  command = 'source %s%s %s'%(pathToScripts, scriptName, dataname)
  if os.path.isfile('impacts.json'): execute('rm impacts.json', pretend)
  execute(command, pretend)
  outname = 'impacts_%s_'%('exp' if runblind else 'obs') + outnamepref(var,mStop,mLSP,year,ch)
  execute('mv impacts.pdf %s%s.pdf'%(outdir,outname),pretend)
