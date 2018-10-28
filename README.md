## Download the code

Download the code from github:

    git clone https://github.com/GonzalezFJR/xuAnalysis.git

or using ssh:

    git clone git@github.com:GonzalezFJR/xuAnalysis.git


## The analysis

By default, the output of the analysis are histograms, filled at different levels of selection.
The MC histograms are normalized to 1 pb-1 for a given input cross section. The weight is computed as:

    self.weight = (cross\_section * genWeight)/(sum\_of\_gen\_weights)

### Create an analysis (example)


### Secuential or multicore processing

Example of how to run the analysis on a sample (WWTo2L2Nu):

    python -c 'from myAnalysis import myAnalysis; myAnalysis("/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/", "WWTo2L2Nu", xsec = 10, run = True)'

Example of how to run the analysis on a sample (WWTo2L2Nu) using :

    python -c 'from myAnalysis import myAnalysis; myAnalysis("/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/", "WWTo2L2Nu", xsec = 10, nSlots = 5, run = True)'

### Send jobs to the lxplus batch system

Example of how to send 3 jobs to the lxplus batch system to analyze a sample:

    python -c 'from myAnalysis import myAnalysis; myAnalysis("/afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/", "WWTo2L2Nu", xsec = 10, nSlots = 3, sendJobs = True)'

## Merge the rootfiles

You can automatically merge any number of rootfies with a name SAMPLE\_[number].root into a SAMPLE.root file.
Use the command:

    python framework/merge.py [folder]

## Explore the trees

You can explore the input samples and trees by executing the following python scritp:

    python framework/fileReader.py

