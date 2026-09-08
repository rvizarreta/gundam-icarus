import uproot
import matplotlib.pyplot as plt
plt.style.use("/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS/ICARUS_CC0pi_GUNDAM/gundam-icarus/style.mplstyle")
import numpy as np

def plot_scatter(filename, is_cross_section, hist_path, xlabel, ylabel, bin_edges_labels, is_y_errors,
                       title_line1=None, label=None, hline_nuisance=False,
                       figsize=(5, 4), pot='POT', remove_last_bin=True, scaling_power_of_10=1.0,
                       show_prior=False, prior_hist_path=None, prior_label='Pre-fit value',
                       prior_color='salmon', prior_alpha=0.6):
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
    show_prior : bool, optional
        Whether to draw a shaded pre-fit (prior) band behind the post-fit points, the
        same way plot_fit_constraints does for nuisance parameters. Default is False.
    prior_hist_path : str, optional
        Path to the pre-fit histogram within the ROOT file. If None (default) and
        show_prior is True, it is derived from hist_path by replacing
        "postFitErrors_TH1D" with "preFitErrors_TH1D" -- the convention GUNDAM uses
        for every parameterSet (both histograms live side by side in the same
        directory, e.g. ".../BackgroundFit true_generator_q2/values/"). Pass this
        explicitly if hist_path doesn't follow that convention.
    prior_label : str, optional
        Legend label for the prior band. Default is 'Pre-fit value' (matches
        plot_fit_constraints' legend wording). Pass None to omit it from the legend.
    prior_color : str, optional
        Color of the prior band. Default is 'salmon' (matches plot_fit_constraints).
    prior_alpha : float, optional
        Alpha of the prior band. Default is 0.6 (matches plot_fit_constraints).

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

    # Optionally fetch the pre-fit (prior) histogram, same bin-removal/scaling treatment
    # as the post-fit one above, so the two are directly comparable bin-for-bin.
    if show_prior:
        if prior_hist_path is None:
            if "postFitErrors_TH1D" not in hist_path:
                raise ValueError(
                    "show_prior=True but prior_hist_path was not given and hist_path "
                    "does not contain 'postFitErrors_TH1D', so the pre-fit histogram "
                    "path can't be derived automatically. Pass prior_hist_path explicitly."
                )
            prior_hist_path = hist_path.replace("postFitErrors_TH1D", "preFitErrors_TH1D")
        prior_hist = file[prior_hist_path]

        if remove_last_bin:
            prior_values_raw = prior_hist.values()[:-1]
            prior_errors_raw = prior_hist.errors()[:-1]
        else:
            prior_values_raw = prior_hist.values()
            prior_errors_raw = prior_hist.errors()

        if is_cross_section:
            prior_values = prior_values_raw * scaling_power_of_10
            prior_errors = prior_errors_raw * scaling_power_of_10
        else:
            prior_values = prior_values_raw
            prior_errors = prior_errors_raw

    # Calculate bin centers from provided bin edges
    bin_edges_array = np.array(bin_edges_labels)
    bin_centers = (bin_edges_array[:-1] + bin_edges_array[1:]) / 2
    bin_widths = np.diff(bin_edges_array)

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)

    # Default the data-point legend label to match plot_fit_constraints' wording
    # ('Post-fit value') whenever the prior band is shown, so the two legend entries
    # are consistent with the knob-pulling plots. Only kicks in when show_prior=True
    # and the caller didn't already ask for a specific label.
    if show_prior and label is None:
        label = 'Post-fit value'

    # Draw the prior band first (zorder=1) so the post-fit points (zorder=3) sit on top
    prior_bar = None
    if show_prior:
        prior_bar = ax.bar(bin_centers,
                            height=2 * prior_errors,
                            bottom=prior_values - prior_errors,
                            width=bin_widths,
                            color=prior_color,
                            alpha=prior_alpha,
                            zorder=1,
                            label=prior_label)

    # Plot using errorbar
    data_points = ax.errorbar(bin_centers,
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
                zorder=3,
                linewidth=2)

    # Set axis labels
    ax.set_xlabel(xlabel, fontsize=12, weight='bold')
    ax.set_ylabel(ylabel, fontsize=12, weight='bold')

    # Set axis limits
    ax.set_xlim(bin_edges_array[0], bin_edges_array[-1])
    y_min = 0
    y_max_candidates = [np.max(bin_values + bin_errors)]
    if show_prior:
        y_max_candidates.append(np.max(prior_values + prior_errors))
    y_max = np.max(y_max_candidates) * 1.6
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
    # (named label_tick, not label, so it doesn't shadow the "label" parameter --
    # we still need the original legend-label string below)
    for label_tick in ax.get_xticklabels() + ax.get_yticklabels():
        label_tick.set_fontfamily('sans-serif')

    ax.yaxis.get_offset_text().set_fontfamily('sans-serif')
    ax.xaxis.get_offset_text().set_fontfamily('sans-serif')

    # Grid
    ax.grid(True, alpha=0.3)

    # Legend: only draw one if there's something to label (prior band and/or data points)
    legend_handles, legend_labels = [], []
    if show_prior and prior_bar is not None and prior_label:
        legend_handles.append(prior_bar)
        legend_labels.append(prior_label)
    if label:
        legend_handles.append(data_points)
        legend_labels.append(label)
    if legend_handles:
        # Same legend styling as plot_fit_constraints (fontsize, framealpha, two
        # columns) so the two plot types read consistently; placed inside the
        # axes' upper-right corner rather than plot_fit_constraints' above-the-frame
        # bbox_to_anchor, since that spot is already used here by the pot/title text.
        ax.legend(legend_handles, legend_labels,
                  loc='upper right',
                  fontsize=10,
                  framealpha=0.9,
                  ncol=2,
                  columnspacing=1)

    # Return the plot AND the raw (unscaled) values for reuse
    return fig, ax, bin_values_raw, bin_errors_raw
