import os, sys, datetime
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)

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

  def SetAnalysisName(self, an):
    self.anName = an

  def SetPretend(self, pretend = True):
    self.pretend = pretend

  def SetVerbose(self, verbose = 1):
    self.verbose = 1

  def AddJob(self, j):
    self.joblist.append(j)

  def GetDependentMod(self, anName=''):
    if anName=='': anName = self.anName
    directories = ['%s'%anName, 'framework']
    files = []
    f = open('%s/%s.py'%(anName, anName))
    GetPythonFile = lambda x : x.replace('.','/')+'.py' if os.path.isfile(basepath+x.replace('.','/')+'.py') else ( anName+'/'+x.replace('.','/')+'.py' if os.path.isfile(basepath+anName+'/'+x.replace('.','/')+'.py') else False)
    for l in f.readlines():
      if not 'import' in l: continue
      fname = False
      if 'from' in l: 
        fname = GetPythonFile(l[l.index('from')+5 : l.index('import')-1])
      else:
        mod = l[l.index('import')+1:]
        if ' ' in mod: mod = mod[:mod.index(' ')]
        fname = GetPythonFile(mod)
      if fname: 
        files.append(fname)
        dname = fname.split('/')[0]
        if not dname in directories: directories.append(dname)
    return directories, files

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
    queue   = self.queue
    nSlots  = 1 # by default
    jname   = "%s_%i"%(self.jobname, index)
    errname = self.GetErrName(index)
    outname = self.GetOutName(index)
    jobfile = self.GetJobName(index) 
    if self.system == 'slurm':
      runCommand = "sbatch -p %s -c %i -J %s -e %s -o %s %s"%(queue, nSlots, jname, errname, outname, jobfile)
    elif self.system == 'condor':
      subname = self.CreateCondorCfg(queue, nSlots, jname, errname, outname, jobfile)
      runCommand = 'condor_submit %s'%(subname)
    else:
      runCommand = "bsub -J %s -o %s -e %s -q %s %s"%(jname, outFolder, errname, queue, jobfile)
    #command += '< '  + self.GetJobName(index)
    return runCommand

  def CreateCondorCfg(self, queue, nSlots, jname, errname, joutname, jobfile):
    outname = 'jobs/condorsubmit_%s.sub'%(self.date+'_'+jname)
    sub = ''
    sub += 'Universe                = Docker\n'
    sub += 'use_x509userproxy       = true\n'
    sub += 'should_transfer_files   = YES\n'
    sub += 'when_to_transfer_output = ON_EXIT\n'
    sub += '+WantDocker             = True\n'
    sub += '+WantWholeNode          = True\n'
    sub += 'docker_image            = "unlhcc/osg-wn-el7"\n'
    sub += '\n'
    sub += 'executable              = %s\n'%jobfile
    sub += 'arguments               = $(ClusterId) $(ProcId)\n'
    sub += 'output                  = %s\n'%joutname
    sub += 'error                   = %s\n'%errname
    sub += 'log                     = log_%s.log\n'%jname
    sub += 'transfer_input_files    = metapy.py\n'%jname
    sub += 'queue\n'
    with open(outname, 'wr') as out: out.write(sub)
    out.close()
    return outname

  def CreateMetapy(self, includeInputs):
    dirs, files = self.GetDependentMod()
    for i in includeInputs:
      if not os.path.isfile(i): continue
      files.append(i)
      if '/' in files: dirs.append(files[:-files[::-1].index('/')])
    nout = 'jobs/metapy.py'
    f = open(nout, 'w')
    f.write('import os,sys\n')
    for d in dirs: f.write('os.system("mkdir -t %s")\n'%d)
    f.write('\n')
    for fname in files:
      fin = open(fname)
      text = fin.read()
      f.write('\nf = open("%s", "w")\nf.write("""%s""")\nf.close()\n'%(fname, text))
      fin.close()
    f.close()
    return nout

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

  def __init__(self, name, outFolder = './jobs/', queue = '8nm', verbose = 1, pretend = False, autorm = False, analysis = ''):
    self.joblist = []
    self.SetOutFolder(outFolder)
    self.SetName(name)
    self.SetQueue(queue)
    self.SetAnalysisName(analysis)

    self.date = GetNow()
    self.pretend = pretend
    self.verbose = verbose
    self.autorm = autorm
    self.system = ''
    hostname = os.uname()[1]
    if 'cern'   in hostname or 't3.unl' in hostname: self.system = 'condor'
    elif 'uniovi' in hostname: self.system = 'slurm'
