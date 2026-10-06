# Run from the configs directory. 'All syst' already exists (asimov_dpT_containment.root / asimov_XSec_dpT_containment.root).

### noSyst
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noSyst_dpT.yaml -o asimov_dpT_containment_noSyst.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noSyst_dpT.yaml -f asimov_dpT_containment_noSyst.root -n 10000 -o asimov_XSec_dpT_containment_noSyst.root --use-bf-as-xsec

### noXsec
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noXsec_dpT.yaml -o asimov_dpT_containment_noXsec.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noXsec_dpT.yaml -f asimov_dpT_containment_noXsec.root -n 10000 -o asimov_XSec_dpT_containment_noXsec.root --use-bf-as-xsec

### noFlux
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noFlux_dpT.yaml -o asimov_dpT_containment_noFlux.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noFlux_dpT.yaml -f asimov_dpT_containment_noFlux.root -n 10000 -o asimov_XSec_dpT_containment_noFlux.root --use-bf-as-xsec

### noDet
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noDet_dpT.yaml -o asimov_dpT_containment_noDet.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noDet_dpT.yaml -f asimov_dpT_containment_noDet.root -n 10000 -o asimov_XSec_dpT_containment_noDet.root --use-bf-as-xsec

### noG4
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noG4_dpT.yaml -o asimov_dpT_containment_noG4.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noG4_dpT.yaml -f asimov_dpT_containment_noG4.root -n 10000 -o asimov_XSec_dpT_containment_noG4.root --use-bf-as-xsec

### noBkg
gundamFitter -c RunConfigs/dpT/Asimov_Containment_NminusX/config_Fitter_noBkg_dpT.yaml -o asimov_dpT_containment_noBkg.root -a
gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment_NminusX/config_CalcXSec_noBkg_dpT.yaml -f asimov_dpT_containment_noBkg.root -n 10000 -o asimov_XSec_dpT_containment_noBkg.root --use-bf-as-xsec
