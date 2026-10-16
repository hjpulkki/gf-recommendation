import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection


def _m_value_line(p_amb, a, b, gf=1.0):
    """Bühlmann M-value adjusted by a constant or pressure-dependent GF."""
    m_raw = a + p_amb / b
    return p_amb + np.asarray(gf) * (m_raw - p_amb)


def plot_compartment_pressures(diveplan, first_stop, compartments=None, title_suffix=""):
    """
    4x4 Buhlmann pressure diagram for all 16 tissue compartments.

    Each subplot plots tissue pressure (y) against ambient pressure (x)
    as a trajectory that evolves over dive time.  Reference lines show
    the M-value at GF=1.0, GF Low, and GF High.

    Coefficients (a, b) are read from diveplan.modelUsed[i].NitrogenA / .NitrogenB.
    Gradient factors are read from diveplan.GFlow / diveplan.GFhigh.

    Parameters
    ----------
    diveplan : DivePlan
        A DivePlan that has been run through calculatePlan() so that
        diveplan.compartmentDF, diveplan.modelUsed, diveplan.GFlow,
        and diveplan.GFhigh are populated.
    compartments : list of int or None
        Compartment numbers to plot (1-16).  None plots all 16 in a 4x4 grid.
        When a subset is given the grid is sized automatically.
    title_suffix : str
        Extra text for the figure title.
    """
    df = diveplan.compartmentDF.copy()
    modelUsed = diveplan.modelUsed
    GFlow = diveplan.GFlow
    GFhigh = diveplan.GFhigh

    all_comps = sorted(df['compartment_number'].unique())
    if compartments is not None:
        all_comps = [c for c in all_comps if c in compartments]
    n_comps = len(all_comps)
    ncols = nrows = int(np.ceil(np.sqrt(n_comps)))

    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 22),
                             sharex=True, sharey=True)
    axes = axes.flatten()

    # Global pressure range for the reference lines
    p_lo = df['ambient_pressure_bar'].min() * 0.9
    p_hi = df['ambient_pressure_bar'].max() * 1.05
    p_range = np.linspace(p_lo, p_hi, 200)

    for idx, comp_num in enumerate(all_comps):
        ax = axes[idx]
        cdf = df[df['compartment_number'] == comp_num].sort_values('runtime_s')
        halftime = cdf['n2_halftime_min'].iloc[0]

        p_amb  = cdf['ambient_pressure_bar'].values
        p_comp = cdf['compartment_pressure_bar'].values

        # Get Buhlmann a, b from the model coefficients
        coeff = modelUsed[comp_num - 1]
        a = coeff.NitrogenA
        b = coeff.NitrogenB

        # --- reference lines ---
        # Equilibrium: tissue pressure = ambient pressure
        # HARD CODED FOR JUST AIR
        ax.plot(p_range, p_range*0.79, color='#BDBDBD', linewidth=0.8,
                linestyle=':', label=r'$P_{tissue} = P_{gas}$')

        # Raw M-value line (GF = 1.0)
        ax.plot(p_range, _m_value_line(p_range, a, b, gf=1.0),
                color='#4CAF50', linewidth=1.2, linestyle='--',
                label=r'M-line (GF=1)  $a + P_{amb}/b$')
        
        p_surface = 1.0
        p_first_stop = first_stop/10+1 #hard coded
        
        p_points = np.array([p_surface, p_first_stop])
        gf_points = np.array([GFhigh, GFlow])
        
        t_points = _m_value_line(p_points, a, b, gf=gf_points)
        
        ax.plot(
            p_points, t_points,
            color='#9C27B0', linewidth=1.2, linestyle='-.',
            label=f'GF line ({GFlow:.0%}/{GFhigh:.0%})'
        )

        # --- tissue trajectory (colored by time: blue=start, red=end) ---
        points   = np.column_stack([p_amb, p_comp])
        segments = np.array([points[:-1], points[1:]]).transpose(1, 0, 2)
        t_norm   = np.linspace(0, 1, len(segments))
        lc = LineCollection(segments, cmap='coolwarm', linewidths=1.6)
        lc.set_array(t_norm)
        ax.add_collection(lc)

        # Start / end markers
        ax.plot(p_amb[0],  p_comp[0],  'o', color='#1565C0',
                markersize=4, zorder=5, label='Start')
        ax.plot(p_amb[-1], p_comp[-1], 's', color='#C62828',
                markersize=4, zorder=5, label='End')

        ax.set_title(f'TC {comp_num}  (t\u00bd={halftime:.0f} min)',
                     fontsize=9, fontweight='bold')
        ax.grid(True, alpha=0.25)
        ax.autoscale_view()

        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_box_aspect(1)  # Square plotting area

    # Hide unused subplots
    for idx in range(n_comps, len(axes)):
        axes[idx].set_visible(False)

    # Axis labels
    for ax in axes[nrows * ncols - ncols:]:
        ax.set_xlabel('Ambient pressure (bar)', fontsize=9)
    for row in range(nrows):
        axes[row * ncols].set_ylabel('Tissue pressure (bar)', fontsize=9)

    # Single legend from the first subplot
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=7,
               fontsize=9, frameon=True, bbox_to_anchor=(0.5, 0.98))

    suptitle = 'B\u00fchlmann ZHL-16C  \u2014  Compartment Pressure Diagram'
    if title_suffix:
        suptitle += f'  ({title_suffix})'
    fig.suptitle(suptitle, fontsize=14, fontweight='bold', y=1.0)

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    return fig
