def tnp_weight_trig_pbpb(pt, eta, idx = 0):
  num=1.0; den=1.0;

  # MC
  if (abs(eta) > 0 and abs(eta) <= 1.2):
    if      (pt > 15 and pt <= 20): den = 0.940563;
    elif (pt > 20 and pt <= 30): den = 0.953007;
    elif (pt > 30 and pt <= 50): den = 0.964625;
    elif (pt > 50 and pt <= 80): den = 0.966917;
    elif (pt > 80 and pt <= 9999): den = 0.958959;
  elif (abs(eta) > 1.2 and abs(eta) <= 2.1):
    if (pt > 15 and pt <= 20): den = 0.9281;
    elif (pt > 20 and pt <= 30): den = 0.940129;
    elif (pt > 30 and pt <= 50): den = 0.953978;
    elif (pt > 50 and pt <= 80): den = 0.958659;
    elif (pt > 80 and pt <= 9999): den = 0.961068;
  elif (abs(eta) > 2.1 and abs(eta) <= 2.4):
    if (pt > 15 and pt <= 20): den = 0.890849;
    elif (pt > 20 and pt <= 30): den = 0.914955;
    elif (pt > 30 and pt <= 50): den = 0.934417;
    elif (pt > 50 and pt <= 80): den = 0.943679;
    elif (pt > 80 and pt <= 9999): den = 0.947818;

  # data
  if (idx == 0 or idx > 10): # nominal
    if (abs(eta) > 0 and abs(eta) <= 1.2):
      if (pt > 15 and pt <= 20): num = 0.875759;
      elif (pt > 20 and pt <= 30): num = 0.92399;
      elif (pt > 30 and pt <= 50): num = 0.948799;
      elif (pt > 50 and pt <= 80): num = 0.949345;
      elif (pt > 80 and pt <= 9999): num = 0.940723;
    elif (abs(eta) > 1.2 and abs(eta) <= 2.1):
      if (pt > 15 and pt <= 20): num = 0.893974;
      elif (pt > 20 and pt <= 30): num = 0.906569;
      elif (pt > 30 and pt <= 50): num = 0.926756;
      elif (pt > 50 and pt <= 80): num = 0.940292;
      elif (pt > 80 and pt <= 9999): num = 0.928692;
    elif (abs(eta) > 2.1 and abs(eta) <= 2.4):
      if (pt > 15 and pt <= 20): num = 0.828836;
      elif (pt > 20 and pt <= 30): num = 0.871728;
      elif (pt > 30 and pt <= 50): num = 0.898965;
      elif (pt > 50 and pt <= 80): num = 0.91405;
      elif (pt > 80 and pt <= 9999): num = 0.889446;
  elif (idx == 1): #stat up
    if (abs(eta) > 0 and abs(eta) <= 1.2):
      if (pt > 15 and pt <= 20): num = 0.890676;
      elif (pt > 20 and pt <= 30): num = 0.928769;
      elif (pt > 30 and pt <= 50): num = 0.952176;
      elif (pt > 50 and pt <= 80): num = 0.954073;
      elif (pt > 80 and pt <= 9999): num = 0.953832;
    elif (abs(eta) > 1.2 and abs(eta) <= 2.1):
      if (pt > 15 and pt <= 20): num = 0.908596;
      elif (pt > 20 and pt <= 30): num = 0.913711;
      elif (pt > 30 and pt <= 50): num = 0.929705;
      elif (pt > 50 and pt <= 80): num = 0.94689;
      elif (pt > 80 and pt <= 9999): num = 0.948762;
    elif (abs(eta) > 2.1 and abs(eta) <= 2.4):
      if (pt > 15 and pt <= 20): num = 0.85611;
      elif (pt > 20 and pt <= 30): num = 0.886324;
      elif (pt > 30 and pt <= 50): num = 0.905823;
      elif (pt > 50 and pt <= 80): num = 0.929945;
      elif (pt > 80 and pt <= 9999): num = 0.940054;
  elif (idx == 2): # stat down
    if (abs(eta) > 0 and abs(eta) <= 1.2):
      if (pt > 15 and pt <= 20): num = 0.859607;
      elif (pt > 20 and pt <= 30): num = 0.919003;
      elif (pt > 30 and pt <= 50): num = 0.945421;
      elif (pt > 50 and pt <= 80): num = 0.944336;
      elif (pt > 80 and pt <= 9999): num = 0.925502;
    elif (abs(eta) > 1.2 and abs(eta) <= 2.1):
      if (pt > 15 and pt <= 20): num = 0.878284;
      elif (pt > 20 and pt <= 30): num = 0.899137;
      elif (pt > 30 and pt <= 50): num = 0.923753;
      elif (pt > 50 and pt <= 80): num = 0.933253;
      elif (pt > 80 and pt <= 9999): num = 0.904548;
    elif (abs(eta) > 2.1 and abs(eta) <= 2.4):
      if (pt > 15 and pt <= 20): num = 0.798669;
      elif (pt > 20 and pt <= 30): num = 0.856249;
      elif (pt > 30 and pt <= 50): num = 0.891814;
      elif (pt > 50 and pt <= 80): num = 0.896099;
      elif (pt > 80 and pt <= 9999): num = 0.819963;
  elif (idx == -1): # syst up
    if (abs(eta) > 0 and abs(eta) <= 1.2): 
      if   (pt > 15 and pt <= 20) : num = 0.884283;
      elif (pt > 20 and pt <= 30) : num = 0.924391;
      elif (pt > 30 and pt <= 50) : num = 0.949199;
      elif (pt > 50 and pt <= 80) : num = 0.949717;
      elif (pt > 80 and pt <= 9999) : num = 0.940982;
    elif (abs(eta) > 1.2 and abs(eta) <= 2.1): 
      if   (pt > 15 and pt <= 20) : num = 0.898453;
      elif (pt > 20 and pt <= 30) : num = 0.907464;
      elif (pt > 30 and pt <= 50) : num = 0.927804;
      elif (pt > 50 and pt <= 80) : num = 0.941646;
      elif (pt > 80 and pt <= 9999) : num = 0.930199;
    elif (abs(eta) > 2.1 and abs(eta) <= 2.4):
      if (pt > 15 and pt <= 20)     : num = 0.835232;
      elif (pt > 20 and pt <= 30)   : num = 0.873788;
      elif (pt > 30 and pt <= 50)   : num = 0.901026;
      elif (pt > 50 and pt <= 80)   : num = 0.916111;
      elif (pt > 80 and pt <= 9999) : num = 0.891507;
  elif (idx == -2): # down
    if (abs(eta) > 0 and abs(eta) <= 1.2): 
      if (pt > 15 and pt <= 20): num = 0.867235;
      elif (pt > 20 and pt <= 30): num = 0.92359;
      elif (pt > 30 and pt <= 50): num = 0.948398;
      elif (pt > 50 and pt <= 80): num = 0.948973;
      elif (pt > 80 and pt <= 9999): num = 0.940464;
    elif (abs(eta) > 1.2 and abs(eta) <= 2.1):
      if (pt > 15 and pt <= 20): num = 0.889496;
      elif (pt > 20 and pt <= 30): num = 0.905675;
      elif (pt > 30 and pt <= 50): num = 0.925708;
      elif (pt > 50 and pt <= 80): num = 0.938938;
      elif (pt > 80 and pt <= 9999): num = 0.927185;
    elif (abs(eta) > 2.1 and abs(eta) <= 2.4): 
      if   (pt > 15 and pt <= 20)  : num = 0.822439;
      elif (pt > 20 and pt <= 30)  : num = 0.869667;
      elif (pt > 30 and pt <= 50)  : num = 0.896904;
      elif (pt > 50 and pt <= 80)  : num = 0.91199;
      elif (pt > 80 and pt <= 9999): num = 0.887386;

  if (idx == 200): den = 1.0;
  if (idx == 300): num = den * den;

  return num,den

from math import sqrt
def GetMuonTrigSF(pt, eta, pt2 = -99, eta2 = -99):
  if pt2 == -99 and eta2 == -99:
    ### One lepton
    n,d     = tnp_weight_trig_pbpb(pt, eta,  0); SF    = n/d
    nyu,dyu = tnp_weight_trig_pbpb(pt, eta, +1); SFsyu = nyu/dyu
    nyd,dyd = tnp_weight_trig_pbpb(pt, eta, -1); SFsyd = nyd/dyd
    ntu,dtu = tnp_weight_trig_pbpb(pt, eta, +2); SFstu = ntu/dtu
    ntd,dtd = tnp_weight_trig_pbpb(pt, eta, -2); SFstd = ntd/dtd

  else:
    geff = lambda e1,e2 : e1+e2-e1*e2
    n1,d1     = tnp_weight_trig_pbpb(pt,  eta,   0);
    nyu1,dyu1 = tnp_weight_trig_pbpb(pt,  eta,  +1);
    nyd1,dyd1 = tnp_weight_trig_pbpb(pt,  eta,  -1);
    ntu1,dtu1 = tnp_weight_trig_pbpb(pt,  eta,  +2);
    ntd1,dtd1 = tnp_weight_trig_pbpb(pt,  eta,  -2);
    n2,d2     = tnp_weight_trig_pbpb(pt2, eta2,  0);
    nyu2,dyu2 = tnp_weight_trig_pbpb(pt2, eta2, +1);
    nyd2,dyd2 = tnp_weight_trig_pbpb(pt2, eta2, -1);
    ntu2,dtu2 = tnp_weight_trig_pbpb(pt2, eta2, +2);
    ntd2,dtd2 = tnp_weight_trig_pbpb(pt2, eta2, -2);
    SF    = geff(n1  ,n2  )/geff(d1  ,  d2)
    SFsyu = geff(nyu1,nyu2)/geff(dyu1,dyu2)
    SFsyd = geff(nyd1,nyd2)/geff(dyd1,dyd2)
    SFstu = geff(ntu1,ntu2)/geff(dtu1,dtu2)
    SFstd = geff(ntd1,ntd2)/geff(dtd1,dtd2)

  toteup = (SF-SFsyu)*(SF-SFsyu) + (SF-SFstu)*(SF-SFstu)
  totedo = (SF-SFsyd)*(SF-SFsyd) + (SF-SFstd)*(SF-SFstd)
  return SF, (sqrt(toteup) + sqrt(totedo))/2
