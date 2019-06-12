from MCbtagEff import MCbtagEff

year = '2017'

path = '/pool/cienciasrw/userstorage/juanr/nanoAODv4/%s/'%year
sample = 'Tree_TTTo2L2Nu'
nslots = 80
 
a = MCbtagEff(path, sample, run = True, nSlots = nslots, options = year)
#a = MCbtagEff(path, sample, run = True, nSlots = 1, options = year, eventRange = [0,1000])

