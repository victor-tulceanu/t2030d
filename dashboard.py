import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from amortization.amount import calculate_amortization_amount
import plotly.io as pio
from pages import typologies

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
fv = {'ng'   : {'str':'ng',   'pgj_rate':12,  'ct_rate':0.061, 'cop':1.0, 'colour':'35, 31, 32', 'label':'Natural Gas'},
      'bh'   : {'str':'bh',   'pgj_rate':20.5, 'ct_rate':0.007, 'cop':1.0, 'colour':'74, 113, 183', 'label':'Blue Hydrogen'},
      'gh'   : {'str':'gh',   'pgj_rate':61.5, 'ct_rate':0.028, 'cop':1.0, 'colour':'56, 180, 73', 'label':'Green Hydrogen'},
      'er'   : {'str':'er',   'pgj_rate':44, 'ct_rate':0.028, 'cop':1.0, 'colour':'251, 175, 63', 'label':'Electrical Resistance'},
      'ashp' : {'str':'ashp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':2.8, 'colour':'145, 38, 143', 'label':'Air Source Heat Pump'},
      'gshp' : {'str':'gshp', 'pgj_rate':44, 'ct_rate':0.028, 'cop':3.1, 'colour':'138, 93, 59', 'label':'Ground Source Heat Pump'},
      'hyb'  : {'str':'hyb',  'pgj_rate':44, 'ct_rate':0.028, 'cop':2.8, 'colour':'239, 64, 54', 'label':'Hybrid ASHP & RNG'}
     }
#-----------------------------------------------------------------------
#CSS - HEADER & FIGURE
#-----------------------------------------------------------------------
app.layout = typologies.create_layout(app)
#-----------------------------------------------------------------------
#CALLBACK
#-----------------------------------------------------------------------
@app.callback(
      dash.dependencies.Output('graph_output', 'figure'),
      [dash.dependencies.Input('ct-slider', 'value'),
       dash.dependencies.Input('payback-slider', 'value'),
       dash.dependencies.Input('boiler-eff-slider', 'value'),
       dash.dependencies.Input('boiler-eff-cost', 'value'),
       dash.dependencies.Input('building-eff-slider', 'value'),
       dash.dependencies.Input('building-eff-cost', 'value'),
      ]
)
#-----------------------------------------------------------------------
#UPDATE FUNCTION
#-----------------------------------------------------------------------
def update_graph(ct_value, payback_value, boiler_eff, boiler_eff_cost, building_eff, building_eff_cost):

      int_rate = 0.03  # slider
      ct = ct_value  # slider
      int_period = payback_value  # slider
      boil_eff = int(boiler_eff)
      boil_eff_cost = int(boiler_eff_cost)
      buil_eff = int(building_eff)
      buil_eff_cost = float(building_eff_cost)

      yaxis_max = []
      avg_list = []
      for i in fv:

            dfa[f'{i}_mech_psf'] = calculate_amortization_amount((dfa[f'{i}_mech_cost'] * ((boil_eff_cost / 100) + 1)), int_rate, int_period) / dfa.typology_sf
            dfa[f'{i}_elec_psf'] = calculate_amortization_amount(dfa[f'{i}_elec_cost'], int_rate, int_period) / dfa.typology_sf
            dfa[f'{i}_fuel_psf'] = (dfa.base_fuel_cost * ((fv[i]['pgj_rate'] + (fv[i]['ct_rate'] * (ct - 30))) / base_pgj_rate)) * (1 / fv[i]['cop']) * (100 / boil_eff) * (1/(1+(buil_eff / 100)))
            dfa[f'{i}_eff_psf'] = buil_eff_cost
            dfa[f'{i}_total_psf'] = dfa[f'{i}_mech_psf'] + dfa[f'{i}_elec_psf'] + dfa[f'{i}_fuel_psf'] + dfa[f'{i}_eff_psf']
            yaxis_max.append(dfa[f'{i}_total_psf'].max())
            avg_list.append(dfa[f'{i}_total_psf'].mean())

      # GENERATE PLOTS
      fig = make_subplots(rows=1, cols=len(fv))
      for i in fv:
            cur_index = list(fv).index(i)
            cur_colour = fv[i]['colour']

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
            fig.add_trace(go.Bar(x=dfa.typology_name,
                                 y=round(dfa[f'{i}_eff_psf'],2),
                                 name='Efficiency Upgrade $/sf',
                                 opacity=1,
                                 marker=dict(color='white', line=dict(width=1, color=f'rgba({cur_colour},1)'))),
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

      fig.update_layout(
            title_text="Yearly Space Heating Cost per Square Foot in Toronto District by Fuel and Building Type",
            title_x=0.5,
            height=640,
            #   width=2000,
            template='simple_white'
      )
      return fig

if __name__ == '__main__':
      app.run_server(debug=True)

