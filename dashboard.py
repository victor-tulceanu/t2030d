import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from amortization.amount import calculate_amortization_amount
import plotly.io as pio

#------------------------------------------------------------
pio.renderers.default = "browser"


app = dash.Dash(__name__)
server = app.server

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

#LOAD DATA
df = pd.read_csv('district_data.csv')
dfa = df  #create a copy

#FUEL VALUES DICTIONARY
fv = {'ng'   : {'str':'ng',   'pgj_rate':3,  'ct_rate':0.061, 'cop':1.0, 'colour':'#231F20', 'label':'Natural Gas'},
      'bh'   : {'str':'bh',   'pgj_rate':18, 'ct_rate':0.007, 'cop':1.0, 'colour':'#4A71B7', 'label':'Blue Hydrogen'},
      'gh'   : {'str':'gh',   'pgj_rate':60, 'ct_rate':0.028, 'cop':1.0, 'colour':'#38B449', 'label':'Green Hydrogen'},
      'er'   : {'str':'er',   'pgj_rate':44, 'ct_rate':0.028, 'cop':1.0, 'colour':'#FBAF3F', 'label':'Electrical Resistance'},
      'ashp' : {'str':'ashp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':2.8, 'colour':'#91268F', 'label':'Air Source Heat Pump'},
      'gshp' : {'str':'gshp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':3.1, 'colour':'#8A5D3B', 'label':'Ground Source Heat Pump'},
      'hyb'  : {'str':'hyb',  'pgj_rate':44, 'ct_rate':0.028, 'cop':2.8, 'colour':'#EF4036', 'label':'Hybrid ASHP & RNG'}
     }

base_pgj_rate = 44

app.layout = html.Div([
      html.H2('Toronto 2030 District',
              style={
                    'padding-top': '10px',
                    'padding-bottom': '0px',
                    'text-align': 'center'
              }
      ),

      html.H5('Yearly Space Heating Cost per Square Foot in Toronto District by Fuel and Building Type',
              style={
                    'padding-top': '0px',
                    'padding-bottom': '0px',
                    'text-align': 'center'
              }
      ),

      dcc.Graph(
            style={
                  'font-size': '200%',
                  'width': '90%',
                  'padding-bottom': '10px',
                  'margin-left': 'auto',
                  'margin-right': 'auto'
            },
            id='graph_output',
            figure={}
      ),

      html.Div(
            className="ct-slider-container",
            style={
                  'float': 'left',
                  'width': '40%',
                  'margin-left': '5%',
                  'margin-right': 'auto',
                  'padding-bottom': '20px'
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

      html.Div(
            className="payback-slider-container",
            style={
                  'width': '40%',
                  'margin-left': 'auto',
                  'margin-right': '5%',
                  'padding-bottom': '20px'
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
                        min=0,
                        max=40,
                        step=1,
                        value=20,
                        marks={
                              0: '0 years',
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

      html.P('*a yearly interest rate of 3% is assumed',
              style={
                  'font-size': '50%',
                  'padding-top': '20px',
                  'padding-bottom': '20px',
                  'text-align': 'center',
                  'margin-right': 'auto',
                  'margin-left': 'auto'
              }
      )
])

# CALLBACK
@app.callback(
      dash.dependencies.Output('graph_output', 'figure'),
      [dash.dependencies.Input('ct-slider', 'value'),
       dash.dependencies.Input('payback-slider', 'value')])
def update_graph(ct_value, payback_value):
      # SET VARIABLES FROM SLIDER
      int_rate = 0.03  # slider
      ct = ct_value  # slider
      int_period = payback_value  # slider

      yaxis_max = []
      avg_list = []
      for i in fv:
            dfa[f'{i}_mech_psf'] = calculate_amortization_amount(dfa[f'{i}_mech_cost'], int_rate,
                                                                 int_period) / dfa.typology_sf
            dfa[f'{i}_elec_psf'] = calculate_amortization_amount(dfa[f'{i}_elec_cost'], int_rate,
                                                                 int_period) / dfa.typology_sf
            dfa[f'{i}_fuel_psf'] = (dfa.base_fuel_cost * (fv[i]['pgj_rate'] / base_pgj_rate) + (
                          fv[i]['ct_rate'] * (ct - 30))) * (1 / fv[i]['cop'])
            dfa[f'{i}_total_psf'] = dfa[f'{i}_mech_psf'] + dfa[f'{i}_elec_psf'] + dfa[f'{i}_fuel_psf']
            yaxis_max.append(dfa[f'{i}_total_psf'].max())
            avg_list.append(dfa[f'{i}_total_psf'].mean())

      #     avg_list_order=sorted(range(len(avg_list)),key=avg_list.__getitem__)

      # GENERATE PLOTS
      fig = make_subplots(rows=1, cols=len(fv))
      for i in fv:
            #         j = list(fv).index(i)
            #         cur_index = avg_list_order[j]
            cur_index = list(fv).index(i)

            fig = go.Figure(
                  fig.add_trace(go.Bar(x=dfa.typology_name,
                                       y=dfa[f'{i}_mech_psf'],
                                       name=fv[i]['label'] + ' - Mechanical',
                                       opacity=1,
                                       marker=dict(color=fv[i]['colour'])),
                                row=1, col=cur_index + 1
                                )
            )
            fig.add_trace(go.Bar(x=dfa.typology_name,
                                 y=dfa[f'{i}_elec_psf'],
                                 name=fv[i]['label'] + ' - Electrical',
                                 opacity=0.3,
                                 marker=dict(color=fv[i]['colour'])),
                          row=1, col=cur_index + 1
                          )
            fig.add_trace(go.Bar(x=dfa.typology_name,
                                 y=dfa[f'{i}_fuel_psf'],
                                 name=fv[i]['label'] + ' - Fuel',
                                 opacity=0.7,
                                 marker=dict(color=fv[i]['colour'])),
                          row=1, col=cur_index + 1
                          )
            fig.update_yaxes(title_text='$ per Square Foor per Year', row=1, col=1)
            fig.update_yaxes(range=[0, max(yaxis_max) + 2])
            fig.update_xaxes(title_text=fv[i]['label'], row=1, col=cur_index + 1)
            avg_y = dfa[f'{i}_total_psf'].mean()
            fig.add_hline(y=avg_y,
                          line_width=4,
                          line_color=fv[i]['colour'],
                          opacity=1,
                          annotation_text=f'avg: {round(avg_y, 2)}$/sf',
                          row=1, col=cur_index + 1
                          )
            fig.update_layout(font_family="Roboto", barmode='stack')

      fig.update_layout(
            #       title_text="Yearly Space Heating Cost per Square Foot in Toronto District by Fuel and Building Type",
            height=640,
            #   width=2000,
            template='simple_white'
      )
      return fig

if __name__ == '__main__':
      app.run_server(debug=True)