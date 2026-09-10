// Generates the diagonal prior covariance for the BackgroundFit true_generator_w
// parameter set (parameterSet_backgroundFit_true_w.yaml). Modeled directly on
// GenerateBackgroundFitQ2Cov.C in this same folder.
//
// CORRECTED from an earlier version of this file that used only 2 aggregate
// parameters (one flat scale factor for all of low-W, one for all of high-W).
// That was wrong: Howard et al.'s actual BackgroundFit scheme keeps the full
// Q2 granularity within each W region --  "Template parameters for CC-other
// events binned in true W and Q-squared... W: below or above 1.4 GeV; Q2:
// uniform binning between 0 and 0.8 GeV^2, bin size of 0.1 GeV^2" -- i.e. 2
// W-bins x 8 Q2-bins = 16 independent parameters. Only the *prior width*
// (40% vs 60%) is flat across each W region, not the parameter itself. This
// matches a 16-parameter BackgroundFit/#0..#15 postfit plot confirmed
// directly against Howard's technote.
//
// NBins MUST match the number of bins in
// ../../binnings/binning_true_generator_w.txt (currently 16: 2 W-regions
// [0,1.4) and [1.4,inf) GeV, each split into 8 true_generator_q2 bins of
// 0.1 GeV^2 from 0 to 0.8 -- ParameterSet::readParameterDefinitionFile()
// sets the parameter count from this covariance matrix's dimension once
// it's present, so a mismatch against the binning file's bin count is a
// hard error.
//
// Row order MUST match binning_true_generator_w.txt's row order exactly:
// bins 0-7 are low-W (Q2 sub-bins 0-7, in order), bins 8-15 are high-W
// (same 8 Q2 sub-bins, in order) -- so fracUnc is 8x0.40 followed by 8x0.60,
// not interleaved.
//
// Caveat carried over from the binning file: unlike our own
// true_generator_q2-only scheme (which has a 9th overflow bin covering
// Q2 >= 0.8), this 16-bin scheme has NO overflow bin in Q2, matching
// Howard's own stated binning as read from his technote. Any background
// event with true_generator_q2 >= 0.8 GeV^2, in either W region, falls
// outside all 16 bins and is left with NO BackgroundFit systematic applied
// at all (implicitly untouched, not implicitly scaled by 1) -- this is a
// real difference from the true_generator_q2-only scheme, not an oversight
// to silently patch over.
//
// Deliberately uncorrelated (diagonal), same as the Q2 version and same as
// all three of Howard's schemes.
//
// Run with: root -l -b -q GenerateBackgroundFitWCov.C

void GenerateBackgroundFitWCov()
{
  const int NBins = 16;

  // Howard's own flat 40% (low-W, bins 0-7) / 60% (high-W, bins 8-15)
  // fractional prior widths -- flat WITHIN each W region, not derived
  // bin-by-bin the way our true_generator_q2-only scheme's widths are.
  const double fracUnc[16] = {
    0.40, 0.40, 0.40, 0.40, 0.40, 0.40, 0.40, 0.40,
    0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60
  };

  std::string outputname = "gundaminput_backgroundfit_true_w.root";
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> backgroundfit_w_cov(NBins);
  for (int i = 0; i < NBins; i++) {
    std::cout << "true_generator_w/q2 bin " << i << "\t" << fracUnc[i] << std::endl;
    backgroundfit_w_cov(i, i) = fracUnc[i] * fracUnc[i];
  }

  backgroundfit_w_cov.Write("backgroundfit_w_cov");

  //_file->Close();
}
