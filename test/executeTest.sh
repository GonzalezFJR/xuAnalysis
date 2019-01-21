# Execute the test analysis from the command line using 8 slots and merging the output
# 100k events from a DY sample.
 
#python -c 'from testAnalysis import testAnalysis; testAnalysis("/pool/ciencias/trees2017/looseSkim06Sep/", "Tree_DYJetsToLL_M_50", eventRange = [0, 100000], xsec = 10, run = True, nSlots = 4)'

# Or send jobs
python -c 'from testAnalysis import testAnalysis; testAnalysis("/pool/ciencias/trees2017/looseSkim06Sep/", "Tree_DYJetsToLL_M_50", eventRange = [0, 100000], xsec = 10, sendJobs = True, nSlots = 8)'

# python ../framework/merger.py -vfr temp/
