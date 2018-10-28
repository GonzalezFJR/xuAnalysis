import os, sys, datetime

### Dates
##########################################
def GetMonthName(n):
  if   n == 1 : return 'Jan'
  elif n == 2 : return 'Feb'
  elif n == 3 : return 'Mar'
  elif n == 4 : return 'Apr'
  elif n == 5 : return 'May'
  elif n == 6 : return 'Jun'
  elif n == 7 : return 'Jul'
  elif n == 8 : return 'Ago'
  elif n == 9 : return 'Sep'
  elif n == 10: return 'Oct'
  elif n == 11: return 'Nov'
  elif n == 12: return 'Dec'

def GetToday():
  now = datetime.datetime.now()
  today = str(now.day) + GetMonthName(now.month) + str(now.year)[2:]
  return today

def GetTimeNow():
  now = datetime.datetime.now()
  time = str(now.hour) + 'h' + str(now.minute) + 'm' + str(now.second) + 's'
  return time

def GetNow():
  return GetToday()+'_'+GetTimeNow()


#########################################################
class jobManager:

  def SetOutFolder(self, out):
    if out == '': out = './'
    if not out[-1] == './': out += '/'
    self.outFolder = out
    if not os.path.isdir(out): os.mkdir(out)

  def SetOutFileName(self, name):
    self.outfName = name

  def SetOutErrorName(self, name):
    self.errorfName = name

  def SetQueue(self, qu):
    self.queue = qu

  def SetName(self, name):
    self.jobname = name

  def SetPretend(self, pretend = True):
    self.pretend = pretend

  def SetVerbose(self, verbose = 1):
    self.verbose = 1

  def AddJob(self, j):
    self.joblist.append(j)

  def GetJobName(self, index = 0):
    ''' Returns the job name '''
    name  = self.outFolder
    name += 'Job_' + self.date + '_' + self.jobname + '_' + str(index) + '.sh'
    return name

  def GetOutName(self, index = 0):
    ''' Returns the name of the output text file  '''
    name  = self.outFolder
    name += 'Out_' + self.date + '_' + self.jobname + '_' + str(index) + '.txt'
    return name

  def GetErrName(self, index = 0):
    ''' Returns the name of the error file '''
    name  = self.outFolder
    name += 'Error_' + self.date + '_' + self.jobname + '_' + str(index) + '.txt'
    return name
  
  def GetSubmitCommand(self, index):
    ''' Crafts the submit command '''
    command  = 'bsub '
    command += '-J ' + self.jobname + '_%i '%index
    command += '-o ' + self.GetOutName(index) + ' '
    command += '-e ' + self.GetErrName(index) + ' '
    command += '-q ' + self.queue + ' '
    command += '< '  + self.GetJobName(index)
    return command

  def CreateJobs(self):
    ''' Create the job files '''
    n = len(self.joblist)
    print ' >> Creating %i jobs...'%n
    for i in range(n):
      name = self.GetJobName(i)
      f = open(name, 'w')
      f.write(self.joblist[i])
      f.close()

  def SubmitJobs(self):
    ''' Submit all the created jobs '''
    n = len(self.joblist)
    print ' >> Submitting jobs...'
    for i in range(n):
      command = self.GetSubmitCommand(i)
      print ' >> ' + command
      if not self.pretend: os.system(command)
    
  def RemoveJobsFiles(self):
    ''' Delete all job files '''
    if not self.autorm: return
    n = len(self.joblist)
    print ' >> Removing %i jobs'%n
    for i in range(n):
      #os.system('mv ' + self.GetJobName(i) + ' ' + self.outFolder)
      os.system('rm ' + self.GetJobName(i))

  def run(self):
    ''' Create jobs and submit ''' 
    self.CreateJobs()
    self.SubmitJobs()
    if self.autorm: self.RemoveJobsFiles()

  def __init__(self, name, outFolder = './jobs/', queue = '8nm', verbose = 1, pretend = False, autorm = False):
    self.joblist = []
    self.SetOutFolder(outFolder)
    self.SetName(name)
    self.SetQueue(queue)

    self.date = GetNow()
    self.pretend = pretend
    self.verbose = verbose
    self.autorm = autorm
