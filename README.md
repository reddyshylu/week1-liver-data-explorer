# Liver Data Explorer

A Week 1 Path C project: a local Streamlit app using `data/hcvdat0.csv`, with Upload & Preview, Dataset Overview, and Compare Groups tabs. It explores tabular liver blood-test data and reviews missing measurements. It is not a biopsy-image model or a diagnostic tool.

Dataset: [UCI Machine Learning Repository HCV data](https://archive.ics.uci.edu/dataset/571/hcv+data), 615 records. The source file is a CSV, which can also be opened in Excel.

From this folder, create an environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run liver_app.py
```

Open the local URL shown in the terminal, usually `http://127.0.0.1:8501/`.

The bundled dataset loads automatically. Upload a CSV with Category, Sex, Age, ALB, ALP, ALT, AST, BIL, CHE, CHOL, CREA, GGT, and PROT columns to explore another compatible dataset. Download the bundled CSV from Upload & Preview as a template. The preview displays the first 50 records; charts use all records matching the sidebar filters.

Missing measurements remain missing. Charts report exclusions; group summaries use medians and quartiles. Category, sex, and age-range filters apply together to all Overview metrics and charts and to Compare Groups. Both age-range endpoints are included. If uploaded records have missing ages, a checkbox lets you include them (on by default). Datasets with only one known age or no known ages also work.

Use **Download filtered records as CSV** in the sidebar to save exactly the records selected by these filters. The export includes all measurements, preserves blanks, and uses the same readable category and sex labels as the app. Download is disabled when no records match; both analysis tabs explain how to adjust the filters. Upload & Preview continues to show the original loaded dataset.

Laboratory units and reference ranges are not included in the source CSV. This app describes the supplied data and does not diagnose conditions.

`liver_app.py` holds the interface; `liver_data.py` handles loading and validation. Existing shared dependencies are listed in `requirements.txt`.

## Missing Data Review

In **Upload & Preview**, scroll below **Missing measurements** to **Missing Data Review**. Choose one or more **Columns to check for missing data** (ALT and AST are selected initially). The summary shows each column's missing count and percentage of all loaded records. The affected-record count and table include each source record once, with a **Missing fields** list, even when multiple selected fields are missing. Sidebar filters and the 50-row preview limit do not restrict this report.

Click **Download Missing Data Review (Excel)** directly below that table to save **missing_data_review.xlsx**. **Records to Review** contains full source rows, including original IDs and extra columns, plus **CSV row number** and **Missing fields**. Row numbers start at 2 after the header and count CSV records rather than physical lines (quoted multiline fields occupy one record). **Summary** contains missing counts and numeric percentages for the selected columns. A report with no affected records still downloads with headers and zero counts. Clear the selection to see guidance to select columns.

Blank cells, whitespace-only cells, and case-insensitive NA, N/A, and null (including surrounding whitespace) are missing. Zero is valid. The source CSV is never edited; the review retains original source values and labels separately from the chart data.

For a quick test, use the bundled dataset and select ALT and AST: ALT has **1** missing value, AST has **0**, and **1** record needs review. Change sidebar filters and confirm the review stays the same. Download the workbook and check both sheets. Upload a compatible CSV with a row missing both ALT and AST to confirm that row appears once with **ALT, AST** under Missing fields.

The Excel export adds `openpyxl==3.1.5` (and its `et-xmlfile` dependency in the lock file). Install dependencies with `python -m pip install -r requirements.txt` in your working Python environment. Run liver checks with `python -m unittest discover -s tests -p "test_liver*.py"` and report checks with `python -m unittest discover -s tests -p "test_missing_review.py"`.
