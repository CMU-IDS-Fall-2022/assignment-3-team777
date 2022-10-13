import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import pyreadr


st.title("Assignment 3 for IDS (Team777) -- Storm tracks data analysis 🌪🌪🌪")



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

st.subheader("Let's first take a look at raw data in the Pandas Data Frame.")

st.write(main_df)

st.write("The data source is from [dplyr's storm tracks data](https://dplyr.tidyverse.org/reference/storms.html#ref-examples). The meanings for each variable are provided below:")


st.markdown("- name: Storm Name \n - year,month,day: Date of report \n - hour: Hour of report (in UTC) \n - lat,long: Location of storm center \n - status: Storm classification (Tropical Depression, Tropical Storm, or Hurricane) \n - category: Saffir-Simpson storm category (estimated from wind speed. -1 = Tropical Depression, 0 = Tropical Storm)\n - wind: storm's maximum sustained wind speed (in knots)\n  - pressure:Air pressure at the storm\'s center (in millibars)\n - tropicalstorm_force_diameter: Diameter (in nautical miles) of the area experiencing tropical storm strength winds (34 knots or above)\n - hurricane_force_diameter: Diameter (in nautical miles) of the area experiencing hurricane strength winds (64 knots or above)\n There are something missing in the raw data. So we will process the data according to our proposed question before visualization.")


st.subheader("Then, let's look at the statistics of this dataset 👉📊:")




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



scale = alt.Scale(domain=storm_duration['status'].value_counts().keys().to_list())
color = alt.Color('status:N', scale=scale, title='Storm Category')
brush = alt.selection_interval(encodings=['x'])
click = alt.selection_multi(encodings=['color'])

points = alt.Chart().mark_point().encode(
    alt.X('duration:Q', title='Duration (h)'),
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

"""
Graph 1:\n
\n\n
- Data process: Group the dataframe by storm names, and calculate the duration of each storm, getting rid of the ones too long.

- Purpose: Visualization of interactive exploration chart, analysing relationship among duration, the type of storms, pressure, and max wind speed.
"""


st.markdown("**Interactive hint**: \nYou can select an area of interest in the above scatter plot, the corresponding data statistics will be updated simultanueously in the bar plot below. You can also click the bars in the bar plot to check the statistics of a particualr storm type. Also, you can select an area in the above chart and drag it to check a particular range of data. Isn't that cool🙌🙌🙌!!")






drop_df = main_df.dropna(subset=['tropicalstorm_force_diameter'])

drop_df = drop_df.loc[~(drop_df['tropicalstorm_force_diameter']==0)]

source = drop_df[:4987]

pts = alt.selection(type="single", encodings=['x'])

rect = alt.Chart(source).mark_rect().encode(
    alt.X('wind:Q', bin=True),
    alt.Y('pressure:Q', bin=True),
    alt.Color('count()',
        scale=alt.Scale(scheme='greenblue'),
        legend=alt.Legend(title='Total Records')
    )
)

circ = rect.mark_point().encode(
    alt.ColorValue('grey'),
    alt.Size('max(tropicalstorm_force_diameter)',
        legend=alt.Legend(title='Max Force Diameter')
    )
).transform_filter(
    pts
)

bar = alt.Chart(source).mark_bar().encode(
    x='status:N',
    y='count()',
    color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
).properties(
    width=550,
    height=200
).add_selection(pts)

chart2=alt.vconcat(
    rect + circ,
    bar
).resolve_legend(
    color="independent",
    size="independent"
)
st.write(chart2)


"""
Graph 2:\n
\n\n
- Data process: Drop the rows with a 0 or NaN in the column tropicalstorm_force_diameter.
- Purpose: Visualization of the relation between the frequency of wind speed and pressure and the diameter of tropical storms, and we add a function of selecting the tpye of storms to provide special perspectives.
"""

st.markdown("**Interactive hint**: \n You can click the bars in the bar plot to check the statistics of a particualr storm type. Give a try!👆👆")


# chart3=alt.Chart(main_df[2000:7000]).mark_boxplot(extent='min-max').encode(
#     x='month:Q',
#     y= 'wind:Q',
# #     color='pressure:N',
# #     column='pressure:N'
# ).properties(
#     width = 500
# )
# st.write(chart3)


st.subheader("Next, let's look at the traces of these storms over the years")

st.map(main_df)

st.write("It's a bit of messy, right 🙂? No, actually it is extremely messy and of disorder, looking like chaos 🤯🤯🤯 !! ")


st.write('But, if we can pick only a few traces according to certain features 🤩, we will have:')

st.write('Selected by Name:')

names = st.multiselect('Name', main_df['name'].unique())
chosen_name_df = main_df[main_df['name'].isin(names)]
st.map(chosen_name_df)

if len(names) == 0:
    st.write("Please choose the year and month you wish to see")

st.write('Selected by Year and Month:')

col1, col2 = st.columns(2)

with col1:
    years = st.multiselect('Year', main_df['year'].unique())

with col2:
    months = st.multiselect('Month', np.sort(main_df['month'].unique()))


if len(years) == 0:
    st.write("Please choose the year and month you wish to see")
else:
    chosen_year_df = main_df[main_df['year'].isin(years)]

if len(months) == 0:
    chosen_year_df = main_df[main_df['year'].isin(years)]
else:
    chosen_year_df = chosen_year_df[chosen_year_df['month'].isin(months)]

if len(years) > 0 and len(months) > 0 and len(chosen_year_df) == 0:
    st.write("No record!")

st.map(chosen_year_df)




# chart = alt.Chart(df).mark_point().encode(
#     x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
#     y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
#     color=alt.Y("species")
# ).properties(
#     width=600, height=400
# ).interactive()

# st.write(chart)

"""
Now, you can clearly see certain tracks of storms by the name or time you select!! Thank you! \n

References:
- https://dplyr.tidyverse.org/reference/storms.html
- https://altair-viz.github.io/index.html
- https://docs.streamlit.io/

"""




st.markdown("This project was created by Zhi Jing and Yifei Wei for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
