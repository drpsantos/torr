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
    st.caption('LAST UPDATED: 09/21/2021')
    st.caption('This dashboard is interactive. Feel free to change the values of the parameters in each section. The dashboard will automatically recalculate the entire report for you :smiley:')


    st.header('Project Updates as of September 21, 2021')
    update = Image.open('update.png')
    st.image(update)

    st.header('I. Production Overview')
    st.caption('This section estimates the minimum operating requirements to meet the desired torrefied biomass quality and production rate.')
    sec1params = st.expander('Parameters',expanded=True)
    sec1results = st.expander('Results',expanded=True)
    #sec1eqs = st.expander('Working Equations',expanded=False)
    sec1params.caption('You can adjust these variables!')
    s1col1,s1col2,s1col3 = sec1params.columns((1,1,1))

    mc_w = s1col1.number_input('Wet Biomass Moisture Content (%wt)',50.0,90.0,50.0,5.0)
    mc_d = s1col2.number_input('Dried Biomass Moisture Content (%wt)',10.0,mc_w,30.0,1.0)
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

    #sec1eqs.caption('To be added soon!')
    #right.plotly_chart(charts.torr_sizing(t_d,t_t,cp_t,m_t))
    #right.plotly_chart(charts.mass_flow_funnel([str(round(mw,2)),str(round(md,2)),str(mt)],[mc_w,mc_d,mc_t]))
    #right.text('To produce '+str(mt)+' kg/h of torrefied biomass, '+str(round(md,2))+' kg/h of dried biomass is needed')

    st.header('II. Sizing of the Torrefaction Reactor')
    fig1 = Image.open('fig1.png')
    fig2 = Image.open('fig2.png')

    st.caption('This section provides an estimation on the required reactor length to achieve the torrefied standards as initialized in Section I. Calculations are for a screw conveyor torrefaction reactor and are based off O&#39;Brien&#39;s model. Constraints such as reactor diameter, motor RPM, conveyor fill factor, and the assumed heat losses are predefined by the user.')
    st.image(fig1,caption='Sample Torrefaction Reactor Configuration')
    st.image(fig2,caption='Thermal Analysis Configuration')
    sec2params = st.expander('Parameters',expanded=True)
    sec2results = st.expander('Results',expanded=True)
    # sec2eqs = st.expander('Working Equations',expanded=False)
    # sec2eqs.caption('To be added soon!')
    s2col1,s2col2 = sec2params.columns((1,1))

    s2col1.text('Reactor Parameters')
    d_reactor = s2col1.number_input('Reactor Diameter (in)',5.0,30.0,18.0,0.5)
    rpm_screw = s2col1.number_input('Conveyor Rotational Frequency (RPM)',0.5,6.0,1.0,0.5)
    fill_frac = s2col1.number_input('Conveyor Fill Factor',0.1,0.8,0.6,0.05)
    s2col2.text('Thermal Parameters')
    heat_loss = s2col2.number_input('System Loss (%)',1.0,99.0,10.0,1.0)/100

    sec2resultsdf = maths.get_sec2results(cp_t,t_d,t_t,d_reactor,fill_frac,rpm_screw)
    sec2results.dataframe(sec2resultsdf)
    mfrate = sec2resultsdf['Value'][1]
    sec2results.plotly_chart(charts.torr_analysis(t_d,t_t,mfrate,d_reactor,rpm_screw,heat_loss,cp_t))



    st.header('III. Rocket Stove')
    st.caption('This section provides a basic calculation of the rocket stove&#39;s output based from experimental data. A sizing guide is developed to estimate the power output given the user-defined geometry.')
    
    sec3expresults = st.expander('Experiment 001', expanded =True)
    sec3expresults.subheader('Experiment Setup')
    sec3expresults.write('The available rocket stove (RS-1) was tested to evaluate the heat output of the system. The temperature at the outlet and at half the height stack was measured.')
    sec3expresults.subheader('Experiment Results')
    sec3expresults.markdown('The rocket stove was able to achieve a maximum outlet temperature of 480 degc and a mid-stack temperature of 280 degC. The computed heat output rate for RS-1 is at **131.81 J/s** or **474.50 kJ/h**')

    sec3exp2results = st.expander('Experiment 002',expanded=True)
    #sec3params = st.expander('Parameters',expanded=True)
    #sec3results = st.expander('Results',expanded=True)
    #sec3eqs = st.expander('Working Equations',expanded=False)

    sec3exp2results.subheader('Experiment Setup')
    sec3exp2results.write('The MBGF (Moving Bed Granular Filter) was fitted with the Rocket Stove (RS) as its primary heat source. Approximately 48kg of sand was placed in a chamber and the temperature was monitored for an hour without movement in the bed. The next hour, sand was conveyed out of the system and its temperature was measured.')
    sec3exp2results.subheader('Experiment Results')
    sec3exp2results.markdown('The sand was able to reach a temperature of 126.4 degC after being heated for 170 mins. The computed sand heating rate is at **0.0123 degC/min kg**. The hot gas has an average temperature difference of 58.62 degC which can be approximated to a **42.08 kJ input of heat/kg of hot air.** This input contributes to the heating of the sand as well as losses from metal parts inside the MBGF')

    sec3insights = st.expander('Insights & Recommendations',expanded=True)
    sec3insights.markdown('At our current RS state, we can heat up 48kg (1 MBGF full) of sand to 500 degC in 803.38 mins./13.38 hours.')
    sec3insights.markdown('Further development of RS design is recommended.')


    # q_rocketstove = sec3params.number_input('Heat Input from Rocket Stove (kW)',10.0,1000.0,500.0,)



