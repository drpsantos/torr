import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
#import maths
#import charts
import pandas as pd
from PIL import Image
from google.oauth2 import service_account
from gsheetsdb import connect
import datetime

st.set_page_config(page_title="Torrefaction Dashboard",layout="centered",initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.title('PMRR Biomass Project Dashboard')

main = st.container()
main1 = st.container()
main2 = st.container()
main3 = st.container()
main4 = st.container()
main.subheader('Key Targets')
s0c1, s0c2 = main.columns(2)
target_test_burn = s0c1.date_input('Target Test Burn',value=datetime.date(2022,10,15))
target_torr_mass = s0c2.number_input('Torrefied Biomass Needed (Tons)',0,100,75)
target_harvest = s0c1.date_input('Target Start of Harvest',value=datetime.date(2022,8,15))


# Create a connection object.
conn = connect()

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache()
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

sheet_url = st.secrets["public_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

def getFinalMass(m_i,mc_i,mc_o):
    m_o = m_i - (m_i*(mc_i-mc_o))
    return m_o

# Print results.
#for row in rows:
#    st.write(f"{row.data} has a {row.trial}")

# farm = st.expander('Farm Parameters',expanded=True)
# farm.number_input('Stalks Needed')


st.subheader('Process Parameters')

s1c1,s1c2,s1c3 = st.columns(3)
s1c1.write('Harvest & Drying')
wet_mc = s1c1.number_input('Wet Biomass Moisture Content',0.6)
dry_mc = s1c1.number_input('Dry Biomass Moisture Content',0.38)
harv_maxweeks = s1c1.number_input('Maximum Weeks for Harvesting',1,12,8)
days_grow = s1c1.number_input('Plant Maturation (days)',90,150,120)

s1c2.write('Pelletization')
pell_mc = s1c2.number_input('Pellet Mositure Content',0.15)
pell_processing_rate = s1c2.number_input('Pelletizer Output Rate (TPH)',0.2)

s1c3.write('Torrefaction')
torr_processing_rate = s1c3.number_input('Torrefaction Input Rate (TPH)',0.284)
torr_mc = s1c3.number_input('Torrefied Moisture Content',0.05)
torr_volatiles = s1c3.number_input('% Mass Volatiles',0.0,0.5,0.45)
torr_output_rate = s1c3.number_input('Torrefaction Output Rate (TPH)', getFinalMass(torr_processing_rate, pell_mc, torr_mc)*torr_volatiles)

main2.subheader('Biomass Requirements in Metric Tons')
c1,c2,c3,c4 = main2.columns(4)
biomass_torr = c4.metric('Torrefied',target_torr_mass)
b_pell = round((target_torr_mass/torr_volatiles)/(1-(pell_mc-torr_mc)),2)
biomass_pell = c3.metric('Pelletized',b_pell)
b_dry = round(b_pell/(1-(dry_mc-pell_mc)),2)
biomass_dried = c2.metric('Dried', b_dry)
b_wet = round(b_dry/(1-(wet_mc-dry_mc)),2)
biomass_wet = c1.metric('Wet', b_wet)

harv_rate = s1c1.number_input('Harvesting Rate (TPD)',b_wet/(harv_maxweeks*7),b_wet/(harv_maxweeks*7),b_wet/(harv_maxweeks*7))

st.subheader('Estimated Lead Times')
s2c1, s2c2,s2c3 = st.columns(3)
s2c1.write('Operations')
hours_farm = s2c1.number_input('Farm work hours per day',8,16,8)
hours_pell = s2c1.number_input('Pelletizer operating hours per day',8,24,16)
hours_pmrrt = s2c1.number_input('PMRR Torrefier operating hours per day',8,24,16)

s2c2.write('Fuel Processing')
days_drying = s2c2.number_input('Air Drying for Wet Biomass',1,7,5)
days_leadpell = s2c2.number_input('Lead Time for Pelletization',0,30,24)

s2c3.write('Transport & Logistics')
days_MAStoGNPK = s2c3.number_input('Transport from Masbate to GNPK',3,24,12)

main3.subheader('Minimum Processing Rates in Tons/day')
m3c1,m3c2,m3c3,m3c4 = main3.columns(4)
harv_rate = round(b_wet/(harv_maxweeks*7),2)
m3c1.metric('Harvested',harv_rate)
days_harv = harv_maxweeks*7
dry_rate = round(b_dry/(harv_maxweeks*7),2)
m3c2.metric('Dried Biomass',dry_rate)
pell_rate =pell_processing_rate*hours_pell
days_pell = b_dry/pell_rate
m3c3.metric('Pelletized Biomass',round(pell_rate,2))
m3c3.metric('Days Pelletizing',np.ceil(days_pell))
torr_rate = torr_processing_rate*hours_pmrrt
days_torr = b_pell/torr_rate
m3c4.metric('Torrefied Biomass',round(torr_rate,2))
m3c4.metric('Days Torrefying',np.ceil(days_torr))

m4c1,m4c2 = main4.columns(2)

main1.subheader('Supply Projection')
mr_wet2dried = b_dry/b_wet
mr_dried2pell = b_pell/b_dry
mr_pell2torr = target_torr_mass/b_pell
mr_wet2torr = target_torr_mass/b_wet
c2.metric('Mass Retention',str(round(mr_wet2dried*100,2))+'%')
c3.metric('Mass Retention',str(round(mr_dried2pell*100,2))+'%')
c4.metric('Mass Retention',str(round(mr_pell2torr*100,2))+'%')
c4.metric('Total Mass Retention',str(round(mr_wet2torr*100,2))+'%')



m1c3,m1c4,m1c5 = main1.columns(3)
days_drying = m1c3.slider('Days for Drying',1,30,5)
days_storePell = m1c4.slider('Pellet Production Lead Time',0,30,6)
days_storeTorr = m1c5.slider('Torrefaction Lead Time',1,30,24)

#@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def projectSupply(harv_rate,dry_rate,pell_rate,torr_rate,days_drying,days_storePell,days_storeTorr,b_wet):
    rangeend = 80
    df = pd.DataFrame(columns=['Wet','Total Wet','Available Wet','Dried','Available Dried','Total Dried','Pelletizer Input','Pelletizer Output','Total Pelletized','Available Pellets','Torrefied Input','Torrefied Output','Total Torrefied'],index=range(0,rangeend),dtype=float)
    df.iloc[0,0:3] = harv_rate
    df.iloc[0,3:] = 0.0
    df.iloc[1:,:] = 0.0
    i = 1
    end_harv = b_wet/harv_rate
    start_pell = days_drying+days_storePell
    start_torr = start_pell + days_storeTorr

    for i in range(1,rangeend):
        if i < harv_maxweeks*7:
            df['Wet'].iloc[i] = harv_rate
        if i >= days_drying and i <days_drying+(harv_maxweeks*7):
            df['Dried'].iloc[i] = dry_rate
        if i >= start_pell and df['Total Pelletized'].iloc[i-1] < b_pell:
            df['Pelletizer Input'].iloc[i] = min(pell_rate/mr_dried2pell,df['Available Dried'].iloc[i-1])
            df['Pelletizer Output'].iloc[i] = min(pell_rate,df['Available Dried'].iloc[i-1]*mr_dried2pell)
        if i >= start_torr and df['Total Torrefied'].iloc[i-1] < target_torr_mass:
            df['Torrefied Input'].iloc[i] = min(torr_rate,df['Available Pellets'].iloc[i-1])
            df['Torrefied Output'].iloc[i] = min(torr_rate*mr_pell2torr,df['Available Pellets'].iloc[i-1]*mr_pell2torr)
        
        #Totals
        df['Total Wet'].iloc[i] = df['Total Wet'].iloc[i-1] + df['Wet'].iloc[i]
        df['Total Dried'].iloc[i] = df['Total Dried'].iloc[i-1] + df['Dried'].iloc[i]
        df['Total Pelletized'].iloc[i] = df['Total Pelletized'].iloc[i-1] + df['Pelletizer Output'].iloc[i]
        df['Total Torrefied'].iloc[i] = df['Total Torrefied'].iloc[i-1] + df['Torrefied Output'].iloc[i]

        #Available
        df['Available Wet'].iloc[i] = df['Wet'].iloc[i] + df['Available Wet'].iloc[i-1] - df['Dried'].iloc[i]
        df['Available Dried'].iloc[i] = df['Dried'].iloc[i] + df['Available Dried'].iloc[i-1] - df['Pelletizer Input'].iloc[i]
        df['Available Pellets'].iloc[i] = df['Pelletizer Output'].iloc[i] + df['Available Pellets'].iloc[i-1] - df['Torrefied Input'].iloc[i]
    
    end_dry = min(df['Total Dried'].loc[df['Total Dried']>b_dry-1].index)
    end_pell = min(df['Total Pelletized'].loc[df['Total Pelletized']>b_pell-1].index)
    end_torr = min(df['Total Torrefied'].loc[df['Total Torrefied']>target_torr_mass-1].index)

    # for i in range(1,120):
    #     if df['Total Wet'].iloc[i-1] < b_wet:
    #         df['Wet'].iloc[i] = harv_rate
    #     else:
    #         df['Wet'].iloc[i] = 0.0

    #     df['Total Wet'].iloc[i] = df['Total Wet'].iloc[i-1] + df['Wet'].iloc[i]

    #     if i >= days_drying:
    #         if df['Wet'].iloc[i-days_drying] > 0.0:
    #             df['Dried'].iloc[i] = dry_rate
    #         else:
    #             df['Dried'].iloc[i] = 0.0
    #     else:
    #         df['Dried'].iloc[i] = 0.0

    #     df['Total Dried'].iloc[i] = df['Total Dried'].iloc[i-1] + df['Dried'].iloc[i]

    #     if i>= start_pell and df['Total Pelletized'].iloc[i-1] < b_pell:
    #         if df['Available Dried'].iloc[i-1]*mr_dried2pell > pell_rate:
    #             df['Pelletizer Input'].iloc[i] = pell_rate/mr_dried2pell
    #             df['Pelletizer Output'].iloc[i] = pell_rate
        
    #     if i == start_pell:
    #         df['Available Dried'].iloc[i] = df['Dried'].iloc[i]+ df['Available Dried'].iloc[i-1] - df['Pelletizer Input'].iloc[i]
    #     elif df['Available Dried'].iloc[i-1] <= 0.0:
    #         df['Available Dried'].iloc[i] = 0.0
    #     else:
    #         df['Available Dried'].iloc[i] = df['Dried'].iloc[i]+ df['Available Dried'].iloc[i-1] - df['Pelletizer Input'].iloc[i]
    #     df['Total Pelletized'].iloc[i] = df['Total Pelletized'].iloc[i-1] + df['Pelletizer Input'].iloc[i]

    #     if i == start_torr:
    #         df['Available Pellets'].iloc[i] = df['Total Pelletized'].iloc[i]
    #     elif df['Available Pellets'].iloc[i-1] <= 0.0:
    #         df['Available Pellets'].iloc[i] = 0.0
    #     else:
    #         df['Available Pellets'].iloc[i] = df['Pelletizer Output'].iloc[i] + df['Available Pellets'].iloc[i-1] - df['Torrefied Input'].iloc[i]

    #     if i >= start_torr and df['Total Torrefied'].iloc[i-1] < target_torr_mass :
    #         if df['Available Pellets'].iloc[i] > torr_rate:
    #             df['Torrefied Input'].iloc[i] = torr_rate
    #             df['Torrefied Output'].iloc[i] = torr_rate * mr_pell2torr

    #     df['Total Torrefied'].iloc[i] = df['Total Torrefied'].iloc[i-1] + df['Torrefied Output'].iloc[i]

    fig = go.Figure()
    fig.add_hline(y=b_wet)
    fig.add_hline(y=b_dry)
    fig.add_hline(y=b_pell)
    fig.add_hline(y=target_torr_mass)
    fig.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Total Wet'],name='Wet'))
    fig.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Total Dried'],name='Dried'))
    fig.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Total Pelletized'],name='Pelletized'))
    fig.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Total Torrefied'],name='Torrefied'))
    fig.update_layout(showlegend=True,yaxis_title='Tons Produced',xaxis_title = 'Days from Start of Harvest')

    fig2 = go.Figure()
    #fig2.add_hline(y=target_torr_mass)
    fig2.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Wet'],name='Wet'))
    fig2.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Dried'],name='Dried'))
    fig2.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Pelletizer Output'],name='Pelletized'))
    fig2.add_trace(go.Scatter(x=np.arange(0,rangeend),y=df['Torrefied Output'],name='Torrefied'))
    fig2.update_layout(showlegend=True,yaxis_title='Tons Produced/day',xaxis_title = 'Days from Start of Harvest')
    main1.write(df)
    return fig,fig2

fig1, fig2 = projectSupply(harv_rate,dry_rate,pell_rate,torr_rate,days_drying,days_storePell,days_storeTorr,b_wet)
main1.plotly_chart(fig1)
main1.plotly_chart(fig2)

harvest_end = target_harvest + datetime.timedelta(days=days_harv)
dry_start = target_harvest + datetime.timedelta(days=days_drying)
dry_end = dry_start + datetime.timedelta(days=days_harv)
pell_start = dry_start
pell_end = pell_start + datetime.timedelta(days=days_pell)
torr_start = pell_start + datetime.timedelta(days=days_leadpell)
torr_end = torr_start + datetime.timedelta(days=days_torr)
MAStoGNPK_start = torr_end+datetime.timedelta(days=1)
MAStoGNPK_end = MAStoGNPK_start+datetime.timedelta(days=days_MAStoGNPK)
earliest_test_burn = MAStoGNPK_end + datetime.timedelta(days=1)

df = pd.DataFrame([
    dict(Task="Start of Harvest", Start=target_harvest, Finish=harvest_end , Group="Farm"),
    dict(Task="Drying", Start=dry_start, Finish=dry_end, Group="Farm"),
    dict(Task="Pelletizing", Start=pell_start, Finish=pell_end, Group="Pelletizer"),
    dict(Task="Torrefaction", Start=torr_start, Finish=torr_end, Group="PMRR Unit"),
    dict(Task="Delivery to GNPK", Start=MAStoGNPK_start, Finish=MAStoGNPK_end, Group="Logistics"),

])

fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Group")
fig.update_yaxes(autorange="reversed")
fig.add_vline(x= target_test_burn)
fig.add_vline(x=earliest_test_burn)
fig.add_vline(x=datetime.date.today())
fig.add_annotation(x=datetime.date.today(), y=-1,text="Today",showarrow=False,yshift=40,textangle=90)
fig.add_annotation(x=earliest_test_burn, y=-1,text="Earliest Test Burn <br>"+str(earliest_test_burn),showarrow=False,yshift=30,textangle=90)
fig.add_annotation(x=target_test_burn, y=-1,text="Target Test Burn <br>"+str(target_test_burn),showarrow=False,yshift=30,textangle=90)
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.21,
    xanchor="right",
    x=1
))
main.subheader('Projected Timeline')
main.plotly_chart(fig)