# Load packages from spack

```
# spack env
. /cvmfs/larsoft.opensciencegrid.org/spack-v0.22.0-fermi/setup-env.sh

# root
# - hljl7gy root@6.28.12%gcc@12.2.0 arch=linux-almalinux9-x86_64_v3
spack load /hljl7gy

# gcc
spack load gcc@12.2.0

# ifdhc
# - b2vqwgc ifdhc@2.8.0%gcc@12.2.0 arch=linux-almalinux9-x86_64_v3
spack load /b2vqwgc

# xrootd
spack load xrootd@5.6.9%gcc@12.2.0
```

# Build GUNDAM

```
# Build and install GUNDAM under "GUNDAM-1.9.X" directory
mkdir GUNDAM-1.9.X
cd GUNDAM-1.9.X

# GUNDAM base directory
export GUNDAM_DIR=$PWD

# Directories
# - REPO_DIR: sources
# - BUILD_DIR: build
# - INSTALL_DIR: package will be installed here
export REPO_DIR=${GUNDAM_DIR}/Repositories/
export BUILD_DIR=${GUNDAM_DIR}/Build/
export INSTALL_DIR=${GUNDAM_DIR}/Install/

mkdir -p ${INSTALL_DIR}
mkdir -p ${BUILD_DIR}
mkdir -p ${REPO_DIR}

mkdir -p ${BUILD_DIR}/json
mkdir -p ${BUILD_DIR}/yaml-cpp
mkdir -p ${BUILD_DIR}/gundam

mkdir -p ${INSTALL_DIR}/json
mkdir -p ${INSTALL_DIR}/yaml-cpp
mkdir -p ${INSTALL_DIR}/gundam

# Checkout source files  
cd ${REPO_DIR}

git clone https://github.com/nlohmann/json.git
git clone https://github.com/jbeder/yaml-cpp.git
git clone https://github.com/gundam-organization/gundam.git

# For gundam, we will use a specific feature branch
cd ${REPO_DIR}/gundam/
# Checking out jskim/ICARUSNuMIXSec/1.9.0_Main
# - Add Jaesung's repo
git remote add jskim git@github.com:jedori0228/gundam.git
# Checking out jskim/ICARUSNuMIXSec/1.9.0_Main
git fetch jskim
git checkout jskim/ICARUSNuMIXSec/1.9.0_Main
# Also checkout submodules
git submodule update --init --remote --recursive
git submodule update --init --recursive

# Now build
# - json
cd $BUILD_DIR/json/
cmake -DCMAKE_INSTALL_PREFIX:PATH=$INSTALL_DIR/json $REPO_DIR/json/.
make -j4 install
# - YAML
cd $BUILD_DIR/yaml-cpp/
cmake -DCMAKE_INSTALL_PREFIX:PATH=$INSTALL_DIR/yaml-cpp -DYAML_BUILD_SHARED_LIBS=on $REPO_DIR/yaml-cpp/.
make -j4 install
# - gundam
cd $BUILD_DIR/gundam/
export CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:${INSTALL_DIR}/yaml-cpp/
export CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:${INSTALL_DIR}/json/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${INSTALL_DIR}/yaml-cpp/lib64/
export LIBRARY_PATH=$LIBRARY_PATH:${INSTALL_DIR}/yaml-cpp/lib64/
cmake -DCMAKE_INSTALL_PREFIX:PATH=$INSTALL_DIR/gundam -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON $REPO_DIR/gundam/.
make -j4 install

# Finalize
export PATH="$INSTALL_DIR/gundam/bin:$PATH"
export LD_LIBRARY_PATH="$INSTALL_DIR/gundam/lib:$LD_LIBRARY_PATH"
```

If the build was succesful, your shell should be able to locate gundamFitter executable, and can run it
```
$ gundamFitter
2025.07.15 22:00:25  INFO GundamGreetings: ────────────────────────────────────────────────────────
2025.07.15 22:00:25  INFO GundamGreetings: Welcome to GUNDAM main fitter v1.9.0f+720-ga4e7b452/HEAD
2025.07.15 22:00:25  INFO GundamGreetings: ────────────────────────────────────────────────────────
2025.07.15 22:00:25  INFO gundamFitter: > gundamFitter is the main interface for the fitter.
2025.07.15 22:00:25  INFO gundamFitter: > 
2025.07.15 22:00:25  INFO gundamFitter: > It takes a set of inputs through config files and command line argument,
2025.07.15 22:00:25  INFO gundamFitter: > and initialize the fitter engine.
2025.07.15 22:00:25  INFO gundamFitter: > Once ready, the fitter minimize the likelihood function and
2025.07.15 22:00:25  INFO gundamFitter: > produce a set of plot saved in the output ROOT file.
...
2025.07.15 22:00:25 ERROR gundamFitter: (int main(int, char**)): No option was provided.
terminate called after throwing an instance of 'std::runtime_error'
  what():  exception thrown by the logger at gundamFitter.cxx:96: clParser.isNoOptionTriggered(): "No option was provided."
Aborted (core dumped)
```
This will fail because we did not give any necessary options, but if you see this messages, the build was successful.
Note that if you open a new shell after this, you need to set environment variables again.
Or you can just run below after changing directory to `GUNDAM-1.9.X`:
```
cd GUNDAM-1.9.X
source setup_GUNDAM.sh
```

# dpT containment-split fit

Simultaneous contained/exiting muon fit for the dpT analysis: 4 fit samples
(`selection_reco_dpT_contained`, `selection_reco_dpT_exiting`,
`sideband_reco_dpT_contained`, `sideband_reco_dpT_exiting`) sharing one
likelihood and one set of 7 truth-level template parameters.

## Binning

- Truth: `configs/binnings/binning_true_dpT.txt` -- 6 finite bins + 1 overflow
  (7 total), medulla-optimized, shared across all 4 samples.
- Reco: per-channel, since contained and exiting muons resolve differently
  - `configs/binnings/binning_reco_dpT_contained.txt` -- 20 finite + 1 overflow (21 rows)
  - `configs/binnings/binning_reco_dpT_exiting.txt` -- 10 finite + 1 overflow (11 rows)
  - `configs/binnings/binning_reco_dpT.txt` -- combined-sample binning (12 finite + 1 overflow), kept for A/B comparison against the pre-containment-split fit

**`cov_bin_range` gotcha (Notebooks/dpT/Asimov_Containment_Studies.ipynb):** the
toyGen `covarianceMatrix_TH2D` keeps the overflow row per sample (so each
sample's true block is 21 or 11 wide), but the `toyGen/plots/histograms/.../MC_TH1D`
category histograms silently drop it (20 or 10 bins). Block boundaries in the
full matrix are therefore at `0, 21, 32, 53, 64` (with-overflow widths), but
each `cov_bin_range` slice must stop one row short of its block boundary to
match the category histograms:

| sample | `cov_bin_range` |
|---|---|
| `selection_reco_dpT_contained` | `(0, 20)` |
| `selection_reco_dpT_exiting` | `(21, 31)` |
| `sideband_reco_dpT_contained` | `(32, 52)` |
| `sideband_reco_dpT_exiting` | `(53, 63)` |

## Fit sample set

`configs/Configs_FitSampleSet/fitSamples_reco_dpT_containment.yaml` -- 4
samples split on `reco_leading_muon_containment`, each pointed at its
per-channel binning file above.

## Asimov closure

```
gundamFitter -c RunConfigs/dpT/Asimov_Containment/config_Fitter_FakeData_dpT.yaml -o asimov_dpT_containment.root -a

gundamToyGenerator -c RunConfigs/dpT/Asimov_Containment/config_ToyGenerator_FakeData_dpT.yaml \
  -f asimov_dpT_containment.root -o prefit_asimov_dpT_containment.root \
  -s 1 -t 8 --use-prefit --use-data-entry Asimov -n 1000

gundamToyGenerator -c RunConfigs/dpT/Asimov_Containment/config_ToyGenerator_FakeData_dpT.yaml \
  -f asimov_dpT_containment.root -o postfit_asimov_dpT_containment.root \
  -s 1 -t 8 --use-bf --use-data-entry Asimov -n 1000
```

Results viewed in `Notebooks/dpT/Asimov_Containment_Studies.ipynb`.

## Fake data studies: low-Q2, containment-split

Motivation: the combined-sample low-Q2 fake data study does not close
(chi2/ndf = 21.2/6, p = 0.002) -- `NormCCRES` absorbs the flat-normalization
piece of the signal, but there is no dedicated nuisance parameter for a
Q2-shaped *background*-only normalization shift, so the residual leaks into
the signal templates. The containment split gives the fit an extra handle:
contained and exiting muons have different momentum resolution, so a genuine
Q2-shaped distortion should imprint differently on the two channels' reco
spectra than a flat-normalization shift would. If chi2/ndf improves relative
to the combined-sample baseline, that supports the degeneracy explanation;
if it doesn't, that points to a real missing nuisance parameter rather than
a statistics/binning limitation.

The fake-data weighting (`configs/Configs_DataSetList/dataSetListConfig_FakeData_Q2.yaml`)
is unchanged -- it's keyed by dataset/tree name, not by fit sample, so it
applies identically under the containment split. Only the fitter/toy-generator
configs needed a `fitSampleSetConfig` swap to point at the containment sample
list; `config_CalcXSec_FakeData_Q2_dpT.yaml` is reused as-is since it runs on
the (unsplit) truth-level sample.

```
gundamFitter -c RunConfigs/dpT/FakeData_Q2_Containment/config_Fitter_FakeData_Q2_dpT.yaml -o fakeData_Q2_containment_dpT.root
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/fakeData_Q2_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_Q2_Containment"
```

```
gundamToyGenerator -c RunConfigs/dpT/FakeData_Q2_Containment/config_ToyGenerator_FakeData_Q2_dpT.yaml \
-f fakeData_Q2_containment_dpT.root \
-o prefit_fakeData_Q2_containment_dpT.root \
-s 1  -t 8 \
--use-prefit \
-n 1000
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_fakeData_Q2_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_Q2_Containment"
```

```
gundamToyGenerator -c RunConfigs/dpT/FakeData_Q2_Containment/config_ToyGenerator_FakeData_Q2_dpT.yaml \
-f fakeData_Q2_containment_dpT.root \
-o postfit_fakeData_Q2_containment_dpT.root \
-s 1  -t 8 \
--use-bf \
-n 1000
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_fakeData_Q2_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/FakeData_Q2_Containment"
```

```
gundamCalcXsec -c RunConfigs/dpT/FakeData_Q2/config_CalcXSec_FakeData_Q2_dpT.yaml \
-f fakeData_Q2_containment_dpT.root -n 10000 -o fakeData_Q2_containment_XSec_dpT.root --use-bf-as-xsec
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/fakeData_Q2_containment_XSec_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/dpT/FakeData_Q2_Containment"
```

Outputs land in `data/Fitter/dpT/FakeData_Q2_Containment/` and
`data/XSection/dpT/FakeData_Q2_Containment/`. Compare the resulting
chi2/ndf directly against the combined-sample baseline (21.2/6) using the
same `cov_bin_range` convention documented above -- note the block
boundaries there were derived for the Asimov containment run and should be
re-verified against this run's actual covariance matrix labels before
trusting the per-sample breakdown, since the fake-data weighting could in
principle change bin population enough to shift PCA-driven parameter
reduction (`enablePca: true`).

## Real data, containment split

`configs/RunConfigs/dpT/RealData_Containment/` -- same containment-split fitSampleSet, but on genuine data (10% unblinded Run 2, 2.36124e19 POT) instead of Asimov/fake data.

Two things carried over unchanged from the combined-sample real-data setup, not introduced by the containment split:

- `BarlowLLH` likelihood (not `PoissonLLH`) -- accounts for finite MC statistics, appropriate for genuine data.
- `dataSetListConfig_RealData.yaml` does not define `ICARUS_NuMI_1muNp0pi_cosmics`/`_cosmics_sideband` (commented out), while the fitSampleSet's selection/sideband samples reference them. This gap already exists identically in the combined-sample config (`fitSamples_reco_dpT.yaml`), so it isn't something the containment split changes -- worth resolving at some point, out of scope here.

```
gundamFitter -c RunConfigs/dpT/RealData_Containment/config_Fitter_RealData_dpT.yaml -o real_containment_dpT.root
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/RealData_Containment"
```

```
gundamToyGenerator -c RunConfigs/dpT/RealData_Containment/config_ToyGenerator_RealData_dpT.yaml \
-f real_containment_dpT.root \
-o prefit_real_containment_dpT.root \
-s 1  -t 8 \
--use-prefit \
-n 1000
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/prefit_real_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/RealData_Containment"
```

```
gundamToyGenerator -c RunConfigs/dpT/RealData_Containment/config_ToyGenerator_RealData_dpT.yaml \
-f real_containment_dpT.root \
-o postfit_real_containment_dpT.root \
-s 1  -t 8 \
--use-bf \
-n 1000
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/postfit_real_containment_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/Fitter/dpT/RealData_Containment"
```

```
gundamCalcXsec -c RunConfigs/dpT/RealData/config_CalcXSec_RealData_dpT.yaml \
-f real_containment_dpT.root -n 10000 -o real_containment_XSec_dpT.root --use-bf-as-xsec
```
```
scp rvizarr@icarusgpvm04.fnal.gov:"/exp/icarus/app/users/rvizarr/gundam-icarus/configs/real_containment_XSec_dpT.root" "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/data/XSection/dpT/RealData_Containment"
```

Results viewed in `Notebooks/dpT/RealData_Containment_Studies.ipynb`. Same `cov_bin_range` values and re-verification caveat as the low-Q2 containment study above.
