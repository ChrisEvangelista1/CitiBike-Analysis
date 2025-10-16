######### Citi Bike Dashboard

##### Imports Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime as dt
from keplergl import KeplerGl
import streamlit as st
from streamlit_keplergl import keplergl_static
from PIL import Image

###### Import Data
top_station_df = pd.read_csv("Data/top_station_df.csv")
rentals_df = pd.read_csv("Data/rentals_df.csv")
KPI_df = pd.read_csv("Data/KPI_df.csv", index_col = "metric")
dow_df = pd.read_csv("Data/dow_df.csv")
hourly_df = pd.read_csv("Data/hourly_df.csv")



##### Dashboard Set Up & Settings
st.set_page_config(page_title = "Citi Bike Analysis", layout = "wide")
# st.title("Citi Bike Analysis")

# Side bar
st.sidebar.title("Table of Contents")
page = st.sidebar.selectbox("Select Page",
                            ["Executive Summary",
                             "Station Performance",
                             "Seasonality & Demand Analysis",
                             "Interactive NYC Map",
                             "Recommendations"])

##### --------Pages
##### ------Executive Summary
if page == "Executive Summary":
    # st.markdown("### Executive Summary")
    st.markdown("# Citi Bike Analysis Dashboard")

    # read KPI_df
    total_rentals = KPI_df.loc["rental_count", "value"]
    total_rentals_delta = KPI_df.loc["rental_count","delta"]

    avg_duration = KPI_df.loc["average_duration", "value"]
    avg_duration_delta = KPI_df.loc["average_duration", "delta"]

    member_perc = KPI_df.loc["member_perc", "value"] * 100
    member_delta = KPI_df.loc["member_perc","delta"] * 100

    ebike_perc = KPI_df.loc["bike_type_perc", "value"] * 100
    ebike_delta = KPI_df.loc["bike_type_perc", "delta"] * 100

    # KPI Card
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Rides (YTD)", f"{total_rentals:,.0f}", 
                f"{total_rentals_delta * 100:+.1f}% vs LY")

    with col2:
        st.metric("Avg Trip Duration", f"{avg_duration:.1f} min", 
                f"{avg_duration_delta * 100:+.1f}% vs LY")

    with col3:
        st.metric("Members %", f"{member_perc:.0f}%", 
                f"{member_delta:+.1f}% vs LY")

    with col4:
        st.metric("Electric Bike %", f"{ebike_perc:.0f}%", 
                f"{ebike_delta:.0f}% vs LY")
        

    # Citi Bike Image
    myImage = Image.open("CitiBikeImage.jpg")
    col1, col2 = st.columns(2)
    with col1:
        st.image(myImage, use_column_width=True)

        st.markdown(
            'Photo by <a href="https://unsplash.com/@spensersembrat?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Spenser Sembrat</a> '
            'on <a href="https://unsplash.com/photos/blue-bicycle-with-pink-umbrella-on-the-road-during-daytime-grJeAdDMxEc?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>',
            unsafe_allow_html=True
        )

    with col2:
        # Commentary
        st.markdown("""
            Citi Bike has grown across New York City, offering millions of trips each year. With this growth comes operational challenges: some stations frequently run out of bikes while others remain full, creating availability issues that impact customer experience.

            This dashboard analyzes Citi Bike 2022 trip data to uncover when, where, and how riders use the rental system. By exploring demand across time, location, and rider type, it highlights:  

            - **Station performance**: Identifying the busiest departure, arrival, and round-trip stations.  
            - **Supply imbalances**: Pinpointing stations that risk running empty or overfilling.  
            - **Usage patterns**: Understanding seasonal, daily, and hourly demand, including commuter peaks.  

            The goal is to provide the business strategy team with actionable insights to optimize bike distribution and identify opportunities for expansion, ensuring a reliable and scalable service for all riders.  
            """)


##### ------ Station Performance / Top 20
elif page == "Station Performance":
    
    st.markdown("### Citi Bike Analysis")
    st.markdown("##### Station Performance")
    
    metric_map = {
        "Departures": "departures",
        "Arrivals": "arrivals",
        "Volume": "total_volume",
        "Round Trips": "round_trips",
        "Imbalance": "imbalance_under",
    }

    ### Sidebar
    st.sidebar.header("Controls")

    metric = st.sidebar.radio(
        "Select metric:",
        list(metric_map.keys()),
        horizontal = False
    )

    n_stations = st.sidebar.slider(
        "Number of stations to display",
        min_value = 5,
        max_value = 20,
        value = 10
    )

    ### Select Chart Metric, with imbalance case
    if metric == "Imbalance":
        col1, col2 = st.columns(2)
        with col1:
            imbalance_direction = st.radio(
                "",
                ["Over Supply", "Under Supply"],
                horizontal = True
            )
        
        with col2: 
            imbalance_type = st.radio(
                "",
                ["Raw", "Ratio"],
                horizontal = True
            )

        if imbalance_direction == "Over Supply" and imbalance_type == "Raw":
            selected_metric = "imbalance_over"

        elif imbalance_direction == "Under Supply" and imbalance_type == "Raw":
            selected_metric = "imbalance_under"
            
        elif imbalance_direction == "Over Supply" and imbalance_type == "Ratio":
            selected_metric = "imbalance_over_ratio"

        elif imbalance_direction == "Under Supply" and imbalance_type == "Ratio":
            selected_metric = "imbalance_under_ratio"

    else:
        selected_metric = metric_map[metric]

    topN = top_station_df.sort_values(selected_metric, ascending = False).head(n_stations)

    ### Charts
    fig = px.bar(
        topN,
        x = selected_metric,
        y = "station",
        orientation = "h",
        title = f"Top {n_stations} Stations by {metric}",
        labels = {selected_metric: "Trips", "station": "Station"},
        text = selected_metric,
        width = 900,
        height = 600,
        color_discrete_sequence = ["steelblue"]
    )

    fig.update_layout(
        yaxis = dict(autorange = "reversed"),
        margin = dict(l=150)
    )

    st.plotly_chart(fig, use_container_width=True)

    

    # Commentary notes
    comments_map = {
        "Departures": "Top start stations. Typically stations where there are large residential areas or subway stations nearby for commuters.",
        "Arrivals": "Top end stations. Typically commuter destinations in the morning such as business districts.",
        "Volume": "Top stations by traffic (Departures + Arrivals).",
        "Round Trips": "Top stations where the start station is also the end station for a rental trip. These stations are often linked to recreational or tourist-heavy locations like parks or waterfronts.",
        "Imbalance": (
            "Top stations where the supply may not meet demand:\n\n"
            "- **Over Supply**: Arrivals > Departures (stations filling up)\n"
            "- **Under Supply**: Departures > Arrivals (stations emptying out)\n"
            "- **Raw**: Actual difference between arrivals and departures\n"
            "- **Ratio**: Difference normalized by total traffic (highlights imbalances regardless of station size)"
        )
    }

    # Display commentary
    st.markdown(f"- {comments_map[metric]}")


##### ------Seasonality & Demand Analysis
elif page == "Seasonality & Demand Analysis":
    st.markdown("#### Citi Bike Analysis")
    st.sidebar.header("Demand Analysis Controls")

    chart_option = st.sidebar.radio(
        "Select chart:",
        ["Monthly (Seasonality)", "Weekly", "Daily"]
    )

    ### Chart 
    if chart_option == "Monthly (Seasonality)":

        fig_2 = make_subplots(specs = [[{"secondary_y": True}]])

        # rental count Line
        fig_2.add_trace(
            go.Scatter(
                x = rentals_df["date"],
                y = rentals_df["trip_count_7davg"],
                name = "Rentals",
                line = dict(color = "darkcyan")
            ),
            secondary_y = False
        )

        # temperature line
        fig_2.add_trace(
            go.Scatter(
                x = rentals_df["date"],
                y = rentals_df["avg_temp_7davg"],
                name = "Temperature",
                line = dict(color = "orangered")
            ),
            secondary_y = True
        )

        # vertical rectangles for season
        season_shades = [
            {"season": "Winter", "start": "2022-01-01", "end": "2022-02-28", "color": "LightSkyBlue"},
            {"season": "Spring", "start": "2022-03-01", "end": "2022-05-31", "color": "MediumSeaGreen"},
            {"season": "Summer", "start": "2022-06-01", "end": "2022-08-31", "color": "DarkOrange"},
            {"season": "Fall",   "start": "2022-09-01", "end": "2022-11-30", "color": "Gold"},
            {"season": "Winter", "start": "2022-12-01", "end": "2022-12-31", "color": "LightSkyBlue"},
        ]

        for s in season_shades:
            fig_2.add_vrect(
                x0 = s["start"], x1 = s["end"],
                fillcolor = s["color"],
                opacity = 0.1,
                line_width = 0,
                layer = "below",
                annotation_text = s["season"],
                annotation_position = "bottom left",
                annotation_font_size = 8,
            )

        fig_2.update_layout(
            title = "Bike Rentals vs Temperature (7-Day Average)",
            height = 600,
            # xaxis_title = "Date",
            yaxis_title = "Rental Count",
            yaxis2_title = "Temperature (C)",
            legend = dict(orientation = "h", y = 1.1),
        )

        st.plotly_chart(fig_2, use_container_width = True)

        st.markdown("""Bike demand is strongly seasonal. Warmer months (spring & summer) see the highest rentals, while winter months experience a clear dip. \
                    This suggests weather driven demand and potential opportunities to rebalance inventory or run promotions in low season.""")

    elif chart_option == "Weekly":
        fig = px.bar(
        x = dow_df["day"],
        y = dow_df["rental_count"],
        labels = {"x":"Day of Week", "y":"Number of Rentals"},
        title = "Rentals by Day of Week",
        color_discrete_sequence = ["steelblue"]
        )

        # highlight weekeday
        fig.add_vrect(
            x0 = -0.5, x1 = 4.5,
            fillcolor = "lavender", opacity = 0.5,
            layer = "below", line_width = 0,
            annotation_text = "Weekdays", annotation_position = "top left", annotation_font_size = 8
        )

        # highlight weekend
        fig.add_vrect(
            x0 = 4.5, x1 = 6.5,
            fillcolor = "yellowgreen", opacity = 0.2,
            layer = "below", line_width = 0,
            annotation_text = "Weekend", annotation_position = "top left", annotation_font_size = 8
        )

        fig.update_layout(
            width = 900, height = 500,
            margin = dict(l = 50, r = 50, t = 80, b = 50)
        )

        st.plotly_chart(fig, use_container_width = True)

        st.markdown("""Weekdays typically show higher usage, reflecting commuting patterns, while weekends show more casual and recreational trips.""")



    elif chart_option == "Daily":
        fig = px.line(
        hourly_df,
        x = "hour", 
        y = "trips", 
        color = "member_casual",
        markers = True,
        title = "Hourly Usage by Member Status",
        labels = {"hour": "Hour of Day", "trips": "Number of Trips", "member_casual": ""},
        color_discrete_map = {
            "member": "seagreen",
            "casual": "goldenrod"
        }
        )

        fig.add_vrect(
            x0 = 7, x1 = 9, 
            fillcolor = "orangered", opacity = 0.1, 
            layer = "below", 
            line_width = 0, 
            annotation_text = "Morning Rush", annotation_position = "bottom left"
        )

        fig.add_vrect(
            x0 = 16, x1 = 19, 
            fillcolor = "navy", opacity = 0.1, 
            layer = "below", 
            line_width = 0, 
            annotation_text = "Evening Rush", annotation_position = "bottom left"
        )

        fig.update_layout(
            xaxis = dict(dtick = 1, range = [0,23], showgrid = False),
            yaxis = dict(showgrid = False),
            plot_bgcolor = "white",
            width = 900,
            height = 500
        )

        st.plotly_chart(fig, use_container_width = True)

        st.markdown("""There are two peaks in demand: morning rush (7-9 AM) and evening rush (4-7 PM), primarily driven by commuting members. Casual riders tend to ride more in midday and evenings.""")

##### ------Map
elif page == "Interactive NYC Map":
    st.markdown("####Citi Bike Analysis")

    html_path = "NYC CitiBike 2022.html"

    # read file
    with open(html_path, "r", encoding="utf-8") as file:
        html_data = file.read()

    ## show file
    st.header("Most Frequented Bike Rental Locations")
    st.components.v1.html(html_data, height = 1000)

else:
    st.header("Conclusions and Recommendations")
    # Citi Bike Image
    myImage2 = Image.open("CitiBikeImage2.jpg")
    col1, col2 = st.columns(2)
    with col1:
        st.image(myImage2, use_column_width = True)

        st.markdown(
            'Photo by <a href="https://unsplash.com/@jayjoshi?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Jay Joshi</a> '
            'on <a href="https://unsplash.com/photos/blue-and-black-bicycle-lot-WdHiBJ1PFmo?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>',
            unsafe_allow_html = True
        )

    with col2:
        # Commentary
        st.markdown("""
        This dashboard and analysis highlights patterns in rider behavior and station usage. Peak demand occurs during weekday commuting hours, with certain stations experiencing either shortages or surpluses of bikes. These imbalances may indicate that operational adjustments are needed to better align supply with demand.  

        **Recommendations:**  
        - **Rebalance operations**: Prioritize redistribution at high-traffic stations with recurring under and/or oversupply.  
        - **Seasonal scaling**: Data shows demand drops significantly from November through April. Scaling back the fleet by 15-20% during these months would reduce idle capacity while still meeting rider needs.  
        - **Waterfront expansion**: To determine how many stations to add along the water, compare current utilization rates per dock in waterfront stations against citywide averages. Persistent over-utilization signals where expansion is most justified.  
        - **Stocking popular stations**: Ensure consistent availability by using real time demand predictions combined with fast and efficient bike redistribution processes.

        A proactive distribution strategy will reduce availability issues, improve customer satisfaction, and support Citi Bike's continued expansion across New York City.  
        """)