#!/bin/bash
# run_gundam_studies.sh
# Runs every "<observable> | Fake Data | <variant>" study and the five
# "<observable> | Real Data" studies from the gundam-icarus wiki:
#   fit -> cross-section extraction -> prefit toys -> postfit toys
# Commands are copied from the wiki pages (scp download commands omitted), except that
# every dpT CalcXSec config (fake and real data) now points to the _Containment folder
# (configs copied there 2026-10-25).
#
# Usage (on the gpvm, inside tmux):
#   ./run_gundam_studies.sh                    # run everything (fake data, then real data)
#   ./run_gundam_studies.sh --fake             # fake-data studies only
#   ./run_gundam_studies.sh --real             # real-data studies only
#   ./run_gundam_studies.sh dpT_MEC muon_angle_Asimov   # run only these studies
#   ./run_gundam_studies.sh --list             # list study names
#
# Behaviour:
#   - Studies run one after another (each GUNDAM call already uses its own threads).
#   - If a fit fails, the rest of that study is skipped and the script moves on.
#   - If xsec/prefit/postfit fails, the remaining steps of that study still run.
#   - Before each step, the -c config file is checked; a missing file is logged and skipped.
#   - Output .root files land in the configs directory, as on the wiki.
#   - One log per step goes to logs_gundam_<timestamp>/ plus a summary at the end.

BASE=/exp/icarus/app/users/rvizarr/gundam-icarus

# ---- Environment (from "ABC on How to Run GUNDAM") ----
cd "$BASE" || { echo "Cannot cd to $BASE"; exit 1; }
source setup_spack.sh
cd GUNDAM-1.9.X/ || exit 1
source setup_GUNDAM.sh
cd ../configs/ || exit 1

set -o pipefail
LOGDIR="logs_gundam_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOGDIR"
SUMMARY=()

# step LABEL COMMAND...  : run one GUNDAM command, log it, record the result
step() {
  local label="$1"; shift
  local log="$LOGDIR/${label//\//__}.log"
  local prev="" a
  for a in "$@"; do
    if [[ "$prev" == "-c" && ! -f "$a" ]]; then
      echo "[MISSING CONFIG] $label -> $a" | tee "$log"
      SUMMARY+=("MISSING  $label  ($a)")
      return 1
    fi
    prev="$a"
  done
  echo ">>> [$(date +%H:%M:%S)] START $label"
  echo "# $*" > "$log"
  "$@" 2>&1 | tee -a "$log"
  local rc=${PIPESTATUS[0]}
  if [[ $rc -eq 0 ]]; then
    SUMMARY+=("OK       $label")
  else
    SUMMARY+=("FAILED   $label  (exit $rc, see $log)")
  fi
  echo ">>> [$(date +%H:%M:%S)] END   $label (exit $rc)"
  return $rc
}

# --- Wiki page: dpT | Fake Data | Asimov ---
study_dpT_Asimov() {
  step "dpT_Asimov/fit" \
    gundamFitter -c RunConfigs/dpT/Asimov_Containment/config_Fitter_FakeData_dpT.yaml -o asimov_dpT_containment.root -a || return 1
  step "dpT_Asimov/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/Asimov_Containment/config_CalcXSec_FakeData_dpT.yaml -f asimov_dpT_containment.root -n 10000 -o asimov_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_Asimov/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/Asimov_Containment/config_ToyGenerator_FakeData_dpT.yaml \
      -f asimov_dpT_containment.root \
      -o prefit_asimov_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "dpT_Asimov/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/Asimov_Containment/config_ToyGenerator_FakeData_dpT.yaml \
      -f asimov_dpT_containment.root \
      -o postfit_asimov_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | LQCD ---
study_dpT_LQCD() {
  step "dpT_LQCD/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_LQCD_Containment/config_Fitter_FakeData_LQCD_dpT.yaml -o fakeData_LQCD_dpT_containment.root || return 1
  step "dpT_LQCD/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_LQCD_Containment/config_CalcXSec_FakeData_LQCD_dpT.yaml -f fakeData_LQCD_dpT_containment.root -n 10000 -o fakeData_LQCD_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_LQCD/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_LQCD_Containment/config_ToyGenerator_FakeData_LQCD_dpT.yaml \
      -f fakeData_LQCD_dpT_containment.root \
      -o prefit_fakeData_LQCD_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_LQCD/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_LQCD_Containment/config_ToyGenerator_FakeData_LQCD_dpT.yaml \
      -f fakeData_LQCD_dpT_containment.root \
      -o postfit_fakeData_LQCD_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | MEC ---
study_dpT_MEC() {
  step "dpT_MEC/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_InteractionMode_MEC_Containment/config_Fitter_FakeData_InteractionMode_MEC_dpT.yaml -o fakeData_InteractionMode_MEC_dpT_containment.root || return 1
  step "dpT_MEC/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_InteractionMode_MEC_Containment/config_CalcXSec_FakeData_InteractionMode_MEC_dpT.yaml -f fakeData_InteractionMode_MEC_dpT_containment.root -n 10000 -o fakeData_InteractionMode_MEC_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_MEC/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_MEC_Containment/config_ToyGenerator_FakeData_InteractionMode_MEC_dpT.yaml \
      -f fakeData_InteractionMode_MEC_dpT_containment.root \
      -o prefit_fakeData_InteractionMode_MEC_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_MEC/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_MEC_Containment/config_ToyGenerator_FakeData_InteractionMode_MEC_dpT.yaml \
      -f fakeData_InteractionMode_MEC_dpT_containment.root \
      -o postfit_fakeData_InteractionMode_MEC_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | MINERvA ---
study_dpT_MINERvA() {
  step "dpT_MINERvA/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_Fitter_FakeData_MINERvA_dpT.yaml -o fakeData_MINERvA_dpT_containment.root || return 1
  step "dpT_MINERvA/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_CalcXSec_FakeData_MINERvA_dpT.yaml -f fakeData_MINERvA_dpT_containment.root -n 10000 -o fakeData_MINERvA_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_MINERvA/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_ToyGenerator_FakeData_MINERvA_dpT.yaml \
      -f fakeData_MINERvA_dpT_containment.root \
      -o prefit_fakeData_MINERvA_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_MINERvA/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_MINERvA_Containment/config_ToyGenerator_FakeData_MINERvA_dpT.yaml \
      -f fakeData_MINERvA_dpT_containment.root \
      -o postfit_fakeData_MINERvA_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | Pion ---
study_dpT_Pion() {
  step "dpT_Pion/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_Pion_Containment/config_Fitter_FakeData_Pion_dpT.yaml -o fakeData_Pion_dpT_containment.root || return 1
  step "dpT_Pion/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_Pion_Containment/config_CalcXSec_FakeData_Pion_dpT.yaml -f fakeData_Pion_dpT_containment.root -n 10000 -o fakeData_Pion_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_Pion/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_Pion_Containment/config_ToyGenerator_FakeData_Pion_dpT.yaml \
      -f fakeData_Pion_dpT_containment.root \
      -o prefit_fakeData_Pion_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_Pion/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_Pion_Containment/config_ToyGenerator_FakeData_Pion_dpT.yaml \
      -f fakeData_Pion_dpT_containment.root \
      -o postfit_fakeData_Pion_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | Q2 ---
study_dpT_Q2() {
  step "dpT_Q2/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_Q2_Containment/config_Fitter_FakeData_Q2_dpT.yaml -o fakeData_Q2_containment_dpT.root || return 1
  step "dpT_Q2/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_Q2_Containment/config_CalcXSec_FakeData_Q2_dpT.yaml -f fakeData_Q2_containment_dpT.root -n 10000 -o fakeData_Q2_containment_XSec_dpT.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_Q2/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_Q2_Containment/config_ToyGenerator_FakeData_Q2_dpT.yaml \
      -f fakeData_Q2_containment_dpT.root \
      -o prefit_fakeData_Q2_containment_dpT.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_Q2/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_Q2_Containment/config_ToyGenerator_FakeData_Q2_dpT.yaml \
      -f fakeData_Q2_containment_dpT.root \
      -o postfit_fakeData_Q2_containment_dpT.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | QE ---
study_dpT_QE() {
  step "dpT_QE/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_InteractionMode_QE_Containment/config_Fitter_FakeData_InteractionMode_QE_dpT.yaml -o fakeData_InteractionMode_QE_dpT_containment.root || return 1
  step "dpT_QE/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_InteractionMode_QE_Containment/config_CalcXSec_FakeData_InteractionMode_QE_dpT.yaml -f fakeData_InteractionMode_QE_dpT_containment.root -n 10000 -o fakeData_InteractionMode_QE_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_QE/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_QE_Containment/config_ToyGenerator_FakeData_InteractionMode_QE_dpT.yaml \
      -f fakeData_InteractionMode_QE_dpT_containment.root \
      -o prefit_fakeData_InteractionMode_QE_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_QE/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_QE_Containment/config_ToyGenerator_FakeData_InteractionMode_QE_dpT.yaml \
      -f fakeData_InteractionMode_QE_dpT_containment.root \
      -o postfit_fakeData_InteractionMode_QE_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | QE(dpT) ---
study_dpT_QE_dpT() {
  step "dpT_QE_dpT/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_QE_dpTShape_Containment/config_Fitter_FakeData_QE_dpTShape_dpT.yaml -o fakeData_QE_dpTShape_dpT_containment.root || return 1
  step "dpT_QE_dpT/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_QE_dpTShape_Containment/config_CalcXSec_FakeData_QE_dpTShape_dpT.yaml -f fakeData_QE_dpTShape_dpT_containment.root -n 10000 -o fakeData_QE_dpTShape_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_QE_dpT/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_QE_dpTShape_Containment/config_ToyGenerator_FakeData_QE_dpTShape_dpT.yaml \
      -f fakeData_QE_dpTShape_dpT_containment.root \
      -o prefit_fakeData_QE_dpTShape_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_QE_dpT/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_QE_dpTShape_Containment/config_ToyGenerator_FakeData_QE_dpTShape_dpT.yaml \
      -f fakeData_QE_dpTShape_dpT_containment.root \
      -o postfit_fakeData_QE_dpTShape_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | QE(Pp) ---
study_dpT_QE_Pp() {
  step "dpT_QE_Pp/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_QE_ProtonP_Containment/config_Fitter_FakeData_QE_ProtonP_dpT.yaml -o fakeData_QE_ProtonP_dpT_containment.root || return 1
  step "dpT_QE_Pp/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_QE_ProtonP_Containment/config_CalcXSec_FakeData_QE_ProtonP_dpT.yaml -f fakeData_QE_ProtonP_dpT_containment.root -n 10000 -o fakeData_QE_ProtonP_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_QE_Pp/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_QE_ProtonP_Containment/config_ToyGenerator_FakeData_QE_ProtonP_dpT.yaml \
      -f fakeData_QE_ProtonP_dpT_containment.root \
      -o prefit_fakeData_QE_ProtonP_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_QE_Pp/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_QE_ProtonP_Containment/config_ToyGenerator_FakeData_QE_ProtonP_dpT.yaml \
      -f fakeData_QE_ProtonP_dpT_containment.root \
      -o postfit_fakeData_QE_ProtonP_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | RES ---
study_dpT_RES() {
  step "dpT_RES/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_InteractionMode_Containment/config_Fitter_FakeData_InteractionMode_dpT.yaml -o fakeData_InteractionMode_dpT_containment.root || return 1
  step "dpT_RES/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_InteractionMode_Containment/config_CalcXSec_FakeData_InteractionMode_dpT.yaml -f fakeData_InteractionMode_dpT_containment.root -n 10000 -o fakeData_InteractionMode_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_RES/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_Containment/config_ToyGenerator_FakeData_InteractionMode_dpT.yaml \
      -f fakeData_InteractionMode_dpT_containment.root \
      -o prefit_fakeData_InteractionMode_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_RES/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_InteractionMode_Containment/config_ToyGenerator_FakeData_InteractionMode_dpT.yaml \
      -f fakeData_InteractionMode_dpT_containment.root \
      -o postfit_fakeData_InteractionMode_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dpT | Fake Data | RES(dpT) ---
study_dpT_RES_dpT() {
  step "dpT_RES_dpT/fit" \
    gundamFitter -c RunConfigs/dpT/FakeData_RES_dpTShape_Containment/config_Fitter_FakeData_RES_dpTShape_dpT.yaml -o fakeData_RES_dpTShape_dpT_containment.root || return 1
  step "dpT_RES_dpT/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/FakeData_RES_dpTShape_Containment/config_CalcXSec_FakeData_RES_dpTShape_dpT.yaml -f fakeData_RES_dpTShape_dpT_containment.root -n 10000 -o fakeData_RES_dpTShape_XSec_dpT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_RES_dpT/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_RES_dpTShape_Containment/config_ToyGenerator_FakeData_RES_dpTShape_dpT.yaml \
      -f fakeData_RES_dpTShape_dpT_containment.root \
      -o prefit_fakeData_RES_dpTShape_dpT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_RES_dpT/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/FakeData_RES_dpTShape_Containment/config_ToyGenerator_FakeData_RES_dpTShape_dpT.yaml \
      -f fakeData_RES_dpTShape_dpT_containment.root \
      -o postfit_fakeData_RES_dpTShape_dpT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dalphaT | Fake Data | Asimov ---
study_dalphaT_Asimov() {
  step "dalphaT_Asimov/fit" \
    gundamFitter -c RunConfigs/dalphaT/Asimov_Containment/config_Fitter_FakeData_dalphaT.yaml -o asimov_dalphaT_containment.root -a || return 1
  step "dalphaT_Asimov/xsec" \
    gundamCalcXsec -c RunConfigs/dalphaT/Asimov_Containment/config_CalcXSec_FakeData_dalphaT.yaml -f asimov_dalphaT_containment.root -n 10000 -o asimov_XSec_dalphaT_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dalphaT_Asimov/prefit" \
    gundamToyGenerator -c RunConfigs/dalphaT/Asimov_Containment/config_ToyGenerator_FakeData_dalphaT.yaml \
      -f asimov_dalphaT_containment.root \
      -o prefit_asimov_dalphaT_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "dalphaT_Asimov/postfit" \
    gundamToyGenerator -c RunConfigs/dalphaT/Asimov_Containment/config_ToyGenerator_FakeData_dalphaT.yaml \
      -f asimov_dalphaT_containment.root \
      -o postfit_asimov_dalphaT_containment.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}

# --- Wiki page: dalphaT | Fake Data | Asimov (2D section) ---
study_dalphaT_Asimov_2D() {
  step "dalphaT_Asimov_2D/fit" \
    gundamFitter -c RunConfigs/dalphaT/Asimov_Containment_2D/config_Fitter_FakeData_dalphaT.yaml -o asimov_dalphaT_containment_2D.root -a || return 1
  step "dalphaT_Asimov_2D/xsec" \
    gundamCalcXsec -c RunConfigs/dalphaT/Asimov_Containment_2D/config_CalcXSec_FakeData_dalphaT.yaml -f asimov_dalphaT_containment_2D.root -n 10000 -o asimov_XSec_dalphaT_containment_2D.root --use-bf-as-xsec
  step "dalphaT_Asimov_2D/prefit" \
    gundamToyGenerator -c RunConfigs/dalphaT/Asimov_Containment_2D/config_ToyGenerator_FakeData_dalphaT.yaml \
      -f asimov_dalphaT_containment_2D.root \
      -o prefit_asimov_dalphaT_containment_2D.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "dalphaT_Asimov_2D/postfit" \
    gundamToyGenerator -c RunConfigs/dalphaT/Asimov_Containment_2D/config_ToyGenerator_FakeData_dalphaT.yaml \
      -f asimov_dalphaT_containment_2D.root \
      -o postfit_asimov_dalphaT_containment_2D.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}

# --- Wiki page: Muon Angle | Fake Data | Asimov ---
study_muon_angle_Asimov() {
  step "muon_angle_Asimov/fit" \
    gundamFitter -c RunConfigs/muon_angle/Asimov_Containment/config_Fitter_FakeData_muon_angle.yaml -o asimov_muon_angle_containment.root -a || return 1
  step "muon_angle_Asimov/xsec" \
    gundamCalcXsec -c RunConfigs/muon_angle/Asimov_Containment/config_CalcXSec_FakeData_muon_angle.yaml -f asimov_muon_angle_containment.root -n 10000 -o asimov_XSec_muon_angle_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "muon_angle_Asimov/prefit" \
    gundamToyGenerator -c RunConfigs/muon_angle/Asimov_Containment/config_ToyGenerator_FakeData_muon_angle.yaml \
      -f asimov_muon_angle_containment.root \
      -o prefit_asimov_muon_angle_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "muon_angle_Asimov/postfit" \
    gundamToyGenerator -c RunConfigs/muon_angle/Asimov_Containment/config_ToyGenerator_FakeData_muon_angle.yaml \
      -f asimov_muon_angle_containment.root \
      -o postfit_asimov_muon_angle_containment.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}

# --- Wiki page: Proton Momentum | Fake Data | Asimov ---
study_proton_momentum_Asimov() {
  step "proton_momentum_Asimov/fit" \
    gundamFitter -c RunConfigs/proton_momentum/Asimov_Containment/config_Fitter_FakeData_proton_momentum.yaml -o asimov_proton_momentum_containment.root -a || return 1
  step "proton_momentum_Asimov/xsec" \
    gundamCalcXsec -c RunConfigs/proton_momentum/Asimov_Containment/config_CalcXSec_FakeData_proton_momentum.yaml -f asimov_proton_momentum_containment.root -n 10000 -o asimov_XSec_proton_momentum_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "proton_momentum_Asimov/prefit" \
    gundamToyGenerator -c RunConfigs/proton_momentum/Asimov_Containment/config_ToyGenerator_FakeData_proton_momentum.yaml \
      -f asimov_proton_momentum_containment.root \
      -o prefit_asimov_proton_momentum_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "proton_momentum_Asimov/postfit" \
    gundamToyGenerator -c RunConfigs/proton_momentum/Asimov_Containment/config_ToyGenerator_FakeData_proton_momentum.yaml \
      -f asimov_proton_momentum_containment.root \
      -o postfit_asimov_proton_momentum_containment.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}

# --- Wiki page: Opening Angle | Fake Data | Asimov ---
study_opening_angle_Asimov() {
  step "opening_angle_Asimov/fit" \
    gundamFitter -c RunConfigs/opening_angle/Asimov_Containment/config_Fitter_FakeData_opening_angle.yaml -o asimov_opening_angle_containment.root -a || return 1
  step "opening_angle_Asimov/xsec" \
    gundamCalcXsec -c RunConfigs/opening_angle/Asimov_Containment/config_CalcXSec_FakeData_opening_angle.yaml -f asimov_opening_angle_containment.root -n 10000 -o asimov_XSec_opening_angle_containment.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "opening_angle_Asimov/prefit" \
    gundamToyGenerator -c RunConfigs/opening_angle/Asimov_Containment/config_ToyGenerator_FakeData_opening_angle.yaml \
      -f asimov_opening_angle_containment.root \
      -o prefit_asimov_opening_angle_containment.root \
      -s 1  -t 8 \
      --use-prefit \
      --use-data-entry Asimov \
      -n 1000
  step "opening_angle_Asimov/postfit" \
    gundamToyGenerator -c RunConfigs/opening_angle/Asimov_Containment/config_ToyGenerator_FakeData_opening_angle.yaml \
      -f asimov_opening_angle_containment.root \
      -o postfit_asimov_opening_angle_containment.root \
      -s 1  -t 8 \
      --use-bf \
      --use-data-entry Asimov \
      -n 1000
}
# --- Wiki page: dpT | Real Data ---
study_dpT_RealData() {
  step "dpT_RealData/fit" \
    gundamFitter -c RunConfigs/dpT/RealData_Containment/config_Fitter_RealData_dpT.yaml -o real_containment_dpT.root || return 1
  step "dpT_RealData/xsec" \
    gundamCalcXsec -c RunConfigs/dpT/RealData_Containment/config_CalcXSec_RealData_dpT.yaml -f real_containment_dpT.root -n 10000 -o real_containment_XSec_dpT.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dpT_RealData/prefit" \
    gundamToyGenerator -c RunConfigs/dpT/RealData_Containment/config_ToyGenerator_RealData_dpT.yaml \
      -f real_containment_dpT.root \
      -o prefit_real_containment_dpT.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dpT_RealData/postfit" \
    gundamToyGenerator -c RunConfigs/dpT/RealData_Containment/config_ToyGenerator_RealData_dpT.yaml \
      -f real_containment_dpT.root \
      -o postfit_real_containment_dpT.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: dalphaT | Real Data ---
study_dalphaT_RealData() {
  step "dalphaT_RealData/fit" \
    gundamFitter -c RunConfigs/dalphaT/RealData_Containment/config_Fitter_RealData_dalphaT.yaml -o real_containment_dalphaT.root || return 1
  step "dalphaT_RealData/xsec" \
    gundamCalcXsec -c RunConfigs/dalphaT/RealData_Containment/config_CalcXSec_RealData_dalphaT.yaml -f real_containment_dalphaT.root -n 10000 -o real_containment_XSec_dalphaT.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "dalphaT_RealData/prefit" \
    gundamToyGenerator -c RunConfigs/dalphaT/RealData_Containment/config_ToyGenerator_RealData_dalphaT.yaml \
      -f real_containment_dalphaT.root \
      -o prefit_real_containment_dalphaT.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "dalphaT_RealData/postfit" \
    gundamToyGenerator -c RunConfigs/dalphaT/RealData_Containment/config_ToyGenerator_RealData_dalphaT.yaml \
      -f real_containment_dalphaT.root \
      -o postfit_real_containment_dalphaT.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: Muon Angle | Real Data ---
study_muon_angle_RealData() {
  step "muon_angle_RealData/fit" \
    gundamFitter -c RunConfigs/muon_angle/RealData_Containment/config_Fitter_RealData_muon_angle.yaml -o real_containment_muon_angle.root || return 1
  step "muon_angle_RealData/xsec" \
    gundamCalcXsec -c RunConfigs/muon_angle/RealData_Containment/config_CalcXSec_RealData_muon_angle.yaml -f real_containment_muon_angle.root -n 10000 -o real_containment_XSec_muon_angle.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "muon_angle_RealData/prefit" \
    gundamToyGenerator -c RunConfigs/muon_angle/RealData_Containment/config_ToyGenerator_RealData_muon_angle.yaml \
      -f real_containment_muon_angle.root \
      -o prefit_real_containment_muon_angle.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "muon_angle_RealData/postfit" \
    gundamToyGenerator -c RunConfigs/muon_angle/RealData_Containment/config_ToyGenerator_RealData_muon_angle.yaml \
      -f real_containment_muon_angle.root \
      -o postfit_real_containment_muon_angle.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: Proton Momentum | Real Data ---
study_proton_momentum_RealData() {
  step "proton_momentum_RealData/fit" \
    gundamFitter -c RunConfigs/proton_momentum/RealData_Containment/config_Fitter_RealData_proton_momentum.yaml -o real_containment_proton_momentum.root || return 1
  step "proton_momentum_RealData/xsec" \
    gundamCalcXsec -c RunConfigs/proton_momentum/RealData_Containment/config_CalcXSec_RealData_proton_momentum.yaml -f real_containment_proton_momentum.root -n 10000 -o real_containment_XSec_proton_momentum.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "proton_momentum_RealData/prefit" \
    gundamToyGenerator -c RunConfigs/proton_momentum/RealData_Containment/config_ToyGenerator_RealData_proton_momentum.yaml \
      -f real_containment_proton_momentum.root \
      -o prefit_real_containment_proton_momentum.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "proton_momentum_RealData/postfit" \
    gundamToyGenerator -c RunConfigs/proton_momentum/RealData_Containment/config_ToyGenerator_RealData_proton_momentum.yaml \
      -f real_containment_proton_momentum.root \
      -o postfit_real_containment_proton_momentum.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

# --- Wiki page: Opening Angle | Real Data ---
study_opening_angle_RealData() {
  step "opening_angle_RealData/fit" \
    gundamFitter -c RunConfigs/opening_angle/RealData_Containment/config_Fitter_RealData_opening_angle.yaml -o real_containment_opening_angle.root || return 1
  step "opening_angle_RealData/xsec" \
    gundamCalcXsec -c RunConfigs/opening_angle/RealData_Containment/config_CalcXSec_RealData_opening_angle.yaml -f real_containment_opening_angle.root -n 10000 -o real_containment_XSec_opening_angle.root --use-bf-as-xsec --TurnRecoOnlyOff
  step "opening_angle_RealData/prefit" \
    gundamToyGenerator -c RunConfigs/opening_angle/RealData_Containment/config_ToyGenerator_RealData_opening_angle.yaml \
      -f real_containment_opening_angle.root \
      -o prefit_real_containment_opening_angle.root \
      -s 1  -t 8 \
      --use-prefit \
      -n 1000
  step "opening_angle_RealData/postfit" \
    gundamToyGenerator -c RunConfigs/opening_angle/RealData_Containment/config_ToyGenerator_RealData_opening_angle.yaml \
      -f real_containment_opening_angle.root \
      -o postfit_real_containment_opening_angle.root \
      -s 1  -t 8 \
      --use-bf \
      -n 1000
}

ALL_STUDIES=(
  dpT_Asimov dpT_LQCD dpT_MEC dpT_MINERvA dpT_Pion dpT_Q2
  dpT_QE dpT_QE_dpT dpT_QE_Pp dpT_RES dpT_RES_dpT
  dalphaT_Asimov dalphaT_Asimov_2D
  muon_angle_Asimov proton_momentum_Asimov opening_angle_Asimov
)
REAL_STUDIES=(
  dpT_RealData dalphaT_RealData muon_angle_RealData proton_momentum_RealData opening_angle_RealData
)
FAKE_STUDIES=("${ALL_STUDIES[@]}")
ALL_STUDIES+=("${REAL_STUDIES[@]}")

case "$1" in
  --list) printf '%s\n' "${ALL_STUDIES[@]}"; exit 0 ;;
  --fake) TO_RUN=("${FAKE_STUDIES[@]}") ;;
  --real) TO_RUN=("${REAL_STUDIES[@]}") ;;
  "")     TO_RUN=("${ALL_STUDIES[@]}") ;;
  *)      TO_RUN=("$@") ;;
esac

for s in "${TO_RUN[@]}"; do
  if declare -f "study_$s" > /dev/null; then
    echo "=================== STUDY: $s ==================="
    "study_$s"
  else
    echo "Unknown study: $s (use --list)"
    SUMMARY+=("UNKNOWN  $s")
  fi
done

echo
echo "=================== SUMMARY ==================="
printf '%s\n' "${SUMMARY[@]}" | tee "$LOGDIR/summary.txt"
