import streamlit as st
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime

st.set_page_config(page_title="Torrefaction Dashboard",layout="centered",initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.title('PMRR Biomass Project Dashboard')
main = st.container() # Key Targets
main1 = st.container() # Requirements
main2 = st.container() # Minimum Processing Rates
main3 = st.container() # Calendar & Charts

def getFinalMass(m_i,mc_i,mc_o):
    m_o = m_i - (m_i*(mc_i-mc_o))
    return m_o

# Sidebar Configuration
st.sidebar.title('Project Parameters')
with st.sidebar:
    st.title('Harvesting & Drying')
    wet_mc = st.number_input('Wet Biomass Moisture Content',0.4,1.0,0.6,help='Moisture content of raw biomass upon harvest')
    dry_mc = st.number_input('Dry Biomass Moisture Content',0.1,0.4,0.38,help='Moisture content of biomass after air drying')
    harv_rateh = st.number_input('Harvesting Rate (TPH)',0.0,5.0,1.5,help='Harvesting rate of E-Farm')
    days_drying = st.slider('Days for Drying',1,7,5,help='Number of days that biomass is air dried')
    hours_farm = st.slider('Farm work hours per day',8,16,8,help='Affects Minimum Harvesting & Drying Rate')
    
    st.title('Pelletization')
    pell_mc = st.number_input('Pellet Mositure Content',0.15,help='Moisture content of produced pellet')
    pell_processing_rate = st.number_input('Pelletizer Output Rate (TPH)',0.2,help='Rated for Colorado Milling Equipment Unit')
    days_storePell = st.slider('Pellet Production Lead Time',0,21,6,help='Number of days to store dried fuel for continuous pelletizing operation')
    hours_pell = st.slider('Pelletizer operating hours per day',8,24,16,help='Affects Minimum Pelletization Rate')

    st.title('Torrefaction')
    torr_processing_rate = st.number_input('Torrefaction Input Rate (TPH)',0.1,2.0,0.284,help='Values are based off PMRR Unit')
    torr_mc = st.number_input('Torrefied Moisture Content',0.05,0.10,0.05,help='Moisture content of torrefied product')
    torr_volatiles = st.number_input('% Mass Volatiles',0.0,0.5,0.45,help='Values based off calculations from testing results')
    torr_output_rate = st.number_input('Torrefaction Output Rate (TPH)', getFinalMass(torr_processing_rate, pell_mc, torr_mc)*torr_volatiles,help='Calculated from Input Rate, Moisture & Volatile Loss')
    days_storeTorr = st.slider('Torrefaction Lead Time',5,21,5,help='Number of days that pellets are stored for continuous torrefaction operation')
    hours_pmrrt = st.slider('PMRR Torrefier operating hours per day',8,24,16,help='Affects Minimum Torrefaction Rate')

    st.title('Logistics')
    days_MAStoGNPK = st.number_input('MAS to GNPK Travel (days)',1,21,14,help='Estimated travel time from Masbate to GNPK site')

# Key Targets
main.subheader('Key Targets')
s0c1,s0c2 = main.columns(2)
target_torr_mass = s0c1.number_input('Torrefied Biomass Needed (Tons)',0,100,75)
target_harvest = s0c2.date_input('Target Start of Harvest',value=datetime.date(2022,9,15))


# Requirements
main1.subheader('Biomass Requirements in Metric Tons')
c1,c2,c3,c4 = main1.columns(4)
biomass_torr = c4.metric('Torrefied',target_torr_mass)
b_pell = round((target_torr_mass/torr_volatiles)/(1-(pell_mc-torr_mc)),2)
biomass_pell = c3.metric('Pelletized',b_pell)
b_dry = round(b_pell/(1-(dry_mc-pell_mc)),2)
biomass_dried = c2.metric('Dried', b_dry)
b_wet = round(b_dry/(1-(wet_mc-dry_mc)),2)
biomass_wet = c1.metric('Wet', b_wet)
mr_wet2dried = b_dry/b_wet
mr_dried2pell = b_pell/b_dry
mr_pell2torr = target_torr_mass/b_pell
mr_wet2torr = target_torr_mass/b_wet
c2.metric('Mass Retention',str(round(mr_wet2dried*100,2))+'%')
c3.metric('Mass Retention',str(round(mr_dried2pell*100,2))+'%')
c4.metric('Mass Retention',str(round(mr_pell2torr*100,2))+'%')
c4.metric('Total Mass Retention',str(round(mr_wet2torr*100,2))+'%')

# Processing Rates
main2.subheader('Minimum Processing Rates in Tons/day')
m3c1,m3c2,m3c3,m3c4 = main2.columns(4)
harv_rate = round(harv_rateh*hours_farm,2)
m3c1.metric('Harvested',harv_rate)
days_harv = round(b_wet/harv_rate,2)
dry_rate = round(b_dry/days_harv,2)
m3c2.metric('Dried Biomass',dry_rate)
pell_rate =pell_processing_rate*hours_pell
days_pell = b_dry/pell_rate
m3c3.metric('Pelletized Biomass',round(pell_rate,2))
m3c3.metric('Days Pelletizing',np.ceil(days_pell))
torr_rate = torr_processing_rate*hours_pmrrt
days_torr = b_pell/torr_rate
m3c4.metric('Torrefied Biomass',round(torr_rate,2))
m3c4.metric('Days Torrefying',np.ceil(days_torr))

# Main Calculation Loop

rangeend = int(days_torr + days_storeTorr + days_storePell + days_drying+21)

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def projectSupply(harv_rate,dry_rate,pell_rate,torr_rate,days_drying,days_storePell,days_storeTorr,b_wet,rangeend):
    df = pd.DataFrame(columns=['Wet','Total Wet','Available Wet','Dried','Available Dried','Total Dried','Pelletizer Input','Pelletizer Output','Total Pelletized','Available Pellets','Torrefied Input','Torrefied Output','Total Torrefied'],index=range(0,rangeend),dtype=float)
    df.iloc[0,0:3] = harv_rate
    df.iloc[0,3:] = 0.0
    df.iloc[1:,:] = 0.0
    i = 1
    end_harv = b_wet/harv_rate
    start_pell = days_drying+days_storePell
    start_torr = start_pell + days_storeTorr

    for i in range(1,rangeend):
        if i <= days_harv:
            df['Wet'].iloc[i] = min(harv_rate,b_wet-df['Total Wet'].iloc[i-1])
        if i >= days_drying and i <days_drying+days_harv:
            df['Dried'].iloc[i] = min(dry_rate,b_dry - df['Total Dried'].iloc[i-1])
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

    return df,end_harv,end_dry,end_pell,end_torr

data,end_dry,end_harv,end_pell,end_torr = projectSupply(harv_rate,dry_rate,pell_rate,torr_rate,days_drying,days_storePell,days_storeTorr,b_wet,rangeend)

harvest_end = target_harvest + datetime.timedelta(days=days_harv)
dry_start = target_harvest + datetime.timedelta(days=days_drying)
dry_end = dry_start + datetime.timedelta(days=end_dry)
pell_start = dry_start+ datetime.timedelta(days=days_storePell)
pell_end = target_harvest + datetime.timedelta(days=end_pell)
torr_start = pell_start + datetime.timedelta(days=days_storeTorr)
torr_end = target_harvest + datetime.timedelta(days=end_torr)
MAStoGNPK_start = torr_end
MAStoGNPK_end = MAStoGNPK_start+datetime.timedelta(days=days_MAStoGNPK)
earliest_test_burn = MAStoGNPK_end


main3.subheader('Project Timeline')
df = pd.DataFrame([
    dict(Task="Start of Harvest", Start=target_harvest, Finish=harvest_end , Group="Farm"),
    dict(Task="Drying", Start=dry_start, Finish=dry_end, Group="Farm"),
    dict(Task="Pelletizing", Start=pell_start, Finish=pell_end, Group="Pelletizer"),
    dict(Task="Torrefaction", Start=torr_start, Finish=torr_end, Group="PMRR Unit"),
    dict(Task="Delivery to GNPK", Start=MAStoGNPK_start, Finish=MAStoGNPK_end, Group="Logistics"),

])

fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color=['blue','red','green','purple','orange'],width = 800,height=400)
fig.update_yaxes(autorange="reversed")
fig.add_vline(x=earliest_test_burn)
fig.add_vline(x=target_harvest)
fig.add_vline(x=datetime.date.today())
fig.add_annotation(x=datetime.date.today(), y=-1,text="Today",showarrow=False,yshift=40,textangle=90)
fig.add_annotation(x=earliest_test_burn, y=-1,text="Earliest Test Burn <br>"+str(earliest_test_burn),showarrow=False,yshift=30,textangle=90)
fig.add_annotation(x=target_harvest, y=-1,text="Target Harvest<br>"+str(target_harvest),showarrow=False,yshift=30,textangle=90)
fig.update_layout(showlegend=False,
    margin=dict(l=10, r=20, t=80, b=20),
legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.21,
    xanchor="right",
    x=1,
))
fig.update_xaxes(range=(datetime.date(2022,9,1),datetime.date(2023,1,1)))
fig.update_yaxes(showgrid=True)
fig.add_vline(x=target_harvest+datetime.timedelta(days=end_torr), line_dash="dot", line_color='purple', line_width=0.5)
main.subheader('Projected Timeline')
main3.plotly_chart(fig)


fig = make_subplots(rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=['Production Timeline','Production Rate']
                   )




fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Total Wet'],name='Wet',line=dict(color='blue')),row=1, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Total Dried'],name='Dried',line=dict(color='red')),row=1, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Total Pelletized'],name='Pelletized',line=dict(color='green')),row=1, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Total Torrefied'],name='Torrefied',line=dict(color='purple')),row=1, col=1,)

fig.add_hline(y=b_wet, line_dash="dot", row=1, col=1, line_color="#000000", line_width=0.5)
fig.add_hline(y=b_dry, line_dash="dot", row=1, col=1, line_color="#000000", line_width=0.5)
fig.add_hline(y=b_pell, line_dash="dot", row=1, col=1, line_color="#000000", line_width=0.5)
fig.add_hline(y=target_torr_mass, line_dash="dot", row=1, col=1, line_color="#000000", line_width=0.5)
fig.add_vline(x=target_harvest, line_dash="solid", row=1, col=1, line_color='black', line_width=2)
fig.add_vline(x=target_harvest+datetime.timedelta(days=end_torr), line_dash="dot", row=1, col=1, line_color='purple', line_width=0.5)
fig.add_annotation(x=target_harvest+datetime.timedelta(days=end_torr),y=0,text="Day "+str(end_torr),showarrow=False,yshift=5,textangle=0,bgcolor='yellow')


fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Wet'],name='Wet',line=dict(color='blue'),showlegend=False),row=2, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Dried'],name='Dried',line=dict(color='red'),showlegend=False),row=2, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Pelletizer Output'],name='Pelletized',line=dict(color='green'),showlegend=False),row=2, col=1,)
fig.add_trace(go.Scatter(x=pd.date_range(target_harvest,target_harvest+datetime.timedelta(rangeend)), y=data['Torrefied Output'],name='Torrefied',line=dict(color='purple'),showlegend=False),row=2, col=1,)

fig.add_vline(x=target_harvest, line_dash="solid", row=2, col=1, line_color='black', line_width=2)
fig.add_vline(x=target_harvest+datetime.timedelta(days=end_torr), line_dash="dot", row=2, col=1, line_color='purple', line_width=0.5)

fig.update_layout(width = 800, height=600,
    margin=dict(l=120, r=20, t=20, b=20),
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.15,
    xanchor="right",
    x=1,
))
                
fig.update_xaxes(range=(datetime.date(2022,9,1),datetime.date(2023,1,1)))
fig.update_yaxes(title_text='Tons Produced',row=1,col=1)
fig.update_yaxes(title_text='Throughput per day (Tons)',row=2,col=1)
main3.plotly_chart(fig)