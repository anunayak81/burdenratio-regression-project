import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


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

_YOUNG_AGES   = ['1-4','5-9','10-14','15-19',
                 '20-24','25-29','30-34','35-39']
_WORKING_AGES = ['40-44','45-49','50-54','55-59',
                 '60-64','65-69']

SEX_COLORS = {'Females': '#1D9E75', 'Males': '#D85A30'}


def _age_band(ag):
    if ag in _YOUNG_AGES:   return 'Young (1-39)'
    if ag in _WORKING_AGES: return 'Working age (40-69)'
    return 'Older (70+)'


def plot_sex_analysis(df, save_path=None):
    """
    Generate a 3-panel sex-disdfregated EDA figure from a pre-cleaned DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned dataframe containing columns:
        'data_year', 'disease_group', 'sex', 'age_group', 'yld', 'daly'
    save_path : str or Path, optional
        If provided, saves the figure to this path.
        If None, the figure is shown interactively.

    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    # ── dfregate ────────────────────────────────────────────────
    df = df.copy()
    df['age_band'] = df['age_group'].apply(_age_band)

    df['group_short']  = df['disease_group'].map(_LABEL_MAP).fillna(df['disease_group'])

    # ── Figure layout ────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 18))
    fig.patch.set_facecolor('white')
    gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.32,
                          left=0.07, right=0.97, top=0.92, bottom=0.05)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    fig.suptitle(
        'Sex Differences in Burden Ratio \u2014 Disdfregated Analysis\n'
        'Females carry more chronic burden; males carry more fatal burden '
        '\u2014 but the gap is conditional on disease group, age, and time',
        fontsize=13, fontweight='bold', y=0.97
    )

    # ── Panel 1: Sex gap by disease group ───────────────────────
    gap_df = (df.groupby(['disease_group', 'group_short', 'sex'])['burden_ratio']
                 .median()
                 .reset_index()
                 .pivot(index=['disease_group', 'group_short'], columns='sex',
                        values='burden_ratio')
                 .reset_index())
    gap_df.columns.name = None
    gap_df['gap'] = gap_df['Females'] - gap_df['Males']
    gap_df = gap_df.sort_values('gap').reset_index(drop=True)

    y_pos   = np.arange(len(gap_df))
    bar_clr = ['#1D9E75' if g > 0 else '#D85A30' for g in gap_df['gap']]

    bars = ax1.barh(y_pos, gap_df['gap'], color=bar_clr, alpha=0.82, height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(gap_df['group_short'], fontsize=10)
    ax1.axvline(0, color='#333333', linewidth=1.2)
    ax1.set_xlabel('Burden Ratio Gap  (Female median \u2212 Male median)', fontsize=11)
    ax1.set_title(
        'Panel 1 \u2014 Sex gap in burden ratio by disease group\n'
        'Green = females more chronic  |  Red = males more chronic',
        fontsize=11, fontweight='bold', pad=8
    )
    ax1.set_facecolor('#f8f9fa')
    ax1.grid(axis='x', alpha=0.35)

    for bar, val in zip(bars, gap_df['gap']):
        xpos = val + 0.003 if val >= 0 else val - 0.003
        ha   = 'left' if val >= 0 else 'right'
        ax1.text(xpos, bar.get_y() + bar.get_height() / 2,
                 f'{val:+.3f}', va='center', ha=ha, fontsize=8.5, fontweight='bold')

    for i, row in gap_df.iterrows():
        ax1.scatter(row['Females'], i, color='#1D9E75', zorder=5, s=40, marker='D')
        ax1.scatter(row['Males'],   i, color='#D85A30', zorder=5, s=40, marker='D')

    legend_items = [
        mpatches.Patch(color='#1D9E75', alpha=0.82, label='Females more chronic (gap > 0)'),
        mpatches.Patch(color='#D85A30', alpha=0.82, label='Males more chronic (gap < 0)'),
        plt.Line2D([0],[0], marker='D', color='w', markerfacecolor='#1D9E75',
                   markersize=8, label='Female median'),
        plt.Line2D([0],[0], marker='D', color='w', markerfacecolor='#D85A30',
                   markersize=8, label='Male median'),
    ]
    ax1.legend(handles=legend_items, loc='lower right', fontsize=9, framealpha=0.88)

    # ── Panel 2: Sex gap over time ───────────────────────────────
    time_df = (df.groupby(['data_year', 'sex'])['burden_ratio']
                  .median()
                  .reset_index())

    for sex in ['Females', 'Males']:
        d = time_df[time_df['sex'] == sex]
        ax2.plot(d['data_year'], d['burden_ratio'],
                 'o-', color=SEX_COLORS[sex], label=sex,
                 linewidth=2.2, markersize=7)

    f_vals = time_df[time_df['sex'] == 'Females'].set_index('data_year')['burden_ratio']
    m_vals = time_df[time_df['sex'] == 'Males'].set_index('data_year')['burden_ratio']
    years  = sorted(f_vals.index)

    ax2.fill_between(years, [f_vals[y] for y in years], [m_vals[y] for y in years],
                     alpha=0.12, color='#7F77DD', label='Sex gap')

    for yr in years:
        gap_val = f_vals[yr] - m_vals[yr]
        mid     = (f_vals[yr] + m_vals[yr]) / 2
        ax2.text(yr, mid, f'{gap_val:+.3f}',
                 ha='center', va='center', fontsize=8,
                 color='#534AB7', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7, ec='none'))

    ax2.set_title(
        'Panel 2 \u2014 Median burden ratio by sex over time\n'
        'Is the sex gap narrowing or widening?',
        fontsize=11, fontweight='bold'
    )
    ax2.set_xlabel('Year', fontsize=10)
    ax2.set_ylabel('Median Burden Ratio', fontsize=10)
    ax2.set_xticks(years)
    ax2.legend(fontsize=9, framealpha=0.88)
    ax2.set_facecolor('#f8f9fa')
    ax2.grid(alpha=0.35)
    ax2.set_ylim(0.4, 1.05)
    ax2.set_xlim(years[0] - 3, years[-1] + 3)

    # ── Panel 3: Sex gap by age band ─────────────────────────────
    band_order = ['Young (1-39)', 'Working age (40-69)', 'Older (70+)']
    band_df    = (df.groupby(['age_band', 'sex'])['burden_ratio']
                     .median()
                     .reset_index())

    x     = np.arange(len(band_order))
    width = 0.35

    for i, sex in enumerate(['Females', 'Males']):
        vals = [band_df[(band_df['age_band'] == b) &
                        (band_df['sex'] == sex)]['burden_ratio'].values[0]
                for b in band_order]
        offset  = (i - 0.5) * width
        bars_p  = ax3.bar(x + offset, vals, width,
                          label=sex, color=SEX_COLORS[sex], alpha=0.82)
        for bar, val in zip(bars_p, vals):
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                     f'{val:.3f}', ha='center', va='bottom',
                     fontsize=9, fontweight='bold')

    for bi, band in enumerate(band_order):
        f_val = band_df[(band_df['age_band'] == band) &
                        (band_df['sex'] == 'Females')]['burden_ratio'].values[0]
        m_val = band_df[(band_df['age_band'] == band) &
                        (band_df['sex'] == 'Males')]['burden_ratio'].values[0]
        gap_v = f_val - m_val
        top   = max(f_val, m_val) + 0.05
        ax3.annotate(
            f'gap\n{gap_v:+.3f}',
            xy=(bi, top), ha='center', fontsize=8.5,
            color='#534AB7', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='#EEEDFE', alpha=0.85, ec='#534AB7')
        )

    ax3.set_xticks(x)
    ax3.set_xticklabels(band_order, fontsize=10)
    ax3.set_ylabel('Median Burden Ratio', fontsize=10)
    ax3.set_title(
        'Panel 3 \u2014 Sex gap by age band\n'
        'Where is the difference between sexes largest?',
        fontsize=11, fontweight='bold'
    )
    ax3.legend(fontsize=10, framealpha=0.88)
    ax3.set_facecolor('#f8f9fa')
    ax3.grid(axis='y', alpha=0.35)
    ax3.set_ylim(0, 1.15)

    # ── Save or show ─────────────────────────────────────────────
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {save_path}")

    return fig
