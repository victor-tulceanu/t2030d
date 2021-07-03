import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from amortization.amount import calculate_amortization_amount
import plotly.io as pio

def create_layout(app):
    pio.renderers.default = "browser"  # fixes graphics loading issue
    app.css.config.serve_locally = True  # loads .css file in assets folder
    app.scripts.config.serve_locally = True
    return html.Div([
        html.H2('Toronto 2030 District',
                style={
                    #'font-color': 'rgb(255,255,255)',
                    'padding-top': '10px',
                    'text-align': 'center',
                    'padding-bottom': '0px',
                    #'background-color': 'rgb(52,58,64)',
                    'margin': '10px'
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
        # -----------------------------------------------------------------------
        # CSS - CARBON TAX SLIDER
        # -----------------------------------------------------------------------
        html.Div(
            className="ct-slider-container",
            style={
                'float': 'left',
                'width': '40%',
                'margin-left': '5%',
                'margin-right': 'auto',
                'padding-bottom': '40px',
                'padding-top': '40px'
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
        # -----------------------------------------------------------------------
        # CSS - AMORTIZATION RATE SLIDER
        # -----------------------------------------------------------------------
        html.Div(
            className="payback-slider-container",
            style={
                'width': '40%',
                'margin-left': 'auto',
                'margin-right': '5%',
                'padding-bottom': '40px',
                'padding-top': '40px'
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
        # -----------------------------------------------------------------------
        # CSS - BOILER EFFICIENCY SLIDER
        # -----------------------------------------------------------------------
        html.Div(
            className="boiler-slider-container",
            style={
                'float': 'left',
                'width': '40%',
                'margin-left': '5%',
                'margin-right': 'auto',
                'padding-bottom': '40px',
                'padding-top': '40px'
            },
            children=[
                html.H5('Boiler Efficiency Heating (%)',
                        style={
                            'padding-bottom': '5px',
                            'text-align': 'center'
                        }
                        ),
                html.P(
                    'this slider allows you to calibrate how efficiently the mechanical systems convert fuel into space heating',
                    style={
                        'font-size': '90%',
                        'text-align': 'center',
                        'padding-bottom': '30px'
                    },
                ),
                dcc.Slider(
                    id='boiler-eff-slider',
                    updatemode='mouseup',
                    min=50,
                    max=100,
                    step=1,
                    value=100,
                    marks={
                        50: '50% of fuel to heat',
                        100: '100%: perfect combustion'
                    },
                    dots=False,
                    tooltip={'always_visible': True}
                ),
            ]
        ),
        # -----------------------------------------------------------------------
        # CSS - BUILDING EFFICIENCY SLIDER
        # -----------------------------------------------------------------------
        html.Div(
            className="building-slider-container",
            style={
                'width': '40%',
                'margin-left': 'auto',
                'margin-right': '5%',
                'padding-bottom': '40px',
                'padding-top': '40px'
            },
            children=[
                html.H5('Building Efficiency Above Average (%)',
                        style={
                            'padding-bottom': '5px',
                            'text-align': 'center'
                        }
                        ),
                html.P(
                    'this slider allows you to calibrate the building energy efficiency relative to the average building in the district:',
                    style={
                        'font-size': '90%',
                        'text-align': 'center',
                        'padding-bottom': '30px'
                    },
                ),
                dcc.Slider(
                    id='building-eff-slider',
                    updatemode='mouseup',
                    min=-50,
                    max=100,
                    step=1,
                    value=0,
                    marks={
                        -50: 'Half as Efficient',
                        0: 'Average Building Efficiency',
                        100: 'Twice as Efficient'
                    },
                    dots=False,
                    tooltip={'always_visible': True}
                ),
            ]
        ),
        # -----------------------------------------------------------------------
        # CSS - BOILER EFFICIENCY COST INPUT
        # -----------------------------------------------------------------------
        html.Div(
            className="boiler-eff-cost-container",
            style={
                'float': 'left',
                'width': '40%',
                'margin-left': '5%',
                'margin-right': 'auto',
                'padding-bottom': '40px',
                'padding-top': '40px'
            },
            children=[
                html.H5('Boiler Efficiency Cost Change (%)',
                        style={
                            'padding-bottom': '5px',
                            'text-align': 'center'
                        }
                        ),
                html.P(
                    'this input controls how much the cost of the mechanical system changes as the heating efficiency improves or declines:',
                    style={
                        'font-size': '90%',
                        'text-align': 'center'
                    },
                ),
                html.Div(
                    style={
                        'padding-bottom': '10px',
                        'text-align': 'center'
                    },
                    children=[dcc.Input(
                        style={
                            'padding-bottom': '20px',
                            'margin-left': 'auto',
                            'margin-right': 'auto',
                            'text-align': 'center',
                            'width': '100px'
                        },
                        id='boiler-eff-cost',
                        min='-99',
                        placeholder='enter % change',
                        type='number',
                        value='0'
                    )
                    ])
            ]
        ),
        # -----------------------------------------------------------------------
        # CSS - BUILDING EFFICIENCY COST INPUT
        # -----------------------------------------------------------------------
        html.Div(
            className="building-eff-cost-container",
            style={
                'width': '40%',
                'margin-left': 'auto',
                'margin-right': '5%',
                'padding-bottom': '40px',
                'padding-top': '40px'
            },
            children=[
                html.H5('Building Efficiency Added Cost ($/sf)',
                        style={
                            'padding-bottom': '5px',
                            'text-align': 'center'
                        }
                        ),
                html.P(
                    'this input allows you to add a baseline $/sf increase for energy efficiency improvements across building categories in accordance to the improved rate above:',
                    style={
                        'font-size': '90%',
                        'text-align': 'center'
                    },
                ),
                html.Div(
                    style={
                        'padding-bottom': '10px',
                        'text-align': 'center',
                        'size': '20px'
                    },
                    children=[dcc.Input(
                        style={
                            'padding-bottom': '20px',
                            'margin-left': 'auto',
                            'margin-right': 'auto',
                            'text-align': 'center',
                            'width': '100px'
                        },
                        id='building-eff-cost',
                        min='0',
                        step='0.25',
                        placeholder='enter added $/sf',
                        type='number',
                        value='0'
                    )]
                )
            ]
        ),
        # -----------------------------------------------------------------------
        # CSS - DISCLAIMER
        # -----------------------------------------------------------------------
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
