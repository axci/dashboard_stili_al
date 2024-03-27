import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go


#######################
# Constants
BLUE = '#006BA2'
CYAN = '#3EBCD2'
GREEN = '#379A8B'
YELLOW = '#EBB434'
OLIVE = '#B4BA39'
PURPLE = '#9A607F'
RED = '#DB444B'
GOLD = '#D1B07C'
GREY =  '#758D99'
BLUE_LIGHT = '#98DAFF'
BLUE_DARK = '#00588D'
CYAN_LIGHT = '#6FE4FB'
CYAN_DARK = '#005F73'
GREEN_LIGHT = '#86E5D4'
GREEN_DARK = '#005F52'
YELLOW_LIGHT = '#FFCB4D'
YELLOW_DARK = '#714C00'
OLIVE_LIGHT = '#D7DB5A'
OLIVE_DARK = '#4C5900'
PURPLE_LIGHT = '#FFC2E3'
PURPLE_DARK = '#78405F'
RED_LIGHT = '#FFA39F'
RED_DARK = '#A81829'
GOLDLIGHT = '#F2CF9A'
GOLD_DARK = '#674E1F'




#######################
# Page configuration
st.set_page_config(
    page_title = "Stili alimentari",
    page_icon='🥑',
    layout='wide',
    initial_sidebar_state='expanded'
)

alt.themes.enable('dark')

#######################
# CSS styling



#######################
# Load Data
df = pd.read_csv('data/stili_al.csv')


#######################
# Utils

metrics_mapping = {
    'stile': ['stili alimentari','Stili alimentari'],
    'q4__4': ['Frequenza acquisto: pasticceria', 'Frequenza acquisto: pasticceria (torte pronte, muffin, crostate, ecc.)'],
    'q4__5': ['Frequenza acquisto: dolci', 'Frequenza acquisto: dolci da ricorrenza italiani (panettoni, pandori, colombe, ecc.)'],
    'q4__6': ['Frequenza acquisto: biscotti','Frequenza acquisto: biscotti'] ,
    'q4__7': ['Frequenza acquisto: merendine', 'Frequenza acquisto: merendine'],
    'q4__8': ['Frequenza acquisto: caffè', 'Frequenza acquisto: caffè'],
    'q4__9': ['Frequenza acquisto: tè e infusi', 'Frequenza acquisto: tè e infusi'],
    'q4__10': ['Frequenza acquisto: cioccolato', 'Frequenza acquisto: cioccolato, cioccolatini, praline'],
    'q5__4': ['Cambiamenti frequenza: pasticceria', 'Cambiamenti frequenza: pasticceria (torte pronte, muffin, crostate, ecc.)'],
    'q5__5': ['Cambiamenti frequenza: dolci', 'Cambiamenti frequenza: dolci da ricorrenza italiani (panettoni, pandori, colombe, ecc.'] ,
    'q5__6': ['Cambiamenti frequenza: biscotti', 'Cambiamenti frequenza: biscotti'],
    'q5__7': ['Cambiamenti frequenza: merendine', 'Cambiamenti frequenza: merendine'],
    'q5__8': ['Cambiamenti frequenza: caffè', 'Cambiamenti frequenza: caffè'],
    'q5__9': ['Cambiamenti frequenza: tè e infusi', 'Cambiamenti frequenza: tè e infusi'],
    'q5__10': ['Cambiamenti frequenza: cioccolato', 'Cambiamenti frequenza: cioccolato, cioccolatini, praline'],
}


#######################
# Sidebar
with st.sidebar:
    st.title('🥑 Stili alimentari')
    checkpoint_countries = []
    checkpoint_regions = []

    countries = ['All'] + list(df.country.unique())
    selected_country = st.selectbox('Select a country', countries)

    if selected_country == 'All':
        df_filtered = df
    else:
        df_filtered = df.query('country == @selected_country')

        # compare with another country
        countries_compare = [country for country in list(df.country.unique()) if country != selected_country]
        checkpoint_countries = st.multiselect('Compare:', countries_compare)
        if checkpoint_countries: # if there are selected countries to compare
            selected_countries = [selected_country] + checkpoint_countries
            df_filtered = df.query('country in @selected_countries')
            
        # region
        regions = ['All'] + list(df_filtered.regio.unique())
        selected_region = st.selectbox('Select a region', regions)
        if selected_region != 'All':
            df_filtered = df_filtered.query('regio == @selected_region')

            # compare with another country
            regions_compare = [region for region in list(df.regio.unique()) if region != selected_region]
            checkpoint_regions = st.multiselect('Compare:', regions_compare)
            if checkpoint_regions: # if there are selected regions to compare
                selected_regions = [selected_region] + checkpoint_regions
                df_filtered = df.query('regio in @selected_regions')        


    # gender
    genders = ['All'] + list(df.s3.unique())
    selected_gender = st.selectbox('Select a gender', genders)
    if selected_gender != 'All':
        df_filtered = df_filtered.query('s3 == @selected_gender')

    # age group
    ages = ['All'] + list(  np.sort(df.eta.unique() ))
    selected_age = st.selectbox('Select an age group', ages)
    if selected_age != 'All':
        df_filtered = df_filtered.query('eta == @selected_age')
    
    # s5
    s5_list = ['All'] + list(df.s5.unique())
    selected_s5 = st.selectbox('Chi si occupa degli acquisti alimentari?', s5_list)
    if selected_s5 != 'All':
        df_filtered = df_filtered.query('s5 == @selected_s5')
    
    # Metric to plot
    st.markdown("""<br><hr>""", unsafe_allow_html=True) # a gap br and a line (hr)
    metrics = ['stile', 'q4__4', 'q4__5', 'q4__6', 'q4__7', 'q4__8', 'q4__9', 'q4__10',
               'q5__4', 'q5__5', 'q5__6', 'q5__7', 'q5__8', 'q5__9', 'q5__10',
               ]
    
    user_friendly_names = [value[0] for value in metrics_mapping.values()]
    selected_metric_name = st.selectbox('📊 Select a metric', user_friendly_names)
    selected_metric = next(key for key, value in metrics_mapping.items() if value[0] == selected_metric_name)

    # Color theme
    st.markdown("""<br><hr>""", unsafe_allow_html=True) # a gap br and a line (hr)
    color_theme_list = ['blue', 'cyan', 'green', 'red', 'yellow', 'olive', 'purple', 'gold']
    selected_color_theme = st.selectbox('🎨 Select a color theme', color_theme_list)

    # number of observations
    n = len(df)
    n_sample = len(df_filtered)


#######################
# Grouping function
def group_df_all(df, metric: str) -> pd.Series:
    # group for a bar chart
    s = (df
            .groupby(metric)
            .count()
        ).country.sort_values()
    return s    


def group_df(df, metric: str, compare_by: str) -> pd.Series:
    # group for a bar chart
    s = (df
            .groupby([compare_by, metric])
            .country
            .count()
            #.sort_values()
        )
    return s

#######################
# Plots
def make_donut(input_color):
    if input_color == 'blue':
        chart_color = [BLUE_LIGHT, BLUE_DARK]
    if input_color == 'cyan':
        chart_color = [CYAN_LIGHT, CYAN_DARK]
    if input_color == 'green':
        chart_color = [GREEN_LIGHT, GREEN_DARK]
    if input_color == 'yellow':
        chart_color = [YELLOW_LIGHT, YELLOW_DARK]
    if input_color == 'red':
        chart_color = [RED_LIGHT, RED_DARK]
    if input_color == 'olive':
        chart_color = [OLIVE_LIGHT, OLIVE_DARK]
    if input_color == 'purple':
        chart_color = [PURPLE_LIGHT, PURPLE_DARK]
    if input_color == 'gold':
        chart_color = [GOLDLIGHT, GOLD_DARK]

    # Calculate percentage
    percentage = (n_sample / n) * 100
    remaining_percentage = 100 - percentage

    # Prepare the data for the donut chart
    data = pd.DataFrame({
        'Category': ['Sample', 'Remaining'],
        'Value': [percentage, remaining_percentage]
    })

    # Create a donut chart
    donut_chart = alt.Chart(data).mark_arc(innerRadius=30, radius=50).encode(
        theta=alt.Theta(field="Value", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(domain=['Sample', 'Remaining'], range=chart_color),legend=None),
        tooltip=["Category", "Value"]
    ).properties(width=130, height=130)

    # Create a text mark for displaying the percentage in the center
    text = alt.Chart(pd.DataFrame({"Value": [f"{percentage:.1f}%"]})).mark_text(size=20, baseline='middle').encode(
        text='Value:N'
    )

    # Layer the donut chart and the text mark
    chart = (donut_chart + text)
    
    return chart    

def make_bars_plotly_all(input_color, s: pd.Series, fixed_order_flag_freq=False, fixed_order_flag_camb=False, width=800, height=600):
    color_map = {
        'blue': BLUE,
        'cyan': CYAN,
        'green': GREEN,
        'yellow': YELLOW,
        'red': RED,
        'olive': OLIVE,
        'purple': PURPLE,
        'gold': GOLD
    }
    chart_color = color_map.get(input_color, 'blue')  # Default to blue if color not found
    # Fixed order for the bars
    if fixed_order_flag_freq:
        fixed_order = [
        'Tutti i giorni o quasi', '2-3 volte a settimana', '1 volta a settimana', 
        '2-3 volte al mese', '1 volta al mese', "4-5 volte all’anno", 
        'Più raramente', 'Mai'
        ][::-1]
        s = s.reindex(fixed_order)

    if fixed_order_flag_camb:
        fixed_order = [
            "Molto aumentato", "Un po’ aumentato", "Uguale",
            "Un po’ diminuito", "Molto diminuito"
        ][::-1]
        s = s.reindex(fixed_order)

    # Calculate percentages
    total = s.sum()
    percentages = (s / total * 100).round(1).astype(str) + '%'

    fig = go.Figure(go.Bar(
        x=s.values,
        y=s.index,
        orientation='h',
        marker=dict(color=chart_color),
        text=percentages,
        textposition='auto',
    ))

    # Update layout for a cleaner look
    fig.update_layout(
        #title=title,
        xaxis=dict(
            showticklabels=True,
            showgrid=True,
            tickangle=0,
            titlefont=dict(size=12),
            title_standoff=25
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            linecolor='black'
        ),
        plot_bgcolor='white',
        showlegend=False,
        width=width,
        height=height,
    )

    fig.update_yaxes(tickfont=dict(size=12), tickmode='array', tickvals=list(s.index))
    fig.update_xaxes(tickfont=dict(size=12))

    return fig

def make_bars_plotly(input_color, s: pd.Series, width=800, height=600):
    if len(s.index.levels[0]) == 2:
        height *= 1.1
    if len(s.index.levels[0]) == 3:
        height *= 1.3
    if len(s.index.levels[0]) > 3:
        height *= 1.5

    # sorting bars
    if s.index.levels[1].name in [f'q5__{i}' for i in range(4, 11)]:
        fixed_order = [
            "Molto aumentato", "Un po’ aumentato", "Uguale",
            "Un po’ diminuito", "Molto diminuito"
        ][::-1]
        new_categories = pd.Categorical(s.index.get_level_values(1), categories=fixed_order, ordered=True)

        # Rebuild the MultiIndex with the new categorical order for the second level
        s.index = pd.MultiIndex.from_arrays([s.index.get_level_values(0), new_categories], names=s.index.names)

        # Sort the Series based on the new index
        s = s.sort_index(level=1)
 
    if s.index.levels[1].name in [f'q4__{i}' for i in range(4, 11)]:
        fixed_order = [
        'Tutti i giorni o quasi', '2-3 volte a settimana', '1 volta a settimana', 
        '2-3 volte al mese', '1 volta al mese', "4-5 volte all’anno", 
        'Più raramente', 'Mai'
        ][::-1]

        new_categories = pd.Categorical(s.index.get_level_values(1), categories=fixed_order, ordered=True)

        # Rebuild the MultiIndex with the new categorical order for the second level
        s.index = pd.MultiIndex.from_arrays([s.index.get_level_values(0), new_categories], names=s.index.names)

        # Sort the Series based on the new index
        s = s.sort_index(level=1)

    color_map = {
        'blue': BLUE,
        'cyan': CYAN,
        'green': GREEN,
        'yellow': YELLOW,
        'red': RED,
        'olive': OLIVE,
        'purple': PURPLE,
        'gold': GOLD
    }
    chart_color = color_map.get(input_color, 'blue')  # Default to blue if color not found
    country_colors = {'Italia': OLIVE, 'Germania': YELLOW, 'Francia': BLUE, 'USA': RED }

    # colors
    colors = chart_color


    fig = go.Figure()

    for i, country in enumerate(s.index.levels[0]):
        country_data = s[country]
        country_total = country_data.sum()
        country_percentages = (country_data / country_total * 100).round(1)
        if s.index.levels[0].name == 'country':
            colors = country_colors[country]
        elif s.index.levels[0].name == 'regio':
            colors = list(color_map.values())[i]
        fig.add_trace(go.Bar(
            x=country_percentages.values,
            y=country_data.index,
            orientation='h',
            marker=dict(color=colors),
            text=country_percentages.apply(lambda x: f'{x}%'),
            textposition='auto',
            name=country  # If you want a legend indicating each country
        ))

    # Update layout for a cleaner look
    fig.update_layout(
        #title=title,
        xaxis=dict(
            showticklabels=True,
            showgrid=True,
            tickangle=0,
            titlefont=dict(size=12),
            title_standoff=25
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            linecolor='black'
        ),
        plot_bgcolor='white',
        showlegend=True,
        width=width,
        height=height,
    )

    return fig
        
#######################
# Dashboard Main Panel    
col = st.columns((1.5, 4.5, 0.5), gap='medium')

with col[0]:
    st.markdown('#### Observations')
    st.markdown(f'#### {n_sample:,}')
    st.markdown(f'####')

    st.markdown('#### % of Total Observations')
    st.altair_chart(make_donut(selected_color_theme))
    

with col[1]:
    st.markdown(f'#### {metrics_mapping[selected_metric][1].capitalize()}')
    #st.text(df_filtered)
    # create a series - value counts for a selected metric
    if selected_country == "All":
        metric_series = group_df_all(df_filtered, selected_metric)
        if selected_metric in [f'q4__{i}' for i in range(4, 11)]:
            fig = make_bars_plotly_all(selected_color_theme, metric_series, fixed_order_flag_freq=True)
        elif selected_metric in [f'q5__{i}' for i in range(4, 11)]:
            fig = make_bars_plotly_all(selected_color_theme, metric_series, fixed_order_flag_camb=True)
        else:
            fig = make_bars_plotly_all(selected_color_theme, metric_series, fixed_order_flag_freq=False)
    
    else:
        if checkpoint_regions:
            metric_series = group_df(df_filtered, selected_metric, 'regio')
        else:
            metric_series = group_df(df_filtered, selected_metric, 'country')
        #st.text(metric_series)
        fig = make_bars_plotly(selected_color_theme, metric_series)
    
    st.plotly_chart(fig)

    #bar_chart = make_bars(input_color=selected_color_theme, s=metric_series, title=selected_metric)
    #st.pyplot(bar_chart)

#######################
