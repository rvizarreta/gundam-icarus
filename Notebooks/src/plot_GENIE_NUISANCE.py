import numpy as np

def _read_nuisflat_dir(file_dir, generator_name, branches, signal_expr,
                       nuisance_var, flux_binwidth_divided,
                       reweight_mode=None):
    """
    Read all nuisflat files from one directory and return the SELECTED
    dataframe (signal cut + reweight applied), the flux integral, and the
    number of files. Histogramming is left to the caller so the same df can
    be re-binned on multiple grids without re-reading files.

    Returns
    -------
    df_sel : pd.DataFrame with columns [nuisance_var, 'FinalWeight']
    flux_integral : float  (cm^-2)
    n_files : int
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
            read_branches = list(branches)
            if reweight_mode is not None and 'Mode' not in read_branches:
                read_branches.append('Mode')

            df = f['FlatTree_VARS'].arrays(read_branches, library='pd')
            if df_all is None:
                df_all = df
                flux_vals = f['FlatTree_FLUX'].to_numpy()[0]
                flux_bins = f['FlatTree_FLUX'].to_numpy()[1]
                flux_integral = (
                    np.sum(flux_vals * np.diff(flux_bins))
                    if flux_binwidth_divided
                    else np.sum(flux_vals)
                )
                flux_integral *= 1e-4  # /m^2 -> /cm^2
            else:
                df_all = pd.concat([df_all, df], ignore_index=True)

    df_all['FinalWeight'] = df_all['InputWeight'] * df_all['fScaleFactor']

    if reweight_mode == 'QE_0p8':
        df_all['FinalWeight'] = df_all['FinalWeight'] * np.where(df_all['Mode'] == 1, 0.8, 1.0)
    elif reweight_mode == 'RES_0p8':
        df_all['FinalWeight'] = df_all['FinalWeight'] * np.where(
            df_all['Mode'].isin([11, 12, 13]), 0.8, 1.0
        )
    elif reweight_mode == 'MEC_0p8':
        df_all['FinalWeight'] = df_all['FinalWeight'] * np.where(
            df_all['Mode'].isin([2]), 0.8, 1.0
        )
    elif reweight_mode is not None:
        raise ValueError(f"Unknown reweight_mode: '{reweight_mode}'. "
                         f"Supported values: 'QE_0p8', 'RES_0p8', None.")

    df_sel = df_all.query(signal_expr)[[nuisance_var, 'FinalWeight']].copy()
    return df_sel, flux_integral, len(files)


def _xsec_from_df(df_sel, nuisance_var, bin_edges, n_files, n_nucleons):
    """
    Histogram df_sel on bin_edges and normalize to a per-Ar cross-section
    shape: h / bin_width / n_files * n_nucleons.
    Flux normalization and scaling_power_of_10 are applied by the caller.
    """
    import numpy as np
    h = np.histogram(df_sel[nuisance_var], bins=bin_edges,
                     weights=df_sel['FinalWeight'])[0]
    bin_widths = np.diff(bin_edges)
    return h / bin_widths / n_files * n_nucleons


def _adaptive_legend(ax):
    """
    Place the legend inside the axes at the least-cluttered corner.
    Fontsize shrinks with entry count so long χ²/p-value labels still fit.
    """
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return

    n = len(handles)

    # Fontsize tiers — explicit, no interpolation
    if n <= 2:
        fontsize = 10
    elif n <= 4:
        fontsize = 9
    elif n <= 6:
        fontsize = 8
    else:
        fontsize = 7

    ax.legend(
        handles[::-1], labels[::-1],
        loc='best',
        fontsize=fontsize,
        framealpha=0.9,
        handlelength=2.0,
        handletextpad=0.5,
        borderaxespad=0.5,
        labelspacing=0.3,
    )


def overlay_genie_nuisance_xsec(fig, ax,
                                nuisance_file_dir,
                                bin_edges,
                                nuisance_file_dir_numubar=None,
                                generator_name='GENIE',
                                n_nucleons=40,
                                do_per_nucleon=False,
                                nuisance_var='ICARUS_1muNp0pi_deltaPT',
                                signal_expr='ICARUS_1muNp0pi_IsSignal == True',
                                flux_binwidth_divided=True,
                                color='steelblue',
                                label='GENIE AR23',
                                alpha=0.4,
                                scaling_power_of_10=1.0,
                                extracted_xsec=None,
                                extracted_xsec_errors=None,
                                reweight_mode=None,
                                finer_binning=False,
                                n_fine_bins=80):
    """
    Overlay GENIE NUISANCE flat-tree cross-section on an existing plot.

    Parameters
    ----------
    fig, ax : existing matplotlib figure and axes
    nuisance_file_dir : str
        Directory containing numu output_GENIE_*.nuisflat.root files.
    bin_edges : array-like
        Coarse analysis bin edges. χ² against extracted_xsec is ALWAYS
        computed on these bins.
    nuisance_file_dir_numubar : str, optional
        Directory containing numubar output_GENIE_*.nuisflat.root files.
    generator_name : str
        Generator prefix used in filenames. Default 'GENIE'.
    n_nucleons : int
        Number of nucleons in target (40 for Ar).
    do_per_nucleon : bool
        If True, divide xsec by n_nucleons.
    nuisance_var : str
        Branch name in FlatTree_VARS to histogram.
    signal_expr : str
        Pandas query string for signal selection.
    flux_binwidth_divided : bool
        Whether the stored flux histogram is already divided by bin width.
    color, label, alpha : plot styling.
    scaling_power_of_10 : float
        Same scaling factor used in plot_scatter so units match.
    extracted_xsec, extracted_xsec_errors : np.ndarray, optional
        Extracted cross-section values and 1-sigma errors per coarse bin.
        If both provided, χ²/ndof is computed and added to the label.
    reweight_mode : {'QE_0p8', 'RES_0p8', None}
        Optional truth-level reweight by GENIE Mode.
    finer_binning : bool
        If True, GENIE is drawn as a smooth continuous curve on a fine grid
        of `n_fine_bins` uniform bins spanning [bin_edges[0], bin_edges[-1]].
        If False (default), original step rendering on `bin_edges`.
    n_fine_bins : int
        Number of uniform fine bins used when finer_binning=True. Default 80.

    Returns
    -------
    fig, ax : modified figure and axes
    xsec : np.ndarray
        GENIE cross-section values on the COARSE bin_edges (used for χ²).
    chi2_info : dict or None
        {'chi2', 'ndof', 'p_value'} if extracted_xsec was provided, else None.
    """
    import numpy as np
    from scipy.stats import chi2 as chi2_dist

    branches = [
        'InputWeight', 'fScaleFactor', 'ELep', 'MLep',
        'ICARUS_1muNp0pi_IsSignal', nuisance_var,
    ]

    bin_edges   = np.array(bin_edges)
    bin_widths  = np.diff(bin_edges)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Build fine grid only when explicitly turned on
    if finer_binning:
        fine_bin_edges = np.linspace(bin_edges[0], bin_edges[-1],
                                     int(n_fine_bins) + 1)
        fine_centers = 0.5 * (fine_bin_edges[:-1] + fine_bin_edges[1:])
    else:
        fine_bin_edges = None

    # ── load selected dfs once per directory ────────────────────────────────
    df_numu, flux_numu, n_files_numu = _read_nuisflat_dir(
        nuisance_file_dir, generator_name, branches, signal_expr,
        nuisance_var, flux_binwidth_divided, reweight_mode=reweight_mode
    )

    if nuisance_file_dir_numubar is not None:
        df_numubar, flux_numubar, n_files_numubar = _read_nuisflat_dir(
            nuisance_file_dir_numubar, generator_name, branches, signal_expr,
            nuisance_var, flux_binwidth_divided, reweight_mode=reweight_mode
        )

    # ── helper: flux-combined, fully scaled xsec on any grid ────────────────
    def _build_xsec(edges):
        xsec_numu_only = _xsec_from_df(df_numu, nuisance_var, edges,
                                       n_files_numu, n_nucleons)
        if nuisance_file_dir_numubar is not None:
            xsec_nbar = _xsec_from_df(df_numubar, nuisance_var, edges,
                                      n_files_numubar, n_nucleons)
            flux_sum = flux_numu + flux_numubar
            xsec_out = (xsec_numu_only * flux_numu
                        + xsec_nbar * flux_numubar) / flux_sum
        else:
            xsec_out = xsec_numu_only
        if do_per_nucleon:
            xsec_out = xsec_out / n_nucleons
        xsec_out = xsec_out * scaling_power_of_10
        return xsec_out

    # Coarse xsec — printout AND χ² against extracted data
    xsec = _build_xsec(bin_edges)

    # Fine xsec — only used for plotting when finer_binning=True
    xsec_fine = _build_xsec(fine_bin_edges) if finer_binning else None

    # ── printout (always on the coarse, analysis bins) ──────────────────────
    print("\n" + "="*70)
    print(f"GENIE NUISANCE Cross-Section ({nuisance_var})"
          + (f" [{reweight_mode}]" if reweight_mode else ""))
    print("="*70)
    print(f"{'Bin range':<25} {'xsec':>20}")
    print("-"*70)
    for i, (lo, hi) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
        print(f"  {lo:.4f} – {hi:.4f}   {xsec[i]:>20.6e}")
    print("="*70)

    # ── χ² / Ndof on coarse bins ────────────────────────────────────────────
    chi2_info = None
    label_with_chi2 = label

    if extracted_xsec is not None and extracted_xsec_errors is not None:
        extracted_xsec        = np.asarray(extracted_xsec)
        extracted_xsec_errors = np.asarray(extracted_xsec_errors)

        valid = (
            np.isfinite(extracted_xsec) &
            np.isfinite(xsec) &
            np.isfinite(extracted_xsec_errors) &
            (extracted_xsec_errors > 0)
        )

        if np.sum(valid) > 0:
            residual = extracted_xsec[valid] - xsec[valid]
            chi2     = np.sum((residual / extracted_xsec_errors[valid]) ** 2)
            ndof     = int(np.sum(valid))
            p_value  = 1.0 - chi2_dist.cdf(chi2, ndof)

            chi2_info = {'chi2': chi2, 'ndof': ndof, 'p_value': p_value}
            label_with_chi2 = (
                f"{label} "
                f"($\\chi^2/n_{{\\rm dof}} = {chi2:.1f}/{ndof}$, "
                f"p-value = {p_value:.3f})"
            )
            print(f"\nχ² / Ndof = {chi2:.1f} / {ndof} = {chi2/ndof:.3f}")
            print(f"p-value = {p_value:.3f}")

    # ── plot ────────────────────────────────────────────────────────────────
    if finer_binning:
        # Smooth continuous curve through fine bin centers
        ax.plot(fine_centers, xsec_fine,
                color=color, linestyle='--', linewidth=1.5,
                label=label_with_chi2, zorder=1)
    else:
        # Original step-style rendering on the coarse bins
        left  = bin_centers - bin_widths / 2
        right = bin_centers + bin_widths / 2
        ax.hlines(xsec, left, right, colors=color, linestyles='--', linewidth=1.5,
                  label=label_with_chi2, zorder=1)
        ax.vlines(left,  0, xsec, colors=color, linestyles='--', linewidth=1.0, zorder=1)
        ax.vlines(right, 0, xsec, colors=color, linestyles='--', linewidth=1.0, zorder=1)

    # Adaptive legend: shrinks fontsize with entry count and moves outside
    # the axes when entries are many or labels are long.
    _adaptive_legend(ax)

    return fig, ax, xsec, chi2_info