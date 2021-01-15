import pandas as pd
import streamlit as st
import plotly.express as px
import plotly
import numpy as np
import altair as alt
import pydeck as pdk


df = pd.read_csv("parler.csv")

#PREPPING THE DATA

@st.cache(persist=True)
def data_load(): 
    data = pd.read_csv("parler.csv")
    lowercase = lambda x: str(x).lower()
    data.drop("Unnamed: 0", axis=1, inplace=True)
    data.columns = ["lat", "lon", "time", "id"]
    data.rename(lowercase, axis="columns", inplace=True)
    data["time"] = pd.to_datetime(data["time"])
    data["time"] = data["time"].apply(lambda x: x.tz_localize('UTC').tz_convert('EST'))
    data = data[data['time'].dt.date.astype(str) == '2021-01-06'] 
    return data

data = data_load()

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

local_css("style.css")

# CREATING FUNCTION FOR MAP

def map(data, lat, lon, zoom):
    layer = pdk.Layer("GridLayer", data, pickable=True, extruded=True, cell_size=30, elevation_scale=3, get_position=["lat", "lon"])
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom, bearing=90, pitch=45)
    st.write(pdk.Deck(map_style="mapbox://styles/mapbox/satellite-v9",initial_view_state=view_state, layers=[layer])
    )



# LAYING OUT THE TEXT
st.title("Attack on The Capitol")
st.subheader(
     """
     Visualizing an hour by hour view of videos uploaded to Parler during the day of attack. 
    By sliding the slider below you can view different times during the day of the attack.
    """)
hour_selected = st.slider("Select hour of day", 10, 23)

# FILTERING DATA BY HOUR SELECTED
data = data[data["time"].dt.hour == hour_selected]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS


# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS

st.subheader("**The Capitol**")
map(data, 38.8899, -77.0091, 14)

filtered = data[
    (data["time"].dt.hour >= hour_selected) & (data["time"].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered["time"].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "videos": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of videos per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected +1 ) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("videos:Q"),
        tooltip=['minute', 'videos']
    ).configure_mark(
        opacity=0.5,
        color='red',
    ).configure(background='#000'
    ).configure_axisLeft(
        labelColor='white',
        titleColor='white',)
  , use_container_width=True)
