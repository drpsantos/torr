import numpy as np

# Physical Constants

# Water
c_pb = 1.36
c_h20l = 4.18
c_h20v = 1.9

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
    T = np.average([t1,t2])
    l = ((32*u_g*(2-oslash_a))/(5*P*oslash_a))*np.sqrt((R_g*T)/(2*np.pi*M))
    laod = ((2*l)+(2*a))/d
    h_wp = ((4*k_g)/d)*(((1+laod)*np.log(1+(1/laod)))-1)
    h_ws = (oslash_w*h_wp)+((1-oslash_w)*((2*k_g/d)/(np.sqrt(2)+laod)))
    L = -np.log((wt-t1)/(wt-t2))*((mfr*cp)/(h_ws*np.pi*dia))
    return L