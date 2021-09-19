import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import maths
import charts
import pandas as pd


st.set_page_config(page_title="Torrefaction Dashboard",layout="wide",initial_sidebar_state="collapsed")

st.title('PMRR Torrefaction Design Dashboard')

st.sidebar.title('Dashboard Features')
st.header('Minimum Operating Requirements')
left,right = st.columns((1,3))
left.subheader('Parameters')
left.caption('You can adjust these variables!')

m_t = left.number_input('Torrefied Biomass Production Rate (kg/h)',10.0,300.0,250.0)
mc_w = left.number_input('Wet Biomass Moisture Content (%wt)',50.0,90.0,50.0,5.0)
mc_d = left.number_input('Dried Biomass Moisture Content (%wt)',20.0,mc_w,30.0,1.0)
mc_t = left.number_input('Torrefied Biomass Moisture Content (%wt)',2.0,mc_d,10.0,1.0)
t_w = left.number_input('Bulk Biomass Wet Temperature (degC)',25.0,30.0,25.0,1.0)
t_d = left.number_input('Bulk Biomass Dried Temperature (degC)',t_w,200.0,120.0,1.0)
t_t = left.number_input('Bulk Biomass Torrefied Temperature (degC)',t_d,300.0,280.0,1.0)

# Calculation of Parameters
m_d = maths.get_m_in(m_t,mc_d/100,mc_t/100)
m_w = maths.get_m_in(m_d,mc_w/100,mc_d/100)
cp_d = maths.get_CP(m_w,mc_w,mc_d)
cp_t = maths.get_CP(m_d,mc_d,mc_t)
q_d = maths.get_Q(m_w,cp_d,t_w,t_d)
q_t = maths.get_Q(m_d,cp_t,t_d,t_t)

rdict = {
    'Parameter':["Mass Flow Rate","Moisture Content In","Moisture Content Out","Bulk Heat Capacity","Initial Bulk Temperature","Final Bulk Temperature","Heat Requirement"],
    'Units':["kg/h","%wt","%wt","kJ/kg K","degC","degC","kJ/h"],
    'Wet':[round(m_w,2),np.nan,mc_w,np.nan,np.nan,t_w,np.nan],
    'Drying':[round(m_d,2),mc_w,mc_d,cp_d,t_w,t_d,q_d],
    'Torrefaction':[round(m_t,2),mc_d,mc_t,cp_t,t_d,t_t,q_t],
}
results = pd.DataFrame(rdict)


right.subheader('Calculated Results')
right.caption('Here are our estimates given your input.')
right.dataframe(results)
right.plotly_chart(charts.torr_sizing(t_d,t_t,cp_t,m_t))
#right.plotly_chart(charts.mass_flow_funnel([str(round(mw,2)),str(round(md,2)),str(mt)],[mc_w,mc_d,mc_t]))
#right.text('To produce '+str(mt)+' kg/h of torrefied biomass, '+str(round(md,2))+' kg/h of dried biomass is needed')

const = st.expander('Physical Constants')

