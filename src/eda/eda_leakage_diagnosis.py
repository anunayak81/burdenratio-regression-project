import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


_AGE_ORDER = [
    '0','1-4','5-9','10-14','15-19','20-24','25-29',
    '30-34','35-39','40-44','45-49','50-54',
    '55-59','60-64','65-69','70-74','75-79',
    '80-84','85-89','90-94','95-99','100+'
]

_LABEL_MAP = {
    'Mental and substance use disorders':   'Mental & substance use',
    'Cancer and other neoplasms':           'Cancer & neoplasms',
    'Reproductive and maternal conditions': 'Reproductive & maternal',
    'Blood and metabolic disorders':        'Blood & metabolic',
    'Infant and congenital conditions':     'Infant & congenital',
    'Hearing and vision disorders':         'Hearing & vision',
    'Injury (external cause)':              'Injury (external)',
    'Kidney and urinary diseases':          'Kidney & urinary',
    'Gastrointestinal disorders':           'Gastrointestinal',
    'Cardiovascular diseases':              'Cardiovascular',
    'Neurological conditions':              'Neurological',
    'Musculoskeletal disorders':            'Musculoskeletal',
    'Respiratory diseases':                 'Respiratory',
    'Endocrine disorders':                  'Endocrine',
    'Infectious diseases':                  'Infectious',
    'Skin disorders':                       'Skin',
    'Oral disorders':                       'Oral',
}


def plot_leakage_diagnosis(df, save_path=None):
    """
    Generate a 3-panel leakage diagnosis EDA figure from a pre-cleaned DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataframe containing columns:
        'data_year', 'disease_group', 'sex', 'age_group',
        'yld', 'daly', 'yll', 'crude_daly_rate', 'crude_yld_rate', 'crude_yll_rate'
    save_path : str or Path, optional
        If provided, saves the figure to this path.
        If None, the figure is shown interactively.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    # ── Aggregate ────────────────────────────────────────────────
    agg = (df.groupby(['data_year', 'disease_group', 'sex', 'age_group'])
             .agg(total_yld=('yld', 'sum'),
                  total_daly=('daly', 'sum'),
                  total_yll=('yll', 'sum'),
                  crude_daly_rate=('crude_daly_rate', 'mean'),
                  crude_yld_rate=('crude_yld_rate', 'mean'),
                  crude_yll_rate=('crude_yll_rate', 'mean'))
             .reset_index())
    agg = agg[agg['total_daly'] > 0].copy()

    # Normalise age_group: convert en-dash (–) to hyphen and strip whitespace,
    # so the mapping works regardless of how the caller preprocessed the data.
    agg['age_group'] = (agg['age_group'].astype(str)
                                        .str.strip()
                                        .str.replace('–', '-', regex=False))

    year_min = agg['data_year'].min()
    year_max = agg['data_year'].max()

    agg['burden_ratio']   = agg['total_yld'] / agg['total_daly']
    agg['yll_fraction']   = agg['total_yll'] / agg['total_daly']
    agg['log_daly']       = np.log1p(agg['total_daly'])
    agg['log_yld']        = np.log1p(agg['total_yld'])
    agg['log_crude_daly'] = np.log1p(agg['crude_daly_rate'])
    agg['age_num']        = agg['age_group'].map(
                                {a: i for i, a in enumerate(_AGE_ORDER)})
    agg['sex_bin']        = (agg['sex'] == 'Males').astype(int)
    agg['year_norm']      = (agg['data_year'] - year_min) / max(year_max - year_min, 1)

    target = 'burden_ratio'

    # ── Feature groups ───────────────────────────────────────────
    leaky_cols = {
        'yll_fraction':   'yll_fraction\n(1 \u2212 burden_ratio)',
        'total_yll':      'total_yll\n(denominator part)',
        'total_yld':      'total_yld\n(direct component)',
        'crude_yll_rate': 'crude_yll_rate\n(rate from yll)',
        'log_yld':        'log_yld\n(transform of yld)',
        'log_daly':       'log_daly\n(transform of daly)',
        'total_daly':     'total_daly\n(denominator)',
        'crude_daly_rate':'crude_daly_rate\n(rate from daly)',
        'crude_yld_rate': 'crude_yld_rate\n(rate from yld)',
        'log_crude_daly': 'log_crude_daly\n(transform of rate)',
    }
    safe_cols = {
        'age_num':   'age_num\n(ordinal age)',
        'sex_bin':   'sex_bin\n(binary sex)',
        'year_norm': 'year_norm\n(normalised year)',
    }

    leaky_corrs = {c: agg[c].corr(agg[target]) for c in leaky_cols}
    safe_corrs  = {c: agg[c].corr(agg[target]) for c in safe_cols}

    # Eta squared for disease_group (categorical)
    grand_mean = agg[target].mean()
    ss_total   = ((agg[target] - grand_mean) ** 2).sum()
    ss_between = (agg.groupby('disease_group')
                     .apply(lambda g: len(g) * (g[target].mean() - grand_mean) ** 2)
                     .sum())
    eta_sq           = ss_between / ss_total
    eta_equivalent_r = np.sqrt(eta_sq)

    # ── Build sorted bar entries ─────────────────────────────────
    entries = []
    for col, label in leaky_cols.items():
        entries.append((label, leaky_corrs[col], '#D85A30', 'pearson', True))
    for col, label in safe_cols.items():
        entries.append((label, safe_corrs[col],  '#1D9E75', 'pearson', False))
    entries.append((
        'disease_group\n(\u03b7\u00b2 = {:.3f}, equiv r = {:.3f})'.format(
            eta_sq, eta_equivalent_r),
        eta_equivalent_r, '#185FA5', 'eta', False
    ))
    entries.sort(key=lambda x: abs(x[1]), reverse=True)

    labels   = [e[0] for e in entries]
    values   = [e[1] for e in entries]
    colors   = [e[2] for e in entries]
    is_leaky = [e[4] for e in entries]
    is_eta   = [e[3] == 'eta' for e in entries]

    # ── Figure layout ────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 17))
    fig.patch.set_facecolor('white')
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.35,
                          left=0.07, right=0.97, top=0.91, bottom=0.05)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    fig.suptitle(
        'Feature Leakage Diagnosis \u2014 Why Raw Burden Columns Must Be Excluded\n'
        'High correlation with the target signals mathematical overlap, '
        'not predictive power',
        fontsize=13, fontweight='bold', y=0.97
    )

    # ── Panel 1: Correlation bar chart ───────────────────────────
    bars = ax1.barh(range(len(labels)), values, color=colors, alpha=0.85, height=0.65)

    for bar, eta in zip(bars, is_eta):
        if eta:
            bar.set_hatch('///')
            bar.set_edgecolor('#0C447C')

    ax1.set_yticks(range(len(labels)))
    ax1.set_yticklabels(labels, fontsize=9.5)
    ax1.axvline(0,    color='#333333', linewidth=1.2)
    ax1.axvline( 0.5, color='#888888', linewidth=0.8, linestyle='--', alpha=0.5)
    ax1.axvline(-0.5, color='#888888', linewidth=0.8, linestyle='--', alpha=0.5)
    ax1.set_xlabel(
        'Pearson r  (numeric features)  |  '
        '\u221a\u03b7\u00b2 equivalent r  (categorical: disease_group)',
        fontsize=10
    )
    ax1.set_title(
        'Panel 1 \u2014 Association strength with burden_ratio for all candidate features\n'
        'Red = leaky (derived from YLD/DALY/YLL)  |  '
        'Green = safe demographic/time  |  '
        'Blue hatched = disease_group (\u03b7\u00b2)',
        fontsize=11, fontweight='bold', pad=8
    )
    ax1.set_facecolor('#f8f9fa')
    ax1.grid(axis='x', alpha=0.35)
    ax1.set_xlim(-1.15, 1.25)

    for bar, val, lk, eta in zip(bars, values, is_leaky, is_eta):
        xpos = val + 0.02 if val >= 0 else val - 0.02
        ha   = 'left' if val >= 0 else 'right'
        color_txt = '#185FA5' if eta else ('#D85A30' if lk else '#1D9E75')
        ax1.text(xpos, bar.get_y() + bar.get_height() / 2,
                 f'{val:+.3f}', va='center', ha=ha,
                 fontsize=9, fontweight='bold', color=color_txt)
        if lk and abs(val) > 0.5:
            ax1.text(1.17, bar.get_y() + bar.get_height() / 2,
                     'LEAKY', va='center', ha='center',
                     fontsize=7.5, color='white', fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.25', fc='#D85A30',
                               ec='none', alpha=0.9))
        if eta:
            ax1.text(1.17, bar.get_y() + bar.get_height() / 2,
                     'TOP\nFEATURE', va='center', ha='center',
                     fontsize=7, color='white', fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.25', fc='#185FA5',
                               ec='none', alpha=0.9))

    leaky_patch = mpatches.Patch(color='#D85A30', alpha=0.85,
        label='Leaky \u2014 derived from target components (EXCLUDE)')
    safe_patch  = mpatches.Patch(color='#1D9E75', alpha=0.85,
        label='Safe \u2014 demographic & time features (KEEP)')
    eta_patch   = mpatches.Patch(color='#185FA5', alpha=0.85, hatch='///',
        label=f'disease_group \u2014 categorical, \u03b7\u00b2 = {eta_sq:.3f}  (KEEP)')
    ax1.legend(handles=[eta_patch, safe_patch, leaky_patch],
               loc='lower right', fontsize=9.5, framealpha=0.92)

    # ── Panel 2: Scatter — yll_fraction mathematical inevitability ──
    sample = agg.sample(min(1500, len(agg)), random_state=42)
    ax2.scatter(sample['yll_fraction'], sample[target],
                alpha=0.25, s=12, color='#D85A30', rasterized=True)

    m, b   = np.polyfit(agg['yll_fraction'], agg[target], 1)
    x_ln   = np.linspace(0, 1, 100)
    r_ll   = agg['yll_fraction'].corr(agg[target])
    ax2.plot(x_ln, m * x_ln + b, color='#7F77DD', linewidth=2,
             label=f'r = {r_ll:.4f}')

    ax2.set_xlabel('yll_fraction  (YLL / DALY)', fontsize=10)
    ax2.set_ylabel('burden_ratio  (YLD / DALY)', fontsize=10)
    ax2.set_title(
        'Panel 2 \u2014 Leaky feature: yll_fraction vs burden_ratio\n'
        f'r = {r_ll:.4f} \u2014 mathematical certainty, not a learned relationship',
        fontsize=10, fontweight='bold'
    )
    ax2.legend(fontsize=10, framealpha=0.88)
    ax2.set_facecolor('#f8f9fa')
    ax2.grid(alpha=0.35)
    ax2.set_xlim(-0.05, 1.05)
    ax2.set_ylim(-0.05, 1.05)
    ax2.text(0.05, 0.08,
             'yll_fraction = 1 \u2212 burden_ratio\nby construction.\n'
             'Including this feature means\npredicting the target from itself.',
             fontsize=8.5, color='#D85A30', style='italic',
             bbox=dict(boxstyle='round,pad=0.4', fc='#FAECE7',
                       ec='#D85A30', alpha=0.9))

    # ── Panel 3: Box plot — disease_group vs burden_ratio ────────
    group_order_p3 = (agg.groupby('disease_group')[target]
                         .median().sort_values().index.tolist())
    bp_data   = [agg[agg['disease_group'] == g][target].values for g in group_order_p3]
    bp_labels = [_LABEL_MAP.get(g, g) for g in group_order_p3]
    medians_p3 = [np.median(d) for d in bp_data]
    bp_colors  = ['#1D9E75' if m >= 0.5 else '#D85A30' for m in medians_p3]

    bp = ax3.boxplot(bp_data, vert=False, patch_artist=True,
                     medianprops={'color': 'white', 'linewidth': 2},
                     whiskerprops={'linewidth': 1, 'color': '#555555'},
                     capprops={'linewidth': 1.2, 'color': '#555555'},
                     flierprops={'marker': 'o', 'markersize': 2.5,
                                 'alpha': 0.3, 'markerfacecolor': '#888888',
                                 'markeredgecolor': 'none'},
                     widths=0.6)
    for patch, col in zip(bp['boxes'], bp_colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.78)

    ax3.set_yticklabels(bp_labels, fontsize=9)
    ax3.set_xlabel('burden_ratio  (YLD / DALY)', fontsize=10)
    ax3.set_title(
        f'Panel 3 \u2014 disease_group vs burden_ratio  (\u03b7\u00b2 = {eta_sq:.3f})\n'
        f'Explains {eta_sq * 100:.1f}% of target variance \u2014 strongest predictor by far',
        fontsize=10, fontweight='bold'
    )
    ax3.set_facecolor('#f8f9fa')
    ax3.grid(axis='x', alpha=0.35)
    ax3.axvline(0.5, color='#555555', linestyle='--', linewidth=1, alpha=0.6)
    ax3.set_xlim(-0.05, 1.15)

    for i, (med, _) in enumerate(zip(medians_p3, bp_labels)):
        ax3.text(med + 0.02, i + 1, f'{med:.2f}',
                 va='center', fontsize=8, fontweight='bold', color='#222222')

    eta_patch2 = mpatches.Patch(color='#185FA5', alpha=0.8,
        label=f'\u03b7\u00b2 = {eta_sq:.3f}  \u2192  explains {eta_sq * 100:.1f}% of variance')
    ax3.legend(handles=[eta_patch2], loc='lower right', fontsize=9, framealpha=0.9)

    # ── Save or show ─────────────────────────────────────────────
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")

    # ── Print summary ─────────────────────────────────────────────
    print(f"disease_group: \u03b7\u00b2 = {eta_sq:.4f}  "
          f"(equivalent r = {eta_equivalent_r:.4f})  -- TOP FEATURE")
    print("\nLeaky features (EXCLUDE):")
    for col, label in leaky_cols.items():
        print(f"  {col:25s}  r = {leaky_corrs[col]:+.4f}")
    print("\nSafe features (KEEP):")
    for col, label in safe_cols.items():
        print(f"  {col:25s}  r = {safe_corrs[col]:+.4f}")    
    return fig
