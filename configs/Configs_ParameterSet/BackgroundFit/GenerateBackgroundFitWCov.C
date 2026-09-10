// Generates the diagonal prior covariance for the BackgroundFit true_generator_w
// parameter set (parameterSet_backgroundFit_true_w.yaml). Modeled directly on
// GenerateBackgroundFitQ2Cov.C in this same folder.
//
// Unlike that Q2 version, this reproduces Howard et al. (ICARUS NuMI CC-mesonless
// technote)'s own adopted BackgroundFit scheme as-is: of the three options he
// tested (flat 40%, flat 40/60% split by low/high-W, bin-by-bin from a GENIE/NuWro
// ratio), he kept flat 40% uncertainty on low-W and 60% on high-W. This is that
// same 2-parameter split, just built on our own true_generator_w branch rather
// than his.
//
// true_generator_w did not exist as a usable branch until now: the framework's
// existing true_W (vars::W()) is NaN for 61-69% of background (categories 4-7)
// events, because it depends on selectors::leading_muon() succeeding, which fails
// for true background/pion-production events with no true muon in the final
// state. true_generator_w reads obj.w directly (a generator-truth field,
// independent of any downstream particle-loop/muon-matching step), confirmed
// empirically to have <0.15% NaN fraction in every true_category, including
// categories 4-7 specifically (see 1muNp0pi_Nge1_uncontained.root,
// events/nominal/selected: true_generator_w NaN frac 0.0001 in categories 4-7,
// vs 0.6712 for true_W in the same sample). It is NOT numerically the same
// quantity as true_W (mean diff +0.46 GeV, correlation 0.38 on the overlap in
// background) -- true_W is restricted to visible final-state energy only, while
// true_generator_w is the generator's own truth hadronic invariant mass -- so
// this is a distinct, not interchangeable, W definition.
//
// Deliberately uncorrelated (diagonal), same as the Q2 version and same as all
// three of Howard's schemes.
//
// NBins MUST match the number of bins in
// ../../binnings/binning_true_generator_w.txt (currently 2: below and above
// 1.4 GeV) -- ParameterSet::readParameterDefinitionFile() sets the parameter
// count from this covariance matrix's dimension once it's present, so a
// mismatch against the binning file's bin count is a hard error.
//
// Run with: root -l -b -q GenerateBackgroundFitWCov.C

void GenerateBackgroundFitWCov()
{
  const int NBins = 2;

  // Howard's own flat 40% (low-W) / 60% (high-W) fractional prior widths.
  // Same order as binning_true_generator_w.txt: [0.0,1.4) low-W, [1.4,inf) high-W.
  const double fracUnc[2] = {
    0.40, 0.60
  };

  std::string outputname = "gundaminput_backgroundfit_true_w.root";
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> backgroundfit_w_cov(NBins);
  for (int i = 0; i < NBins; i++) {
    std::cout << "true_generator_w bin " << i << "\t" << fracUnc[i] << std::endl;
    backgroundfit_w_cov(i, i) = fracUnc[i] * fracUnc[i];
  }

  backgroundfit_w_cov.Write("backgroundfit_w_cov");

  //_file->Close();
}
