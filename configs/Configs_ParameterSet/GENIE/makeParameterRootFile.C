std::vector<std::string> GetGENIEMorphKnobNames();
std::vector<std::string> GetGENIEMultisigmaKnobNames();

void makeParameterRootFile()
{

  std::vector<std::string> genieMultisigmaNames = GetGENIEMultisigmaKnobNames();
  std::vector<std::string> genieMorphNames = GetGENIEMorphKnobNames();

  std::vector<std::string> KnobNames;
  KnobNames.insert(KnobNames.end(), genieMultisigmaNames.begin(), genieMultisigmaNames.end());
  KnobNames.insert(KnobNames.end(), genieMorphNames.begin(), genieMorphNames.end());
  const unsigned int NKnob = KnobNames.size();

  std::string outputname = "gundaminput_geniesyst.root";

  // Make the covariance matrix: ((0,1), (1,0))
  TFile *file = new TFile(outputname.c_str(),"RECREATE");
  file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> xsec_cov(NKnob);
  for (int i = 0; i < NKnob; i++) {

    std::string this_knobname = KnobNames[i];

    double this_prefit_err = 1.0;

    if(i<genieMultisigmaNames.size()){
      this_prefit_err = 1.0;
    }
    else{
      this_prefit_err = 1.0;
    }

    std::cout << this_knobname << "\t" << this_prefit_err << std::endl;

    xsec_cov(i, i) = this_prefit_err*this_prefit_err;

  }

  // Z-exp
  double ZExpCorr[4][4];
  ZExpCorr[0][0] = 1.000000;
  ZExpCorr[0][1] = 0.350000;
  ZExpCorr[0][2] = -0.678000;
  ZExpCorr[0][3] = 0.611000;
  ZExpCorr[1][0] = 0.350000;
  ZExpCorr[1][1] = 1.000000;
  ZExpCorr[1][2] = -0.898000;
  ZExpCorr[1][3] = 0.367000;
  ZExpCorr[2][0] = -0.678000;
  ZExpCorr[2][1] = -0.898000;
  ZExpCorr[2][2] = 1.000000;
  ZExpCorr[2][3] = -0.685000;
  ZExpCorr[3][0] = 0.611000;
  ZExpCorr[3][1] = 0.367000;
  ZExpCorr[3][2] = -0.685000;
  ZExpCorr[3][3] = 1.000000;
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      xsec_cov(i,j) = ZExpCorr[i][j];
    }
  }

  xsec_cov.Write("xsec_cov");

  TObjArray xsec_param_names;
  for(const auto& name: genieMultisigmaNames){
    xsec_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writting " << name << std::endl;
  }
  for(const auto& name: genieMorphNames){
    xsec_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writting " << name << std::endl;
  }
  file->WriteObjectAny( &xsec_param_names, "TObjArray", "xsec_param_names" );

  TVectorD xsec_param_prior(NKnob);
  TVectorD xsec_param_lb(NKnob);
  TVectorD xsec_param_ub(NKnob);
  for(int i=0; i<NKnob; i++){
    if(i<genieMultisigmaNames.size()){
      xsec_param_prior[i] = 0.;
      xsec_param_lb[i] = -3.;
      xsec_param_ub[i] = +3.;
    }
    else if(i==genieMultisigmaNames.size()){
      xsec_param_prior[i] = 0.005;
      xsec_param_lb[i] = -3;
      xsec_param_ub[i] = 3.;
    }
    else{
      xsec_param_prior[i] = 0.;
      xsec_param_lb[i] = -3;
      xsec_param_ub[i] = 3.;
    }
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

std::vector<std::string> GetcGENIEMultisigmaKnobNames(){
  return {
"GENIEReWeight_SBN_v1_multisigma_ZExpPCAB1",
"GENIEReWeight_SBN_v1_multisigma_ZExpPCAB2",
"GENIEReWeight_SBN_v1_multisigma_ZExpPCAB3",
"GENIEReWeight_SBN_v1_multisigma_ZExpPCAB4",
"GENIEReWeight_SBN_v1_multisigma_RPA_CCQE",
"GENIEReWeight_SBN_v1_multisigma_CoulombCCQE",
"GENIEReWeight_SBN_v1_multisigma_NormCCMEC",
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
