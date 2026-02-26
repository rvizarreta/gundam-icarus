import matplotlib.pyplot as plt

def overlay_manual_cross_section(fig, ax, root_file_path, bins_mev,
                                 n_targets,
                                 flux,
                                 signal_tree_path="events/full/signal",
                                 variable_name="true_dpT",
                                 category_cuts=[0, 1, 3, 4],
                                 color='red',
                                 marker='s',
                                 label='Manual Calculation',
                                 scaling_power_of_10=1e0,
                                 energy_conversion=False,
                                 markersize=7):
    """
    Calculate cross-section manually and overlay on existing plot.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Existing figure object from plot_cross_section
    ax : matplotlib.axes.Axes
        Existing axes object from plot_cross_section
    root_file_path : str
        Path to the ROOT file containing the signal tree
    bins_mev : list of tuples
        List of bin edges in MeV, e.g., [(0, 80), (80, 160), (160, 240), (240, 320), (320, 520), (520, 99999)]
    n_targets : float
        Number of target nucleons
    flux : float
        Neutrino flux
    signal_tree_path : str, optional
        Path to the signal tree. Default is "events/full/signal"
    variable_name : str, optional
        Variable name to bin. Default is "true_dpT"
    category_cuts : list, optional
        Category values for signal selection. Default is [0, 1, 3, 4]
    color : str, optional
        Color for manual calculation points. Default is 'red'
    marker : str, optional
        Marker style. Default is 's' (square)
    label : str, optional
        Label for legend. Default is 'Manual Calculation'
    markersize : int, optional
        Marker size. Default is 7

    Returns
    -------
    fig, ax : modified matplotlib figure and axis objects
    cross_sections : np.ndarray
        Array of calculated cross-section values (in 10^-40 cm²/GeV units for plotting)
    """
    import uproot
    import awkward as ak
    import numpy as np

    # Open ROOT file and get tree
    file = uproot.open(root_file_path)
    tree = file[signal_tree_path]

    # Read branches
    arrays = tree.arrays([variable_name, "category"], library="ak")

    # Apply signal selection
    signal_mask = ak.zeros_like(arrays.category, dtype=bool)
    for cat in category_cuts:
        signal_mask = signal_mask | (arrays.category == cat)

    signal_events = arrays[signal_mask]

    # Calculate cross-section per bin
    print("\n" + "="*90)
    print("Signal Events and Cross-Section per True Bin")
    print("="*90)
    if energy_conversion:
        exponent = int(np.log10(scaling_power_of_10))
    else:
        exponent = int(np.log10(scaling_power_of_10*1e3))
    print(f"{'Bin Range (MeV/c)':<25} {'N_Signal':<12} {'Bin Width (MeV)':<18} {'σ (x10^-' + str(exponent) + ' cm²/GeV)'}")
    print("-"*90)

    cross_sections = []
    bin_centers_gev = []
    bin_widths_gev = []

    total_signal = 0
    for bin_low, bin_high in bins_mev:
        # Count events in this bin
        bin_mask = (signal_events[variable_name] >= bin_low) & (signal_events[variable_name] < bin_high)
        n_signal = int(ak.sum(bin_mask))
        n_signal_weighted = float(n_signal)

        # Calculate bin width in MeV
        if bin_high < 99999:
            bin_width_mev = bin_high - bin_low
            bin_width_str = f"{bin_width_mev:.0f}"

            # Calculate cross-section x 1eXX: σ = N_events / (N_targets × Flux × bin_width) × 1e3 (convert MeV to GeV)
            cross_section = 1e3 * scaling_power_of_10 * n_signal_weighted / (n_targets * flux * bin_width_mev)
            cross_sections.append(cross_section)
            xs_str = f"{cross_section:.6e}"

            # Calculate bin center and width in GeV for plotting
            if energy_conversion:
                bin_center_gev = (bin_low + bin_high) / 2 / 1000
                bin_width_gev = bin_width_mev / 1000
            else:
                bin_center_gev = (bin_low + bin_high) / 2
                bin_width_gev = bin_width_mev
            bin_centers_gev.append(bin_center_gev)
            bin_widths_gev.append(bin_width_gev)
        else:
            bin_width_str = "∞"
            xs_str = "N/A (infinite bin)"

        print(f"{bin_low:>6.0f} - {bin_high:<6.0f} MeV/c    {n_signal:<12} {bin_width_str:<18} {xs_str}")
        total_signal += n_signal

    print("-"*90)
    print(f"{'Total':<25} {total_signal}")
    print("="*90)

    # Convert to numpy arrays
    cross_sections = np.array(cross_sections)
    bin_centers_gev = np.array(bin_centers_gev)
    bin_widths_gev = np.array(bin_widths_gev)

    # Overlay on existing plot
    line = ax.bar(bin_centers_gev,
                  cross_sections,
                  width=bin_widths_gev,
                  color=color,
                  alpha=0.30,
                  edgecolor=color,
                  linewidth=0,
                  label=label)

    # Add legend
    ax.legend(loc='best', fontsize=10, framealpha=0.9)

    return fig, ax, cross_sections