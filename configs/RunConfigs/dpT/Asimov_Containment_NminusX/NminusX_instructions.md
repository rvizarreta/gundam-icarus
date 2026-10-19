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
