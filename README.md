# Sales & Revenue Analysis

> [!TIP]
> **[Open the live dashboard on Render](https://waris-sales-revenue-analysis-klx0.onrender.com/)**

An interactive retail analytics dashboard built from 9,994 Tableau Sample Superstore sales lines covering 2014–2017. It tracks revenue, profit, margin, order volume, average order value, year-over-year growth, and discounts.

## Dashboard features

- Filter by year, region, state, category, sub-category, and customer segment.
- Explore monthly revenue and profit, seasonal trends, and regional performance.
- Rank products by revenue, profit, or largest loss.
- Review the regional revenue ANOVA and the relationship between discounts and profit margin.

## Run locally

Use Python 3.10 or later. Run these commands from the repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
bash build.sh
```

Open `dist/index.html` in your browser. The build downloads a pinned copy of the public Superstore sample and embeds the cleaned sales data and statistical results in the dashboard.

## Project files

| File | Purpose |
| --- | --- |
| `analysis.py` | Cleans sales data, runs the statistical tests, and generates the dashboard. |
| `dashboard.template.html` | Dashboard layout, filters, and visualizations. |
| `build.sh` | Generates the static site in `dist/`. |
| [Power BI setup](POWER_BI.md) | Data model, DAX measures, and report setup. |
| [Survey questionnaire](SURVEY.md) | Evaluation questions and scoring instructions. |

The survey analysis requires collected responses. The repository includes a blank response template.
