def _read_nuisflat_dir(file_dir, generator_name, branches, signal_expr,
                       nuisance_var, bin_edges, flux_binwidth_divided):
    """
    Read all nuisflat files from one directory.
    Returns (h, flux_integral, n_files) where h is the raw weighted histogram
    (NOT yet divided by bin width or n_files).
    """
    import uproot
    import pandas as pd
    import numpy as np
    import glob
    import os

    files = sorted(glob.glob(os.path.join(file_dir, f'output_{generator_name}_*.nuisflat.root')))
    if not files:
        raise FileNotFoundError(f'No files found in {file_dir}')

    df_all = None
    flux_integral = None

    for f_path in files:
        with uproot.open(f_path) as f:
            df = f['FlatTree_VARS'].arrays(branches, library='pd')
            if df_all is None:
                df_all = df
                flux_vals = f['FlatTree_FLUX'].to_numpy()[0]
                flux_bins = f['FlatTree_FLUX'].to_numpy()[1]
                flux_integral = (
                    np.sum(flux_vals * np.diff(flux_bins))
                    if flux_binwidth_divided
                    else np.sum(flux_vals)
                )
                flux_integral *= 1e-4   # /m² → /cm²
            else:
                df_all = pd.concat([df_all, df], ignore_index=True)

    df_all['FinalWeight'] = df_all['InputWeight'] * df_all['fScaleFactor']
    df_sel = df_all.query(signal_expr)
    h = np.histogram(df_sel[nuisance_var], bins=bin_edges, weights=df_sel['FinalWeight'])[0]

    return h, flux_integral, len(files)

def overlay_genie_nuisance_xsec(fig, ax,
                                 nuisance_file_dir,
                                 bin_edges,
                                 nuisance_file_dir_numubar = None,
                                 generator_name            = "GENIE",
                                 n_nucleons                = 40,
                                 do_per_nucleon            = False,
                                 nuisance_var              = 'ICARUS_1muNp0pi_deltaPT',
                                 signal_expr               = 'ICARUS_1muNp0pi_IsSignal == True',
                                 flux_binwidth_divided      = True,
                                 color                     = 'steelblue',
                                 label                     = 'GENIE AR23',
                                 alpha                     = 0.4,
                                 scaling_power_of_10       = 1.0):
    """
    Overlay GENIE NUISANCE flat-tree cross-section as a histogram on an existing plot.

    Parameters
    ----------
    fig, ax : existing matplotlib figure and axes (e.g. from plot_scatter)
    nuisance_file_dir : str
        Directory containing numu output_GENIE_*.nuisflat.root files.
    bin_edges : array-like
        Bin edges in the same units as the plot (GeV/c for deltaPT).
    nuisance_file_dir_numubar : str, optional
        Directory containing numubar output_GENIE_*.nuisflat.root files.
        If provided, the combined cross-section is computed as a flux-weighted
        average of numu and numubar, matching Jaesung's notebook method.
    generator_name : str
        Generator prefix used in filenames. Default 'GENIE'.
    n_nucleons : int
        Number of nucleons in target (40 for Ar). Default 40.
    do_per_nucleon : bool
        If True, divide xsec by n_nucleons. Default False (per Ar).
    nuisance_var : str
        Branch name in FlatTree_VARS to histogram.
    signal_expr : str
        Pandas query string for signal selection.
    flux_binwidth_divided : bool
        Whether the stored flux histogram is already divided by bin width. Default True.
    color, label, alpha : plot styling.
    scaling_power_of_10 : float
        Same scaling factor used in plot_scatter so units match. Default 1.0.

    Returns
    -------
    fig, ax : modified figure and axes
    xsec : np.ndarray
        Cross-section values per bin
    """
    import numpy as np

    branches = [
        'InputWeight', 'fScaleFactor', 'ELep', 'MLep',
        'ICARUS_1muNp0pi_IsSignal', nuisance_var,
    ]

    bin_edges   = np.array(bin_edges)
    bin_widths  = np.diff(bin_edges)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # ── numu ────────────────────────────────────────────────────────────────
    h_numu, flux_numu, n_files_numu = _read_nuisflat_dir(
        nuisance_file_dir, generator_name, branches, signal_expr,
        nuisance_var, bin_edges, flux_binwidth_divided
    )

    # ── numubar (optional) ──────────────────────────────────────────────────
    if nuisance_file_dir_numubar is not None:
        h_numubar, flux_numubar, n_files_numubar = _read_nuisflat_dir(
            nuisance_file_dir_numubar, generator_name, branches, signal_expr,
            nuisance_var, bin_edges, flux_binwidth_divided
        )
        # Flux-weighted average (Jaesung's method from CalcXsec.ipynb)
        flux_sum = flux_numu + flux_numubar
        xsec_numu    = h_numu    / bin_widths / n_files_numu    * n_nucleons
        xsec_numubar = h_numubar / bin_widths / n_files_numubar * n_nucleons
        xsec = (xsec_numu * flux_numu + xsec_numubar * flux_numubar) / flux_sum
    else:
        xsec = h_numu / bin_widths / n_files_numu * n_nucleons

    if do_per_nucleon:
        xsec /= n_nucleons
    xsec *= scaling_power_of_10

    # ── printout ─────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print(f"GENIE NUISANCE Cross-Section ({nuisance_var})")
    print("="*70)
    print(f"{'Bin range':<25} {'xsec':>20}")
    print("-"*70)
    for i, (lo, hi) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
        print(f"  {lo:.4f} – {hi:.4f}   {xsec[i]:>20.6e}")
    print("="*70)

    # ── plot ─────────────────────────────────────────────────────────────────
    left  = bin_centers - bin_widths / 2
    right = bin_centers + bin_widths / 2

    ax.hlines(xsec, left, right, colors=color, linestyles='--', linewidth=1.5, label=label, zorder=1)
    ax.vlines(left,  0, xsec,   colors=color, linestyles='--', linewidth=1.0, zorder=1)
    ax.vlines(right, 0, xsec,   colors=color, linestyles='--', linewidth=1.0, zorder=1)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='best', fontsize=10, framealpha=0.9)

    return fig, ax, xsec