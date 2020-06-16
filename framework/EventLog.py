class EventLog:

  def start(self, evt, tree=None):
    if tree!=None: self.tree = tree
    if evt in self.listOfEvents:
      print '\n>>>> Event: '+str(evt)
      self.activate = True
    else: self.activate = False

  def end(self):
    #print '---------------------------------'
    self.activate = False

  def printmsg(self, message):
    if self.activate: print ' >  ' + message

  def printval(self, name, val, index=-1):
    if not self.activate: return
    istr = '[%i]'%index if index >= 0 else '   '
    self.printmsg('%s %s %s (%g)'%(' '*7, self.fixSize(name+istr), ' ', float(val)))

  def printbranch(self, listOfBranches=[], index=[]):
    if not self.activate: return
    if isinstance(listOfBranches, str):
      listOfBranches = [listOfBranches] if not  ',' in listOfBranches else listOfBranches.replace(' ', '').split(',')
    if isinstance(index, str):
      index = [index] if not  ',' in index else index.replace(' ', '').split(',')
    elif isinstance(index, int): index = [index]
    for br,i in zip(listOfBranches,index):
      i = int(i)
      val  = getattr(self.tree, br) if i < 0 else getattr(self.tree, br)[i]
      self.printval(br, val, i)

  def printCut(self, name, cut, val=None, op='>', index=-1, deactivate=False):
    if not self.activate: return
    if val==None: val  = getattr(self.tree, name) if index < 0 else getattr(self.tree, name)[index]
    cpass = val>cut if op=='>' else (val<cut if op=='<' else (val>=cut if op=='>=' else (val<=cut if op=='<=' else (val==cut if op=='==' else val!=cut)))) 
    txtpass = 'True ' if cpass else 'FALSE'
    self.printmsg('[%s] %s %s %g (%g)'%(txtpass, self.fixSize(name), op, float(cut), float(val)))
    if deactivate and not cpass: self.activate = False

  def fixSize(self, w, n=25):
    if len(w)>=n: w = w[0:n]
    while len(w) < n: w+=' '
    return w

  def __init__(self, listOfEvents, verbose=1, outfile='eventlog.log', tree=None):
    self.tree = tree
    self.listOfEvents = listOfEvents
    self.activate = False
