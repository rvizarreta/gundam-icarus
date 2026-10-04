Real-data extraction for the dalphaT contained/exiting simultaneous fit (4 samples:
contained/exiting selection + contained/exiting sideband). 10% unblinded Run 2 data
(2.36124e19 POT). Same chain as `RunConfigs/dpT/RealData_Containment`. Run everything
from the `configs` directory.

### FITTER
```bash
gundamFitter -c RunConfigs/dalphaT/RealData_Containment/config_Fitter_RealData_dalphaT.yaml -o real_containment_dalphaT.root
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_dalphaT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dalphaT/RealData_Containment"
```

### CROSS-SECTION
```bash
gundamCalcXsec -c RunConfigs/dalphaT/RealData_Containment/config_CalcXSec_RealData_dalphaT.yaml -f real_containment_dalphaT.root -n 10000 -o real_containment_XSec_dalphaT.root --use-bf-as-xsec
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_XSec_dalphaT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/dalphaT/RealData_Containment"
```

### TOY GENERATOR PREFIT
```bash
gundamToyGenerator -c RunConfigs/dalphaT/RealData_Containment/config_ToyGenerator_RealData_dalphaT.yaml \
-f real_containment_dalphaT.root \
-o prefit_real_containment_dalphaT.root \
-s 1  -t 8 \
--use-prefit \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_real_containment_dalphaT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dalphaT/RealData_Containment"
```

### TOY GENERATOR POSTFIT
```bash
gundamToyGenerator -c RunConfigs/dalphaT/RealData_Containment/config_ToyGenerator_RealData_dalphaT.yaml \
-f real_containment_dalphaT.root \
-o postfit_real_containment_dalphaT.root \
-s 1  -t 8 \
--use-bf \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_real_containment_dalphaT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dalphaT/RealData_Containment"
```
