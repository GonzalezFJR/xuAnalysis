from ROOT import *
gROOT.SetBatch(1)
getFile = lambda ms, ml : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/29apr/LEE/Unc/SR/2018/mass%s_%s/tempfiles/ttZ.root'%(str(ms), str(ml))
outpath = '~/www/temp/'

def Draw(masses, name='temp'):
  c = TCanvas('c', 'c', 10, 10, 1200, 800)
  color = 1
  for ms, ml in masses:
    f = TFile.Open(getFile(ms,ml))
    h = f.Get('dnn')
    h.SetDirectory(0)
    h.SetStats(0); h.SetLineColor(color); h.SetLineWidth(2); h.SetFillColor(0)
    color += 1
    h.Draw('hist,same')

  for f in ['png', 'pdf']: c.SaveAs(outpath+name+'.'+f)

Draw([[175,1],[225,50],[275,100]])
