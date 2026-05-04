//std::vector<std::string> GetGENIEMorphKnobNames();
std::vector<std::string> GetFluxMultisigmaKnobNames();

void GenerateFLUXCov()
{

  std::vector<std::string> fluxMultisigmaNames = GetFluxMultisigmaKnobNames();
  //std::vector<std::string> genieMorphNames = GetGENIEMorphKnobNames();

  std::vector<std::string> KnobNames;
  KnobNames.insert(KnobNames.end(), fluxMultisigmaNames.begin(), fluxMultisigmaNames.end());
  const unsigned int NKnob = KnobNames.size();

  std::string outputname = "gundaminput_fluxsyst.root";

  // Make the covariance matrix: ((0,1), (1,0))
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> flux_cov(NKnob);
  for (int i = 0; i < NKnob; i++) {

    std::string this_knobname = KnobNames[i];

    double this_prefit_err = 1.0;

    if(i<fluxMultisigmaNames.size()){
      this_prefit_err = 1.0;
    }
    else{
      this_prefit_err = 1.0;
    }

    std::cout << this_knobname << "\t" << this_prefit_err << std::endl;

    flux_cov(i, i) = this_prefit_err*this_prefit_err;

  }
  
  flux_cov.Write("flux_cov");

  TObjArray flux_param_names;
  for(const auto& name: fluxMultisigmaNames){
    flux_param_names.Add( new TObjString(name.c_str()) );
    std::cout << "@@ Writting " << name << std::endl;
  }
  
  _file->WriteObjectAny( &flux_param_names, "TObjArray", "flux_param_names" );

  TVectorD flux_param_prior(NKnob);
  TVectorD flux_param_lb(NKnob);
  TVectorD flux_param_ub(NKnob);
  for(int i=0; i<NKnob; i++){
    if(i<fluxMultisigmaNames.size()){
      flux_param_prior[i] = 0.;
      flux_param_lb[i] = -3.;
      flux_param_ub[i] = +3.;
    }
    else{
      flux_param_prior[i] = 0.;
      flux_param_lb[i] = -3;
      flux_param_ub[i] = 3.;
    }
  }
  flux_param_prior.Write("flux_param_prior");
  flux_param_lb.Write("flux_param_lb");
  flux_param_ub.Write("flux_param_ub");

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

std::vector<std::string> GetFluxMultisigmaKnobNames(){
  return {
    "hysyst_beam_horn_2kA",
      "hysyst_beam_horn1_x_3mm",
      "hysyst_beam_horn1_y_3mm",
      "hysyst_beam_spot_1_3mm",
      "hysyst_beam_spot_1_7mm",
      "hysyst_beam_horn2_x_3mm",
      "hysyst_beam_horn2_y_3mm",
      "hysyst_beam_horns_0mm_water",
      "hysyst_beam_horns_2mm_water",
      "hysyst_beam_Beam_shift_x_1mm",
      "hysyst_beam_Beam_shift_y_1mm",
      "hysyst_beam_Target_z_7mm",
      "hysyst_hpc_0",
      "hysyst_hpc_1",
      "hysyst_hpc_2",
      "hysyst_hpc_3",
      "hysyst_hpc_4",
      "hysyst_hpc_5",
      "hysyst_hpc_6",
      "hysyst_hpc_7",
      "hysyst_hpc_8",
      "hysyst_hpc_9",
      "hysyst_hpc_10",
      "hysyst_hpc_11",
      "hysyst_hpc_12",
      "hysyst_hpc_13",
      "hysyst_hpc_14"
      };
}
