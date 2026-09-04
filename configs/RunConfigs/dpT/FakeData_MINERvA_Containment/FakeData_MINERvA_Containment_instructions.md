### PREREQUISITE
This study requires `MINERvAZExpFitCorrection_weight` to exist as a branch in
the GUNDAM input file (`icarus_numi_numu_mc_onbeam_offbeam_syst_gundam.root`).
As of writing, it does not -- it requires pulling Kiyoung's updated
`to_gundam.cc` (medulla fork,
https://github.com/kyjung123/medulla/blob/f62fefff00b3c2e80fc9a623afa9f7f63a6d8305/systematics/src/to_gundam.cc#L218-L227
and #L331-L337) into the systematics-tree generation step and regenerating
the file. Do not run the steps below until that's done.

This study is built containment-split (contained/exiting simultaneous fit)
only -- no combined-sample variant.

### FITTER
```bash
gundamFitter -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_Fitter_FakeData_MINERvA_dpT.yaml -o fakeData_MINERvA_dpT_containment.root
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/fakeData_MINERvA_dpT_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_MINERvA_Containment"
```
### CROSS-SECTION
```bash
gundamCalcXsec -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_CalcXSec_FakeData_MINERvA_dpT.yaml -f fakeData_MINERvA_dpT_containment.root -n 10000 -o fakeData_MINERvA_XSec_dpT_containment.root --use-bf-as-xsec
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/fakeData_MINERvA_XSec_dpT_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/dpT/FakeData_MINERvA_Containment"
```
### TOY GENERATOR ASIMOV PREFIT
```bash
gundamToyGenerator -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_ToyGenerator_FakeData_MINERvA_dpT.yaml \
-f fakeData_MINERvA_dpT_containment.root \
-o prefit_fakeData_MINERvA_dpT_containment.root \
-s 1  -t 8 \
--use-prefit \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_fakeData_MINERvA_dpT_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_MINERvA_Containment"
```
### TOY GENERATOR ASIMOV POSTFIT
```bash
gundamToyGenerator -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_ToyGenerator_FakeData_MINERvA_dpT.yaml \
-f fakeData_MINERvA_dpT_containment.root \
-o postfit_fakeData_MINERvA_dpT_containment.root \
-s 1  -t 8 \
--use-bf \
-n 1000
```
```bash
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_fakeData_MINERvA_dpT_containment.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_MINERvA_Containment"
```

### NOTE ON THE FAKE DATA DEFINITION
Fake data = nominal MC reweighted by `MINERvAZExpFitCorrection_weight`, a
single-weight export (not a full multisim spline) of the MINERvA-informed
Z-expansion axial form factor correction dial from Kiyoung's medulla fork
(see `Configs_DataSetList/dataSetListConfig_FakeData_MINERvA.yaml` for the full
derivation notes). Unlike `FakeData_QE_dpTShape`/`FakeData_QE_ProtonP`, this
weight comes directly from a GENIEReWeight computation already baked into
the GUNDAM input tree (once regenerated), not a hand-derived binned table --
no `true_interaction_mode` gate is needed in the formula since the dial
itself returns ~1.0 outside its physical domain.
