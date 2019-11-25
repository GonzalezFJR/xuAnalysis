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

def GetMuonTrigEff(pt, eta, sys = 0):
  n, d = tnp_weight_trig_pbpb(pt,  eta, 0);
  if abs(sys) == 1:
    nu, du = tnp_weight_trig_pbpb(pt,  eta, sys);
    ns, ds = tnp_weight_trig_pbpb(pt,  eta, 2*sys);
    dn = sqrt((n-nu)*(n-nu) + (n-ns)*(n-ns))
    dd = sqrt((d-du)*(d-du) + (d-ds)*(d-ds))
    n = n + dn if sys > 0 else n - dn
    d = d + dd if sys > 0 else d - dd
  return n, d

##################################################################
### Tracking

def tnp_weight_glbtrk_pbpb_MC(eta):
  den = 1
  if   (eta >= -2.4 and eta <= -2.1):  den = 0.985973;
  elif (eta >  -2.1 and eta <= -1.6):  den = 0.99412;
  elif (eta >  -1.6 and eta <= -1.2):  den = 0.996646;
  elif (eta >  -1.2 and eta <= -0.9):  den = 0.991832;
  elif (eta >  -0.9 and eta <=  0  ):  den = 0.985575;
  elif (eta >   0   and eta <=  0.9):  den = 0.985295;
  elif (eta >   0.9 and eta <=  1.2):  den = 0.992634;
  elif (eta >   1.2 and eta <=  1.6):  den = 0.996896;
  elif (eta >   1.6 and eta <=  2.1):  den = 0.994506;
  elif (eta >   2.1 and eta <=  2.4):  den = 0.987764;
  return den


def tnp_weight_glbtrk_pbpb_Data(eta, idx = 0):
		if (idx == 0):
			if (eta >= -2.4 and eta <= -2.1): num = 1;
			elif (eta > -2.1 and eta <= -1.6): num = 0.986484;
			elif (eta > -1.6 and eta <= -1.2): num = 0.998253;
			elif (eta > -1.2 and eta <= -0.9): num = 0.987887;
			elif (eta > -0.9 and eta <= 0): num = 0.987426;
			elif (eta > 0 and eta <= 0.9): num = 0.981425;
			elif (eta > 0.9 and eta <= 1.2): num = 0.984663;
			elif (eta > 1.2 and eta <= 1.6): num = 0.992795;
			elif (eta > 1.6 and eta <= 2.1): num = 0.983557;
			elif (eta > 2.1 and eta <= 2.4): num = 0.954671;

		elif (idx == 1): # stat up
			if (eta >= -2.4 and eta <= -2.1): num = 1;
			elif (eta > -2.1 and eta <= -1.6): num = 0.99644;
			elif (eta > -1.6 and eta <= -1.2): num = 1;
			elif (eta > -1.2 and eta <= -0.9): num = 0.994144;
			elif (eta > -0.9 and eta <= 0): num = 0.992029;
			elif (eta > 0 and eta <= 0.9): num = 0.987024;
			elif (eta > 0.9 and eta <= 1.2): num = 0.992709;
			elif (eta > 1.2 and eta <= 1.6): num = 0.997686;
			elif (eta > 1.6 and eta <= 2.1): num = 0.991048;
			elif (eta > 2.1 and eta <= 2.4): num = 0.979823;

		elif (idx == 2):  # stat down
			if   (eta >= -2.4 and eta <= -2.1): num = 0.979675;
			elif (eta >  -2.1 and eta <= -1.6): num = 0.974748;
			elif (eta >  -1.6 and eta <= -1.2): num = 0.993399;
			elif (eta >  -1.2 and eta <= -0.9): num = 0.978866;
			elif (eta >  -0.9 and eta <=  0  ): num = 0.98235;
			elif (eta >   0   and eta <=  0.9): num = 0.974871;
			elif (eta >   0.9 and eta <=  1.2): num = 0.974046;
			elif (eta >   1.2 and eta <=  1.6): num = 0.985567;
			elif (eta >   1.6 and eta <=  2.1): num = 0.974474;
			elif (eta >   2.1 and eta <=  2.4): num = 0.92457;
		
		elif (idx == -1):  # syst up
			if (eta >= -2.4 and eta <= -2.1): num = 1.0107;
			elif (eta > -2.1 and eta <= -1.6): num = 0.992138;
			elif (eta > -1.6 and eta <= -1.2): num = 0.999945;
			elif (eta > -1.2 and eta <= -0.9): num = 0.988701;
			elif (eta > -0.9 and eta <= 0): num = 0.988734;
			elif (eta > 0 and eta <= 0.9): num = 0.985979;
			elif (eta > 0.9 and eta <= 1.2): num = 0.987238;
			elif (eta > 1.2 and eta <= 1.6): num = 0.994278;
			elif (eta > 1.6 and eta <= 2.1): num = 0.98701;
			elif (eta > 2.1 and eta <= 2.4): num = 0.960013;
		
		elif (idx == -2) : # syst down
			if (eta >= -2.4 and eta <= -2.1): num = 0.989305;
			elif (eta > -2.1 and eta <= -1.6): num = 0.980829;
			elif (eta > -1.6 and eta <= -1.2): num = 0.99656;
			elif (eta > -1.2 and eta <= -0.9): num = 0.987074;
			elif (eta > -0.9 and eta <= 0): num = 0.986119;
			elif (eta > 0 and eta <= 0.9): num = 0.976872;
			elif (eta > 0.9 and eta <= 1.2): num = 0.982088;
			elif (eta > 1.2 and eta <= 1.6): num = 0.991312;
			elif (eta > 1.6 and eta <= 2.1): num = 0.980103;
			elif (eta > 2.1 and eta <= 2.4): num = 0.949328;

		return num

def tnp_weight_muid_pbpb_MC(eta):
   if   (eta >= -2.4 and eta <= -2.1): den = 0.994139; 
   elif (eta >  -2.1 and eta <= -1.6): den = 0.99449; 
   elif (eta >  -1.6 and eta <= -1.2): den = 0.983536; 
   elif (eta >  -1.2 and eta <= -0.9): den = 0.964562; 
   elif (eta >  -0.9 and eta <= -0.6): den = 0.973316; 
   elif (eta >  -0.6 and eta <= -0.3): den = 0.981446; 
   elif (eta >  -0.3 and eta <=  0  ): den = 0.968189; 
   elif (eta >   0   and eta <=  0.3): den = 0.9617; 
   elif (eta >   0.3 and eta <=  0.6): den = 0.979738; 
   elif (eta >   0.6 and eta <=  0.9): den = 0.969536; 
   elif (eta >   0.9 and eta <=  1.2): den = 0.960259; 
   elif (eta >   1.2 and eta <=  1.6): den = 0.983279; 
   elif (eta >   1.6 and eta <=  2.1): den = 0.99477; 
   elif (eta >   2.1 and eta <=  2.4): den = 0.994065; 
   return den


def tnp_weight_muid_pbpb_Data(eta, idx = 0):
   syst = 0.6e-2
   if (idx == 0):
	   if (eta >= -2.4 and eta <= -2.1): num = 0.984278; 
	   elif (eta > -2.1 and eta <= -1.6): num = 0.994031; 
	   elif (eta > -1.6 and eta <= -1.2): num = 0.978562; 
	   elif (eta > -1.2 and eta <= -0.9): num = 0.954321; 
	   elif (eta > -0.9 and eta <= -0.6): num = 0.966508; 
	   elif (eta > -0.6 and eta <= -0.3): num = 0.98402; 
	   elif (eta > -0.3 and eta <= 0): num = 0.958369; 
	   elif (eta > 0 and eta <= 0.3): num = 0.959429; 
	   elif (eta > 0.3 and eta <= 0.6): num = 0.976528; 
	   elif (eta > 0.6 and eta <= 0.9): num = 0.967646; 
	   elif (eta > 0.9 and eta <= 1.2): num = 0.961046; 
	   elif (eta > 1.2 and eta <= 1.6): num = 0.980274; 
	   elif (eta > 1.6 and eta <= 2.1): num = 0.991677; 
	   elif (eta > 2.1 and eta <= 2.4): num = 0.993007; 
   elif (idx == 1): # stat up
	   if (eta >= -2.4 and eta <= -2.1): num = 0.987203; 
	   elif (eta > -2.1 and eta <= -1.6): num = 0.995641; 
	   elif (eta > -1.6 and eta <= -1.2): num = 0.981641; 
	   elif (eta > -1.2 and eta <= -0.9): num = 0.958889; 
	   elif (eta > -0.9 and eta <= -0.6): num = 0.970274; 
	   elif (eta > -0.6 and eta <= -0.3): num = 0.986882; 
	   elif (eta > -0.3 and eta <= 0): num = 0.962433; 
	   elif (eta > 0 and eta <= 0.3): num = 0.96344; 
	   elif (eta > 0.3 and eta <= 0.6): num = 0.979706; 
	   elif (eta > 0.6 and eta <= 0.9): num = 0.971414; 
	   elif (eta > 0.9 and eta <= 1.2): num = 0.965537; 
	   elif (eta > 1.2 and eta <= 1.6): num = 0.983167; 
	   elif (eta > 1.6 and eta <= 2.1): num = 0.99336; 
	   elif (eta > 2.1 and eta <= 2.4): num = 0.995579; 
	   num *= (1+syst)
   elif (idx == -1): # stat down
	   if (eta >= -2.4 and eta <= -2.1): num = 0.98094; 
	   elif (eta > -2.1 and eta <= -1.6): num = 0.992199; 
	   elif (eta > -1.6 and eta <= -1.2): num = 0.975247; 
	   elif (eta > -1.2 and eta <= -0.9): num = 0.949482; 
	   elif (eta > -0.9 and eta <= -0.6): num = 0.962497; 
	   elif (eta > -0.6 and eta <= -0.3): num = 0.980916; 
	   elif (eta > -0.3 and eta <= 0): num = 0.954075; 
	   elif (eta > 0 and eta <= 0.3): num = 0.955169; 
	   elif (eta > 0.3 and eta <= 0.6): num = 0.973111; 
	   elif (eta > 0.6 and eta <= 0.9): num = 0.963634; 
	   elif (eta > 0.9 and eta <= 1.2): num = 0.956295; 
	   elif (eta > 1.2 and eta <= 1.6): num = 0.977135; 
	   elif (eta > 1.6 and eta <= 2.1): num = 0.987932; 
	   elif (eta > 2.1 and eta <= 2.4): num = 0.989895; 
	   num *= (1-syst)
   elif (idx == 2): # syst up
     return tnp_weight_muid_pbpb_Data(eta) * (1 + syst)
   elif (idx == -2): # syst down
     return tnp_weight_muid_pbpb_Data(eta) * (1 - syst)
   else: 
     print 'WARNING: wrong ID'
     return 1;
   return num


def GetMuonEff(pt, eta, sys = 0):
  geff = lambda e1,e2 : e1+e2-e1*e2
  data  = tnp_weight_glbtrk_pbpb_Data(eta, sys)
  mc    = tnp_weight_glbtrk_pbpb_MC(eta)
  data2 = tnp_weight_muid_pbpb_Data(eta, sys)
  mc2   = tnp_weight_muid_pbpb_MC(eta)
  #SF    = (data/mc)*(data2/mc2)
  SF    = (data2/mc2)
  return SF

def GetMuonEffDimuon(pt, eta, pt2, eta2, sys):
  SF1 = GetMuonEff(pt,  eta,  sys)
  SF2 = GetMuonEff(pt2, eta2, sys)
  return SF1*SF2

#def tnp_weight_trig_pbpb_MC(pt, eta, idx):
#  if pt < 15: pt = 15.01
#  return 0.9775;

def testSFs():
  nb = 10
  for ieta in range(nb):
    eta0 = -2.3
    eta  = eta0 + (2.3*2)/nb*(1+ieta)
    data  = tnp_weight_glbtrk_pbpb_Data(eta)
    mc    = tnp_weight_glbtrk_pbpb_MC(eta)
    data2 = tnp_weight_muid_pbpb_Data(eta)
    mc2   = tnp_weight_muid_pbpb_MC(eta)
    print '[%1.2f]    Reco: %1.3f,    ID: %1.3f'%(eta, data/mc, data2/mc2)

def testTrig():
  for pt in [20, 30, 40, 50, 60]:
    for eta in [-2, -1, 0, 1, 2]:
      print "[%1.0f, %1.0f] %1.2f"%(pt, eta, GetMuonTrigSF(pt,eta, 15, eta)[0])

