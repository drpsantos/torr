import plotly.graph_objects as go
import numpy as np
import maths

def mass_flow_funnel(mass_flows,moisture_content):

    fig = go.Figure(go.Funnelarea(
        # textinfo = [str(round(mass_flows[0],2))+" kg/h <br>Before Drying",str(round(mass_flows[1],2))+" kg/h <br>After Drying",str(mass_flows[2])+" kg/h <br>After Torrefaction"],
        text = ["Before Drying at MC="+str(moisture_content[0])+"%","After Drying at MC="+str(moisture_content[1])+"%","After Torrefaction at MC="+str(moisture_content[2])+"%"],
        values = mass_flows,
        textinfo = 'value+text'

        ))
    fig.update_layout(
        title='Feedstock Mass Flow Requirements (kg/h)',
        title_x=0.5,
        showlegend=False
    )
    fig.update_yaxes(
        showticklabels = False
    )
    return fig
    

def torr_sizing(t1,t2,cp,mfr):
    reactor_diameter = np.arange(0.5,6.0,0.5)
    wall_temp = np.arange(200.0,500.0,100.0)
    results = np.zeros(shape=(len(reactor_diameter),len(wall_temp)))

    for i in range(0,len(reactor_diameter)):
        for j in range(0,len(wall_temp)):
            results[i,j] = maths.get_L_torr(maths.kelvin(wall_temp[j]),maths.kelvin(t1),maths.kelvin(t2),cp,reactor_diameter[i],mfr)

    fig = go.Figure()
    for i in range(0,len(reactor_diameter)):
        fig.add_trace(go.Scatter(x=reactor_diameter,y=results[i,:],name=(str(round(wall_temp[i],2)))))
    fig.update_xaxes(title="Reactor Length (m)")
    fig.update_yaxes(title="Wall Temperature (K)")
    fig.update_layout(
        showlegend=True,
        legend=dict(title="Reactor Diameter (m)"),
        title = "Minimum Reactor Wall Temperature Requirement at ",
        title_x = 0.5
    )
    return fig

