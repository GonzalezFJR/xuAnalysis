import os
for ms, ml in [[275,100]]: #70],[245,100]]:
  for ch in ['ee', 'mumu','all']:
    for year in ['comb']:#[2016,2017,2018]:#,'comb']:
      command = 'python ttmt2Tails.py --year %s --chan %s --mStop %i --mLSP %i'%(str(year), ch, ms, ml)
      print command
      os.system(command)

