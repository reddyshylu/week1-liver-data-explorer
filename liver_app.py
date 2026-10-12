"""Beginner-friendly local liver dataset explorer."""
from pathlib import Path
import plotly.express as px
import streamlit as st
from liver_data import NUMERIC, read_liver, missing_data_review, missing_review_workbook

DATA = Path(__file__).parent / 'data' / 'hcvdat0.csv'
LABELS = {
    'Age': 'Age (years)', 'ALB': 'Albumin (ALB)', 'ALP': 'Alkaline phosphatase (ALP)',
    'ALT': 'Alanine aminotransferase (ALT)', 'AST': 'Aspartate aminotransferase (AST)',
    'BIL': 'Bilirubin (BIL)', 'CHE': 'Cholinesterase (CHE)', 'CHOL': 'Cholesterol (CHOL)',
    'CREA': 'Creatinine (CREA)', 'GGT': 'Gamma-glutamyl transferase (GGT)', 'PROT': 'Protein (PROT)',
}
def distribution_chart(data, measurement, title, bins):
    """Use consistent, readable styling for frequency distributions."""
    chart = px.histogram(data, x=measurement, nbins=bins, labels=LABELS,
                         title=title, color_discrete_sequence=['#2563EB'],
                         template='plotly_white')
    chart.update_traces(marker_line_color='white', marker_line_width=1,
                        hovertemplate=LABELS[measurement] + ' range: %{x}<br>Records: %{y}<extra></extra>')
    chart.update_layout(height=380, bargap=0.06, showlegend=False,
                        margin=dict(l=20, r=20, t=60, b=50),
                        title=dict(x=0, font=dict(size=20)),
                        xaxis_title=LABELS[measurement], yaxis_title='Number of records',
                        font=dict(size=14), hovermode='closest')
    chart.update_xaxes(showgrid=False, zeroline=False)
    chart.update_yaxes(rangemode='tozero', dtick=1 if len(data) < 20 else None,
                       gridcolor='#E5E7EB', zeroline=False)
    return chart


st.set_page_config(page_title='Liver Data Explorer', layout='wide')
st.title('Liver Data Explorer')
st.write('Explore the records, understand distributions, and compare groups one measurement at a time.')
st.caption('Descriptive exploration only. Laboratory units and reference ranges are not supplied in the CSV.')
preview, overview, compare = st.tabs(['Upload & Preview', 'Dataset Overview', 'Compare Groups'])
with preview:
    st.header('Start with your data')
    uploaded = st.file_uploader('Upload a liver dataset CSV', type=['csv'])
    st.caption('Leave this empty to use data/hcvdat0.csv. Uploaded data replaces the bundled dataset in every tab.')
    st.download_button('Download liver CSV template', DATA.read_bytes(), 'hcvdat0.csv', 'text/csv')
    try:
        frame = read_liver(uploaded if uploaded is not None else DATA)
    except ValueError as error:
        st.error(str(error))
        st.stop()
    st.success(f'Loaded {len(frame):,} records from {uploaded.name if uploaded is not None else "hcvdat0.csv"}.')
    st.dataframe(frame.head(50), hide_index=True, width='stretch')
    st.caption('Preview shows the first 50 records. The unnamed row ID is excluded from analysis.')
    with st.expander('What do the columns mean?'):
        st.write('Category is the supplied group label; Sex is the recorded sex. Age is in years.')
        st.dataframe([{'Column': key, 'Description': value} for key, value in LABELS.items()], hide_index=True)
    st.subheader('Missing measurements')
    missing = frame[NUMERIC].isna().sum().rename('Missing values').to_frame()
    st.dataframe(missing, width='stretch')
    st.plotly_chart(px.bar(missing.reset_index(names='Measurement'),
                           x='Missing values', y='Measurement', orientation='h',
                           title='Missing measurements in the full dataset',
                           text='Missing values'), width='stretch')
    st.caption('Missing values are preserved. Each chart excludes only records missing its selected measurement.')
    st.subheader('Missing Data Review')
    st.caption('Checks the full loaded dataset, independently of sidebar filters. Blanks, whitespace, NA, N/A, and null are missing; zero is valid.')
    review_columns = st.multiselect('Columns to check for missing data',
                                    list(frame.attrs.get('source_records', frame.to_dict('list'))),
                                    default=['ALT', 'AST'])
    if review_columns:
        records, review_summary = missing_data_review(frame, review_columns)
        st.dataframe(review_summary, hide_index=True, width='stretch',
                     column_config={'Missing percentage': st.column_config.NumberColumn(format='percent')})
        st.write(f'Records missing at least one selected value: {len(records):,} of {len(frame):,}')
        st.dataframe(records, hide_index=True, width='stretch')
        st.caption('Each affected record appears once. CSV row number starts at 2 after the header (record order, not physical lines for multiline fields). Original IDs and extra columns are retained.')
        st.download_button('Download Missing Data Review (Excel)',
                           missing_review_workbook(records, review_summary),
                           'missing_data_review.xlsx',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        st.info('Select one or more columns to create the missing-data review.')

with st.sidebar:
    st.header('Explore a subset')
    categories = sorted(frame['Category'].unique())
    sexes = sorted(frame['Sex'].unique())
    selected_categories = st.multiselect('Categories', categories, default=categories)
    selected_sexes = st.multiselect('Sex', sexes, default=sexes)
    known_ages = frame['Age'].dropna()
    age_mask = frame['Age'].notna()
    if not known_ages.empty:
        minimum_age, maximum_age = float(known_ages.min()), float(known_ages.max())
        if minimum_age < maximum_age:
            age_range = st.slider('Age range (years)', min_value=minimum_age,
                                  max_value=maximum_age, value=(minimum_age, maximum_age), step=1.0)
            age_mask = frame['Age'].between(*age_range)
            st.caption('Both ends of the age range are included.')
        else:
            st.caption(f'All recorded ages are {minimum_age:g} years.')
    if frame['Age'].isna().any():
        include_missing_age = st.checkbox('Include records with missing age', value=True)
        if include_missing_age:
            age_mask = age_mask | frame['Age'].isna()
filtered = frame[frame['Category'].isin(selected_categories) & frame['Sex'].isin(selected_sexes) & age_mask]
st.sidebar.caption(f'{len(filtered):,} of {len(frame):,} records selected. Filters apply to Overview and Compare Groups.')
st.sidebar.download_button('Download filtered records as CSV',
                           filtered.to_csv(index=False).encode('utf-8'),
                           'filtered_liver_records.csv', 'text/csv', disabled=filtered.empty)
if filtered.empty:
    st.sidebar.caption('No records match. Adjust the filters to enable download.')

with overview:
    st.header('Understand the dataset')
    if filtered.empty:
        st.info('No records match. Adjust the category, sex, or age filters in the sidebar.')
    else:
        a, b, c = st.columns(3)
        a.metric('Records', len(filtered))
        ages = filtered['Age'].dropna()
        b.metric('Age range', f'{ages.min():g}–{ages.max():g}' if not ages.empty else 'Unavailable')
        c.metric('Missing numeric values', int(filtered[NUMERIC].isna().sum().sum()))
        st.caption(f'{int(filtered[NUMERIC].isna().any(axis=1).sum()):,} selected records have at least one missing measurement. Records remain available for other charts.')
        with st.expander('Missing-value counts in the selected subset'):
            st.dataframe(filtered[NUMERIC].isna().sum().rename('Missing values').to_frame(), width='stretch')
        counts = filtered.groupby('Category').size().reset_index(name='Records')
        st.plotly_chart(px.bar(counts, x='Category', y='Records', title='Records by category', text='Records'), width='stretch')
        st.caption('Bar height shows group size. Unequal group sizes matter when interpreting comparisons.')
        st.plotly_chart(distribution_chart(filtered.dropna(subset=['Age']), 'Age',
                                           'Age distribution', 15), width='stretch')
        st.caption(f'A histogram counts records within ranges. Age missing for {filtered["Age"].isna().sum()} selected records.')
        measurement = st.selectbox('Explore a laboratory measurement', NUMERIC[1:], format_func=lambda name: LABELS[name])
        values = filtered.dropna(subset=[measurement])
        if values.empty:
            st.info('No recorded values for this measurement in the selected subset.')
        else:
            st.plotly_chart(distribution_chart(values, measurement,
                                               f'Distribution of {LABELS[measurement]}', 25), width='stretch')
        st.caption(f'{len(values)} usable records; {len(filtered) - len(values)} missing values excluded. Wide ranges can reflect extreme observations.')

with compare:
    st.header('Compare groups')
    measurement = st.selectbox('Measurement', NUMERIC, index=3, format_func=lambda name: LABELS[name])
    grouping = st.radio('Group by', ['Category', 'Sex'], horizontal=True)
    points = st.checkbox('Show individual records', value=False)
    logarithmic = st.checkbox('Use a logarithmic vertical axis', value=False)
    values = filtered.dropna(subset=[measurement])
    if values.empty:
        st.info('No usable records. Adjust the filters or choose another measurement.')
    else:
        use_log = logarithmic and values[measurement].gt(0).all()
        if logarithmic and not use_log:
            st.info('A logarithmic axis requires positive values. Showing the ordinary scale.')
        st.plotly_chart(px.box(values, x=grouping, y=measurement, points='all' if points else False,
                              log_y=use_log, labels=LABELS, title=f'{LABELS[measurement]} by {grouping.lower()}'), width='stretch')
        st.caption('The middle line is the median. The box contains the middle 50% of values; whiskers show spread. Points beyond whiskers may be extreme observations.')
        summary = values.groupby(grouping)[measurement].agg(Count='count', Median='median', Q1=lambda x: x.quantile(.25), Q3=lambda x: x.quantile(.75))
        st.dataframe(summary.round(2), width='stretch')
        st.caption(f'{len(values)} usable records; {len(filtered) - len(values)} missing values excluded. Small groups have less stable summaries. Differences describe this dataset and do not establish causes.')
    if st.checkbox('Show ALT versus AST relationship', value=False):
        paired = filtered.dropna(subset=['ALT', 'AST'])
        if paired.empty:
            st.info('No records have both ALT and AST in the selected subset. Adjust the filters.')
        else:
            st.plotly_chart(px.scatter(paired, x='ALT', y='AST', color='Category',
                                      labels=LABELS, title='ALT versus AST by category',
                                      hover_data=['Age', 'Sex']), width='stretch')
            st.caption(f'{len(paired):,} usable records; {len(filtered) - len(paired):,} missing ALT or AST excluded. Each point is one record; association does not establish causation.')
