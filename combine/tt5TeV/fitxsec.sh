#!/bin/bash

#cd $1
pwd

CARD=$1
POIS="-P r"
SCAN=100

combine  ${POIS} -M MultiDimFit -t -1 --expectSignal 1  --robustFit 1 ${CARD}

#POIS=' --redefineSignalPOIs r,rttX,rZZ,rconvs -P r '
#POIS='-P r --floatOtherPOIs 1'

# Get full uncertainty on signal strength
echo "GET FULL UNCERTAINTY ON SIGNAL STRENGTH"
#combine -M MultiDimFit -t -1 --expectSignal 1   --algo=grid --points=${SCAN} ${POIS} ${CARD}  -n Nominal
combine -M MultiDimFit --algo=grid --points=${SCAN} ${POIS} ${CARD}  -n Nominal
plot1DScan.py higgsCombineNominal.MultiDimFit.mH120.root 
mv scan.pdf fullUncertaintyScan.pdf
mv scan.png fullUncertaintyScan.png

# Uncertainty breakdown
echo "UNCERTAINTY BREAKDOWN"

#combine -M MultiDimFit -t -1 --expectSignal 1 --algo none --rMin 0.1 --rMax 2.0 ${CARD} ${POIS} -n Bestfit --saveWorkspace
#combine -M MultiDimFit -t -1 --expectSignal 1 --algo grid --points ${SCAN} --rMin 0.1 --rMax 2.0 -n Systs higgsCombineBestfit.MultiDimFit.mH120.root --snapshotName MultiDimFit --freezeParameters "tt,DY,Nonprompt,tW,VV,MuonEff,ElecEff,TrigEff,JES,JER,Prefire,PU,PDF,Scale,ISR,FSR,hdamp,UE,autoMCStats" ${POIS}
combine -M MultiDimFit --algo none --rMin 0.1 --rMax 2.0 ${CARD} ${POIS} -n Bestfit --saveWorkspace
combine -M MultiDimFit --algo grid --points ${SCAN} --rMin 0.1 --rMax 2.0 -n Systs higgsCombineBestfit.MultiDimFit.mH120.root --snapshotName MultiDimFit --freezeParameters "tt,DY,Nonprompt,tW,VV,MuonEff,ElecEff,TrigEff,JES,JER,Prefire,PU,PDF,Scale,ISR,FSR,hdamp,UE,autoMCStats" ${POIS}

plot1DScan.py higgsCombineNominal.MultiDimFit.mH120.root --others  'higgsCombineSysts.MultiDimFit.mH120.root:Freeze all:31' --breakdown syst,stat
