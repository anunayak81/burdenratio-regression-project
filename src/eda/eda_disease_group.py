import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_disease_group_eda(df, save_path=None):
    """
    Generate a 3-panel disease-group EDA figure from a pre-cleaned DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataframe containing columns:
        'data_year', 'disease_group', 'sex', 'age_group', 'total_yld', 'total_daly'
    save_path : str or Path, optional
        If provided, saves the figure to this path (e.g. '../outputs/eda_disease_group.png').
        If None, the figure is shown interactively.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    label_map = {
        'Mental and substance use disorders':  'Mental & substance use',
        'Cancer and other neoplasms':          'Cancer & neoplasms',
        'Reproductive and maternal conditions':'Reproductive & maternal',
        'Blood and metabolic disorders':       'Blood & metabolic',
        'Infant and congenital conditions':    'Infant & congenital',
        'Hearing and vision disorders':        'Hearing & vision',
        'Injury (external cause)':             'Injury (external)',
        'Kidney and urinary diseases':         'Kidney & urinary',
        'Gastrointestinal disorders':          'Gastrointestinal',
        'Cardiovascular diseases':             'Cardiovascular',
        'Neurological conditions':             'Neurological',
        'Musculoskeletal disorders':           'Musculoskeletal',
        'Respiratory diseases':                'Respiratory',
        'Endocrine disorders':                 'Endocrine',
        'Infectious diseases':                 'Infectious',
        'Skin disorders':                      'Skin',
        'Oral disorders':                      'Oral',
    }

    # ── dfregate to disease-group level ────────────────────────
    df['group_short'] =df['disease_group'].map(label_map).fillna(df['disease_group'])
    # ── Sort disease groups by median burden ratio ───────────────
    group_order = (df.groupby('disease_group')['burden_ratio']
                   .median()
                   .sort_values()
                   .index.tolist())
    short_order = [label_map.get(g, g) for g in group_order]

    medians = df.groupby('group_short')['burden_ratio'].median()
    palette = {g: '#C0392B' if medians[g] < 0.5 else '#1D9E75' for g in short_order}

    # ── Figure layout: 3 panels ─────────────────────────────────
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor('white')
    gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.32,
                          left=0.07, right=0.97, top=0.91, bottom=0.06)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    fig.suptitle(
        'Burden Ratio by Disease Group — Evidence Supporting H1 and H2\n'
        'Disease group structures the target (H1); within-group variance '
        'justifies nonlinear modelling (H2)',
        fontsize=13, fontweight='bold', y=0.97
    )

    # ── Panel 1: Box plot ────────────────────────────────────────
    bp_data = [df[df['group_short'] == g]['burden_ratio'].values for g in short_order]
    colors   = [palette[g] for g in short_order]

    bp = ax1.boxplot(
        bp_data, vert=False, patch_artist=True,
        medianprops={'color': 'white', 'linewidth': 2.5},
        whiskerprops={'linewidth': 1.2, 'color': '#444444'},
        capprops={'linewidth': 1.5, 'color': '#444444'},
        flierprops={'marker': 'o', 'markersize': 3, 'alpha': 0.4,
                    'markerfacecolor': '#888888', 'markeredgecolor': 'none'},
        widths=0.6
    )
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.82)

    ax1.set_yticklabels(short_order, fontsize=10)
    ax1.set_xlabel('Burden Ratio (YLD / DALY)', fontsize=11)
    ax1.set_title('Panel 1 — Burden ratio distribution by disease group  '
                  '(sorted low → high median)',
                  fontsize=11, fontweight='bold', pad=8)
    ax1.set_xlim(-0.05, 1.15)
    ax1.axvline(0.5, color='#555555', linestyle='--', linewidth=1, alpha=0.6)
    ax1.set_facecolor('#f8f9fa')
    ax1.grid(axis='x', alpha=0.35)

    for i, g in enumerate(short_order):
        med = medians[g]
        ax1.text(med + 0.02, i + 1, f'{med:.2f}',
                 va='center', fontsize=8.5, color='#222222', fontweight='bold')

    ax1.axvspan(-0.05, 0.5,  alpha=0.04, color='#C0392B')
    ax1.axvspan(0.5,   1.15, alpha=0.04, color='#1D9E75')
    ax1.text(0.13, 17.7, 'Life insurance zone\n(fatal burden dominant)',
             fontsize=8, color='#C0392B', ha='center', style='italic')
    ax1.text(0.82, 17.7, 'Income protection zone\n(chronic burden dominant)',
             fontsize=8, color='#1D9E75', ha='center', style='italic')

    legend_patches = [
        mpatches.Patch(color='#C0392B', alpha=0.8, label='Fatal-dominant (median < 0.50)'),
        mpatches.Patch(color='#1D9E75', alpha=0.8, label='Chronic-dominant (median ≥ 0.50)'),
    ]
    ax1.legend(handles=legend_patches, loc='lower right', fontsize=9, framealpha=0.85)

    # ── Panel 2: Data-driven top 5 by absolute change ───────────
    # dfregate to national level (collapse sex & age) for trend comparison
    national = (df.groupby(['data_year', 'disease_group'])
                   .agg(total_yld=('total_yld', 'sum'), total_daly=('total_daly', 'sum'))
                   .reset_index())
    national['burden_ratio'] = national['total_yld'] / national['total_daly']

    years = sorted(national['data_year'].unique())
    year_min, year_max = years[0], years[-1]

    pivot = national[national['data_year'].isin([year_min, year_max])].pivot(
        index='disease_group', columns='data_year', values='burden_ratio')
    pivot.columns = ['ratio_first', 'ratio_last']
    pivot['abs_change'] = (pivot['ratio_last'] - pivot['ratio_first']).abs()
    pivot['net_change'] =  pivot['ratio_last'] - pivot['ratio_first']

    top5_groups = pivot.nlargest(5, 'abs_change').index.tolist()
    top5_short  = [label_map.get(g, g) for g in top5_groups]
    focus_colors = ['#1D9E75' if pivot.loc[g, 'net_change'] > 0 else '#D85A30'
                    for g in top5_groups]
    line_styles  = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]

    for group, short, color, ls in zip(top5_groups, top5_short, focus_colors, line_styles):
        trend = national[national['disease_group'] == group].sort_values('data_year')
        chg   = pivot.loc[group, 'net_change']
        ax2.plot(trend['data_year'], trend['burden_ratio'],
                 marker='o', linestyle=ls, color=color, linewidth=2.2, markersize=6,
                 label=f"{short}  ({chg:+.3f})")

        last_val = trend[trend['data_year'] == year_max]['burden_ratio'].values
        if len(last_val):
            ax2.annotate(
                f"{chg:+.3f}",
                xy=(year_max, last_val[0]),
                xytext=(9, 0), textcoords='offset points',
                fontsize=8.5, color=color, va='center', fontweight='bold'
            )

    ax2.set_title(
        f'Panel 2 — Top 5 disease groups by absolute\n'
        f'burden ratio change, {year_min} \u2192 {year_max}  (data-driven selection)',
        fontsize=11, fontweight='bold'
    )
    ax2.set_xlabel('Year', fontsize=10)
    ax2.set_ylabel('Burden Ratio (YLD / DALY)', fontsize=10)
    ax2.set_xticks(years)
    ax2.set_facecolor('#f8f9fa')
    ax2.grid(alpha=0.35)
    ax2.set_ylim(0, 1.05)
    ax2.set_xlim(year_min - 3, year_max + 3)
    ax2.axhline(0.5, color='#555555', linestyle='--', linewidth=0.8, alpha=0.5)

    rising_patch   = mpatches.Patch(color='#1D9E75', label='Rising chronic burden')
    declining_patch = mpatches.Patch(color='#D85A30', label='Declining chronic burden')
    ax2.legend(
        handles=[rising_patch, declining_patch] + [
            plt.Line2D([0], [0], color=c, lw=2, linestyle=ls,
                       label=f"{s}  ({pivot.loc[g, 'net_change']:+.3f})")
            for g, s, c, ls in zip(top5_groups, top5_short, focus_colors, line_styles)
        ],
        fontsize=7.8, loc='upper left', framealpha=0.88,
        title='Group  (net change)', title_fontsize=7.8
    )

    # ── Panel 3: Within-group variance ──────────────────────────
    std_vals = df.groupby('group_short')['burden_ratio'].std().reindex(short_order)
    bar_colors = [palette[g] for g in short_order]
    bars = ax3.barh(short_order, std_vals.values, color=bar_colors, alpha=0.8)
    ax3.set_title('Panel 3 — Within-group std deviation of burden ratio\n'
                  'High variance \u2192 linear model will underfit \u2192 supports H2',
                  fontsize=11, fontweight='bold')
    ax3.set_xlabel('Standard Deviation of Burden Ratio', fontsize=10)
    ax3.set_facecolor('#f8f9fa')
    ax3.grid(axis='x', alpha=0.35)

    for bar, val in zip(bars, std_vals.values):
        if not np.isnan(val):
            ax3.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                     f'{val:.3f}', va='center', fontsize=8.5)

    ax3.axvline(0.10, color='#D85A30', linestyle='--', linewidth=1,
                alpha=0.7, label='0.10 threshold')
    ax3.legend(fontsize=8.5, framealpha=0.85)

    # ── Save or show ─────────────────────────────────────────────
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")

    return fig
