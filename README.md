## Download the code

Download the code from github:

    git clone https://github.com/GonzalezFJR/xuAnalysis.git

or using ssh:

    git clone git@github.com:GonzalezFJR/xuAnalysis.git


## Create an analysis

    python framework/AnalysisCreator.py myAnalysis

Implement your analysis in "myAnalysis/myAnalysis.py".
Edit the cfg file "myAnalysis/testcfg.cfg". Introduce the path to the trees and the sample. 

    source executeTest.sh

## Description of the analysis

### The framework
Your analysis is a class that inherit from the class "analysis" in *framework/analysis.py*. The output of the analysis is a .root file with histograms, trees or other outputs created in the analysis.

Several functions to calculate kinematic properties, construct objets (leptons, jets...) can be found on *framework/functions.py*

The cpp modules are located in the *src/*  folder and can compiled (only once) using:

    gROOT.LoadMacro("%s/src/myClass.C+"%basepath)

and loaded in your analysis with:

    gROOT.Load("%s/src/myClass_cc.so"%basepath)

External (comon) python modules are stored in the *modules/*  folder.

Input files (such as histograms or TGraphs with scale factors) are located in the *inputs/* folder.

The analysis looks for a tree named "Events" (by default) and histograms "Count" and "SumWeights" inside the root files to calculate the normalization weights.

### Structure of the analysis class
The function *init*  is executed once per sample. Use this function to:
  - Create histograms, trees or other outputs. For example using the function *CreateTH1F*.
     self.CreateTH1F("name", "title", 20, 0, 100)
  - Set custom-sample options.
  - Initialize objects, open histograms...

The function *insideLoop* is executed once for event. Implement here your object and event selection, weights, uncertainties, etc, and fill the histograms (or output trees).
The function is called with the input TChain as the argument *t*. Use this variable to access the tree branches (Example: nJets = t.nJet).

### The class members
Use the default class members:

  - self.outname     : The output name... use this name to apply per-sample weights/selections.
  - self.options     : The input options, including the ones introduced 'by hand' with --options (or through the .cfg file)
  - self.isData      : True for data samples, based on the existence of some gen-level variables.
  - self.EventWeight : Weight to nomalize an event to 1./pb, calculated as genWeight·xsec/SumWeights.

There are some other variables to store the number of events in the sample and other information.

### Example of loading and using scale factors
You can use the functions *self.LoadHisto* inside the *init*. Example:

    self.LoadHisto('MuonIsoSF', basepath+'./inputs/MuonISO.root', 'NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')

Once the histogram is open, you can get the scale factor within the *insideLoop* using the function *self.GetSFandErr* as:

    sf, err = self.GetSFandErr('MuonIsoSF', pt, abs(eta))

### Example of loading and using an external module
Load the modules at the begining of your analysis. Example:

    from modules.GetBTagSF import BtagReader

Create an object inside the *init*. Example:

    self.BtagSF   = BtagReader('DeepCSV', 'mujets', 'Medium', 2017)

Use the object in your analysis, inside the *insideLoop* function. Example:

    isBtag = self.BtagSF.IsBtag(alg, flavour, pt, eta, 0)

### Example of muon selection
Create a list to store the selected muons

    self.muons = []

Loop over the muons in the tree *t*:

    for i in range(t.nMuon):

Create the TLorentzVector, apply selection criteria and create the lepton objects:

    p = TLorentzVector()
    p.SetPtEtaPhiM(t.Muon_pt[i], t.Muon_eta[i], t.Muon_phi[i], t.Muon_mass[i])
    charge = t.Muon_charge[i]
    if not t.Muon_tightId[i]: continue # Tight ID
    if not t.Muon_pfRelIso04_all[i] < 0.15: continue # Tight ISO, RelIso04 < 0.15
    dxy = abs(t.Muon_dxy[i]) 
    dz  = abs(t.Muon_dz[i] )
    if dxy > 0.05 or dz > 0.1: continue # Tight IP
    if p.Pt() < 20 or abs(p.Eta()) > 2.4: continue # pt and eta cuts
    self.muons.append(lepton(p, charge, 13)) # 13 for muons


## Run the analysis

    python run.py myAnalysis/testcfg.cfg

Or just introduce all the parameters in the run command. You can get the usage by executing run.py with no arguments.
Example:

    python run.py myAnalysis/testcfg.cfg -n 20 -s sample

Arguments:
   - -n, --nSlots   : Run on n slots (or send n jobs)
   - -p, --pretend  : Create the files but not send the jobs
   - -t, --test     : Test locally with 1000 events
   - -j, --sendJobs : Send jobs
   - -q, --queue    : Choose the queue ("batch" by defaul)
   - -v, --verbose  : Control the verbosity
   - -s, --sample   : Run on a single sample (from the cfg file!)
   - -x, --xsec     : Set a cross section value
   - -o, --options  : Options to pass to your analysis (stored in self.options)
   - --outname  : Customize the name of the output file
   - --outpath  : Customize the name of the output path
   - --nEvents  : Run over a given number of events

### Run on mini trees

[Under construction]

## Merge rootfiles

    python framework/merge.py output_folder/ -frv

Options:

  - -f : force if there are some merged trees with the same name as output.
  - -r : auto-remove single files after merging
  - -v : verbose

## Explore the trees

You can explore the input samples and trees by executing the following python scritp:

    python framework/fileReader.py

