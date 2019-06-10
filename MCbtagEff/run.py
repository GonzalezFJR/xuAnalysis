from MCbtagEff import MCbtagEff

path = '/pool/ciencias/userstorage/juanr/nanoAODv4/2018/'
sample = 'Tree_TTTo2L2Nu'
nslots = 1
 
a = MCbtagEff(path, sample, eventRange = [0, 1000], run = True, nSlots = nslots)

