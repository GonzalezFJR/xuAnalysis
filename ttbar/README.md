### Process all the files

Look for the path to point to the n-tuples. In Pisa, you can take the n-tuples (skimmed nanoAOD) from:
 
    /gpfs/ddn/cms/user/cmsdas/2019/ttbar/dilepton_skim/

Run the analysis over all the samples. You can do it automatically by executing:

    python processSample.py --all 8 --path [PATH]

In this example, you are using 8. You could send jobs to the lxplus batch system. You can explore the file to change the cross sections of the samples or you can run the samples one by one.
The output will be stored, by default, in the ./temp/ directory. Merge the output executing:

    python ../framework/merger.py temp/ -frv

### Draw plots and tables

To obtaing all the outputs from the analysis, execute the script CreatePlotsAndTables.py. If you changed the name of the output folder for the results of the analysis, you may need to change the input path in the script. Execute as:

    python CreatePlotsAndTables.py

