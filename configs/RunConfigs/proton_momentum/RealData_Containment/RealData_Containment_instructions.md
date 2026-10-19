Real-data extraction for the proton-momentum contained/exiting simultaneous fit (4 samples:
contained/exiting selection + contained/exiting sideband). 10% unblinded Run 2 data
(2.36124e19 POT). Same chain as `RunConfigs/dpT/RealData_Containment`. Run everything
from the `configs` directory.

### LOCAL FOLDERS (run once on your Mac before the scp commands)
```bash
mkdir -p "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/RealData_Containment" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/proton_momentum/RealData_Containment"
```

### FITTER
```bash
gundamFitter -c RunConfigs/proton_momentum/RealData_Containment/config_Fitter_RealData_proton_momentum.yaml -o real_containment_proton_momentum.root
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_proton_momentum.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/RealData_Containment"
```

### CROSS-SECTION
```bash
gundamCalcXsec -c RunConfigs/proton_momentum/RealData_Containment/config_CalcXSec_RealData_proton_momentum.yaml -f real_containment_proton_momentum.root -n 10000 -o real_containment_XSec_proton_momentum.root --use-bf-as-xsec
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_XSec_proton_momentum.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/proton_momentum/RealData_Containment"
```

### TOY GENERATOR PREFIT
```bash
gundamToyGenerator -c RunConfigs/proton_momentum/RealData_Containment/config_ToyGenerator_RealData_proton_momentum.yaml \
-f real_containment_proton_momentum.root \
-o prefit_real_containment_proton_momentum.root \
-s 1  -t 8 \
--use-prefit \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_real_containment_proton_momentum.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/RealData_Containment"
```

### TOY GENERATOR POSTFIT
```bash
gundamToyGenerator -c RunConfigs/proton_momentum/RealData_Containment/config_ToyGenerator_RealData_proton_momentum.yaml \
-f real_containment_proton_momentum.root \
-o postfit_real_containment_proton_momentum.root \
-s 1  -t 8 \
--use-bf \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_real_containment_proton_momentum.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/RealData_Containment"
```
