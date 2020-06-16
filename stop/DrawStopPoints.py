from framework.fileReader import GetFiles, GetHisto
from ROOT import TCanvas, gROOT, TH2F
gROOT.SetBatch(1)
path = {
  2016 : '/pool/ciencias/nanoAODv6/29jan2020_MC/2016/',
  2017 : '/pool/ciencias/nanoAODv6/29jan2020_MC/2017/',
  2018 : '/pool/ciencias/nanoAODv6/29jan2020_MC/2018/',
}
sample ={
  2016 : 'SMS_T2tt_3J_xqcut_20_top_corridor_2Lfilter_TuneCUETP8M2T4_madgra',
  2017 : 'SMS_T2tt_3J_xqcut_20_top_corridor_2Lfilter_TuneCP5_MLM_p',
  2018 : 'SMS_T2tt_3J_xqcut_20_top_corridor_2Lfilter_TuneCP5_MLM_p',
}

Files = []
for year in [2016, 2017, 2018]: Files += GetFiles(path[year], sample[year]) 
h = GetHisto(Files, 'hSMS')

#h2D = TH2F('h', '', 30, 0, 150, 34, 145, 315)
h2D = TH2F('h', '', 34, 145, 315, 30, 0, 150)

for ix in range(h.GetNbinsX()+1):
  x = h.GetXaxis().GetBinCenter(ix)
  for iy in range(h.GetNbinsY()+1):
    y = h.GetXaxis().GetBinCenter(iy)
    c = h.GetBinContent(ix, iy, 1)
    if c != 0: h2D.SetBinContent(h2D.FindBin(y, x, 0), c)
    #if c != 0: print '[Y=%i, X=%i] --> [mStop: %1.2f, mLSP: %1.2f]     | %1.1f'%(iy, ix, y, x, c)
    
h2D.SetStats(0)
h2D.GetXaxis().SetTitle("m(#tilde{t}_{1}) (GeV)")
h2D.GetYaxis().SetTitle("m(#tilde{#chi}_{1}^{0}) (GeV)")

c = TCanvas('c', 'c', 10, 10, 1200, 800)
p = c.GetPad(0)
p.SetRightMargin(0.12)
h2D.Draw('colz')
c.SaveAs('MassPoints.png')
c.SaveAs('MassPoints.pdf')



