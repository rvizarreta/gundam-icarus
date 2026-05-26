import uproot
import matplotlib.pyplot as plt
plt.style.use("/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/gundam-icarus/style.mplstyle")
import numpy as np

def plot_scatter(filename, is_cross_section, hist_path, xlabel, ylabel, bin_edges_labels, is_y_errors,
                       title_line1=None, label=None, hline_nuisance=False,
                       figsize=(5, 4), pot='POT', remove_last_bin=True, scaling_power_of_10=1.0):
    """
    Plot cross-section data from a ROOT file with error bars.

    Parameters
    ----------
    filename : str
        Path to the ROOT file
    hist_path : str
        Path to the histogram within the ROOT file (e.g., "gundam/calcXsec/throws/histograms/TrueDeltaPT_XS_TH1D;1")
    xlabel : str
        Label for the x-axis (use raw string with LaTeX, e.g., r'True $\delta_{pT}$ [GeV]')
    ylabel : str
        Label for the y-axis (use raw string with LaTeX, e.g., r'$\frac{d\sigma}{dp_T}$ $\left[\frac{cm^2}{GeV/c^2}\right]$')
    bin_edges_labels : list
        List of bin edge values to display on x-axis (e.g., [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    title_line1 : str, optional
        First line of title (e.g., "ICARUS · NuMI Data (10% Run 2)")
    figsize : tuple, optional
        Figure size (width, height). Default is (5, 4)
    scaling_power_of_10 : float, optional
        Scaling factor for cross-section values (e.g., 1e40). Default is 1.0
    pot : str, optional
        POT label to display. Default is 'POT'
    remove_last_bin : bool, optional
        Whether to remove the last (overflow) bin. Default is True
    is_cross_section : bool
        Whether the data is a cross-section (applies scaling)
    is_y_errors : bool
        Whether to plot y-error bars
    label : str, optional
        Legend label for the data points
    hline_nuisance : bool, optional
        Whether to add a horizontal line at y=1. Default is False

    Returns
    -------
    fig, ax : matplotlib figure and axis objects
    bin_values_raw : np.ndarray
        Raw bin values (before scaling_power_of_10 applied)
    bin_errors_raw : np.ndarray
        Raw bin errors (before scaling_power_of_10 applied)
    """
    # Open the ROOT file
    file = uproot.open(filename)

    # Navigate to the histogram
    hist = file[hist_path]

    # Extract bin values and errors (raw, unscaled)
    if remove_last_bin:
        bin_values_raw = hist.values()[:-1]
        bin_errors_raw = hist.errors()[:-1]
    else:
        bin_values_raw = hist.values()
        bin_errors_raw = hist.errors()

    # Apply scaling for plotting
    if is_cross_section:
        bin_values = bin_values_raw * scaling_power_of_10
        bin_errors = bin_errors_raw * scaling_power_of_10
    else:
        bin_values = bin_values_raw
        bin_errors = bin_errors_raw

    # Calculate bin centers from provided bin edges
    bin_edges_array = np.array(bin_edges_labels)
    bin_centers = (bin_edges_array[:-1] + bin_edges_array[1:]) / 2
    bin_widths = np.diff(bin_edges_array)

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot using errorbar
    ax.errorbar(bin_centers,
                bin_values,
                xerr=bin_widths / 2,  # Half bin width for symmetric error bars
                yerr=bin_errors if is_y_errors else None,
                fmt='o',
                markersize=7,
                markerfacecolor='black',
                markeredgecolor='black',
                color='black',
                capsize=4,
                capthick=1.5,
                elinewidth=1.75,
                label=label,
                linewidth=2)

    # Set axis labels
    ax.set_xlabel(xlabel, fontsize=12, weight='bold')
    ax.set_ylabel(ylabel, fontsize=12, weight='bold')

    # Set axis limits
    ax.set_xlim(bin_edges_array[0], bin_edges_array[-1])
    y_min = 0
    y_max = np.max(bin_values + bin_errors) * 1.6
    ax.set_ylim(y_min, y_max)

    if hline_nuisance:
        ax.axhline(y=1, color='black', linestyle='--', linewidth=1.0, alpha=0.8)

    # Set tick parameters
    ax.tick_params(axis='both', which='major',
                   labelsize=12,
                   size=8,
                   width=2,
                   direction='in')

    # Enable minor ticks
    ax.minorticks_on()
    ax.tick_params(axis='y', which='minor',
                   size=4,
                   width=1,
                   direction='in')
    ax.tick_params(axis='x', which='minor',
                   size=4,
                   width=1,
                   direction='in')

    # Add two-line title if provided
    if title_line1:
        yrange = ax.get_ylim()
        usey = yrange[1] + 0.01*(yrange[1] - yrange[0])
        xrange = ax.get_xlim()
        usex = xrange[0] + 0.01*(xrange[1] - xrange[0])
        color = 'black' if 'mock' in title_line1.lower() else ('chocolate' if 'data' in title_line1.lower() else 'blue')
        ax.text(x=usex, y=usey, s=title_line1, fontsize=10, color=color, verticalalignment='bottom')
        usex_right = xrange[1] - 0.025*(xrange[1] - xrange[0])
        ax.text(x=usex_right, y=usey, s=pot, fontsize=10, color="black",
                verticalalignment='bottom', horizontalalignment='right')

    # Force font family on tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily('sans-serif')

    ax.yaxis.get_offset_text().set_fontfamily('sans-serif')
    ax.xaxis.get_offset_text().set_fontfamily('sans-serif')

    # Grid
    ax.grid(True, alpha=0.3)

    # Return the plot AND the raw (unscaled) values for reuse
    return fig, ax, bin_values_raw, bin_errors_raw