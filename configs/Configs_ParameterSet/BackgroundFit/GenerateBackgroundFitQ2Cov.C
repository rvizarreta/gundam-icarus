// Generates the diagonal prior covariance for the BackgroundFit true_generator_q2
// parameter set (parameterSet_backgroundFit_true_q2.yaml). Modeled directly on
// GenerateDetSysCov.C / GenerateFLUXCov.C in the sibling DetSys/ and Flux/ folders.
//
// Convention, following Howard et al. (ICARUS NuMI CC-mesonless technote)'s
// "BackgroundFit" template parameters on nu-CC-other events: each parameter is a
// scale factor with a prior of 1 (GUNDAM's ParameterSet.cpp defaults an omitted
// prior vector to 1 per parameter -- see defineParameters(), which is why no
// parameterPriorTVectorD is written here), constrained by a per-bin fractional
// Gaussian uncertainty. Deliberately uncorrelated (diagonal): none of Howard's
// three schemes (flat 40%, flat 40/60% split by low/high-W, bin-by-bin from a
// GENIE/NuWro ratio) introduce off-diagonal correlations between background bins.
//
// Unlike the earlier flat-40% version, these widths are bin-by-bin, derived
// directly from our own MC and generator files rather than borrowed from
// Howard's technote -- see Notebooks/dpT/BackgroungTemplates.ipynb ("Step 5"):
// for each true_generator_q2 bin, |R-1| where R = (NuWro CC-other fraction of
// CC-inclusive) / (GENIE CC-other fraction of CC-inclusive), using all 10 GENIE
// and 10 NuWro NUISANCE flat-tree files under data/Generators/{GENIE,NuWro}/fhc_Nu14.
// CC-other here is the generator-truth proxy flagCCINC & !flagCC0pi -- an
// approximation of categories 4-7, since no detector simulation/selection is
// applied in those flat trees. See the notebook for the full derivation and its
// caveats (binning-support and reco-separating-power checks also live there).
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

  // Bin-by-bin fractional prior widths from the GENIE-vs-NuWro CC-other/Q2
  // comparison (Notebooks/dpT/BackgroungTemplates.ipynb, Step 5) -- replaces
  // the earlier flat 0.4 for every bin. Same order as binning_true_generator_q2.txt:
  // [0.0,0.1), [0.1,0.2), [0.2,0.3), [0.3,0.4), [0.4,0.5), [0.5,0.6), [0.6,0.7),
  // [0.7,0.8), [0.8,inf).
  const double fracUnc[9] = {
    0.421, 0.140, 0.015, 0.059, 0.105, 0.140, 0.169, 0.189, 0.198
  };

  std::string outputname = "gundaminput_backgroundfit_true_q2.root";
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> backgroundfit_q2_cov(NBins);
  for (int i = 0; i < NBins; i++) {
    std::cout << "true_generator_q2 bin " << i << "\t" << fracUnc[i] << std::endl;
    backgroundfit_q2_cov(i, i) = fracUnc[i] * fracUnc[i];
  }

  backgroundfit_q2_cov.Write("backgroundfit_q2_cov");

  //_file->Close();
}
