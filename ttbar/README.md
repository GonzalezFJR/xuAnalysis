### Process all the files

Change the path to point to the n-tuples. In lxplus, you can take the n-tuples (skimmed nanoAOD) from:
 
    /afs/cern.ch/work/j/jrgonzal/public/Run2017G/skim2l/ 

Run the analysis over all the samples. You can do it automatically by executing:

    python processSample.py --all 8 --path [PATH]

Using, in this example, 8 cores.
The output will be stored, by default, in the ./temp/ directory. Merge the output executing:

    python ../framework/merger.py temp/ -frv

### Draw plots and tables

To obtaing all the outputs from the analysis, execute the script CreatePlotsAndTables.py. If you changed the name of the output folder for the results of the analysis, you may need to change the input path in the script. Execute as:

    python CreatePlotsAndTables.py

