// Generates the diagonal prior covariance for the BackgroundFit true_generator_w
// parameter set's THIRD variant -- Howard et al.'s "bin-by-bin uncertainties from
// Fig. 104," built the way he actually built it: from the GENIE/NuWro ratio,
// split by true W (below/above 1.4 GeV), not just Q2.
//
// This replaces an earlier, WRONG stand-in for this variant
// (parameterSet_backgroundFit_true_q2.yaml / GenerateBackgroundFitQ2Cov.C), which
// only varied with true_generator_q2 and had no W-splitting at all. That version
// was built (Notebooks/dpT/BackgroungTemplates.ipynb) at a time when true_W was
// NaN for ~61-67% of our own background events -- before true_generator_w
// existed. This file redoes that same derivation keeping the W split Howard's
// own Fig. 104 has.
//
// Derivation (run against our local GENIE/NuWro NUISANCE flat-tree productions,
// data/Generators/{GENIE,NuWro}/{fhc_Nu14,fhc_Nu-14}/output_*.nuisflat.root):
//   - Population: BOTH numu (fhc_Nu14) and numubar (fhc_Nu-14) samples combined,
//     each event weighted by InputWeight*fScaleFactor -- NOT numu-only. An
//     earlier pass used numu-only (inherited unexplained from the original
//     Step-5 notebook, which never justified dropping numubar); checking it
//     showed numubar is 21.4% (GENIE) / 21.3% (NuWro) of the total weighted
//     CC-inclusive sample -- too large to drop, and the near-identical
//     GENIE/NuWro numubar fractions (a cross-check the numu-only version can't
//     make) confirms this combined version is on solid footing.
//   - CC-other generator-truth proxy: flagCCINC & !flagCC0pi (same proxy as the
//     original Step 5 -- approximates detector-level categories 4-7, since no
//     ICARUS detector simulation or selection exists in these flat trees).
//   - W: the flat trees' own W_nuc_rest branch (MeV), split at 1400 MeV --
//     matches Howard's true-W cut point and our own true_generator_w binning.
//   - Q2: Q2_true branch (MeV^2, converted to GeV^2), binned in the same 8
//     bins of 0.1 GeV^2 from 0 to 0.8 used by binning_true_generator_w.txt.
//   - Per (W-region, Q2-bin): f = sum(weight, CC-other AND in this Q2 bin) /
//     sum(weight, CC-inclusive in this W region) -- normalizing by the
//     W-region's own CC-inclusive weighted count (not the global one), so
//     each W region is its own population, mirroring Fig. 104's three
//     separately-normalized curves.
//   - R = f_NuWro / f_GENIE; width = |R - 1|.
//
// File coverage: GENIE fhc_Nu14 10/10, GENIE fhc_Nu-14 10/10 (an earlier
// attempt hit unreadable files 1,2,6 before the user's re-download finished --
// now clean), NuWro fhc_Nu14 10/10, NuWro fhc_Nu-14 9/10 (index 5 was never
// produced, not a download gap -- confirmed absent both before and after the
// GENIE re-download).
//
// Result (computed once, not derived on the fly here):
//   low-W  (bins 0-7):  0.427, 0.270, 0.225, 0.186, 0.155, 0.124, 0.089, 0.045
//   high-W (bins 8-15): 0.613, 0.180, 0.025, 0.037, 0.061, 0.073, 0.082, 0.080
// Both regions peak sharply at the lowest Q2 bin and fall toward mid-to-high
// Q2, qualitatively matching the shape of Howard's own Fig. 104 (ratio
// furthest from 1 at low Q2, converging toward 1 at higher Q2, high-W
// diverging more than low-W at low Q2) -- unlike the all-W-collapsed attempt
// at reproducing Fig. 104 in GENIE_NuWro.ipynb, which did not reproduce his
// published shape at all.
//
// Same caveats as the original Step 5: this is a generator-truth-level proxy
// (no detector simulation, approximate category match), not a claim this exact
// vector is final -- but it is the direct, W-aware, numu+numubar-complete
// analog of what Howard's technote text describes for this specific variant.
//
// NBins MUST match ../../binnings/binning_true_generator_w.txt (16: 2 W-regions
// [0,1.4) and [1.4,inf) GeV, each split into 8 true_generator_q2 bins of 0.1
// GeV^2 from 0 to 0.8) -- ParameterSet::readParameterDefinitionFile() sets the
// parameter count from this covariance matrix's dimension, so a mismatch is a
// hard error.
//
// Row order MUST match binning_true_generator_w.txt: bins 0-7 low-W (Q2
// sub-bins 0-7, in order), bins 8-15 high-W (same 8 Q2 sub-bins, in order).
//
// Deliberately uncorrelated (diagonal), same as every one of Howard's three
// schemes and our own true_generator_q2 version.
//
// Run with: root -l -b -q GenerateBackgroundFitWBinByBinCov.C

void GenerateBackgroundFitWBinByBinCov()
{
  const int NBins = 16;

  // GENIE-vs-NuWro |R-1|, numu+numubar combined (InputWeight*fScaleFactor
  // weighted), split by true W (low-W bins 0-7, high-W bins 8-15) -- see
  // derivation above. Replaces both the flat 40%/60% of GenerateBackgroundFitWCov.C
  // and an earlier numu-only version of this same file.
  const double fracUnc[16] = {
    0.4274, 0.2699, 0.2245, 0.1861, 0.1548, 0.1238, 0.0888, 0.0450,
    0.6134, 0.1804, 0.0246, 0.0365, 0.0607, 0.0729, 0.0819, 0.0799
  };

  std::string outputname = "gundaminput_backgroundfit_w_binbybin.root";
  std::unique_ptr<TFile> _file( TFile::Open(outputname.c_str(), "RECREATE") );
  _file->cd();

  std::cout << "@@ Prefit error by covariance matrix" << std::endl;
  TMatrixTSym<double> backgroundfit_w_binbybin_cov(NBins);
  for (int i = 0; i < NBins; i++) {
    std::cout << "true_generator_w/q2 bin " << i << "\t" << fracUnc[i] << std::endl;
    backgroundfit_w_binbybin_cov(i, i) = fracUnc[i] * fracUnc[i];
  }

  backgroundfit_w_binbybin_cov.Write("backgroundfit_w_binbybin_cov");

  //_file->Close();
}
