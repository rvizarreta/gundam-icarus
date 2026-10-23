# N-X study (PoissonLLH, gundamCalcXsec --TurnRecoOnlyOff), G4 sets binned in particle momentum/KE
# Run from the configs directory on the GPVM, inside tmux, with the GUNDAM environment set up.
# Outputs: asimov_dpT_containment_<tag>_poisson.root (fit) and
#          asimov_XSec_dpT_containment_<tag>_recoOff_poisson.root (xsec, 10000 toys).
# 'All syst' = main fit asimov_dpT_containment.root -> asimov_XSec_dpT_containment_recoOff_poisson.root.
# noG4 and noSyst contain no G4 sets, so their existing outputs
# (asimov_XSec_dpT_containment_noG4_recoOff_poisson.root, asimov_XSec_dpT_containment_noSyst_poisson.root)
# do not change with the G4 binning and are not rerun here.

```bash
( set -e
  cd /exp/icarus/app/users/rvizarr/gundam-icarus/configs
  R=RunConfigs/dpT/Asimov_Containment_NminusX
  mkdir -p nminusx_logs
  [ -s asimov_dpT_containment.root ] || { echo "FAIL: main fit asimov_dpT_containment.root not found in $(pwd)"; exit 1; }
  echo "== all syst: xsec ($(date +%H:%M))"
  gundamCalcXsec -c RunConfigs/dpT/Asimov/config_CalcXSec_FakeData_dpT.yaml -f asimov_dpT_containment.root -n 10000 \
    -o asimov_XSec_dpT_containment_recoOff_poisson.root --use-bf-as-xsec --TurnRecoOnlyOff > nminusx_logs/allSyst_xsec.log 2>&1
  for t in noDet noFlux noXsecSignal noXsecBkgd; do
    echo "== $t: fit ($(date +%H:%M))"
    gundamFitter -c $R/config_Fitter_${t}_dpT.yaml -o asimov_dpT_containment_${t}_poisson.root -a > nminusx_logs/${t}_fit.log 2>&1
    echo "== $t: xsec ($(date +%H:%M))"
    gundamCalcXsec -c $R/config_CalcXSec_${t}_dpT.yaml -f asimov_dpT_containment_${t}_poisson.root -n 10000 \
      -o asimov_XSec_dpT_containment_${t}_recoOff_poisson.root --use-bf-as-xsec --TurnRecoOnlyOff > nminusx_logs/${t}_xsec.log 2>&1
  done
  echo "== done ($(date +%H:%M))"
  ls -la --time-style=long-iso asimov_XSec_dpT_containment_{,noDet_,noFlux_,noXsecSignal_,noXsecBkgd_}recoOff_poisson.root
)
```

# ---------------------------------------------------------------------------
# Previous instructions (BarlowLLH era, kept for reference):
# Run from the configs directory. All outputs carry a _barlow suffix (BarlowLLH, flux/det/GENIE on selection+sideband+signal).
# 'All syst' baseline = asimov_dpT_containment_barlow.root / asimov_XSec_dpT_containment_barlow.root (GPVM names).

### noSyst
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noSyst_dpT.yaml -o asimov_dpT_containment_noSyst_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noSyst_dpT.yaml -f asimov_dpT_containment_noSyst_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noSyst_barlow.root --use-bf-as-xsec

### noXsec
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noXsec_dpT.yaml -o asimov_dpT_containment_noXsec_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noXsec_dpT.yaml -f asimov_dpT_containment_noXsec_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noXsec_barlow.root --use-bf-as-xsec

### noFlux
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noFlux_dpT.yaml -o asimov_dpT_containment_noFlux_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noFlux_dpT.yaml -f asimov_dpT_containment_noFlux_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noFlux_barlow.root --use-bf-as-xsec

### noDet
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noDet_dpT.yaml -o asimov_dpT_containment_noDet_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noDet_dpT.yaml -f asimov_dpT_containment_noDet_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noDet_barlow.root --use-bf-as-xsec

### noG4
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noG4_dpT.yaml -o asimov_dpT_containment_noG4_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noG4_dpT.yaml -f asimov_dpT_containment_noG4_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noG4_barlow.root --use-bf-as-xsec

### noBkg
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noBkg_dpT.yaml -o asimov_dpT_containment_noBkg_barlow.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noBkg_dpT.yaml -f asimov_dpT_containment_noBkg_barlow.root -n 10000 -o asimov_XSec_dpT_containment_noBkg_barlow.root --use-bf-as-xsec
