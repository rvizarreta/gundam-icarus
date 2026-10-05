Asimov closure for the muon-angle contained/exiting simultaneous fit (4 samples:
contained/exiting selection + contained/exiting sideband). Same chain as
`RunConfigs/dpT/Asimov_Containment`. Run everything from the `configs` directory.

### FITTER
```bash
gundamFitter -c RunConfigs/muon_angle/Asimov_Containment/config_Fitter_FakeData_muon_angle.yaml -o asimov_muon_angle_containment.root -a
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/asimov_muon_angle_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/muon_angle/Asimov_Containment"
```
### CROSS-SECTION
```bash
gundamCalcXsec -c RunConfigs/muon_angle/Asimov_Containment/config_CalcXSec_FakeData_muon_angle.yaml -f asimov_muon_angle_containment.root -n 10000 -o asimov_XSec_muon_angle_containment.root --use-bf-as-xsec
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/asimov_XSec_muon_angle_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/muon_angle/Asimov_Containment"
```
### TOY GENERATOR ASIMOV PREFIT
```bash
gundamToyGenerator -c RunConfigs/muon_angle/Asimov_Containment/config_ToyGenerator_FakeData_muon_angle.yaml \
-f asimov_muon_angle_containment.root \
-o prefit_asimov_muon_angle_containment.root \
-s 1  -t 8 \
--use-prefit \
--use-data-entry Asimov \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_asimov_muon_angle_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/muon_angle/Asimov_Containment"
```
### TOY GENERATOR ASIMOV POSTFIT
```bash
gundamToyGenerator -c RunConfigs/muon_angle/Asimov_Containment/config_ToyGenerator_FakeData_muon_angle.yaml \
-f asimov_muon_angle_containment.root \
-o postfit_asimov_muon_angle_containment.root \
-s 1  -t 8 \
--use-bf \
--use-data-entry Asimov \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_asimov_muon_angle_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/muon_angle/Asimov_Containment"
```
