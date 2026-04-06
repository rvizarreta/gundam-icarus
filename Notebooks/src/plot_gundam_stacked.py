import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

def plot_gundam_stacked(
    postfit_file_path,
    fitterengine_file_path,
    fit_type='pre-fit',
    sample_name='signal_dpT',
    variable_name='reco_dpT_lp',
    cov_bin_range=(0, 12),
    categories_config=None,
    is_data=False,
    stack_order=None,
    xlabel=r'$\delta p_T$ [MeV/c]',
    ylabel=r'$\mathbf{Events / (MeV/c)}$',
    title='ICARUS CC0π',
    pot='NuMI 2.22×10¹⁹ POT',
    xlim=None,
    ylim_top=None,
    ylim_ratio=(0.5, 1.75),
    figsize=(7, 4),
    style_file=None,
    output_file=None,
    show_plot=True
):
    """
    Plot stacked histogram from GUNDAM output with data overlay and ratio panel.

    Parameters
    ----------
    postfit_file_path : str
        Path to the ROOT file
    fit_type : str
        'pre-fit' or 'post-fit'
    sample_name : str
        Sample name (e.g., 'signal_dpT')
    variable_name : str
        Variable name (e.g., 'reco_dpT')
    cov_bin_range : tuple
        (start, end) bin indices for this variable in the covariance matrix
    categories_config : dict
        Category configuration {cat_id: (label, color), ...}
    stack_order : list
        Order for stacking categories (backgrounds first)
    xlabel : str
        X-axis label
    ylabel : str
        Y-axis label
    title : str
        Plot title (top left)
    pot : str
        POT text (top right)
    xlim : tuple
        X-axis limits (min, max)
    ylim_top : tuple
        Y-axis limits for top panel (min, max)
    ylim_ratio : tuple
        Y-axis limits for ratio panel (min, max)
    figsize : tuple
        Figure size (width, height)
    style_file : str
        Path to matplotlib style file
    output_file : str
        Path to save figure (if None, don't save)
    show_plot : bool
        Whether to display the plot

    Returns
    -------
    fig, (ax1, ax2) : matplotlib figure and axes
    """

    # Apply custom style if provided
    if style_file:
        plt.style.use(style_file)

    # Default category configuration
    if categories_config is None:
        categories_config = {
            0: ('Signal', 'darkgreen'),
            3: ('Signal', 'darkgreen'),
            1: ('Signal', 'darkgreen'),
            4: ('Signal', 'darkgreen'),
            6: ('Other CC', 'C1'),
            7: ('Other CC', 'C1'),
            8: ('Other CC', 'C1'),
            9: (r'$\nu$ NC', 'deepskyblue'),
            2: ('OOFV', 'orchid'),
            5: ('OOFV', 'orchid'),
            #10: ('Cosmic', 'C4'),  # Add Cosmic category
        }

    # Default stack order (backgrounds first, signal last)
    if stack_order is None:
        stack_order = [10, 9, 6, 7, 8, 2, 5, 1, 4, 0, 3]

    # Open ROOT file
    file = uproot.open(postfit_file_path) # toyGen file
    fitterengine_file = uproot.open(fitterengine_file_path) # FitterEngine file

    # Extract all category histograms
    category_data = {}
    bin_edges = None
    if fit_type == 'pre-fit':
        path_template = f"toyGen/plots/histograms/{sample_name} (pre-fit)/{variable_name}/category/{{cat}}/MC_TH1D"
    else:  # post-fit
        path_template = f"toyGen/plots/histograms/{sample_name}/{variable_name}/category/{{cat}}/MC_TH1D"

    for cat in categories_config.keys():
        path = path_template.format(cat=cat)
        try:
            hist = file[path]
            values, edges = hist.to_numpy()
            if bin_edges is None:
                bin_edges = edges
            category_data[cat] = values
        except KeyError:
            print(f"Warning: Category {cat} not found at {path}")

    # Extract data values and errors from FitterEngine path
    if is_data is False:
        if fit_type == 'pre-fit':
            data_path = f"FitterEngine/preFit/plots/histograms/{sample_name}/{variable_name}/MC_TH1D"
        else:  # post-fit
            data_path = f"FitterEngine/preFit/plots/histograms/{sample_name}/{variable_name}/MC_TH1D"
    if is_data:
        if fit_type == 'pre-fit':
            data_path = f"FitterEngine/preFit/plots/histograms/{sample_name}/{variable_name}/Data_TH1D"
        else:  # post-fit
            data_path = f"FitterEngine/preFit/plots/histograms/{sample_name}/{variable_name}/Data_TH1D"

    data_hist = fitterengine_file[data_path]
    data_values = data_hist.values()  # Remove overflow
    data_errors = data_hist.errors()  # Get stored statistical errors


    # Extract SYSTEMATIC UNCERTAINTIES from covariance matrix
    cov_matrix_hist = file["toyGen/matrices/covarianceMatrix_TH2D"]
    cov_matrix = cov_matrix_hist.values()

    # Extract diagonal elements for this variable's bins
    bin_start, bin_end = cov_bin_range
    cov_diag = np.diag(cov_matrix)[bin_start:bin_end]
    syst_errors = np.sqrt(cov_diag)

    # Group categories by (label, color)
    unique_categories = {}
    for cat in stack_order:
        if cat not in category_data:
            continue
        label, color = categories_config[cat]
        key = (label, color)
        if key not in unique_categories:
            unique_categories[key] = np.zeros_like(category_data[cat])
        unique_categories[key] += category_data[cat]

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize,
                                    gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})

    # Top panel: Calculate cumulative FIRST (before drawing)
    cumulative = np.zeros_like(list(unique_categories.values())[0])
    for (label, color), values in unique_categories.items():
        cumulative += values

    # Draw SYSTEMATIC UNCERTAINTY BAND FIRST (underneath)
    ax1.fill_between(
        bin_edges[:-1],
        cumulative - syst_errors,
        cumulative + syst_errors,
        step='post',
        facecolor='lightgray',
        edgecolor='gray',
        alpha=1,
        hatch='xxx',
        linewidth=0.8,
        label='Systematic Unc.',
        zorder=1  # LOW z-order, draws first
    )
    ax1.fill_between(
        [bin_edges[-2], bin_edges[-1]],
        [cumulative[-1] - syst_errors[-1], cumulative[-1] - syst_errors[-1]],
        [cumulative[-1] + syst_errors[-1], cumulative[-1] + syst_errors[-1]],
        facecolor='lightgray',
        edgecolor='gray',
        alpha=1,
        hatch='xxx',
        linewidth=0.8,
        zorder=1
    )

    # ADD border line on top of uncertainty band
    y_top = cumulative + syst_errors
    ax1.step(bin_edges,
             np.append(y_top, y_top[-1]),
             where='post',
             color='grey',
             linewidth=1.5,
             zorder=2)

    # NOW draw stacked histogram ON TOP
    cumulative = np.zeros_like(list(unique_categories.values())[0])
    for (label, color), values in unique_categories.items():
        ax1.fill_between(
            bin_edges[:-1],
            cumulative,
            cumulative + values,
            step='post',
            label=label,
            color=color,
            alpha=0.85,
            linewidth=0,
            zorder=3  # HIGHER z-order, draws on top
        )
        ax1.fill_between(
            [bin_edges[-2], bin_edges[-1]],
            [cumulative[-1], cumulative[-1]],
            [cumulative[-1] + values[-1], cumulative[-1] + values[-1]],
            color=color,
            alpha=0.95,
            linewidth=0,
            zorder=3
        )
        cumulative += values

    # ADD PREDICTION LINE (total MC)
    total_events = cumulative.sum()
    ax1.step(bin_edges,
             np.append(cumulative, cumulative[-1]),
             where='post',
             color='black',
             linewidth=1.5,
             label=f'Prediction ({total_events:.1f} events)',
             zorder=7)

    # Data points
    data_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    data_widths = np.diff(bin_edges) / 2  # Half bin width for xerr

    ax1.errorbar(
        data_centers,
        data_values,
        xerr=data_widths,
        yerr=data_errors,
        fmt='o',
        color='black',
        markersize=5,
        markerfacecolor='black',
        markeredgecolor='black',
        linewidth=1.5,
        capsize=3,
        capthick=1.5,
        elinewidth=1.5,
        label='Data',
        zorder=10
    )

    # Top panel styling
    ax1.set_ylabel(ylabel, fontsize=12, weight='bold')
    if xlim:
        ax1.set_xlim(xlim)
    else:
        ax1.set_xlim(bin_edges[0], bin_edges[-1])

    if ylim_top:
        ax1.set_ylim(ylim_top)
    else:
        ax1.set_ylim(0, ax1.get_ylim()[1] * 1.30)

    # Tick parameters matching plot_scatter style
    ax1.tick_params(axis='both', which='major',
                    labelsize=12,
                    size=8,
                    width=2,
                    direction='in',
                    labelbottom=False)
    ax1.minorticks_on()
    ax1.tick_params(axis='y', which='minor',
                    size=4,
                    width=1,
                    direction='in')
    ax1.tick_params(axis='x', which='minor',
                    size=4,
                    width=1,
                    direction='in')

    # Calculate total MC events and individual category events
    total_mc_events = cumulative.sum()
    category_events = {}
    for (label, color), values in unique_categories.items():
        category_events[label] = values.sum()

    # Build new labels with event counts
    new_handles = []
    new_labels = []

    handles, labels = ax1.get_legend_handles_labels()

    # Separate systematic from others
    syst_handle = None
    syst_label = None

    # First pass: collect non-systematic items
    for handle, label in zip(handles, labels):
        if 'Systematic Unc.' in label:
            # Create custom patch for systematic with NO EDGE
            syst_handle = plt.Rectangle((0, 0), 1, 1,
                                        facecolor='lightgray',
                                        edgecolor='gray',
                                        alpha=1,
                                        hatch='xxx',
                                        linewidth=0.6)  # Remove contour
            syst_label = 'Stats & Interaction Uncertainty'
            continue
        elif 'Prediction' in label:
            new_handles.append(handle)
            new_labels.append(label)
        elif 'Data' in label:
            new_handles.append(handle)
            new_labels.append(f'Data ({data_values.sum():.1f})')
        else:
            # Add event count and percentage for MC categories
            for cat_label, count in category_events.items():
                if cat_label in label:
                    percentage = 100 * count / total_mc_events
                    new_handles.append(handle)
                    new_labels.append(f'{cat_label} ({count:.1f}, {percentage:.2f}%)')
                    break

    # Reverse the current list (Data at top)
    new_handles = new_handles[::-1]
    new_labels = new_labels[::-1]

    # Add systematic at the END (bottom of legend)
    if syst_handle is not None:
        new_handles.append(syst_handle)
        new_labels.append(syst_label)

    ax1.legend(new_handles, new_labels, loc='upper right', fontsize=8, framealpha=0.9, frameon=False)

    # Top panel tick parameters - add ticks on all sides
    ax1.tick_params(axis='both', which='major',
                    labelsize=12,
                    size=8,
                    width=2,
                    direction='in',
                    labelbottom=False,
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides
    ax1.minorticks_on()
    ax1.tick_params(axis='y', which='minor',
                    size=4,
                    width=1,
                    direction='in',
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides
    ax1.tick_params(axis='x', which='minor',
                    size=4,
                    width=1,
                    direction='in',
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides

    # Title using text placement (top left and top right like plot_scatter)
    yrange = ax1.get_ylim()
    xrange = ax1.get_xlim()
    usey = yrange[1] + 0.01*(yrange[1] - yrange[0])
    usex = xrange[0] + 0.01*(xrange[1] - xrange[0])
    color = 'black' if 'mock' in title.lower() else ('chocolate' if 'data' in title.lower() else 'blue')
    ax1.text(x=usex, y=usey, s=title,
             fontsize=10, color=color, verticalalignment='bottom')
    usex_right = xrange[1] - 0.025*(xrange[1] - xrange[0])
    ax1.text(x=usex_right, y=usey, s=pot, fontsize=10, color="black",
             verticalalignment='bottom', horizontalalignment='right')

    # Force font family on tick labels
    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontfamily('sans-serif')
    ax1.yaxis.get_offset_text().set_fontfamily('sans-serif')
    ax1.xaxis.get_offset_text().set_fontfamily('sans-serif')

    # Bottom panel: Data/MC ratio
    ratio = data_values / cumulative
    ratio_err = data_errors / cumulative
    ratio_syst = syst_errors / cumulative

    # Bottom panel data points - ADD xerr
    ax2.errorbar(
        data_centers,
        ratio,
        xerr=data_widths,  # ADD THIS
        yerr=ratio_err,
        fmt='o',
        color='black',
        markersize=6,  # Change from 7 to 6
        markerfacecolor='black',
        markeredgecolor='black',
        linewidth=1.5,  # Change from 2 to 1.5
        capsize=4,      # Change from 4 to 3
        capthick=1.5,
        elinewidth=1.5
    )

    # Systematic uncertainty band on ratio plot
    ax2.fill_between(
        bin_edges[:-1],
        1 - ratio_syst,
        1 + ratio_syst,
        step='post',
        facecolor='lightgray',  # Change from 'gray'
        edgecolor='gray',
        alpha=0.6,  # Change from 0.3
        hatch='xxx',  # Change from '///'
        linewidth=0.8  # Change from 0
    )
    # LAST BIN for ratio plot
    ax2.fill_between(
        [bin_edges[-2], bin_edges[-1]],
        [1 - ratio_syst[-1], 1 - ratio_syst[-1]],
        [1 + ratio_syst[-1], 1 + ratio_syst[-1]],
        facecolor='lightgray',
        edgecolor='gray',
        alpha=0.6,
        hatch='xxx',
        linewidth=0.8
    )

    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)
    ax2.set_xlabel(xlabel, fontsize=12, weight='bold')
    ax2.set_ylabel(r'$\mathbf{Data/MC}$', fontsize=11, weight='bold')

    if xlim:
        ax2.set_xlim(xlim)
    else:
        ax2.set_xlim(bin_edges[0], bin_edges[-1])

    ax2.set_ylim(ylim_ratio)

    # Tick parameters for bottom panel - add ticks on all sides
    ax2.tick_params(axis='both', which='major',
                    labelsize=12,
                    size=8,
                    width=2,
                    direction='in',
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides
    ax2.minorticks_on()
    ax2.tick_params(axis='y', which='minor',
                    size=4,
                    width=1,
                    direction='in',
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides
    ax2.tick_params(axis='x', which='minor',
                    size=4,
                    width=1,
                    direction='in',
                    top=True, right=True, left=True, bottom=True)  # ADD: all sides

    # Force font family on tick labels
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontfamily('sans-serif')
    ax2.yaxis.get_offset_text().set_fontfamily('sans-serif')
    ax2.xaxis.get_offset_text().set_fontfamily('sans-serif')

    # Save if requested with higher DPI
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')

    # Show if requested
    if show_plot:
        plt.show()

    return fig, (ax1, ax2)