import requests
import json
import streamlit as st
import datetime
import pandas as pd

def get_formatted_time(timestamp):
    if timestamp is not None:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%H:%M')
    else:
        return "Data error :("

def get_duration(rawDuration):
    if rawDuration is not None:
        rawMinutes = rawDuration / 60
        return str(round(rawMinutes)) + " mins"
    else:
        return "An error occured sorry :("

def is_air_cadet(device):
    # Implement your logic to determine if a device is an air cadet
    # For example, you could check the aircraft type or other relevant fields
    return False  # Assuming no specific criteria for air cadets

st.title("An unoffical AGC(W) Glider data tracker :airplane:")

# Create a checkbox to filter air cadets
hide_air_cadets = st.checkbox("Hide Air Cadets", value=True)

selected_date = st.date_input("Select Date", datetime.date.today())
url = f"https://flightbook.glidernet.org/api/logbook/EGDJ/{selected_date}"

response = requests.get(url)

if response.status_code == 200:
    # Get the JSON data
    data = json.loads(response.text)

    # Prepare data for the table
    table_data = []
    for flight in data['flights']:
        device_index = flight['device']
        device = data['devices'][device_index]

        launch_time = flight['start_tsp']
        formattedLaunchTime = get_formatted_time(launch_time)  # Function for clarity

        land_time = flight['stop_tsp']
        formattedLandTime = get_formatted_time(land_time)  # Function for clarity

        rawDuration = flight['duration']
        duration = get_duration(rawDuration)  # Function for clarity

        tailNum = device.get('competition')
        devType = device['aircraft']
        registration = device['registration']

        # Check if it's an air cadet flight and exclude if necessary
        if not hide_air_cadets or not (is_air_cadet(device) or (registration >= 'ZE496' and registration <= 'ZE686')):
            table_data.append([duration, formattedLaunchTime, formattedLandTime,
                               tailNum, devType, registration])

    # Create a DataFrame with column headers
    df = pd.DataFrame(table_data, columns=["Duration (mins)", "Launch Time", "Land Time",
                                           "Aircraft", "Aircraft Type", "Registration"])

    # Display the DataFrame as a table
    st.dataframe(df)

else:
    st.error("Error fetching data: Status code", response.status_code)