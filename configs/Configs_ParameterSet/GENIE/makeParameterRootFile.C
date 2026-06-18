std::vector<std::string> GetGENIEMorphKnobNames();
std::vector<std::string> GetGENIEMultisigmaKnobNames();

// Prior width multiplier for MaCCRES/MvCCRES — set to 1, 2, 3, 5, or large for ~unconstrained
const double RES_PRIOR_SCALE = 1.0;

void makeParameterRootFile()
{

  std::vector<std::string> genieMultisigmaNames = GetGENIEMultisigmaKnobNames();
  std::vector<std::string> genieMorphNames = GetGENIEMorphKnobNames();

  std::vector<std::string> KnobNames;
  KnobNames.insert(KnobNames.end(), genieMultisigmaNames.begin(), genieMultisigmaNames.end());
  KnobNames.insert(KnobNames.end(), genieMorphNames.begin(), genieMorphNames.end());
  const unsigned int NKnob = KnobNames.size();

  std::string outputname = "gundaminput_geniesyst.root";

  TFile *file = new TFile(outputname.c_str(),"RECREATE");
  file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> xsec_cov(NKnob);

  // Initialize to identity, with RES form-factor priors scaled
  for (int i = 0; i < NKnob; i++) {
    double w = 1.0;
    if (KnobNames[i].find("MaCCRES") != std::string::npos ||
        KnobNames[i].find("MvCCRES") != std::string::npos) {
      w = RES_PRIOR_SCALE;
    }
    xsec_cov(i, i) = w * w;
    std::cout << KnobNames[i] << "\t" << w*w << std::endl;
  }

  // ZExp PCA b-parameters are uncorrelated by construction (PCA diagonalizes
  // the covariance matrix). They occupy indices 0-3 in genieMultisigmaNames.
  // The identity matrix is already correct for them — no off-diagonal terms needed.
  //
  // For reference, the original ZExp A-parameter correlation matrix from
  // PRD 93, 113015 (Meyer et al. 2016) was:
  //   ZExpCorr[0][0]=1.000  [0][1]=0.350  [0][2]=-0.678  [0][3]=0.611
  //   ZExpCorr[1][0]=0.350  [1][1]=1.000  [1][2]=-0.898  [1][3]=0.367
  //   ZExpCorr[2][0]=-0.678 [2][1]=-0.898 [2][2]=1.000   [2][3]=-0.685
  //   ZExpCorr[3][0]=0.611  [3][1]=0.367  [3][2]=-0.685  [3][3]=1.000
  // The PCA rotation diagonalizes this matrix, so b1-b4 are independent.

  xsec_cov.Write("xsec_cov");

  TObjArray xsec_param_names;
  for(const auto& name: genieMultisigmaNames){
    xsec_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writing " << name << std::endl;
  }
  for(const auto& name: genieMorphNames){
    xsec_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writing " << name << std::endl;
  }
  file->WriteObjectAny( &xsec_param_names, "TObjArray", "xsec_param_names" );

  TVectorD xsec_param_prior(NKnob);
  TVectorD xsec_param_lb(NKnob);
  TVectorD xsec_param_ub(NKnob);
  for(int i=0; i<NKnob; i++){
    xsec_param_prior[i] = 0.;
    if (KnobNames[i].find("VecFFCCQEshape") != std::string::npos) {
     xsec_param_prior[i] = 0.005;
    }
    double bound = 3.0;
    if (KnobNames[i].find("MaCCRES") != std::string::npos ||
        KnobNames[i].find("MvCCRES") != std::string::npos) {
      bound = 3.0 * RES_PRIOR_SCALE;
    }
    xsec_param_lb[i] = -bound;
    xsec_param_ub[i] = +bound;
  }
  xsec_param_prior.Write("xsec_param_prior");
  xsec_param_lb.Write("xsec_param_lb");
  xsec_param_ub.Write("xsec_param_ub");

  file->Close();
}

std::vector<std::string> GetGENIEMorphKnobNames(){
  return {
"GENIEReWeight_SBN_v1_multisigma_VecFFCCQEshape",
"GENIEReWeight_SBN_v1_multisigma_DecayAngMEC",
"GENIEReWeight_SBN_v1_multisigma_Theta_Delta2Npi",
"GENIEReWeight_SBN_v1_multisigma_ThetaDelta2NRad",
  };
}

std::vector<std::string> GetGENIEMultisigmaKnobNames(){
  return {
// ZExp PCA b-parameters (replace ZExpA1-A4CCQE)
// Uncorrelated by PCA construction — identity covariance
"ZExpPCAWeighter_myreweighter_b1",
"ZExpPCAWeighter_myreweighter_b2",
"ZExpPCAWeighter_myreweighter_b3",
"ZExpPCAWeighter_myreweighter_b4",
// Remaining GENIE knobs (unchanged)
"GENIEReWeight_SBN_v1_multisigma_RPA_CCQE",
"GENIEReWeight_SBN_v1_multisigma_CoulombCCQE",
"GENIEReWeight_SBN_v1_multisigma_NormCCMEC",
//"Synthetic_multisigma_NormCCRES",
"GENIEReWeight_SBN_v1_multisigma_NormNCMEC",
"GENIEReWeight_SBN_v1_multisigma_MaNCEL",
"GENIEReWeight_SBN_v1_multisigma_EtaNCEL",
"GENIEReWeight_SBN_v1_multisigma_MaCCRES",
"GENIEReWeight_SBN_v1_multisigma_MvCCRES",
"GENIEReWeight_SBN_v1_multisigma_MaNCRES",
"GENIEReWeight_SBN_v1_multisigma_MvNCRES",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvpCC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvpCC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvpNC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvpNC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvnCC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvnCC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvnNC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvnNC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarpCC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarpCC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarpNC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarpNC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarnCC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarnCC2pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarnNC1pi",
"GENIEReWeight_SBN_v1_multisigma_NonRESBGvbarnNC2pi",
"GENIEReWeight_SBN_v1_multisigma_RDecBR1gamma",
"GENIEReWeight_SBN_v1_multisigma_RDecBR1eta",
"GENIEReWeight_SBN_v1_multisigma_NormCCCOH",
"GENIEReWeight_SBN_v1_multisigma_NormNCCOH",
"GENIEReWeight_SBN_v1_multisigma_AhtBY",
"GENIEReWeight_SBN_v1_multisigma_BhtBY",
"GENIEReWeight_SBN_v1_multisigma_CV1uBY",
"GENIEReWeight_SBN_v1_multisigma_CV2uBY",
"GENIEReWeight_SBN_v1_multisigma_MFP_pi",
"GENIEReWeight_SBN_v1_multisigma_FrCEx_pi",
"GENIEReWeight_SBN_v1_multisigma_FrInel_pi",
"GENIEReWeight_SBN_v1_multisigma_FrAbs_pi",
"GENIEReWeight_SBN_v1_multisigma_FrPiProd_pi",
"GENIEReWeight_SBN_v1_multisigma_MFP_N",
"GENIEReWeight_SBN_v1_multisigma_FrCEx_N",
"GENIEReWeight_SBN_v1_multisigma_FrInel_N",
"GENIEReWeight_SBN_v1_multisigma_FrAbs_N",
"GENIEReWeight_SBN_v1_multisigma_FrPiProd_N",
  };
}