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

st.title("An glider data tracker based of OGN data :airplane:")
hide_air_cadets = False
selected_field = "EGHL"

selected_field = "EGDJ"
selected_date = "2024-10-19"

selected_field = st.text_input("Enter the ICAO (e.g. EGDJ) or GB (e.g. GB-0419 for Keevil) code of your airfild", placeholder="EGHL")
selected_date = st.date_input("Select Date", datetime.date.today())
url = f"https://flightbook.glidernet.org/api/logbook/{selected_field}/{selected_date}"

# Create a checkbox to filter air cadets
if selected_field == "EGDJ":
    hide_air_cadets = st.checkbox("Hide Air Cadets", value=True)

response = requests.get(url)

if response.status_code == 200:
    # Get the JSON data
    data = json.loads(response.text)

    # Prepare data for the table
    table_data = []
    a_day = data["a_day"]
    airfield_code = data["airfield"]["code"]
    airfield_elevation = data["airfield"]["elevation"]
    airfield_latlng = data["airfield"]["latlng"]
    airfield_name = data["airfield"]["name"]
    dawn_time = data["airfield"]["time_info"]["dawn"]
    noon_time = data["airfield"]["time_info"]["noon"]
    sunrise_time = data["airfield"]["time_info"]["sunrise"]
    sunset_time = data["airfield"]["time_info"]["sunset"]
    twilight_time = data["airfield"]["time_info"]["twilight"]
    tz_name = data["airfield"]["time_info"]["tz_name"]
    tz_offset = data["airfield"]["time_info"]["tz_offset"]
    # output = (airfield_code + ": " + airfield_name + ":city_sunrise: Dawn: " + dawn_time + ":city_sunset: Twilight: " + twilight_time)
    html_str = f"""
    <style>
    p.a {{
    font: bold 25px monospace;
    }}
    </style>
    <p class="a">{airfield_code}: {airfield_name} &#127751; Dawn: {dawn_time} &#127750; Twilight: {twilight_time} </p>
    """

    st.markdown(html_str, unsafe_allow_html=True)
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

    # Add new columns for PIC Name and P2 Name
    # Create the selectbox with a default selection (optional)
    selected_row = st.selectbox("Select Row", range(len(df)), index=0)

    df["PIC Name"] = "Not Available"  # Initialize with a default value
    df["P2 Name"] = "Not Available"  # Initialize with a default value

    # Handle potential NoneType for selected_row and avoid negative indexing
    #if selected_row is not None:
       # Use selected_row directly for indexing (no subtraction)
     #   df.loc[selected_row, "PIC Name"] = st.text_input(f"Edit PIC Name for Row {selected_row + 1}",
      #                                                   value=df.loc[selected_row, "PIC Name"])
       # df.loc[selected_row, "P2 Name"] = st.text_input(f"Edit P2 Name for Row {selected_row}",
     #                                                    value=df.loc[selected_row, "PIC Name"])
    #else:
     #   # Optionally display a message indicating no data for the date
      #  st.info("No glider flights found for the selected date.")

    # Display the DataFrame as a table
    st.dataframe(df)

else:
    st.error("Error fetching data: Status code", response.status_code)
"""
*Please note the PIC feature doesn't yet! work*
\n
\n
\n

The code for this project is made avilable under GNU Lesser General Public License v2.1 the license text can be found in the repositery for ths prodject

The OGN data in this work is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0// """