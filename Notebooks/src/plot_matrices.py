import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import re

plt.style.use(
    "/Users/rvizarreta/Library/CloudStorage/GoogleDrive-rvizarreta14@gmail.com"
    "/My Drive/🏛 PhD Repository/🚀 Research/🤖 Experiments&Projects/ICARUS"
    "/ICARUS_CC0pi_GUNDAM/gundam-icarus/style.mplstyle"
)

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_labels(hist, n_params):
    """Extract and clean parameter labels from a TH2D histogram axis."""
    labels = []
    try:
        axis = hist.axis("x")
        if hasattr(axis, "labels"):
            raw_labels = list(axis.labels())
        else:
            raw_labels = []
            for i in range(1, n_params + 1):
                try:
                    raw_labels.append(axis.label(i))
                except Exception:
                    raw_labels.append(f"Param {i}")

        for label in raw_labels:
            if "_multisigma_" in label:
                labels.append(label.split("_multisigma_")[-1])
            elif "hysyst_" in label:
                actual_name = re.sub(r'^#\d+_', '', label)
                actual_name = actual_name.split("hysyst_", 1)[-1]
                labels.append(actual_name)
            else:
                labels.append(label)

    except Exception as e:
        print(f"Could not extract labels: {e}")
        labels = [f"Param {i + 1}" for i in range(n_params)]

    return labels


def _title_color(title_line1):
    """Replicate the title colour logic from plot_fit_constraints."""
    if title_line1 is None:
        return "blue"
    tl = title_line1.lower()
    if "mock" in tl:
        return "black"
    if "data" in tl:
        return "chocolate"
    return "blue"


def _apply_common_style(ax):
    """Apply the same tick / minor-tick style used in plot_fit_constraints."""
    ax.tick_params(
        axis="both", which="major",
        labelsize=8, size=8, width=2, direction="in",
    )
    ax.minorticks_on()
    ax.tick_params(axis="both", which="minor", size=4, width=1, direction="in")
    ax.grid(False)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily("sans-serif")


# ─────────────────────────────────────────────────────────────────────────────
# Main function
# ─────────────────────────────────────────────────────────────────────────────

def plot_both_matrices(
    filename,
    cov_path,
    corr_path,
    bin_range=None,
    title_line1=None,
    figsize=(14, 24),
    cmap="RdBu_r",
    label_name=None,
    annotate=False,
    annotate_threshold=0.3,
):
    """
    Plot the covariance and correlation matrices stacked vertically.

    Parameters
    ----------
    filename : str
        Path to the ROOT file.
    cov_path : str
        Path to the covariance TH2D inside the ROOT file.
        E.g. "FitterEngine/postFit/Hesse/errors/Cross Section Systematics/matrices/Covariance_TH2D;1"
        or   "FitterEngine/postFit/Hesse/hessian/postfitCovariance_TH2D;1"
    corr_path : str
        Path to the correlation TH2D inside the ROOT file.
        E.g. "FitterEngine/postFit/Hesse/errors/Cross Section Systematics/matrices/Correlation_TH2D;1"
        or   "FitterEngine/postFit/Hesse/hessian/postfitCorrelation_TH2D;1"
    bin_range : tuple of int, optional
        (start, stop) indices — Python slice convention, stop is exclusive.
        E.g. (0, 12) plots only the first 12 bins (selection sample).
        E.g. (12, 24) plots the sideband bins.
        If None, all bins are plotted.
    title_line1 : str, optional
        Title text (e.g., "ICARUS · NuMI Asimov").
    figsize : tuple, optional
        Total figure size (width, height). Height is shared between both panels.
    cmap : str, optional
        Matplotlib colormap for both panels. 'RdBu_r' keeps zero = white.
    annotate : bool, optional
        If True, print the correlation value inside each cell whose |rho|
        exceeds annotate_threshold. Recommended only for small submatrices.
    annotate_threshold : float, optional
        Only cells with |rho| >= this value get a text annotation.

    Returns
    -------
    (fig_cov, ax_cov), (fig_corr, ax_corr) : two (figure, axis) tuples,
        one for the covariance matrix and one for the correlation matrix.
    """
    file = uproot.open(filename)

    cov_hist  = file[cov_path]
    corr_hist = file[corr_path]

    cov_full  = cov_hist.values()
    corr_full = corr_hist.values()
    n_full    = cov_full.shape[0]
    print(f"Full matrix size: {n_full}×{n_full}")

    labels_full = _extract_labels(cov_hist, n_full)

    # ── Apply bin range slice ─────────────────────────────────────────────────
    if bin_range is not None:
        start, stop = bin_range
        if stop > n_full:
            raise ValueError(
                f"bin_range stop ({stop}) exceeds matrix size ({n_full})."
            )
        cov_matrix  = cov_full[start:stop, start:stop]
        corr_matrix = corr_full[start:stop, start:stop]
        labels      = labels_full[start:stop]
        n           = stop - start
        print(f"Plotting bin range [{start}, {stop}) → {n}×{n} submatrix")
    else:
        cov_matrix  = cov_full
        corr_matrix = corr_full
        labels      = labels_full
        n           = n_full

    tick_pos = np.arange(n)

    fig_cov,  ax_cov  = plt.subplots(1, 1, figsize=figsize,
                                          constrained_layout=True)
    fig_corr, ax_corr = plt.subplots(1, 1, figsize=figsize,
                                          constrained_layout=True)

    # ── Shared axis formatting helper ─────────────────────────────────────────
    def _format_axes(ax, label_name):
        ax.set_xticks(tick_pos)
        ax.set_yticks(tick_pos)
        ax.set_xticklabels(labels, rotation=90, fontsize=7, ha="center")
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel(
            label_name, fontsize=12, labelpad=8
        )
        ax.set_ylabel(
            label_name, fontsize=12, labelpad=8
        )
        _apply_common_style(ax)

    # ── Covariance panel ──────────────────────────────────────────────────────
    vmax_cov = np.max(np.abs(cov_matrix))
    norm_cov = TwoSlopeNorm(vmin=-vmax_cov, vcenter=0.0, vmax=vmax_cov)
    ax_cov.set_facecolor("lightgray")
    im_cov = ax_cov.imshow(
        cov_matrix, cmap="RdBu_r", norm=norm_cov, aspect="equal", origin="upper",
        alpha=0.85
    )
    cbar_cov = fig_cov.colorbar(im_cov, ax=ax_cov, fraction=0.046, pad=0.04)
    cbar_cov.set_label(r"$\mathbf{Covariance}$", fontsize=11)
    cbar_cov.ax.tick_params(labelsize=9)
    _format_axes(ax_cov, label_name)

    # ── Correlation panel ─────────────────────────────────────────────────────
    norm_corr = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
    ax_corr.set_facecolor("lightgray")
    im_corr = ax_corr.imshow(
        corr_matrix, cmap=cmap, norm=norm_corr, aspect="equal", origin="upper",
        alpha=0.85
    )
    cbar_corr = fig_corr.colorbar(im_corr, ax=ax_corr, fraction=0.046, pad=0.04)
    cbar_corr.set_label(
        r"$\mathbf{Correlation\ coefficient}\ \rho_{ij}$", fontsize=11
    )
    cbar_corr.set_ticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    cbar_corr.ax.tick_params(labelsize=9)

    if annotate:
        for i in range(n):
            for j in range(n):
                val = corr_matrix[i, j]
                if abs(val) >= annotate_threshold:
                    text_color = "white" if abs(val) > 0.7 else "black"
                    ax_corr.text(
                        j, i, f"{val:.2f}",
                        ha="center", va="center",
                        fontsize=5, color=text_color,
                    )

    _format_axes(ax_corr, label_name)

    # ── Title on both panels ─────────────────────────────────────────────────
    if title_line1:
        color = _title_color(title_line1)
        for ax in (ax_cov, ax_corr):
            ax.set_title(
                title_line1,
                fontsize=10,
                color=color,
                loc="left",
                pad=6,
            )

    return (fig_cov, ax_cov), (fig_corr, ax_corr)