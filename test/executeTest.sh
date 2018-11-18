# Execute the test analysis from the command line using 8 slots and merging the output
# 100k events from a DY sample.
 
python -c 'from testAnalysis import testAnalysis; testAnalysis("/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/", "DYJetsToLL_MLL50", eventRange = [0, 100000], xsec = 10, run = True, nSlots = 4)'

# Or send jobs
# python -c 'from testAnalysis import testAnalysis; testAnalysis("/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/", "DYJetsToLL_MLL50", eventRange = [0, 100000], xsec = 10, sendJobs = True, nSlots = 8)'

# python ../framework/merger.py -vfr temp/
