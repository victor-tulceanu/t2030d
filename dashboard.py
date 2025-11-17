import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from amortization.amount import calculate_amortization_amount
import plotly.io as pio
#-----------------------------------------------------------------------
#PREAMBLES
#-----------------------------------------------------------------------
app = dash.Dash(__name__)
server = app.server

pio.renderers.default = "browser" #fixes graphics loading issue
app.css.config.serve_locally = True #loads .css file in assets folder
app.scripts.config.serve_locally = True
#-----------------------------------------------------------------------
#LOAD DATA
#-----------------------------------------------------------------------
df = pd.read_csv('district_data.csv')
dfa = df  #create a copy
base_pgj_rate = 44 #whatever the base value of electricity is in $/GJ
#-----------------------------------------------------------------------
#FUEL VALUES DICTIONARY
#-----------------------------------------------------------------------
fv = {'ng'   : {'str':'ng',   'pgj_rate':9,  'ct_rate':0.061, 'cop':1.0, 'colour':'35, 31, 32', 'label':'Natural Gas'},
      'bh'   : {'str':'bh',   'pgj_rate':18, 'ct_rate':0.007, 'cop':1.0, 'colour':'74, 113, 183', 'label':'Blue Hydrogen'},
      'gh'   : {'str':'gh',   'pgj_rate':60, 'ct_rate':0.028, 'cop':1.0, 'colour':'56, 180, 73', 'label':'Green Hydrogen'},
      'er'   : {'str':'er',   'pgj_rate':44, 'ct_rate':0.028, 'cop':1.0, 'colour':'251, 175, 63', 'label':'Electrical Resistance'},
      'ashp' : {'str':'ashp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':2.8, 'colour':'145, 38, 143', 'label':'Air Source Heat Pump'},
      'gshp' : {'str':'gshp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':3.1, 'colour':'138, 93, 59', 'label':'Ground Source Heat Pump'},
      'hyb'  : {'str':'hyb',  'pgj_rate':52.7, 'ct_rate':0.028, 'cop':2.8, 'colour':'239, 64, 54', 'label':'Hybrid ASHP & RNG'}
     }
#pgj_rate of hybrid option = 95% elec->(44*0.95 = 41.8) + 5% RNG->(29+9 * 0.05 = 1.9) + 100% NG delivery->(9 * 1 = 9) = 52.7

#-----------------------------------------------------------------------
#CSS - HEADER & FIGURE
#-----------------------------------------------------------------------
app.layout = html.Div([
      html.Header(
        style={
        'padding-top': '0px',
        'padding-bottom': '0px',
        'text-align': 'center',
        'background-color': 'rgb(52,58,64)',
        'margin': '10px'
        },
          children=[
              html.H4('Toronto 2030 District',
                  style={
                      'padding-top': '0px',
                      'padding-bottom': '0px',
                      'text-align': 'center',
                      'background-color': 'rgb(52,58,64)',
                      'color': 'white'
                  },
              ),
          ]
      ),
      html.Div([
          dcc.Graph(
            style={
                  'font-size': '200%',
                  'width': '95%',
                  'padding-bottom': '10px',
                  'margin-left': '2%',
                  'margin-right': 'auto'
            },
            id='graph_output',
            figure={}
      ),
    #-----------------------------------------------------------------------
    #CSS - CARBON TAX SLIDER
    #-----------------------------------------------------------------------
          html.Div(
                className="ct-slider-container",
                style={
                      'float': 'left',
                      'width': '25%',
                      'margin-left': '5%',
                      'margin-right': 'auto',
                      'padding-bottom': '20px',
                      'padding-top': '20px'
                },
                children=[
                      html.H5('Carbon Tax (in $/ton of CO2)',
                              style={
                                    'padding-bottom': '20px',
                                    'text-align': 'center'
                              }
                              ),
                      dcc.Slider(
                            id='ct-slider',
                            updatemode='mouseup',
                            min=30,
                            max=340,
                            step=10,
                            value=30,
                            marks={
                                  30: '30$/ton (current)',
                                  170: '170$/ton (projected)',
                                  340: '340$/ton',
                            },
                            dots=False,
                            tooltip={'always_visible': True}
                      )
                ]
          ),
    #-----------------------------------------------------------------------
    #CSS - AMORTIZATION RATE SLIDER
    #-----------------------------------------------------------------------
          html.Div(
                className="payback-slider-container",
                style={
                      'width': '25%',
                      'margin-left': '35%',
                      'margin-right': 'auto',
                      'padding-bottom': '20px',
                      'padding-top': '20px'
                },
                children=[
                      html.H5('Amortization Period of Capital Costs in Years*',
                              style={
                                    'padding-bottom': '20px',
                                    'text-align': 'center'
                              }
                              ),
                      dcc.Slider(
                            id='payback-slider',
                            updatemode='mouseup',
                            min=1,
                            max=40,
                            step=1,
                            value=20,
                            marks={
                                  1: '1 year',
                                  10: '10 years',
                                  20: '20 years',
                                  30: '30 years',
                                  40: '40 years',
                            },
                            dots=True,
                            tooltip={'always_visible': True}
                      )
                ]
          ),
    #-----------------------------------------------------------------------
    #CSS - ELEC PRICE SLIDER
    #-----------------------------------------------------------------------
          html.Div(
                className="elec-price-slider-container",
                style={
                      'float': 'left',
                      'width': '25%',
                      'margin-left': '5%',
                      'margin-right': 'auto',
                      'padding-bottom': '20px',
                      'padding-top': '20px'
                },
                children=[
                      html.H5('Assumed Price of Electricity ($/kWh)',
                              style={
                                    'padding-bottom': '20px',
                                    'text-align': 'center'
                              }
                              ),
                      dcc.Slider(
                            id='elec-slider',
                            updatemode='mouseup',
                            min=0.00,
                            max=0.30,
                            step=0.01,
                            value=0.16,
                            marks={
                                  0: '0.00$/kWH',
                                  0.16: '0.16$/kWH',
                                  0.30: '0.30$/kWH',
                            },
                            dots=True,
                            tooltip={'always_visible': True}
                      )
                ]
          ),
    #-----------------------------------------------------------------------
    #CSS - AMORTIZATION RATE SLIDER
    #-----------------------------------------------------------------------
          html.Div(
                className="interest-slider-container",
                style={
                      'width': '25%',
                      'margin-left': '35%',
                      'margin-right': 'auto',
                      'padding-bottom': '20px',
                      'padding-top': '20px'
                },
                children=[
                      html.H5('Interest Rate',
                              style={
                                    'padding-bottom': '20px',
                                    'text-align': 'center'
                              }
                              ),
                      dcc.Slider(
                            id='interest-slider',
                            updatemode='mouseup',
                            min=0,
                            max=10,
                            step=0.5,
                            value=5,
                            marks={
                                  0: '0.0% interest',
                                  5: '5.0% interest',
                                  10: '10.0% interest'
                            },
                            dots=True,
                            tooltip={'always_visible': True}
                      )
                ]
          ),
          ])
#-----------------------------------------------------------------------
#CSS - DISCLAIMER
#-----------------------------------------------------------------------
      # html.P('*a yearly interest rate of 3% is assumed',
      #         style={
      #             'font-size': '50%',
      #             'padding-top': '20px',
      #             'padding-bottom': '20px',
      #             'text-align': 'center',
      #             'margin-right': 'auto',
      #             'margin-left': 'auto'
      #         }
      # )
])
#-----------------------------------------------------------------------
#CALLBACK
#-----------------------------------------------------------------------
@app.callback(
      dash.dependencies.Output('graph_output', 'figure'),
      [dash.dependencies.Input('ct-slider', 'value'),
       dash.dependencies.Input('payback-slider', 'value'),
       dash.dependencies.Input('elec-slider', 'value'),
       dash.dependencies.Input('interest-slider', 'value'),
      ]
)
#-----------------------------------------------------------------------
#UPDATE FUNCTION
#-----------------------------------------------------------------------
def update_graph(ct_value, payback_value, elec_value, interest_value):


      ct = ct_value  # slider
      int_period = payback_value  # slider
      int_rate = (interest_value / 100)  # slider

#DIRTY WAY TO UPDATE VARIABLE ELECTRICITY PRICES (FROM SLIDER)
      fv['er']['pgj_rate'] = elec_value / 0.0036
      fv['ashp']['pgj_rate'] = elec_value / 0.0036
      fv['gshp']['pgj_rate'] = elec_value / 0.0036
      fv['hyb']['pgj_rate'] = ((elec_value * 0.95) / 0.0036) + ((29+9) * 0.05)
      # pgj_rate of hybrid option = 95% elec->(44*0.95 = 41.8) + 5% RNG->(29+9 * 0.05 = 1.9) + 100% NG delivery->(9 * 1 = 9) = 52.7

      yaxis_max = []
      avg_list = []
      for i in fv:

            dfa[f'{i}_mech_psf'] = calculate_amortization_amount(dfa[f'{i}_mech_cost'], int_rate, int_period) / dfa.typology_sf
            dfa[f'{i}_elec_psf'] = calculate_amortization_amount(dfa[f'{i}_elec_cost'], int_rate, int_period) / dfa.typology_sf
            dfa[f'{i}_fuel_psf'] = (dfa.base_fuel_cost * ((fv[i]['pgj_rate'] + (fv[i]['ct_rate'] * (ct - 30))) / base_pgj_rate)) * (1 / fv[i]['cop'])
            dfa[f'{i}_total_psf'] = dfa[f'{i}_mech_psf'] + dfa[f'{i}_elec_psf'] + dfa[f'{i}_fuel_psf']
            yaxis_max.append(dfa[f'{i}_total_psf'].max())
            avg_list.append(dfa[f'{i}_total_psf'].mean())

      # GENERATE PLOTS
      fig = make_subplots(rows=1, cols=len(fv))

      for i in fv:
            cur_index = list(fv).index(i)
            cur_colour = fv[i]['colour']
            pgj_rate_value = fv[i]['pgj_rate']
            fig = go.Figure(
                  fig.add_trace(go.Bar(x=dfa.typology_name,
                                       y=round(dfa[f'{i}_mech_psf'],2),
                                       name='Mechanical System $/sf',
                                       marker=dict(color=f'rgba({cur_colour},1)', line=dict(width=1, color=f'rgba({cur_colour},1)'))),
                                       row=1, col=cur_index + 1
                                )
                  )
            fig.add_trace(go.Bar(x=dfa.typology_name,
                                 y=round(dfa[f'{i}_elec_psf'],2),
                                 name='Electrical System $/sf',
                                 marker=dict(color=f'rgba({cur_colour},0.25)', line=dict(width=1, color=f'rgba({cur_colour},1)'))),
                                 row=1, col=cur_index + 1
                         )
            fig.add_trace(go.Bar(x=dfa.typology_name,
                                 y=round(dfa[f'{i}_fuel_psf'],2),
                                 name='Fuel Cost $/sf',
                                 marker=dict(color=f'rgba({cur_colour},0.67)', line=dict(width=1, color=f'rgba({cur_colour},1)'))),
                                 row=1, col=cur_index + 1
                         )
            fig.update_yaxes(title_text='$ per Square Foot per Year', row=1, col=1)
            fig.update_yaxes(range=[0, max(yaxis_max) + 1])
            fig.update_xaxes(title_text=fv[i]['label'], row=1, col=cur_index + 1)
            avg_y = dfa[f'{i}_total_psf'].mean()
            fig.add_hline(y=avg_y,
                          line_width=4,
                          line_color=f'rgba({cur_colour},1)',
                          opacity=1,
                          annotation_text=f'avg: {round(avg_y, 2)}$/sf',
                          row=1, col=cur_index + 1
                          )
            fig.update_layout(font_family="Roboto", barmode='stack', hovermode='x unified',
                              hoverlabel=dict(namelength=-1),
                              showlegend=False
                             )
      # fig.add_annotation(x=dfa.typology_name, y=[max(yaxis_max) - 1],
      #                    text=f'Electricity Cost = {round(pgj_rate_value, 2)}$/GJ',
      #                    showarrow=False,
      #                    arrowhead=1)

      fig.add_annotation(text=f'Carbon Tax = {round(ct, 0)}$/ton',
                         xref="paper", yref="paper",
                         x=0.01, y=0.95, showarrow=False)
      fig.add_annotation(text=f'Electricity Cost = {round(pgj_rate_value, 2)}$/GJ',
                         xref="paper", yref="paper",
                         x=0.01, y=0.90, showarrow=False)
      fig.add_annotation(text=f'Amortization Period = {int_period} years',
                         xref="paper", yref="paper",
                         x=0.01, y=0.85, showarrow=False)
      fig.add_annotation(text=f'Interest Rate = {round(int_rate*100, 1)}%',
                         xref="paper", yref="paper",
                         x=0.01, y=0.80, showarrow=False)

      fig.update_layout(
            title_text="Yearly Space Heating Cost per Square Foot in Toronto District by Fuel and Building Type",
            title_x=0.5,
            height=640,
            #   width=2000,
            template='simple_white'
      )
      return fig

if __name__ == '__main__':
      app.run_server(debug=False)

