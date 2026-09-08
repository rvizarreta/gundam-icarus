import uproot
import numpy as np
import re
import matplotlib.pyplot as plt
plt.style.use("/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/gundam-icarus/style.mplstyle")

# Hardcoded mapping from raw token (as it appears in GUNDAM bin labels)
# to the human-readable label we want on the plot.
# Hardcoded mapping from raw token in GUNDAM bin labels to the
# human-readable label. Covers detector systematics (var01–var09),
# NuMI beam focusing dials, and hadron-production PCA components (HPC).
DETSYS_LABEL_MAP = {
    # PCA Components of Z Expansion # ────────────────────────────────────
    'b1' : 'ZExp_PCA_b1',
    'b2' : 'ZExp_PCA_b2',
    'b3' : 'ZExp_PCA_b3',
    'b4' : 'ZExp_PCA_b4',
    # '#0_GENIEReWeight_SBN_v1_multisigma_ZExpA1CCQE' : 'ZExp_PCA_A1',
    # '#1_GENIEReWeight_SBN_v1_multisigma_ZExpA2CCQE' : 'ZExp_PCA_A2',
    # '#2_GENIEReWeight_SBN_v1_multisigma_ZExpA3CCQE' : 'ZExp_PCA_A3',
    # '#3_GENIEReWeight_SBN_v1_multisigma_ZExpA4CCQE' : 'ZExp_PCA_A4',
    # ── Detector systematics ────────────────────────────────────────────
    'var01': 'Induction Gain',
    'var02': 'TPC Coherent Noise',
    'var03': 'TPC Intrinsic Noise',
    'var04': 'Lifetime',
    'var05': 'Scintillation (PMT QE)',
    'var06': 'Induction Gap',
    'var07': 'YZ Uniformity',
    'var08': 'Recombination',
    'var09': 'Cathode Bending',

    # ── NuMI beam focusing dials ────────────────────────────────────────
    'beam_horn_2kA':         r'Horn Current ($\pm$2 kA)',
    'beam_horn1_x_3mm':      r'Horn 1 X Position ($\pm$3 mm)',
    'beam_horn1_y_3mm':      r'Horn 1 Y Position ($\pm$3 mm)',
    'beam_horn2_x_3mm':      r'Horn 2 X Position ($\pm$3 mm)',
    'beam_horn2_y_3mm':      r'Horn 2 Y Position ($\pm$3 mm)',
    'beam_spot_1_3mm':       r'Beam Spot Size (1.3 mm)',
    'beam_spot_1_7mm':       r'Beam Spot Size (1.7 mm)',
    'beam_horns_0mm_water':  r'Horn Water Layer (0 mm)',
    'beam_horns_2mm_water':  r'Horn Water Layer ($\pm$2 mm)',
    'beam_Beam_shift_x_1mm': r'Beam X Shift ($\pm$1 mm)',
    'beam_Beam_shift_y_1mm': r'Beam Y Shift ($\pm$1 mm)',
    'beam_Target_z_7mm':     r'Target Z Position ($\pm$7 mm)',

    # ── Hadron Production PCA components (HPC) ──────────────────────────
    'hpc_0':  'HPC PC 0',
    'hpc_1':  'HPC PC 1',
    'hpc_2':  'HPC PC 2',
    'hpc_3':  'HPC PC 3',
    'hpc_4':  'HPC PC 4',
    'hpc_5':  'HPC PC 5',
    'hpc_6':  'HPC PC 6',
    'hpc_7':  'HPC PC 7',
    'hpc_8':  'HPC PC 8',
    'hpc_9':  'HPC PC 9',
    'hpc_10': 'HPC PC 10',
    'hpc_11': 'HPC PC 11',
    'hpc_12': 'HPC PC 12',
    'hpc_13': 'HPC PC 13',
    'hpc_14': 'HPC PC 14',
}


def plot_fit_constraints(filename, directory_path,
                        title_line1=None,
                        y_label=None,
                        figsize=(10, 14)):
    """
    Plot pre-fit and post-fit parameter constraints from GUNDAM ROOT file.

    Parameters
    ----------
    filename : str
        Path to the ROOT file
    directory_path : str
        Path to the directory containing the histograms
    title_line1 : str, optional
        Title text (e.g., "ICARUS · NuMI Data")
    figsize : tuple, optional
        Figure size (width, height). Default is (10, 14)

    Returns
    -------
    fig, ax : matplotlib figure and axis objects
    """

    # Open the ROOT file
    file = uproot.open(filename)

    # Get the pre-fit and post-fit histograms
    prefit_hist = file[f"{directory_path}/preFitErrors_TH1D"]
    postfit_hist = file[f"{directory_path}/postFitErrors_TH1D"]

    # Extract data
    prefit_values = np.array(prefit_hist.values())
    prefit_errors = np.array(prefit_hist.errors())
    postfit_values = np.array(postfit_hist.values())
    postfit_errors = np.array(postfit_hist.errors())

    n_params = len(prefit_values)
    print(f"Number of parameters: {n_params}")

    # Get parameter names from bin labels
    labels = []
    try:
        axis = prefit_hist.axis()
        if hasattr(axis, 'labels'):
            raw_labels = list(axis.labels())
        else:
            raw_labels = []
            for i in range(1, n_params + 1):
                try:
                    label = axis.label(i)
                    raw_labels.append(label)
                except:
                    raw_labels.append(f"Param {i}")

        # Clean up labels: extract actual name from {string}_multisigma_{actual name}
        for label in raw_labels:
            if '_multisigma_' in label:
                actual_name = label.split('_multisigma_')[-1]
            elif 'hysyst_' in label:
                # Strip leading "#N_" index and everything up to and including "hysyst_"
                actual_name = re.sub(r'^#\d+_', '', label)  # remove "#0_", "#23_", etc.
                actual_name = actual_name.split('hysyst_', 1)[-1]  # remove "hysyst_" prefix
            else:
                actual_name = label

            # Apply hardcoded detector-systematics remap if a known token is present.
            # NOTE: We don't use \b boundaries because '_' is a word character,
            # so '\bvar01\b' would NOT match inside '#0_var01'. Instead, require
            # that the token is not followed by another digit, so 'var01' won't
            # accidentally match 'var010' if you extend the list later.
            for token, pretty in DETSYS_LABEL_MAP.items():
                if re.search(rf'{re.escape(token)}(?!\d)', actual_name):
                    actual_name = pretty
                    break

            labels.append(actual_name)

    except Exception as e:
        print(f"Could not extract labels: {e}")
        labels = [f"Param {i+1}" for i in range(n_params)]

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)

    y_positions = np.arange(n_params) + 1.5

    # Plot pre-fit uncertainties as bars - capture first bar for legend
    prefit_bar = None
    for i in range(n_params):
        bar = ax.barh(y_positions[i],
                      2 * prefit_errors[i],
                      left=prefit_values[i] - prefit_errors[i],
                      height=1,
                      color='salmon',
                      alpha=0.6)
        if i == 0:  # Save first bar for legend
            prefit_bar = bar

    # Plot post-fit values as points with error bars
    postfit_points = ax.errorbar(postfit_values, y_positions,
                                  xerr=postfit_errors,
                                  yerr=0.475,
                                  fmt='o',
                                  color='black',
                                  markersize=4,
                                  capsize=3,
                                  elinewidth=1,
                                  linewidth=0)

    # Set axis labels
    ax.set_ylabel(y_label, fontsize=12, labelpad=100)
    ax.set_xlabel(r'$\mathbf{Parameter\ values}$ (a.u.)', fontsize=12)

    # Set y-axis with major ticks at integer positions (grid lines)
    ax.set_ylim(n_params+2, 0)
    ax.set_yticks(np.arange(n_params + 1))  # Grid lines at 0, 1, 2, ..., n_params
    ax.set_yticklabels([])  # No labels on primary axis

    # Manually add labels at the shifted positions (between grid lines)
    for i, label in enumerate(labels):
        ax.text(-0.02, y_positions[i], label,
                transform=ax.get_yaxis_transform(),
                ha='right', va='center', fontsize=8)

    # Set x-axis limits
    #ax.set_xlim(-1.25, 1.25)

    # Set tick parameters
    ax.tick_params(axis='both', which='major',
                   labelsize=12,
                   size=8,
                   width=2,
                   direction='in')

    # Enable minor ticks
    ax.minorticks_on()
    ax.tick_params(axis='x', which='minor',
                   size=4,
                   width=1,
                   direction='in')
    ax.tick_params(axis='y', which='minor',
                   size=4,
                   width=1,
                   direction='in')

    # Add title if provided - place ABOVE the plot on the LEFT
    if title_line1:
        color = 'black' if 'mock' in title_line1.lower() else ('chocolate' if 'data' in title_line1.lower() else 'blue')
        ax.text(0.01, 1.01, title_line1,
                transform=ax.transAxes,
                fontsize=10, color=color,
                ha='left', va='bottom')

    # Force font family on tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily('sans-serif')

    # Grid
    ax.grid(True, alpha=1)

    ax.legend([prefit_bar, postfit_points],
              ['Pre-fit value', 'Post-fit value'],
              loc='lower right',
              bbox_to_anchor=(1.0, 1.01),
              fontsize=10,
              framealpha=0.9,
              ncol=2,
              columnspacing=1)

    return fig, ax