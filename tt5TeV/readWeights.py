import os,sys
sys.path.append(os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/')
from plotter.TopHistoReader import TopHistoReader
from plotter.WeightReader import WeightReader
from ROOT.TMath import Sqrt as sqrt
from framework.functions import GetLumi
from plotterconf import *


### Input and output
'''
path = '/mnt_pool/ciencias_users/user/juanr/test/PAFnanoAOD/temp2017/'
sample = 'TTTo2L2Nu'

pathToTrees = '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2017/'
motherfname = 'TTTo2L2Nu'
'''

process = processDic
DYsamples   = processDic['DY']
datasamples = processDic['data']
sample = 'TT'
pathToTrees = '/pool/ciencias/userstorage/juanr/nanoAODv4/5TeV/5TeV_5sept/'
motherfname = 'TT_TuneCP5_PSweights_5p02TeV'

outpath = './outputs/'

## PDF and scale systematics
def DrawWeightSystematics(sample, chan = 'ElMu', lev = '2jets'):
  w = WeightReader(path, outpath, chan, lev, sampleName = sample, pathToTrees=pathToTrees, motherfname=motherfname, PDFname = 'PDFweights', ScaleName = 'ScaleWeights', lumi = 296.1, histoprefix='') #59.7
  w.PrintMEscale('ScaleWeights_'+chan+'_'+lev)
  w.PrintPDFyields('PDFweights_'+chan+'_'+lev)
  #w.PrintPSunc('PSunc_'+chan+'_'+lev)

DrawWeightSystematics(sample)
