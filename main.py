import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import maths
import charts
import pandas as pd
from PIL import Image


st.set_page_config(page_title="Torrefaction Dashboard",layout="centered",initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.sidebar.title('PMRR Design Dashboard')
password = st.sidebar.text_input(label='Enter password to access report')

if password == st.secrets['report_password']:
    st.title('PMRR Torrefaction Design Dashboard')
    st.caption('Initial Calculations as of SEP 19 2021')
    st.caption('This dashboard is interactive. Feel free to change the values of the parameters in each section. The dashboard will automatically recalculate the entire report for you :smiley:')

    st.header('I. Production Overview')
    st.caption('This section estimates the minimum operating requirements to meet the desired torrefied biomass quality and production rate.')
    sec1params = st.expander('Parameters',expanded=True)
    sec1results = st.expander('Results',expanded=True)
    sec1eqs = st.expander('Working Equations',expanded=False)
    sec1params.caption('You can adjust these variables!')
    s1col1,s1col2,s1col3 = sec1params.columns((1,1,1))

    mc_w = s1col1.number_input('Wet Biomass Moisture Content (%wt)',50.0,90.0,50.0,5.0)
    mc_d = s1col2.number_input('Dried Biomass Moisture Content (%wt)',20.0,mc_w,30.0,1.0)
    mc_t = s1col3.number_input('Torrefied Biomass Moisture Content (%wt)',2.0,mc_d,10.0,1.0)
    t_w = s1col1.number_input('Bulk Biomass Wet Temperature (degC)',25.0,30.0,25.0,1.0)
    t_d = s1col2.number_input('Bulk Biomass Dried Temperature (degC)',t_w,200.0,120.0,1.0)
    t_t = s1col3.number_input('Bulk Biomass Torrefied Temperature (degC)',t_d,300.0,280.0,1.0)
    m_t = s1col3.number_input('Torrefied Biomass Production Rate (kg/h)',10.0,300.0,250.0)

    # Calculation of Parameters
    m_d = maths.get_m_in(m_t,mc_d/100,mc_t/100)
    m_w = maths.get_m_in(m_d,mc_w/100,mc_d/100)
    cp_d = maths.get_CP(m_w,mc_w/100,mc_d/100)
    cp_t = maths.get_CP(m_d,mc_d/100,mc_t/100)
    q_d = maths.get_Q(m_w,cp_d,t_w,t_d)
    q_t = maths.get_Q(m_d,cp_t,t_d,t_t)

    sec1rdict = {
        'Parameter':["Mass Flow Rate","Moisture Content In","Moisture Content Out","Bulk Heat Capacity","Initial Bulk Temperature","Final Bulk Temperature","Heat Requirement"],
        'Units':["kg/h","%wt","%wt","kJ/kg K","degC","degC","kJ/h"],
        'Wet':[round(m_w,2),np.nan,mc_w,np.nan,np.nan,t_w,np.nan],
        'Drying':[round(m_d,2),mc_w,mc_d,cp_d,t_w,t_d,q_d],
        'Torrefaction':[round(m_t,2),mc_d,mc_t,cp_t,t_d,t_t,q_t],
    }
    sec1resultsdf = pd.DataFrame(sec1rdict)
    sec1results.dataframe(sec1resultsdf)

    sec1eqs.caption('To be added soon!')
    #right.plotly_chart(charts.torr_sizing(t_d,t_t,cp_t,m_t))
    #right.plotly_chart(charts.mass_flow_funnel([str(round(mw,2)),str(round(md,2)),str(mt)],[mc_w,mc_d,mc_t]))
    #right.text('To produce '+str(mt)+' kg/h of torrefied biomass, '+str(round(md,2))+' kg/h of dried biomass is needed')

    st.header('II. Sizing of the Torrefaction Reactor')
    fig1 = Image.open('fig1.png')
    st.caption('This section provides an estimation on the required reactor length to achieve the torrefied standards as initialized in Section I. Calculations are for a screw conveyor torrefaction reactor and are based off O&#39;Brien&#39;s model. Constraints such as reactor diameter, feedstock heating rate, and motor RPM are preset by the user.')
    st.image(fig1,caption='Sample Torrefaction Reactor Configuration')
    sec2params = st.expander('Parameters',expanded=True)
    sec2results = st.expander('Results',expanded=True)
    sec2eqs = st.expander('Working Equations',expanded=False)
    sec2eqs.caption('To be added soon!')
    s2col1,s2col2 = sec2params.columns((1,1))

    s2col1.text('Reactor Parameters')
    d_reactor = s2col1.number_input('Reactor Diameter (in)',5.0,30.0,18.0,0.5)
    rpm_screw = s2col1.number_input('Conveyor Rotational Frequency (RPM)',0.5,6.0,1.0,0.5)
    fill_frac = s2col1.number_input('Conveyor Fill Factor',0.1,0.8,0.6,0.05)
    s2col2.text('Thermal Parameters')
    heat_loss = s2col2.number_input('System Loss (%)',0.01,0.99,0.1,0.01)

    sec2resultsdf = maths.get_sec2results(cp_t,t_d,t_t,d_reactor,fill_frac,rpm_screw)
    sec2results.dataframe(sec2resultsdf)
    mfrate = sec2resultsdf['Value'][1]
    sec2results.plotly_chart(charts.torr_analysis(t_d,t_t,mfrate,d_reactor,rpm_screw,heat_loss,cp_t))



    # st.header('III. Heat Transfer Analysis for Torrefaction Reactor')
    # st.caption('This section provides a basic simulation of the heat transfer in the system given a predefined heat input. Only heat transfer via conduction is considered in this simulation.')
    # st.caption('Content to be added by 20 SEP 2021')
    # sec3params = st.expander('Parameters',expanded=True)
    # sec3results = st.expander('Results',expanded=True)
    # sec3eqs = st.expander('Working Equations',expanded=False)
    # sec2eqs.caption('To be added soon!')

    

    # q_rocketstove = sec3params.number_input('Heat Input from Rocket Stove (kW)',10.0,1000.0,500.0,)



