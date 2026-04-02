# BurdenRatio-Predictor: Chronic or Fatal? — Predicting Disease Burden Character from Australia's Population Health Data
Name : Anuradha Nayak
Challenge: Regression  
Impact Certificate: Applied Machine Learning  - Tomorrow University
Industry Focus: Healthcare & Insurance

---

## 1. Introduction
**Australia's disease burden** is shifting. Chronic and non-fatal conditions — mental health disorders, musculoskeletal disease, and obesity-linked illness — are claiming an increasingly large share of the population's healthy years, while the insurance products and risk models designed to respond to these trends remain anchored in historical patterns that no longer reflect the current epidemiological landscape. This misalignment between where disease burden is heading and what risk models anticipate has consequences for premium adequacy, product design, and the **long-term sustainability of health insurance systems**.

The **Australian Burden of Disease Study 2024 (ABDS 2024)**, published by the Australian Institute of Health and Welfare (AIHW), provides a uniquely structured lens through which to examine this shift. Covering 205 diseases and injuries across 17 disease groups, stratified by age, sex, and five reference years spanning 2003 to 2024, the dataset captures not only the magnitude of disease burden but its character — the proportion that is lived with versus died from. This character is operationalised here as the **burden ratio (Years Lived with Disability / Disability-Adjusted Life Years)**: a continuous measure bounded between 0 (burden is entirely attributable to premature mortality) and 1 (burden is entirely non-fatal and chronic). Conditions with a high burden ratio generate long-term disability and income protection exposure; those with a low ratio represent primarily life insurance and critical illness risk.

This project applies **supervised regression modelling** to predict the burden ratio across Australian disease-age-sex-year cohorts from demographic and disease classification features alone. By identifying which of these features drive the ratio — and by analysing how model prediction errors shift over time across all 17 disease groups — I aim to surface actionable insights for the Australian insurance industry, public health policymakers, and ESG reporting teams who need to understand where chronic disease risk is growing faster than existing models anticipate. 

The urgency is practical: if risk models cannot predict where chronic burden is heading, premiums will be mispriced and preventive programs will be underfunded — with consequences for both insurer solvency and population health outcomes. This **residual drift analysis** introduces a sustainability layer that treats systematic prediction error as a quantitative signal of structural change in chronic disease burden, directly supporting progress tracking against **UN SDG 3 (Good Health and Well-being), Target 3.4**. The project is framed throughout as **population-level pattern detection** rather than individual risk prediction, and all inferences must be interpreted accordingly.

---

## 2. Problem Statement & Hypotheses

- **What to predict**: The burden ratio (YLD / DALY) for each disease-age-sex-year cohort in Australia —  a continuous variable from 0.0 (burden is entirely fatal) to 1.0 (burden is entirely chronic/disability) — for each disease-age-sex-year cohort in Australia.
- **Why it matters**: Australian insurers face escalating claims complexity from chronic diseases, aging populations, and a mental health surge, but existing risk models rely on historical patterns that lag behind the actual trajectory of population health. A model that predicts the burden character of disease cohorts — and whose errors reveal where burden is growing beyond historical expectation — gives insurers and policymakers an evidence base to act before the trend reaches the claims book. If risk models cannot predict where chronic burden is heading, premiums will be mispriced and preventive programs will be underfunded.
- **How it supports positive change**: This project aligns with Tomorrow University's mission of data science for social good. It demonstrates that freely available, government-validated population health data can be transformed into actionable sustainability intelligence, supporting evidence-based insurance product innovation and SDG 3 progress tracking.  Regression models that detect where chronic burden is growing beyond demographic expectations give insurers, governments and ESG teams a quantifiable signal for SDG 3 progress — and a basis for preventive product design rather than reactive claims management.

**Important framing**: This project performs population-level predictive modelling and pattern detection. It does not predict individual health risk. All outputs describe disease-age-sex cohort behaviour, not individuals.

### Hypotheses

- **H1 — Prediction**: Disease category, age group, sex, and year can predict the YLD/DALY burden ratio with R² > 0.50, confirming that the chronic-versus-fatal character of disease burden is systematically structured by demographic and epidemiological classification — not random.
- **H2 — Model complexity**: Tree-based and boosting models will significantly outperform linear regression (by more than 0.20 R² points), because the relationship between disease burden character and its demographic drivers is nonlinear — particularly the interaction between age group and disease category, and the bimodal distribution of the target.
- **H3 — Residual drift (sustainability signal)**: When residual error (actual − predicted) is analysed across all 17 disease groups and five study years, certain disease groups will show a statistically significant positive trend in mean residual between 2003 and 2024 — indicating that their chronic burden is growing faster than demographic and disease classification patterns alone can predict. This systematic, disease-specific drift is interpreted as a structural signal of unmodelled burden growth. Mental health and musculoskeletal conditions are the a priori candidates based on ABDS 2024 trend data, but the analysis spans all disease groups and does not pre-select findings.

---

## 3. Target Variable

- **Burden Ratio (`burden_ratio`)** → `YLD / DALY` → continuous numeric variable in the range \[0.0, 1.0\]
- **Regression suitability**: The ratio is quantitative, continuous, and bounded — appropriate for regression. Its bimodal distribution (spike near 0 for fatal-dominant conditions; spike near 1 for chronic-dominant conditions) is the structural reason tree-based models are expected to outperform linear regression.
- **Insurance interpretation**:
  - `burden_ratio → 1.0`:  condition generates long-term disability claims → income protection and disability product exposure
  - `burden_ratio → 0.0`:  condition generates premature death claims → life insurance exposure

---

## 4. Features

The model uses only four groups of features, all drawn from the ABDS 2024 S1 dataset. No external data sources are required.
Features are restricted to demographic classification variables and time only. Burden-derived metrics (YLD, DALY, YLL, crude rates) are excluded as features to prevent mathematical leakage into the target.

| Feature | Type | Description | Why included |
|---|---|---|---|
| `disease_group` | Categorical (one-hot, 17 levels) | Major disease grouping (e.g., Mental and substance use disorders, Cardiovascular diseases) | Strongest structural predictor of burden character — disease category determines whether a condition tends to kill or to disable |
| `age_num` | Ordinal integer (0–20) | Age group encoded in order from 1–4 (0) to 100+ (20) | Age shapes the fatal/chronic split — chronic burden dominates working ages, fatal burden rises in oldest cohorts |
| `sex_bin` | Binary (0=Females, 1=Males) | Biological sex | Males carry higher fatal burden; females carry higher chronic burden, particularly for mental health and musculoskeletal conditions |
| `year_norm` | Continuous (0=2003, 1=2024) | Study year normalised to \[0,1\] | Captures secular trend — chronic burden ratio has been rising over 21 years, particularly for mental health |

**Deliberately excluded features** (and reasons):
- `crude_daly_rate`, `log_crude_daly_rate`: derived from DALY — the denominator of the target.
- `yll_fraction`, `crude_yll_rate`, `crude_yld_rate`: derived from YLL or YLD — components of the target.
- `disease` (individual condition name): 205 unique values with too many sparse cells; disease_group is the appropriate level of granularity.

---

## 5. Dataset Info

- **Dataset name**: *Australian Burden of Disease Study 2024 — National Disease Burden Data Tables*
- **Publisher**: Australian Institute of Health and Welfare (AIHW), Australian Government
- **Why chosen**: Government-validated, peer-reviewed, uses WHO-standardised DALY methodology. Freely available, annually updated, and directly aligned with insurance risk segmentation by disease, age, and sex. The dataset's aggregated nature — which made individual-level classification difficult — is well-suited to population-level regression, which is the appropriate framing for this sustainability analysis.
- **Format**: Excel (.xlsx), structured tabular format, multiple supplementary sheets
- **Sheet used**: S1 — Number (YLL, YLD, DALY) and crude rate by sex, year, and 5-year age groups
- **Raw size**: 70,794 rows × 12 columns
- **Clean size**: 31,733 rows after filtering aggregate rows (sex = 'Persons', age = 'Total'), rows where DALY = 0, and the integer age = 0 label
- **License**: Creative Commons Attribution 3.0 Australia (CC BY 3.0 AU)
- **Geographic coverage**: Australia (national estimates)
- **Temporal coverage**: 2003, 2011, 2015, 2018, 2024 (five snapshot years; 21-year span)
- **Disease coverage**: 205 diseases and injuries across 17 disease groups
- **Demographic coverage**: 21 five-year age groups (1–4 to 100+), male and female
- **Target variable**: `burden_ratio` = YLD / DALY (engineered; continuous, 0–1)
- **Source**: [AIHW ABDS 2024 Data Tables](https://www.aihw.gov.au/reports/burden-of-disease/australian-burden-of-disease-study-2024/contents/data)
- **Demographic stratification:** 21 age groups (1–4 to 100+) × 2 sexes × 205 diseases across 17 disease groups × 5 years
- **Ethical & legal considerations:** No personal or individually identifiable data is present. The dataset contains population-level aggregates only and is free from privacy risk at the point of use. Downstream application of model outputs for individual underwriting or risk scoring would require separate ethical review under the Privacy Act 1988 and the Disability Discrimination Act 1992. The open licence (CC BY 3.0 AU) permits academic and commercial reuse with attribution.
---

## 6. Data Quality Assessment

| Dimension | Assessment | Notes |
|---|---|---|
| **Accuracy** | High | Government-validated, WHO-standardised DALY methodology, peer-reviewed framework |
| **Completeness** | Good | 220 diseases, 20 risk factors, 21 age groups, both sexes — no missing values in core analysis columns after filtering |
| **Consistency** | High | Standardised column names, consistent age group labelling, same disease hierarchy across all years |
| **Timeliness** | Current | Projected estimates for 2024; 2003–2018 estimates revised for comparability |
| **Relevance** | Strong | Disease × age × sex × year structure directly maps to insurance underwriting and product segmentation dimensions |
| **Representativeness** | Moderate | National estimates only — no sub-national, socioeconomic, or remoteness stratification in ABDS 2024 (available in ABDS 2018) |

---

## 7. Limitations

- **Aggregated, population-level data**: Each row is a disease-age-sex-year cohort, not an individual. The model predicts cohort-level burden character. Applying these predictions to individuals would be an ecological fallacy and is explicitly out of scope.
- **Temporal sparsity**: Only five snapshot years (2003, 2011, 2015, 2018, 2024). Time trends are detectable but not granular. The residual drift analysis compares five points, not a continuous time series.
- **No socioeconomic stratification**: SEIFA quintile, remoteness, income, and education are not in ABDS 2024 national estimates. These are known predictors of disease burden character and represent the primary limitation for the sustainability framing.
- **No comorbidity data**: Each disease is modelled independently. The ABDS does not capture conditions that co-occur within individuals, which affects how insurers actually experience claims.
- **Projected 2024 estimates**: The 2024 figures are model-based projections using historical trend data, not fully observed values. This introduces some uncertainty in the most recent time point — which is also the most important for the residual drift test.
- **No direct healthcare cost linkage**: Burden in DALYs cannot be converted to claims costs without additional actuarial assumptions. The insurance product alignment claims in this project are directional, not quantitative.

---

## 8. Methodological Risks & Mitigations

Three risks were specifically identified in project review and are addressed explicitly:

**Risk 1 — Mathematical leakage in target construction**
YLD / DALY is a ratio derived from the dataset's own columns. Including YLL, YLD, DALY, or their rate equivalents as features would allow the model to reconstruct the target from its components.
*Mitigation*: Features are restricted to disease category, age, sex, and year only. No burden-derived columns are used as predictors.

**Risk 2 — Ecological inference**
Relationships modelled at cohort level may not hold at the individual level. Patterns observed in population-level data cannot be directly attributed to causal mechanisms at the individual level.
*Mitigation*: All findings are framed explicitly as population-level pattern detection. The phrase "individual risk prediction" is not used anywhere in this project.

**Risk 3 — Residual drift interpretation**
Labelling residual error as an "ESG signal" without statistical validation would be an unsupported leap.
*Mitigation*: The residual drift claim is formalised through three statistical tests: (1) one-sample t-test of mean residual per disease group per year; (2) linear regression of residual on year per disease group to detect significant slope; (3) demographic parity test comparing residual distribution across sex and age bands. The SDG 3 framing is made only after these tests are conducted and results are reported.

---

## 9. Stakeholders, Beneficiaries & Impact

**Stakeholders**:
- Actuaries and underwriters (risk pricing for income protection and life insurance)
- Insurance product development teams (evidence base for chronic disease product design)
- Preventive health and wellbeing teams (program targeting and ROI estimation)
- ESG and sustainability reporting teams (SDG 3 evidence and annual refresh capability)
- Regulators (APRA, OAIC — fairness oversight, algorithmic accountability)

**Beneficiaries**:
- Policyholders (better-aligned products, preventive programs targeting their demographic cohort)
- Public health policymakers and governments (quantified evidence of structural change in chronic burden)
- Researchers (a formalised framework for using model residuals as a health trajectory signal)
- People living with chronic conditions (earlier detection of underserved segments)
- Communities facing mental health and obesity burden (targeted preventive investment)

**Impact**:
- **Insurance product alignment**: identifies disease groups and age-sex cohorts where chronic burden is rising fastest, enabling evidence-based product innovation rather than reactive repricing.
- **Sustainability accountability**: formalised residual drift test provides a replicable, annually refreshable methodology for tracking whether Australia's SDG 3 progress is reflected in population health burden patterns.
- **Equity signal**: demographic parity checks on model error identify age and sex groups where the model systematically over- or underestimates chronic burden — a fairness baseline for any downstream application.
- **Preventive investment case:** Identifying disease groups with growing positive residuals provides an evidence base for calculating ROI on wellness programs.

---

## 10. Methodology Overview

The project follows a full supervised machine learning pipeline with a sustainability analysis layer:

1. **Data loading & cleaning**: Filter to individual-level sex (exclude 'Persons'), named age groups (exclude 'Total'), rows where DALY > 0.
2. **Feature engineering**: Construct `burden_ratio` (target), `age_num` (ordinal), `sex_bin` (binary), `year_norm` (continuous). No burden-derived features.
3. **EDA**: Explore target distribution (bimodality), burden ratio by disease group and age, temporal trends by sex, top diseases by total DALY, feature correlation matrix.
4. **Preprocessing**: One-hot encoding for `disease_group`, standard scaling for numeric features. 80/20 train-test split.
5. **Modelling — Tier 1 (Statistical)**: Linear Regression, Ridge (L2), Lasso (L1), Polynomial Regression (degree 2).
6. **Modelling — Tier 2 (Interpretable ML)**: Decision Tree, Random Forest, Support Vector Regressor.
7. **Modelling — Tier 3 (Boosting)**: Gradient Boosting, XGBoost, LightGBM.
8. **Evaluation**: R², RMSE, MAE on held-out test set; 5-fold cross-validation for Tier 1 and 2 models; residual plots; feature importance; SHAP values.
9. **Residual Drift Analysis (Sustainability Layer):**Applied across all 17 disease groups — findings are data-driven, not pre-selected:
   - *Temporal drift:* mean residual by disease group × year; one-sample t-test against zero per group per year
   - *Disease-specific drift:* linear regression of residual on year per disease group; slope coefficient and significance reported
   - *Demographic parity:* residual magnitude and direction by sex and age band; identifies systematic over- or underestimation
   - *Spotlight:* disease groups with the largest statistically significant positive slope are reported as the primary sustainability signal
10. **Ethical Reflection:** Demographic error parity check; ecological fallacy framing; regulatory compliance notes (Privacy Act 1988, Disability Discrimination Act 1992, APRA Prudential Standards).
11. **Communication:** Output plots covering EDA, model comparison, residuals, SHAP, drift analysis, and insurance product alignment matrix.

---

## 11. Repository Structure

```
BurdenRatio-ml-project/
│
├── data/
│   └── AIHW-BOD-40-ABDS-2024-national-disease-burden-data-tables.xlsx
│
├── notebooks/
│   └── abds_regression_notebook.py       # Full pipeline: EDA → modelling → sustainability
│
├── outputs/
│   ├── 01_eda.png
│   ├── 02_decision_tree.png
│   ├── 03_model_comparison.png
│   ├── 04_residuals.png
│   ├── 05_feature_importance.png
│   ├── 06_shap.png
│   ├── 07_sustainability_residual_drift.png
│   ├── 08_demographic_parity.png
│   └── 09_product_alignment.png
│
├── docs/
│   ├── project_overview.docx             # Full project write-up with placeholders
│   └── regression_problem_framing.docx   # Five-component problem framing document
│
└── README.md
```

---

## 12. Next Steps

- Update notebook to remove leaky features (`log_crude_daly_rate`, `yll_fraction`) and retrain all models on the clean four-feature set.
- Formalise residual drift tests: one-sample t-test per disease group per year; linear regression of residual on year.
- Add companion datasets: AIHW Health System Spending on Disease 2023–24 (cost per case) and NHS 2022 Risk Factor Prevalence (obesity, inactivity, smoking by age-sex).
- Complete placeholder sections in `project_overview.docx` with final model results and plots.
- Prepare stakeholder summary for insurance and public health audiences.

---

## 13. References

- Australian Institute of Health and Welfare (2024). *Australian Burden of Disease Study 2024*. AIHW, Australian Government. https://www.aihw.gov.au/reports/burden-of-disease/australian-burden-of-disease-study-2024
- AIHW (2025). *Health system spending on disease and injury in Australia 2023–24*. AIHW, Australian Government.
- AIHW (2022). *Health system spending per case of disease and for certain risk factors*. AIHW, Australian Government.
- United Nations (2015). *Sustainable Development Goal 3: Good Health and Well-being*. https://sdgs.un.org/goals/goal3
- Machireddy, J. (2025). 'Data Analytics in Health Insurance: Transforming Risk, Fraud, and Personalised Care'. *SSRN Electronic Journal*. https://doi.org/10.2139/ssrn.5159635
- Nwaimo, C., Lee, D. & Tran, J. (2024). 'Transforming healthcare with data analytics: predictive models for patient outcomes'. *GSC Online Press*.
- CALI (2025). Mental health claims data, TPD age 30s.
- TAL (2024). Mental health claims report.
- AIA Australia (2024). Mental health claims trends report.

---

## 14. Acknowledgements

Dataset published by the **Australian Institute of Health and Welfare (AIHW)**, Australian Government. Licensed under **Creative Commons Attribution 3.0 Australia (CC BY 3.0 AU)**.

Prepared as part of an academic project on data-driven sustainability and insurance innovation at Tomorrow University.

Professor feedback and methodological guidance acknowledged — particularly on target leakage risk, ecological inference framing, and the formalisation of residual drift as a sustainability signal.