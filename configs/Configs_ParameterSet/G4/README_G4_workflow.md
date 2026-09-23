## Prerequisites
Be on an ICARUS GPVM (e.g., `icarusgpvm04`), then start from a fresh tmux session:
For AL9 only, you just need to run:
```bash
cd /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection
source medulla_env/bin/activate
```
## Step 1 — Create & Launch the project
```bash
rm -rf /pnfs/icarus/scratch/users/rvizarr/1muNp0pi_uncontained_G4_project
```
```bash
python3 /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection/batch/medulla.py \
  -t /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection/selection/toml/1muNp0pi_Nge1_uncontained_G4.toml \
  -p /pnfs/icarus/scratch/users/rvizarr/1muNp0pi_uncontained_G4_project \
  -b 500 \
  --create-project
```
```bash
python3 /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection/batch/medulla.py \
  -p /pnfs/icarus/scratch/users/rvizarr/1muNp0pi_uncontained_G4_project \
  -e icarus \
  --launch-jobs
```
Now merge files.
```bash
hadd -f /exp/icarus/data/users/rvizarr/medulla/1muNp0pi_Nge1_uncontained_G4.root /pnfs/icarus/scratch/users/rvizarr/1muNp0pi_uncontained_G4_project/output/output_jobid*.root
```
Always check the merged file's POT before copying it locally — a wrong file path, incomplete merge, or stale local file can silently give you the wrong POT. Expected output: `Total sum= 2.15909e+20`
```bash
root -l -b -q '/exp/icarus/data/users/rvizarr/medulla/1muNp0pi_Nge1_uncontained.root' -e '_file0->cd("events/nominal"); POT->Print();'
```
## Step 2 — Run Systematics
First generate txt file if not generated yet.
```bash
for f in /pnfs/icarus/persistent/users/rvizarr/spine/G4Reweight_NuMI_CV_combined/*.flat.root; do
    echo "xroot://fndcadoor.fnal.gov:1094/pnfs/fnal.gov/usr/icarus/persistent/users/rvizarr/spine/G4Reweight_NuMI_CV_combined/$(basename $f)"
done > /exp/icarus/data/users/rvizarr/medulla/NuMI_nuCos_CV_weights.txt
```
Run medulla systematics
```bash
cd /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection/systematics/toml
./../../build/systematics/run_systematics NuMI_nu_mu_G4.toml
```
And download it:
```bash
scp rvizarr@icarusgpvm04.fnal.gov:/exp/icarus/data/users/rvizarr/medulla/1muNp0pi_Nge1_uncontained_systematics_G4.root "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_Selection/data"
```
Add the PPFX reweight and flux systematics, then back to GPVM:
```bash
scp -o ServerAliveInterval=30 -o ServerAliveCountMax=10 "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_Selection/data/icarus_numi_numu_mc_onbeam_offbeam_syst_ppfx_G4.root" rvizarr@icarusgpvm04.fnal.gov:/exp/icarus/data/users/rvizarr/medulla/
```
## Step 3 — Generate Covariance Matrix
Turn on python env
```bash
cd /exp/icarus/app/users/rvizarr/gundam-icarus/configs/Configs_ParameterSet/G4
source ~/g4venv/bin/activate
```
Run scripts (one per particle x containment split; separate covariance matrices for
contained vs. exiting muon samples, binned in reco_dpT_lp)
```bash
python3 calc_geant4_covariance.py config_G4Proton_contained.json
python3 calc_geant4_covariance.py config_G4Proton_exiting.json
python3 calc_geant4_covariance.py config_G4Piplus_contained.json
python3 calc_geant4_covariance.py config_G4Piplus_exiting.json
python3 calc_geant4_covariance.py config_G4Piminus_contained.json
python3 calc_geant4_covariance.py config_G4Piminus_exiting.json
```
For each dial, check the printed "Universe-mean / CV ratio per bin (should be close
to 1)" line is close to 1 -- that's the sanity check that the multisim reweighting is
unbiased. Then confirm all 6 outputs were written:
```bash
ls -la outputs/
```
Expect 6 files: `output_CovMat_G4{Proton,Piplus,Piminus}_{contained,exiting}.root`.

## Step 4 — Register the ParameterSets in GUNDAM
Add these 6 lines to your active `Configs_ParameterSetList` yaml (e.g.
`Configs_ParameterSetList/parameterSetList_true_dpT.yaml`), alongside the existing
GENIE/Flux/DetSys entries:
```yaml
# GEANT4 hadron reinteraction ("fate") systematics
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Proton_contained.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Proton_exiting.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piplus_contained.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piplus_exiting.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piminus_contained.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piminus_exiting.yaml"
```

## Step 5 — Run GUNDAM
TODO: fill in the actual `gundam-fitter` invocation used for this fit. Check the log
for each of the 6 G4 ParameterSet blocks loading its covariance matrix
(`covarianceMatrixFilePath`/`covarianceMatrixTMatrixD`) without error, and completing
eigen-decomposition (`allowPca`/`useEigenDecompInFit`) without crashing.
