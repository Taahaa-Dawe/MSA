import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime,timedelta
import streamlit as st

Response = requests.get("https://www.islamicfinder.org/world/united-states/5574991/boulder-prayer-times/")

soup = BeautifulSoup(Response.text ,"html.parser")

prayername = soup.find_all("span",class_="prayername")
prayertime = soup.find_all("span",class_="prayertime")

prayernamelist = []
prayertimelist = []
for i in range(len(prayername)):
    prayernamelist.append(list(prayername[i])[0])
    prayertimelist.append(prayertime[i].text.strip())



df = pd.DataFrame({"Namaz": prayernamelist, "Namaz Time": prayertimelist})



df['Namaz Time'] = pd.to_datetime(df['Namaz Time'])

# Add new columns
df['Engineer Center'] = ''
df['Norlin Library'] = ''
df['UMC'] = ''
df['ICB'] = ''

# Calculate values for 'Engineer Center', 'Norlin Library', and 'UMC' columns for all prayers except 'Sunrise'
for i in range(len(df)):
    if df.loc[i, 'Namaz'] != 'Sunrise  ':
        namaz_time = pd.to_datetime(df.loc[i, 'Namaz Time'])

        # Check if it's Friday and Dhuhr time
        if namaz_time.dayofweek == 4 and df.loc[i, 'Namaz'] == 'Dhuhr':
            # Replace 'Dhuhr' with 'Jumma'
            df.at[i, 'Namaz'] = 'Jumma'
            # Set 'Engineer Center' and 'Norlin Library' columns for 'Dhuhr' to empty
            df.at[i, 'Engineer Center'] = ''
            df.at[i, 'Norlin Library'] = ''
            # Set 'UMC' column for 'Dhuhr' to 1:30 PM
            df.at[i, 'UMC'] = '01:30 PM'
            # Set 'ICB' column for 'Dhuhr' to 1:00 PM
            df.at[i, 'ICB'] = '01:00 PM'
        else:
            # Calculate 'Engineer Center' column (add 2 minutes)
            e_time = namaz_time + pd.Timedelta(minutes=2)

            # Calculate 'Norlin Library' column (add 1 hour)
            n_time = e_time + pd.Timedelta(minutes=30)

            # For 'Isha', skip checking the next Namaz time condition
            if df.loc[i, 'Namaz'] == 'Isha':
                c_time = n_time + pd.Timedelta(minutes=30)
            else:
                # Calculate 'UMC' column (add 2 hours)
                c_time = n_time + pd.Timedelta(minutes=30)
                # Check if 'UMC' time exceeds the next Namaz time, adjust it
                next_namaz_index = (i + 1) % len(df)
                next_namaz_time = pd.to_datetime(df.loc[next_namaz_index, 'Namaz Time'])
                while c_time >= next_namaz_time:
                    c_time -= pd.Timedelta(minutes=1)

            # Update DataFrame with calculated times
            df.at[i, 'Engineer Center'] = e_time.strftime("%I:%M %p")
            df.at[i, 'Norlin Library'] = n_time.strftime("%I:%M %p")
            df.at[i, 'UMC'] = c_time.strftime("%I:%M %p")

# Display the DataFrame

df['Namaz Time'] = df['Namaz Time'].dt.strftime('%I:%M %p')

df.columns = ['Namaz', 'Salah Time', 'Engineering Center 359 ECOT Iqamah', 'Norlin Library 1st Floor Mindfulness Room Iqamah', 'UMC Quiet Room Iqamah', 'ICB']
df.set_index("Namaz", inplace=True)
st.set_page_config(layout="wide")
st.table(df)
