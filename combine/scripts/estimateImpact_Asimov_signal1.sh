#!/bin/bash

# Prerequisite: installing the combineTool.py tool.
#       Method 1 (install only the script):
#                  bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
#       Method 2 (install the whole CombineHarvester):
#                  cd $CMSSW_BASE/src
#                  git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
#                  scram b -j 6


DATACARD=$1
MASS="1"

if [ "$1" != "" ]; then
    DATACARD=${1}
fi

echo "Preliminary: convert to rootspace"
echo "---------------------------------"

rm ${DATACARD}.root
text2workspace.py ${DATACARD}.txt -m 1
DATACARD="${DATACARD}.root"

echo "First Stage: fit for each POI"
echo "-----------------------------"
combineTool.py -M Impacts -d ${DATACARD} -m ${MASS} -t -1 --expectSignal 1 --doInitialFit --robustFit 1 --rMin -10

echo "Second Stage: fit scan for each nuisance parameter"
echo "--------------------------------------------------"
combineTool.py -M Impacts -d ${DATACARD} -m ${MASS} -t -1 --expectSignal 1 --robustFit 1 --doFits --parallel 7 --rMin -10

echo "Third Stage: collect outputs"
echo "----------------------------"
combineTool.py -M Impacts -d ${DATACARD} -m ${MASS} -t -1 --expectSignal 1 -o impacts.json --rMin -10

echo "Fourth Stage: plot pulls and impacts"
echo "------------------------------------"
plotImpacts.py -i impacts.json -o impacts
