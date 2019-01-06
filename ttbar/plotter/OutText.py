import os

class OutText:
  ''' Class to produce output text files '''
  
  def SetSeparatorLength(self, n):
    self.seplen = n
    self.separator = '-'*n
    self.sepbar = '='*n

  def SetOutPath(self,p):
    if not p[-1] == '/': p+='/'
    self.path = p

  def SetTexAlign(self, texalign):
    self.texalign = texalign
 
  def SetOutName(self,o):
    self.outname = o

  def SetOutFormat(self, f='txt'):
    self.outformat = f

  def SetMode(self,m):
    if   m == 'new': m = 'w'
    elif m == 'add' or m == 'append': m = 'a'
    self.mode = m

  def SetPrint(self, t=True):
    self.doPrint = t

  def text(self, t):
    ''' Add text... '''
    self.t += t
    if self.doPrint: print t,

  def line(self, t=''):
    ''' Add line '''
    if self.outformat == "tex": self.text(t+' \\\\ \n')
    else: self.text(t+'\n')

  def sep(self):
    ''' Draws a separating line '''
    if self.outformat == "tex": self.text("\hline\n")
    else: self.line(self.separator)

  def bar(self):
    ''' Draws a separating double line '''
    if self.outformat == "tex": self.text("\hline\n")
    else: self.line(self.sepbar)
  
  def vsep(self):
    ''' Draws a vertical separator '''
    if self.outformat == "tex": return ' & '
    else: return ' | '

  def pm(self):
    ''' Inserts a plus/minus sign '''
    if self.outformat == "tex": return ' {$\pm$} '
    else: return ' +/- '

  def write(self):
    ''' Opens the file '''
    filename = self.path + self.outname + '.' + self.outformat
    if not os.path.isdir(self.path): os.mkdir(self.path)
    if os.path.isfile(filename) and (self.mode == 'new' or self.mode == 'w'):
      print '[INFO] %s exists!! moving to .bak...'%filename
      os.rename(filename, filename+'.bak')
    if self.mode == 'r' or self.mode == 'w':
      self.f = open(filename, self.mode)
    self.line()
    text  = ''
    if self.outformat == 'tex':
      text += '\\documentclass{article}\n'
      text += '\\begin{document}\n'
      text += '\\begin{tabular}{ ' + self.texalign + '}\n'
      text += self.t + '\n'
      text += '\\end{tabular}\n'
      text += '% \\caption{}\n'
      text += '% \\label{tab:}\n'
      text += '\\end{document}\n'
    else: text = self.t
    self.f.write(text)
    self.f.close()

  def GetText(self):
    ''' Returns all the text '''
    return self.t

  def fix(self,s, n, align = 'l', add = ''):
   ''' Fixing spaces '''
   if add == '': self.GetDefaultFixOption()
   v = 0
   while len(s) < n:
     if   align == 'l': s += ' '
     elif align == 'r': s = ' ' + s
     elif align == 'c': 
       if   v%2 == 0: s = ' ' + s
       else         : s += ' '
       v += 1
     else: return s
   if add: self.text(s)
   else: return s

  def SetDefaultFixOption(self, op = True):
    self.defaultFixOption = op

  def GetDefaultFixOption(self):
    return self.defaultFixOption

  def __init__(self, path = 'temp/', outname = 'out', mode = 'new', textformat = 'txt', doPrint = True):
    self.SetOutPath(path)
    self.SetOutName(outname)
    self.SetOutFormat(textformat)
    self.SetMode(mode)
    self.SetPrint(doPrint)
    self.SetDefaultFixOption()
    self.t = ''
    self.line()
