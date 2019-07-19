## Download the code

Download the code from github:

    git clone https://github.com/GonzalezFJR/xuAnalysis.git

or using ssh:

    git clone git@github.com:GonzalezFJR/xuAnalysis.git


## The analysis

By default, the output of the analysis are histograms, filled at different levels of selection.
The MC histograms are normalized to 1 pb-1 for a given input cross section. The weight is computed as:

    self.weight = (cross\_section * genWeight)/(sum\_of\_gen\_weights)

Anyway, this is fully customizable.

### Create an analysis

    python framework/AnalysisCreator.py myAnalysis

Edit the cfg file "myAnalysis/testcfg.cfg". Introduce the path to the trees and the sample. 

    source executeTest.sh

### Run the analysis

    python run.py myAnalysis/testcfg.cfg

Or just introduce all the parameters in the run command. You can get the usage by executing run.py with no arguments.
Example:

    python run.py myAnalysis/testcfg.cfg -n 20 -s sample

Other interesting argumens:
   - -j : Send jobs
   - -t : Make a test with 1000 events


### Run on mini trees

## Merge rootfiles

    python framework/merge.py output_folder/ -frv

## Explore the trees

You can explore the input samples and trees by executing the following python scritp:

    python framework/fileReader.py

