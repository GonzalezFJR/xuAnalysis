import ROOT
import math, os,re, tarfile, tempfile
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

libraries.append('WeightCalculatorFromHistogram')

for lib in libraries:
  ROOT.gROOT.ProcessLine(".L %s/src/%s.cc++" %(basepath,lib))
