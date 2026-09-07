// Generates the diagonal prior covariance for the BackgroundFit true_generator_q2
// parameter set (parameterSet_backgroundFit_true_q2.yaml). Modeled directly on
// GenerateDetSysCov.C / GenerateFLUXCov.C in the sibling DetSys/ and Flux/ folders.
//
// Convention, following Howard et al. (ICARUS NuMI CC-mesonless technote) 's
// "BackgroundFit" template parameters on nu-CC-other events: each parameter is a
// scale factor with a prior of 1 (GUNDAM's ParameterSet.cpp defaults an omitted
// prior vector to 1 per parameter -- see defineParameters(), which is why no
// parameterPriorTVectorD is written here), constrained by a flat fractional
// Gaussian uncertainty per bin -- Howard's first, simplest choice of the three
// he tested (flat 40%, flat 40/60% split by low/high-W, bin-by-bin from a
// GENIE/NuWro ratio). Deliberately uncorrelated (diagonal): none of his three
// schemes introduce off-diagonal correlations between background bins.
//
// NBins MUST match the number of bins in
// ../../binnings/binning_true_generator_q2.txt (currently 9: eight 0.1 GeV^2 bins
// from 0 to 0.8, plus one overflow bin) -- ParameterSet::readParameterDefinitionFile()
// sets the parameter count from this covariance matrix's dimension once it's
// present, so a mismatch against the binning file's bin count is a hard error.
//
// Run with: root -l -b -q GenerateBackgroundFitQ2Cov.C

void GenerateBackgroundFitQ2Cov()
{
  const int NBins = 9;

  // Flat 40% prior uncertainty per bin -- revisit if postfit pulls suggest the
  // prior is too tight or too loose (Howard also tried 60% on the high-W bins,
  // and a bin-by-bin scheme read off the GENIE/NuWro ratio).
  const double flatFracUnc = 0.4;

  std::string outputname = "gundaminput_backgroundfit_true_q2.root";
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> backgroundfit_q2_cov(NBins);
  for (int i = 0; i < NBins; i++) {
    std::cout << "true_generator_q2 bin " << i << "\t" << flatFracUnc << std::endl;
    backgroundfit_q2_cov(i, i) = flatFracUnc * flatFracUnc;
  }

  backgroundfit_q2_cov.Write("backgroundfit_q2_cov");

  //_file->Close();
}
