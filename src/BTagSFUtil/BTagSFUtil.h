#include <string>
#include "BTagCalibrationStandalone.h"
#include <Riostream.h>
#include "TRandom3.h"
#include "TMath.h"
#include "TF1.h"
#include "TH2F.h"
#include "TFile.h"

using namespace std;

class BTagSFUtil{

 public:
    
  BTagSFUtil(const string& MeasurementType, 
	     const TString& BTagSFPath, const string& BTagAlgorithm, 
	     const TString& OperatingPoint, int SystematicIndex = 0, int year = 2017, TString FastSimDataset = "");
  ~BTagSFUtil();

  float GetJetSF(float JetDiscriminant, int JetFlavor, float JetPt, float JetEta);
  bool IsTagged(float JetDiscriminant, int JetFlavor, float JetPt, float JetEta, UInt_t Seed = 0);
  void IsFastSim(Bool_t is = 1){ gIsFastSim = is;}
  Float_t GetFastSimBtagSF(Int_t flav, Float_t eta, Float_t pt, Float_t csv, Float_t sys = 0);
  float JetTagEfficiency(int JetFlavor, float JetPt, float JetEta);
  float ptMax = 140;

 private:

  Bool_t gIsFastSim;
  BTagCalibrationReader *reader_b, *reader_c, *reader_l, *FastSimReader_b, *FastSimReader_c, *FastSimReader_l;

  void GetBTagPayload(TString BTagAlgorithm, TString DataPeriod);
  void GetFastSimPayload(TString BTagAlgorithm, TString FastSimDataset);

  float ScaleFactorB(float JetPt, int SystematicFlag);
  float ScaleFactorLight(float JetPt, float JetEta, int SystematicFlag);
  float ScaleFactorJet(int JetFlavor, float JetPt, float JetEta, int SystematicFlag);

  void  LoadHistos(const TString& path, int year, const TString& tagger, const TString& wp);
  float TagEfficiencyB(float JetPt, float JetEta);
  float TagEfficiencyC(float JetPt, float JetEta);
  float TagEfficiencyLight(float JetPt, float JetEta);

  float FastSimCorrectionFactor(int JetFlavor, float JetPt, float JetEta);
  
  TRandom3* rand_;

  TString TaggerName, TaggerOP;
  float TaggerCut;

  TF1 *funSFb, *funSFlight[4][3];
 
  TH2F* btagmceff;
  TH2F* btagmceffC;
  TH2F* btagmceffL;

  int nBTagPtBins;
  float BTagPtBinEdge[50];
  float SFb_error[50];

  int nBTagEtaBins;
  float BTagEtaBinEdge[50];

  bool IsFastSimDataset;
  int nFastSimPtBins, nFastSimEtaBins[3];
  float FastSimPtBinEdge[50], FastSimEtaBinEdge[50][3];
  float FastSimCF[50][2][3];
  float FastSimCF_error[50][2][3]; int FastSimSystematic;

  string SystematicFlagBC, SystematicFlagL;
    
};

