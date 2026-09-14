// Generates the diagonal prior covariance for the BackgroundFit true_generator_w
// parameter set's THIRD variant -- Howard et al.'s "bin-by-bin uncertainties from
// Fig. 104," built the way he actually built it: from the GENIE/NuWro ratio,
// split by true W (below/above 1.4 GeV), not just Q2.
//
// This is a corrected re-derivation of a previous version of this same file. The
// previous version used a CC-other proxy (flagCCINC & !flagCC0pi) and a
// per-W-region-normalized fraction ratio, and did not reproduce Howard's Fig.
// 104 shape (it had the low-W and high-W curves backwards relative to his
// published plot). Both the selection and the ratio construction have been
// corrected below; see the two bullets marked CORRECTED.
//
// Derivation (run against our local GENIE/NuWro NUISANCE flat-tree productions,
// data/Generators/{GENIE,NuWro}/{fhc_Nu14,fhc_Nu-14}/output_*.nuisflat.root):
//   - Population: BOTH numu (fhc_Nu14) and numubar (fhc_Nu-14) samples combined,
//     each event weighted by InputWeight*fScaleFactor -- NOT numu-only. numubar
//     is a non-negligible fraction of the combined weighted sample in both
//     generators (checked under an earlier version of the selection below), so
//     it is not dropped.
//   - [CORRECTED] CC-other generator-truth proxy: abs(Mode) > 3 && abs(Mode) < 30
//     (NEUT reaction-code convention, as used by NUISANCE), i.e. the CC
//     resonance-production channel. This is the selection Howard's own Fig. 104
//     is built from, per Stephen Dolan (via J. Park, private communication,
//     Sept. 2026) -- not flagCCINC & !flagCC0pi, which was this file's original,
//     unverified stand-in. Mode must be taken in absolute value: NUISANCE stores
//     it with the NEUT sign convention, which is negative for antineutrino
//     (fhc_Nu-14) events; without abs(), the numubar half of the sample would
//     fail this cut entirely.
//   - W: the flat trees' own W_nuc_rest branch (MeV), split at 1400 MeV --
//     matches Howard's true-W cut point and our own true_generator_w binning.
//     Events are additionally required to have W_nuc_rest > 0 (removes a
//     negligible number of unphysical/unset entries, <0.001% of the CC-RES
//     sample), matching the cut Stephen Dolan's plot applies.
//   - Q2: Q2_true branch (MeV^2, converted to GeV^2), binned in the same 8
//     bins of 0.1 GeV^2 from 0 to 0.8 used by binning_true_generator_w.txt.
//   - [CORRECTED] Per (W-region, Q2-bin): N_GENIE,i and N_NuWro,i are the raw
//     weighted CC-RES counts in that bin (no normalization by the W-region's
//     total population). R_i = N_NuWro,i / N_GENIE,i; width_i = |R_i - 1|.
//     The previous version instead normalized each generator's per-bin count
//     by its own W-region total before taking the ratio (f = N_i/N_region,
//     R = f_NuWro/f_GENIE). That normalization is mathematically equivalent to
//     this raw ratio times an extra constant factor per W-region equal to
//     (N_region,GENIE / N_region,NuWro) -- i.e. it folds the two generators'
//     disagreement on the OVERALL CC-inclusive rate into what is supposed to be
//     a bin-by-bin CC-other shape uncertainty. Since the nuisance parameter
//     this prior constrains scales the CC-other background prediction directly
//     (not a fraction of CC-inclusive), the raw ratio is the correct quantity,
//     and it is also what reproduces Stephen Dolan's numbers directly (checked
//     against his "All W" curve to ~5% bin-by-bin).
//
// File coverage: GENIE fhc_Nu14 10/10, GENIE fhc_Nu-14 10/10, NuWro fhc_Nu14
// 10/10, NuWro fhc_Nu-14 9/10 (index 5 was never produced, not a download gap).
//
// Result (computed once, not derived on the fly here):
//   low-W  (bins 0-7):  0.4395, 0.3279, 0.2804, 0.2268, 0.1726, 0.1310, 0.0858, 0.0533
//   high-W (bins 8-15): 0.0412, 0.2197, 0.3136, 0.3482, 0.3598, 0.3647, 0.3668, 0.3643
// low-W falls off steadily from the lowest Q2 bin; high-W instead starts small
// and rises then plateaus -- the opposite low/high shape from the previous,
// uncorrected version of this file, and now qualitatively consistent with
// Howard's own Fig. 104 (high-W varies more than low-W away from the lowest Q2
// bin) and with Stephen Dolan's plot, which this derivation reproduces directly.
//
// Same caveats as the original Step 5: this is a generator-truth-level proxy
// (no detector simulation, approximate category match), not a claim this exact
// vector is final -- but it is the direct, W-aware, numu+numubar-complete,
// Stephen-Dolan-selection analog of what Howard's technote text describes for
// this specific variant.
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

  // GENIE-vs-NuWro |R-1| (R = N_NuWro/N_GENIE, raw per-bin counts, no
  // per-region normalization), numu+numubar combined (InputWeight*fScaleFactor
  // weighted, abs(Mode) CC-RES selection), split by true W (low-W bins 0-7,
  // high-W bins 8-15) -- see derivation above. Replaces both the flat 40%/60%
  // of GenerateBackgroundFitWCov.C and the earlier, uncorrected version of this
  // same file.
  const double fracUnc[16] = {
    0.4395, 0.3279, 0.2804, 0.2268, 0.1726, 0.1310, 0.0858, 0.0533,
    0.0412, 0.2197, 0.3136, 0.3482, 0.3598, 0.3647, 0.3668, 0.3643
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
