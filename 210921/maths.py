import numpy as np

# Physical Constants
c_pb = 1.36
c_h20l = 4.18
c_h20v = 1.9
rho_biomass = 380.0 #kg/m3
rho_sand = 1631.0 #kg/m3
k_ss = 0.8
rho_ss = 8000.0
cp_ss = 0.468 #kJ/kg K
cp_sand = 1.130 #kJ/kg K
cp_air = 0.718 #kJ/kg  K

#Conversion Constants
hourstoseconds = 1/3600

# OBrien Constants
R_g = 8.314
P = 101325
oslash_a = 0.8
oslash_w = 0.8
M = 0.0289
k_g = 0.026
k_p = 0.109
d = 0.0127
a = 0.0005
u_g = 0.000019


def kelvin(temp):
    k = temp + 273.15
    return k

def get_CP(m_biomass,mc_in,mc_out):
    m_biomass = m_biomass*hourstoseconds
    m_h2oin = (m_biomass*mc_in)
    m_h20out = (m_biomass*mc_out)
    m_h20vout = m_h2oin-m_h20out
    cp = ((c_pb*m_biomass)+(c_h20l*m_h20out)+(c_h20v*m_h20vout))/(m_biomass+m_h20out+m_h20vout)
    return cp

def get_m_in(m_out,mc_in,mc_out):
    m_in = m_out*(1-mc_out)/(1-mc_in)
    return m_in

def get_Q(mfr,cp,t1,t2):
    Q = mfr*cp*(kelvin(t2)-kelvin(t1))
    return Q

def get_L_torr(wt,t1,t2,cp,dia,mfr):
    T = kelvin(np.average([t1,t2]))
    l = ((32*u_g*(2-oslash_a))/(5*P*oslash_a))*np.sqrt((R_g*T)/(2*np.pi*M))
    laod = ((2*l)+(2*a))/d
    h_wp = ((4*k_g)/d)*(((1+laod)*np.log(1+(1/laod)))-1)
    h_ws = (oslash_w*h_wp)+((1-oslash_w)*((2*k_g/d)/(np.sqrt(2)+laod)))
    L = -np.log((wt-t2)/(wt-t1))*((mfr*cp)/(h_ws*np.pi*dia))

def get_sec2results(cp,t1,t2,d_reactor,fill_frac,rpm_screw):
    d_reactor = d_reactor*0.0254
    thick_m = 0.003
    d_shaft = 0.05*d_reactor
    r_shaft = d_shaft/2
    r_reactor = (d_reactor/2)-thick_m
    r_pitch_ratio = 1.0
    pitch_screw = r_reactor*r_pitch_ratio
    d_sleeve = 1.5*d_reactor
    r_sleeve = (d_sleeve/2)-thick_m
    fill_frac = 0.6
    v_rev = (np.pi/4)*(np.power(r_reactor,2)-np.power(r_shaft,2))*pitch_screw*fill_frac
    vfrate = (v_rev*rpm_screw/60)*rho_biomass/60
    mfrate = rho_biomass*vfrate
    mfrate_h = mfrate*3600

    sec2rdict = {
    'Parameter':['Volumetric Flow Rate','Mass Flow Rate (Dried Biomass)','',],
    'Variable':['v_frate','m_frate','',],
    'Value':[round(vfrate,4),round(mfrate,4),round(mfrate_h,4)],
    'Units':['m3/s','kg/s','kg/h',],
    }
    return sec2rdict

def get_thermal_analysis(t1,t2,mfrate,deltaT,d_reactor,rpm_screw,heat_loss,cp):
    d_reactor = d_reactor*0.0254
    thick_m = 0.003
    d_shaft = 0.05*d_reactor
    r_shaft = d_shaft/2
    r_reactor = (d_reactor/2)-thick_m
    r_pitch_ratio = 1.0
    pitch_screw = r_reactor*r_pitch_ratio
    d_sleeve = 1.5*d_reactor
    r_sleeve = (d_sleeve/2)-thick_m

    # Get Residence Time
    t_res = (t2-t1)/deltaT
    t_res_s = t_res/60
    L_reactor = (rpm_screw*t_res)/pitch_screw

    q_bps = mfrate*cp*deltaT/60
    q_perm = q_bps*t_res_s/L_reactor
    T = kelvin(t2)
    l = ((32*u_g*(2-oslash_a))/(5*P*oslash_a))*np.sqrt((R_g*T)/(2*np.pi*M))
    laod = ((2*l)+(2*a))/d
    h_wp = ((4*k_g)/d)*(((1+laod)*np.log(1+(1/laod)))-1)
    h_ws = (oslash_w*h_wp)+((1-oslash_w)*((2*k_g/d)/(np.sqrt(2)+laod)))
    g = -((h_ws*np.pi*d_reactor*L_reactor)/(mfrate*cp))
    t_wall = (kelvin(t2)+(kelvin(t1)*np.exp(g)))/(1-np.exp(g))
    rho_air = P/(R_g*kelvin(t2))
    q_reactor = mfrate*cp*(deltaT/60)
    t_rw = kelvin(t2)
    t_ws = (np.log((r_reactor-thick_m)/r_reactor)*q_reactor)/(2*np.pi*L_reactor*k_ss)+t_rw
    vol_rw = np.pi*L_reactor*(np.power(r_reactor,2)-np.power(r_reactor-thick_m,2))
    m_rw = vol_rw*rho_ss
    q_rw_abs = m_rw*cp_ss*deltaT/60
    q_wall = q_rw_abs + q_reactor
    vol_htm = np.pi*L_reactor*(np.power(r_sleeve,2)-np.power(r_reactor,2))
    mass_htm = vol_htm*rho_sand
    q_htm_abs = mass_htm*cp_sand*deltaT/60
    q_htm = q_htm_abs + q_wall
    mass_htm_a = vol_htm*rho_air
    q_htm_abs_a = mass_htm*cp_air*deltaT/60
    q_htm_a = q_htm_abs_a + q_wall
    q_htm_h = q_htm*3600
    q_htm_a_h = q_htm_a*3600
    htm_diff = (q_htm/q_htm_a)
    htm_diff_h = q_htm_h/q_htm_a_h
    q_sys = (1+heat_loss)*q_htm
    q_sys_a = (1+heat_loss)*q_htm_a

    return [t_res, L_reactor, q_reactor,q_rw_abs,q_htm_abs,q_htm_abs_a,q_sys,q_sys_a]