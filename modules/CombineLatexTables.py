import os, sys

class LatexTableCombinator:

  def SetOutName(self, outname):
    self.outname = outname

  def SetTextBeforeTable(self, t):
    self.texbefore = t

  def SetTextAfterTable(self, t):
    self.texafter = t

  def HasFirstRaw(self, has=True):
    self.hasFirstRaw = has

  def Set11(self, ele=''):
    self.e11 = ele

  def SetFirstRawElements(self, ele=[]):
    self.firstRawElements = ele

  def GetTableElements(self,line):
    elements = line.split('&')
    first = elements[0]
    values = []
    for e in elements[1:]:
      values.append(e.replace("\\\\", '').replace('\n', ''))
    return first, values

  def SetValuesFromFile(self,fname, colname='', hasFirstRaw=None):
    if hasFirstRaw!=None: self.HasFirstRaw(hasFirstRaw)
    self.rownames = []
    self.rowelements = []
    if colname!='': self.elements[colname]={}
    with open(fname) as f:
      tbefore = ''; tafter = ''; isbefore=True; isafter=False; isFirst = not self.hasFirstRaw;
      for l in f.readlines():
        if l.startswith('%'): continue
        if 'tabular' in l:
          if   isbefore:    
            tbefore += '\\begin{tabular}{l' +' c'*len(self.columnNames) + '}\n'
            isbefore=False
          elif not isafter: 
            tafter += l
            isafter =True
          continue
        if   isbefore: tbefore += l
        elif isafter : tafter  += l
        else:
          if not '&' in l: self.rowelements.append(l)
          else: 
            if not isFirst:
              isFirst = True
              first, values = self.GetTableElements(l)
              self.colname = values
              self.Set11(first)
            else:
              first, values = self.GetTableElements(l)
              self.rownames.append(first)
              self.rowelements.append(first)
              if colname!='': self.elements[colname][first] = values
    self.SetTextBeforeTable(tbefore)
    self.SetTextAfterTable(tafter)
            
  def AddValuesFromFile(self,fname, colname):
    self.elements[colname] = {}
    with open(fname) as f:
      tbefore = ''; tafter = ''; isbefore=True; isafter=False;
      for l in f.readlines():
        if 'tabular' in l and not l.startswith('%'):
          if   isbefore:    isbefore=False
          elif not isafter: isafter =False
          continue
        if not isbefore and not isafter:
          if not '&' in l: continue
          first, values = self.GetTableElements(l)
          if not first in self.rownames: continue
          self.elements[colname][first] = values

  def __init__(self, files, outname, columnNames, hasFirstRaw=True, runLatex=False):
    if isinstance(columnNames, str): columnNames=columnNames.replace(' ', '').split(',')
    if isinstance(files, str): files=files.replace(' ', '').split(',')
    if not isinstance(files, list) and len(files) > 0:
      print 'ERROR: wrong format for files'
      return
    self.runLatex = runLatex
    self.SetOutName(outname)
    self.elements = {}
    self.columnNames = columnNames
    self.e11 = ''
    self.HasFirstRaw(hasFirstRaw)
    f0 = files[0]
    c0 = columnNames[0]
    self.SetValuesFromFile(f0, c0)
    for f, c in zip(files[1:], columnNames[1:]): self.AddValuesFromFile(f,c)

  def Print(self):
    fout = open(self.outname, 'w')
    fout.write(self.texbefore)
    line = self.e11
    for c in self.columnNames: line += ' & ' + c
    line += '\\\\ \n'
    fout.write(line)
    for l in self.rowelements:
      if l in self.rownames:
        line = l
        for c in self.columnNames: 
          elements = self.elements[c][l]
          for e in elements: line+= ' & ' + e
        line += '\\\\ \n'
        fout.write(line)
      else: fout.write(l)
    print 'Combined table in: '+self.outname
    fout.write(self.texafter)
    fout.close()
    if self.runLatex:
      if not '/' in self.outname:
        oname = self.outname
        odir = './'
      else:
        idx = self.outname[::-1].index('/')
        oname = self.outname[-idx:]
        odir = self.outname[:-idx]
      print 'Running pdflatex...'
      os.system('pdflatex -output-directory=%s %s'%(odir, oname) )
    
path = '/nfs/fanae/user/juanr/www/tt5TeV/28apr/'
GetFname = lambda ch : path+'Yields_%s_2jets_MC.tex'%ch
GetSname = lambda ch : path+'Systematics_%s_2jets_MC.tex'%ch
files  = [GetFname(x) for x in ['ElEl', 'ElMu', 'MuMu']]
filesS = [GetSname(x) for x in ['ElEl', 'ElMu', 'MuMu']]
l = LatexTableCombinator(files, path+'Yields_all.tex', 'ee, $e\mu$, $\mu\mu$', False, True)
l.Print()

s = LatexTableCombinator(filesS, path+'Systematics_all.tex', 'ee, $e\mu$, $\mu\mu$', True, True)
s.Print()
