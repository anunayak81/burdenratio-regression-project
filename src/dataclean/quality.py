def identify_quality_issues(df):
    """Comprehensive data quality assessment.

    Checks for invalid years, sex values, age groups, negative YLL/DALY,
    and YLL > DALY.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned and filtered disease burden dataframe.

    Returns
    -------
    dict
        Mapping of issue name to count of affected rows.
    """
    issues = {}

    if 'data_year' in df.columns:
        invalid_years = df[~df['data_year'].between(2003, 2024)]
        issues['invalid_data_year'] = len(invalid_years)

    invalid_sex = df[~df['sex'].isin(['Males', 'Females'])]
    print(f"Invalid sex values: {len(invalid_sex)}")

    valid_age_groups = [
        '0', '1\u20134', '5\u20139', '10\u201314', '15\u201319', '20\u201324',
        '25\u201329', '30\u201334', '35\u201339', '40\u201344', '45\u201349',
        '50\u201354', '55\u201359', '60\u201364', '65\u201369', '70\u201374',
        '75\u201379', '80\u201384', '85\u201389', '90\u201394', '95\u201399', '100+'
    ]
    if 'age_group' in df.columns:
        invalid_ages = df[~df['age_group'].astype(str).isin(valid_age_groups)]
        issues['invalid_age_group'] = len(invalid_ages)

    if 'yld' in df.columns:
        issues['negative_YLD'] = len(df[df['yld'] < 0])
    if 'daly' in df.columns:
        issues['negative_DALY'] = len(df[df['daly'] < 0])
    if 'yld' in df.columns and 'daly' in df.columns:
        issues['YLD_greater_than_DALY'] = len(df[df['yld'] > df['daly']])

    return issues
