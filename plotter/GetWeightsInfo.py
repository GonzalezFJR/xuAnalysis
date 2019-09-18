'''
 Obtain info of PS, PDF and ME weights from a nanoAOD file
 Usage: 
   GetWeigthsInfo(file, outfile = 'weights.info')
'''
from ROOT import TFile

fname = {
  #2016 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2016/Tree_TTTo2L2Nu_TuneCP5_PSweights_0.root',
  2016 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2016/Tree_TTTo2L2Nu_TuneCP5_PSweights_0.root',
  2017 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2017/Tree_TTTo2L2Nu_0.root',
  2018 : '/pool/cienciasrw/userstorage/juanr/nanoAODv4/2018/Tree_TTTo2L2Nu_0.root',
}

def GetBranchInfo(fname, branchname, treeName = 'Events', verbose = 1):
  '''
  Obtain info of PS, PDF and ME weights from a nanoAOD file
  Usage: 
    GetBranchInfo(fname, "PSWeight, LHEScaleWeight, LHEPdfWeight")
  '''
  f = TFile.Open(fname)
  t = f.Get(treeName)
  t.GetEntry(1) # Explore first event:
  out = "Looking for branch/branches '%s' in tree '%s'\nin file '%s'...\n"%(branchname, treeName, fname)
  if isinstance(branchname, str) and ',' in branchname: branchname = branchname.replace(' ', '').split(',')
  elif isinstance(branchname, str): branchname = [branchname]
  for brname in branchname:
    nbranch = 'n'+brname
    info    = t.GetBranch(brname) .GetTitle()
    ninfo   = t.GetBranch(nbranch).GetTitle()
    out    += " %s : %s\n"%(brname,  info)
    out    += " %s : %s\n"%(nbranch, ninfo)
    nbr     = getattr(t, nbranch)
    lbr     = getattr(t, brname)
    out    += "Priting values for one event...\n %s : %i\n %s :"%(nbranch, nbr, brname)
    for i in range(nbr): 
      out += " %1.2f,"%lbr[i]
    if out.endswith(','): out = out[:-1] + '\n'
    out += '\n'
  out += '\n'
  f.Close()
  if verbose: print out
  return out


GetBranchInfo(fname[2016], "PSWeight, LHEScaleWeight, LHEPdfWeight")
GetBranchInfo(fname[2017], "PSWeight, LHEScaleWeight, LHEPdfWeight")
GetBranchInfo(fname[2018], "PSWeight, LHEScaleWeight, LHEPdfWeight")
