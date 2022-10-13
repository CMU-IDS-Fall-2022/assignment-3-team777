import streamlit as st
import pandas as pd
import altair as alt

import pyreadr


st.title("Let's analyze some Penguin Data 🐧📊.")

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)

# df = load_data()



main_df = pyreadr.read_r('storms.rda')['storms']
main_df.rename(columns={'long':'lon'}, inplace=True)
main_df.dropna(subset=['wind','pressure', 'status'], inplace=True)
main_df['year'] = main_df['year'].astype('int64')
main_df['month'] = main_df['month'].astype('int64')

st.write("Let's first look at raw data in the Pandas Data Frame.")

st.write(main_df)


st.map(main_df)

st.write('Let\'s choose a few storms to visualize.')
st.write('By Name:')

names = st.multiselect('Name', main_df['name'].unique())
chosen_name_df = main_df[main_df['name'].isin(names)]
st.map(chosen_name_df)

st.write('By Year:')
years = st.multiselect('Year', main_df['year'].unique())
chosen_year_df = main_df[main_df['year'].isin(years)]
st.map(chosen_year_df)



st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

# chart = alt.Chart(df).mark_point().encode(
#     x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
#     y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
#     color=alt.Y("species")
# ).properties(
#     width=600, height=400
# ).interactive()

# st.write(chart)


"""
Data process: Group the dataframe by storm names, 
and calculate the duration of each storm, getting rid of the ones too long.
"""
storm_duration = pd.DataFrame(columns=['duration', 'wind', 'pressure', 'status'])
dfs = []

for name, group in main_df.groupby('name'):        
    
    temp_df = pd.DataFrame(group[['wind', 'pressure', 'status']])
    temp = pd.to_datetime(group[['year','month', 'day', 'hour']])
    dura = pd.to_timedelta(temp - temp.iloc[0]).astype('timedelta64[h]')

    if dura.max() > 1000:
        continue
    
    temp_df.loc[:, 'duration'] = dura

    dfs.append(temp_df)

storm_duration = pd.concat(dfs)

"""
Visualization of interactive exploration chart, analysing relationship 
among duration, the type of storms, pressure, and max wind speed.
"""

scale = alt.Scale(domain=storm_duration['status'].value_counts().keys().to_list())
color = alt.Color('status:N', scale=scale, title='Storm Category')
brush = alt.selection_interval(encodings=['x'])
click = alt.selection_multi(encodings=['color'])

points = alt.Chart().mark_point().encode(
    alt.X('duration:Q', title='Hours'),
    alt.Y('pressure:Q',
        title='Air Pressure at the Storm\'s Center',
        scale=alt.Scale(domain=[880, 1025])
    ),
    color=alt.condition(brush, color, alt.value('lightgray')),
#     color = color,
    size=alt.Size('wind:Q', scale=alt.Scale(range=[0, 50]), title="Maximum Sustained Wind Speed")
).properties(
    width=550,
    height=300
).add_selection(
    brush
).transform_filter(
    click
)

bars = alt.Chart().mark_bar().encode(
    alt.X('count()', title='Number of Each Category'),
    alt.Y('status:N',
        title='Storm Category'
    ),
    color=alt.condition(click, color, alt.value('lightgray')),
).transform_filter(
    brush
).properties(
    width=550,
).add_selection(
    click
)

chart1 = alt.vconcat(
    points,
    bars,
    data=storm_duration,
    title="Storm"
)

st.write(chart1)



st.markdown("This project was created by Zhi Jing and Yifei Wei for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
