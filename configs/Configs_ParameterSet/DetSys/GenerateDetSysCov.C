//std::vector<std::string> GetGENIEMorphKnobNames();
std::vector<std::string> GetDetSysMultisigmaKnobNames();

void GenerateDetSysCov()
{

  std::vector<std::string> detsysMultisigmaNames = GetDetSysMultisigmaKnobNames();
  //std::vector<std::string> genieMorphNames = GetGENIEMorphKnobNames();

  std::vector<std::string> KnobNames;
  KnobNames.insert(KnobNames.end(), detsysMultisigmaNames.begin(), detsysMultisigmaNames.end());
  const unsigned int NKnob = KnobNames.size();

  std::string outputname = "gundaminput_detsyst.root";

  // Make the covariance matrix: ((0,1), (1,0))
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> detsys_cov(NKnob);
  for (int i = 0; i < NKnob; i++) {

    std::string this_knobname = KnobNames[i];

    double this_prefit_err = 1.0;

    if(i<detsysMultisigmaNames.size()){
      this_prefit_err = 1.0;
    }
    else{
      this_prefit_err = 1.0;
    }

    std::cout << this_knobname << "\t" << this_prefit_err << std::endl;

    detsys_cov(i, i) = this_prefit_err*this_prefit_err;

  }
  
  detsys_cov.Write("detsys_cov");

  TObjArray detsys_param_names;
  for(const auto& name: detsysMultisigmaNames){
    detsys_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writting " << name << std::endl;
  }
  
  _file->WriteObjectAny( &detsys_param_names, "TObjArray", "detsys_param_names" );

  TVectorD detsys_param_prior(NKnob);
  TVectorD detsys_param_lb(NKnob);
  TVectorD detsys_param_ub(NKnob);
  for(int i=0; i<NKnob; i++){
    if(i<detsysMultisigmaNames.size()){
      detsys_param_prior[i] = 0.;
      detsys_param_lb[i] = -3.;
      detsys_param_ub[i] = +3.;
    }
    else{
      detsys_param_prior[i] = 0.;
      detsys_param_lb[i] = -3;
      detsys_param_ub[i] = 3.;
    }
  }
  detsys_param_prior.Write("detsys_param_prior");
  detsys_param_lb.Write("detsys_param_lb");
  detsys_param_ub.Write("detsys_param_ub");

  //_file->Close();

}

/*
std::vector<std::string> GetGENIEMorphKnobNames(){

  return {
    "VecFFCCQEshape",
      "DecayAngMEC",
      "Theta_Delta2Npi",
      "ThetaDelta2NRad",
      };

}
*/

std::vector<std::string> GetDetSysMultisigmaKnobNames(){
  return {
    "var00",
      "var01",
      "var02",
      "var03",
      "var04",
      "var05",
      "var06",
      "var07",
      "var08",
      };
}
