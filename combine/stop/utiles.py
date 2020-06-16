def GetLumi(year, era = 'all'):
  if not isinstance(year, int): return GetLumi(2016)+GetLumi(2017)+GetLumi(2018)
  lumi = {
    2016 : {
             'B' : 5.783,
             'C' : 2.5639,
             'D' : 4.248,
             'E' : 4.0089,
             'F' : 3.101,
             'G' : 3.1013,
             'H' : 7.54,
             'all': 35.92,
           },
    2017 : {
             'B' : 4.823,
             'C' : 9.664,
             'D' : 4.252,
             'E' : 9.278,
             'F' : 13.540,
             'G' : 0.297,
             'H' : 0.22,
            'all': 41.53,
           },
     2018 : {
              'A' :  14.00,
              'B' :   7.10,
              'C' :   6.94,
              'D' :  31.93,
              'all': 59.74,
            }
  }
  return lumi[year][era]


