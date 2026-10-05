Asimov closure for the proton-momentum contained/exiting simultaneous fit (4 samples:
contained/exiting selection + contained/exiting sideband). Same chain as
`RunConfigs/dpT/Asimov_Containment`. Run everything from the `configs` directory.

### LOCAL FOLDERS (run once on your Mac before the scp commands)
```bash
mkdir -p "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/Asimov_Containment" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/proton_momentum/Asimov_Containment"
```

### FITTER
```bash
gundamFitter -c RunConfigs/proton_momentum/Asimov_Containment/config_Fitter_FakeData_proton_momentum.yaml -o asimov_proton_momentum_containment.root -a
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/asimov_proton_momentum_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/Asimov_Containment"
```
### CROSS-SECTION
```bash
gundamCalcXsec -c RunConfigs/proton_momentum/Asimov_Containment/config_CalcXSec_FakeData_proton_momentum.yaml -f asimov_proton_momentum_containment.root -n 10000 -o asimov_XSec_proton_momentum_containment.root --use-bf-as-xsec
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/asimov_XSec_proton_momentum_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/proton_momentum/Asimov_Containment"
```
### TOY GENERATOR ASIMOV PREFIT
```bash
gundamToyGenerator -c RunConfigs/proton_momentum/Asimov_Containment/config_ToyGenerator_FakeData_proton_momentum.yaml \
-f asimov_proton_momentum_containment.root \
-o prefit_asimov_proton_momentum_containment.root \
-s 1  -t 8 \
--use-prefit \
--use-data-entry Asimov \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_asimov_proton_momentum_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/Asimov_Containment"
```
### TOY GENERATOR ASIMOV POSTFIT
```bash
gundamToyGenerator -c RunConfigs/proton_momentum/Asimov_Containment/config_ToyGenerator_FakeData_proton_momentum.yaml \
-f asimov_proton_momentum_containment.root \
-o postfit_asimov_proton_momentum_containment.root \
-s 1  -t 8 \
--use-bf \
--use-data-entry Asimov \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_asimov_proton_momentum_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/proton_momentum/Asimov_Containment"
```
