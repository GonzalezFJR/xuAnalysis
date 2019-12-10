import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader
from plotter.WeightReader import WeightReader
from ROOT.TMath import Sqrt as sqrt

### Input and output

path = '/mnt_pool/ciencias_users/user/juanr/test/PAFnanoAOD/temp2017/'
sample = 'TTTo2L2Nu'

pathToTrees = '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2017/'
motherfname = 'TTTo2L2Nu'

outpath = './outputs/'

## PDF and scale systematics
def DrawWeightSystematics(sample, chan = 'ElMu', lev = '1btag'):
  w = WeightReader(path, outpath, chan, lev, sampleName = sample, pathToTrees=pathToTrees, motherfname=motherfname, PDFname = 'PDFweights', ScaleName = 'ScaleWeights', lumi = 41.5)
  w.PrintMEscale('ScaleWeights_'+chan+'_'+lev)
  w.PrintPDFyields('PDFweights_'+chan+'_'+lev)
  w.PrintPSunc('PSunc_'+chan+'_'+lev)

DrawWeightSystematics(sample)
