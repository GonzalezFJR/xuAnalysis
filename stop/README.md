### Create all rootfiles for each stop mass point
Script: CreateRootFiles.py
Select SR, CR, BS... 3 years, different mass points...
First round: create temp files
After, use the merger script: python framework/merger.py -frv output/folder/tempfiles/ (--recursive)
Second run: produce combine-like rootfiles
After, use the following file to produce plots
Script: ReadFromCombineRootfile.py

### Same-sign region for nonprompt
Script: SS.py
Use it as the CreateRootFiles.py script
In the second round, it produces several plots

### Study the mt2 tails
Script: ttmt2Tails.py
Use it as the CreateRootFiles.py script
After, the same script produces plots

### PDF and ME uncertainties
Script: CalculatePDFweights.py
Use it as the CreateRootFiles.py script
Output: rootfiles with histograms nom, pdfUp, pdfDown, meUp, meDown
It also creates comparison histograms with uncertainties

### FSR uncertaintiy for 2016
Script: RunFSR2016.py 

#########################################################################
### Prepare final files
Script: CraftUncertainties.py
This is necesary to merge different uncertainties (PDF, ME, non-gauss, FSR 2016)
into de final files. Make sure that you created all the inputs and the paths are ok.
You need to have:
- Combine-like rootfiles (CreateRootFiles.py), all steps
- PDF/ME uncertainties (CalculatePDFweights.py)
- FSR uncertainy for 2016


### Summary scripts
- CreateRootFiles.py
- ReadFromCombineRootfile.py
- ttmt2Tails.py
- SS.py
- CalculatePDFweights.py
- RunFSR2016.py
- CraftUncertainties.py
