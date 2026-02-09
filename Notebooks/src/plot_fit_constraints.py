import uproot
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/gundam-icarus/style.mplstyle")

def plot_fit_constraints(filename, directory_path,
                        title_line1=None,
                        figsize=(10, 14),
                        output_name=None):
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
    output_name : str, optional
        Output filename for saving the plot

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
                labels.append(actual_name)
            else:
                labels.append(label)

    except Exception as e:
        print(f"Could not extract labels: {e}")
        labels = [f"Param {i+1}" for i in range(n_params)]

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)

    y_positions = np.arange(n_params)

    # Plot pre-fit uncertainties as bars
    for i in range(n_params):
        ax.barh(y_positions[i],
                2 * prefit_errors[i],
                left=prefit_values[i] - prefit_errors[i],
                height=0.95,
                color='salmon',
                alpha=0.7)

    # Add line at pre-fit central value
    ax.scatter(prefit_values, y_positions,
               marker='|', s=100, color='darkred', linewidths=1.5, zorder=3)

    # Plot post-fit values as points with error bars
    ax.errorbar(postfit_values, y_positions,
                xerr=postfit_errors,
                fmt='o',
                color='black',
                markersize=5,
                capsize=3,
                label='Post-fit values',
                elinewidth=2,
                linewidth=0,
                zorder=4)

    # Set axis labels
    ax.set_ylabel(r'$\mathbf{Parameter}$', fontsize=12)
    ax.set_xlabel(r'$\mathbf{Parameter\ values}$ (a.u.)', fontsize=12)

    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=8)

    # Set x-axis limits
    all_values = np.concatenate([prefit_values + prefit_errors,
                                  prefit_values - prefit_errors,
                                  postfit_values + postfit_errors,
                                  postfit_values - postfit_errors])
    x_max = max(abs(np.max(all_values)), abs(np.min(all_values)))
    ax.set_xlim(-x_max * 1.15, x_max * 1.15)

    # Get y-axis limits for proper title placement
    y_min, y_max = ax.get_ylim()

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

    # Add vertical line at x=0
    ax.axvline(x=0, color='black', linewidth=1.5, linestyle='-', zorder=5)

    # Add title if provided - place ABOVE the plot on the LEFT
    if title_line1:
        xrange = ax.get_xlim()
        usex_left = xrange[0] + 0.01*(xrange[1] - xrange[0])
        usey = y_max + 0.01*(y_max - y_min)

        color = 'chocolate' if 'data' in title_line1.lower() else 'blue'
        ax.text(x=usex_left, y=usey, s=title_line1, fontsize=10, color=color,
                verticalalignment='bottom')

    # Force font family on tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily('sans-serif')

    # Grid
    ax.grid(True, alpha=0.3)

    # Legend positioned at the TOP RIGHT, above the plot
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D
    legend_elements = [
        Rectangle((0, 0), 1, 1, fc='salmon', alpha=0.7, label='Pre-fit value'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='black',
               markersize=8, label='Post-fit value')
    ]
    ax.legend(handles=legend_elements,
              loc='lower right',  # Anchor point of the legend box
              bbox_to_anchor=(1, 1),  # Position: right edge (1), just above top (1.02)
              fontsize=10,
              framealpha=0.9,
              ncol=2,  # Put legend items in 2 columns (horizontal layout)
              borderaxespad=0,
              columnspacing=0)

    # Save if requested
    if output_name:
        plt.savefig(output_name, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_name}")

    return fig, ax