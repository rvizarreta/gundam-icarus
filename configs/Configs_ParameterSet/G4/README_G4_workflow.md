# GEANT4 reinteraction systematics workflow

Three ParameterSets, one per particle (proton, pi+, pi-), shared by the contained
and exiting muon samples and by the sideband:

| Set | Binning variable | Bins |
|---|---|---|
| G4 Proton Fate | `true_leading_proton_momentum` (GeV/c) | [0,0.4) [0.4,0.6) [0.6,0.8) [0.8,1.0) [1.0,inf) |
| G4 Piplus Fate | `true_leading_pion_ke` (MeV), leading pion is a pi+ | [0,200) [200,700) [700,inf) |
| G4 Piminus Fate | `true_leading_pion_ke` (MeV), leading pion is a pi- | [0,200) [200,700) [700,inf) |

The covariance of each set is fractional and CV-centered, built on the G4Reweight
sample (`events/full/selected` + `events/full/sideband`, no cosmics) with 1000
universes. Kinematic bins are used instead of particle multiplicity because the
multiplicity branches (`true_n*_G4`) count all primaries without a threshold and
their distributions differ strongly between the G4 sample and the nominal MC,
while the leading-particle kinematics agree. The previous reco-dpT-binned sets
(contained/exiting, six files) are kept in `old_dpT_binned_20261023/`.

## Prerequisites
Be on an ICARUS GPVM (e.g., `icarusgpvm04`), then start from a fresh tmux session:
```bash
tmux new -s g4
```
For AL9 only (Steps 1-2), you just need to run:
```bash
cd /exp/icarus/app/users/rvizarr/ICARUS-NuMI-CC0pi-Selection
source medulla_env/bin/activate
```

## Step 1 - Create & Launch the project
Note: this deletes the previous project directory on scratch.
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
Always check the merged file's POT before copying it locally - a wrong file path, incomplete merge, or stale local file can silently give you the wrong POT. Expected output: `Total sum= 2.15909e+20`
```bash
root -l -b -q '/exp/icarus/data/users/rvizarr/medulla/1muNp0pi_Nge1_uncontained_G4.root' -e '_file0->cd("events/nominal"); POT->Print();'
```

## Step 2 - Run Systematics
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
Add the PPFX reweight and flux systematics (output: `icarus_numi_numu_mc_onbeam_offbeam_syst_ppfx_G4.root`), then back to GPVM:
```bash
scp -o ServerAliveInterval=30 -o ServerAliveCountMax=10 "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_Selection/data/icarus_numi_numu_mc_onbeam_offbeam_syst_ppfx_G4.root" rvizarr@icarusgpvm04.fnal.gov:/exp/icarus/data/users/rvizarr/medulla/
```

## Step 3 - Generate Covariance Matrices
Run this step inside the SL7 container with `sbnana` set up (the same shell used
to build medulla), NOT in native AL9. The script writes the `TMatrixDSym` output
through PyROOT, and only the SL7 UPS Python has it. `~/g4venv` is an AL9 venv
without PyROOT: there the script silently falls back to `.npz` files that GUNDAM
cannot read.

One-time setup of the SL7 environment (inside the SL7 container, after
`setup sbnana v10_01_02_01 -q e26:prof`):
```bash
python3 -m venv --system-site-packages ~/g4venv_sl7
source ~/g4venv_sl7/bin/activate
python3 -m pip install --upgrade pip
pip install --only-binary=:all: pandas matplotlib
```
Run the three covariances (one block, runs in the foreground, stops at the first problem):
```bash
( set -e
  cd /exp/icarus/app/users/rvizarr/gundam-icarus/configs/Configs_ParameterSet/G4
  source ~/g4venv_sl7/bin/activate
  python3 -c "import ROOT, uproot, numpy, pandas, matplotlib; print('env OK, ROOT', ROOT.gROOT.GetVersion())"
  mkdir -p outputs; touch outputs/.run_marker
  for p in Proton Piplus Piminus; do
    echo "===== G4${p} ====="
    python3 calc_geant4_covariance.py config_G4${p}.json > outputs_log_G4${p}.txt 2>&1
    if grep -q "PyROOT is not importable" outputs_log_G4${p}.txt; then echo "FAIL: no PyROOT for ${p}"; exit 1; fi
    f=outputs/output_CovMat_G4${p}.root
    [ -s $f ] && [ $f -nt outputs/.run_marker ] || { echo "FAIL: $f missing or not fresh"; exit 1; }
    grep -E -A2 "Fractional uncertainty per bin, CV-centered|Universe-mean / CV ratio" outputs_log_G4${p}.txt
  done
  ls -la --time-style=long-iso outputs/output_CovMat_G4{Proton,Piplus,Piminus}.root
)
```
Reference values (test run on the 2026-10-23 G4 file): fractional uncertainty per bin
Proton 0.15, 2.1, 3.1, 3.5, 3.5%; Piplus 1.1, 7.8, 16.8%; Piminus 1.5, 8.2, 16.6%.
The "Universe-mean / CV ratio" should be within ~1% of 1 in every bin; that is the
check that the multisim reweighting is unbiased.

Download the three matrices (from your Mac; explicit names, no globs):
```bash
DEST="/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/gundam-icarus/configs/Configs_ParameterSet/G4/outputs/"
SRC=/exp/icarus/app/users/rvizarr/gundam-icarus/configs/Configs_ParameterSet/G4/outputs
for p in Proton Piplus Piminus; do
  scp "rvizarr@icarusgpvm04.fnal.gov:${SRC}/output_CovMat_G4${p}.root" "$DEST"
done
```

## Step 4 - ParameterSets in GUNDAM
Already registered. `parameterSetList_true_dpT.yaml` and its N-X variants
(`_NX_noBkg`, `_noDet`, `_noFlux`, `_noG4`, `_noSyst`, `_noXsec`) contain:
```yaml
# GEANT4 hadron reinteraction ("fate") systematics
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Proton.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piplus.yaml"
- "${GUNDAM_CONFIG_DIR}/Configs_ParameterSet/G4/parameterSet_G4Piminus.yaml"
```
The previous versions of these lists are in `Configs_ParameterSetList/old_G4_dpT_binned_20261023/`.

## Step 5 - Run GUNDAM
Same `gundamFitter` command as before. In the log, check that each of the three G4
sets loads its covariance (`covarianceMatrixFilePath` / `covarianceMatrixTMatrixD`)
with the right size (Proton 5x5, Piplus 3x3, Piminus 3x3) and that the
eigen-decomposition (`allowPca`) completes. The four proton bins above 0.4 GeV/c
are almost fully correlated (~1.0), so watch for warnings about a near-singular matrix.
