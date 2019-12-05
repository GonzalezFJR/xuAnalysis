import os, sys, argparse
from fileReader import guessPathAndName, findValidRootfiles, getDicFiles

def manageMergedOutput(folder, sampleName, force = False):
  ''' Checks if out dir exits, manages the 'force'... '''
  if not os.path.isdir(folder):
    print 'Output dir does not exist! Creating...'
    os.mkdir(folder)
    print ' >> Created output dir: ' + folder
  if os.path.isfile(folder + sampleName + '.root'):
    print 'WARNING: out \'' + sampleName + '\' file exists!'
    if not force:
      print 'Skipping...'
      return False
    else:
      print 'Moving to .bkg...'
      os.system('mv ' + folder + sampleName + '.root ' + folder + sampleName + '.root.bkg')
      return True 
  return True

def hadd(listOfFiles, name = '', inputdir = '', outputDir = '', verbose = False, pretend = False, force = False, rm = False):
  ''' Executes the hadd '''
  if len(listOfFiles) == 0:
    print 'WARNING: no input files found for process "' + name + '"'
    return
  path, fname, n = guessPathAndName(listOfFiles[0])
  if name == '': name = fname
  if outputDir == '': outputDir = path
  if inputdir != '': 
    if not inputdir[-1] == '/': inputdir += '/'
    if outputDir == '': outputDir = inputdir
    if path == '': listOfFiles = [inputdir + x for x in listOfFiles]
  out = outputDir + name + '.root'
  inf = ''; 
  nfiles = 0
  if out in listOfFiles: listOfFiles.pop(listOfFiles.index(out))
  for x in listOfFiles: 
    nfiles += 1
    inf += x + ' ' 
  if nfiles <= 1: return
  if not manageMergedOutput(outputDir, name, force): return
  print ' >> Adding ' + name + ' (%i files)'%nfiles
  command = 'hadd ' + out + ' ' + inf
  if not pretend:
    if verbose: print 'Executing command: ' + command
    os.system(command)
    if rm:  
      for x  in listOfFiles: 
        os.system('rm ' + x)
  else: print ' >> PRETENDING!!\n >> ' + command

def main():
 #######################################################
 ### Start the execution
 verbose = False; pretend = False; force = False; rm = False
 sampleName = ''
 inFolder = ''
 outFolder = ''

 # Parsing options
 pr = argparse.ArgumentParser()
 pr.add_argument('folder', help='Input folder')
 pr.add_argument('--sample', type = str, default = '')
 pr.add_argument('--outdir', type = str, default = '')
 pr.add_argument('-v','--verbose', action='store_true', help='Activate verbosing')
 pr.add_argument('-f','--force', action='store_true', help='If out saple exists, moves to .bck and executes the merging')
 pr.add_argument('-p','--pretend', action='store_true', help='Returns the hadd commands')
 pr.add_argument('-r','--rm', action='store_true', help='Returns the hadd commands')

 args = pr.parse_args()
 inFolder = args.folder
 if args.verbose: verbose = True
 if args.force:   force   = True
 if args.pretend: pretend = True
 if args.rm:      rm = True
 if args.sample:  sampleName = args.sample
 if args.outdir:  outFolder = args.outdir
 
 if outFolder == '': outFolder = inFolder 
 if not inFolder[-1] == '/': inFolder+= '/'
 if not outFolder[-1] == '/': outFolder += '/'
 # Check input folder...
 if not os.path.isdir(inFolder):
   print 'ERROR: Directory "' + inFolder + '"  does not exist!!'
   exit()

 if sampleName == '':  ### Automatic option
   print 'INFO: Automatic merge of files in folder: ' + inFolder
   listOfFiles = getDicFiles(inFolder)
   if len(listOfFiles) == 0:
     print 'WARNING: no files to merge in "' + inFolder + '"'
     exit()
   for L in listOfFiles: hadd(listOfFiles[L], L, inFolder, outFolder, verbose, pretend, force, rm)
 
 else:    ### hadd only one sample
   listOfFiles = findValidRootfiles(inFolder, sampleName)
   hadd(listOfFiles, sampleName, inFolder, outFolder, verbose, pretend, force, rm)

if __name__ == '__main__':
  main()
