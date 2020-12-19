# %%
from IPython.display import display
from plotly.subplots import make_subplots
import pandas as pd
import matplotlib as plt
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import pickle

from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



# %%
df = pd.read_pickle('../data/main_df.pkl')
players_df = pd.read_pickle('../data/details_df.pkl')
# %% [markdown]
#~~best overall wins by conference?~~

#~~best overall team by wins~~
#   - ~~home~~
#   - ~~away~~
# 
# ~~most losses~~
# - ~~home~~
# - ~~away~~
# 
# ~~stats for all the below aggregated by latest highest stat per player position and team~~
# ~~Rebounds~~
# ~~Field~~
# ~~Field Goals Attempted~~
# ~~3Pt Made~~
# ~~3Pt Attempted~~
# ~~Free Throws Made~~
# ~~Free Throws Attempted~~
# ~~Offensive Rebounds~~
# ~~Defensive Rebounds~~
# ~~Steals~~
# ~~Blocks~~
# ~~Turn Overs~~
# ~~Personal Fouls~~
# 
# 
# 
# 
# 
# 
# 
#~~defense wins games - pressure busts pipes -  analyze impact~~
#~~pressure makes diamonds - look into highest scoring individuals~~
#~~   - overall~~
#~~   - by conference~~

# time series of scoring?

# look into relationship between home team win pct at arenas vs centers vs other for funsies
# 
# look into raptor rating
# 




# %%
# plt.figure(figsize=(20,15))
# df.hist(figsize=(20,15));
# %%
# Create all win/loss numbers in order to gather sums later
df['away_team_wins'] = df['home_team_wins'].apply(lambda x: 1.0 if x == 0 else 0)
df['home_team_losses'] = df['away_team_wins'].apply(lambda x: 1.0 if x == 1 else 0)
df['away_team_losses'] = df['home_team_wins'].apply(lambda x: 1.0 if x == 1 else 0)
# %%
# %%
# Groups sums of home team stats for the entire data
home_history_totals = df.groupby(by='home_team_id').sum()[['home_team_wins','home_team_losses','sum_of_fgm_home','sum_of_fga_home', 'sum_of_fg3m_home', 'sum_of_fg3a_home','sum_of_ftm_home', 'sum_of_fta_home','sum_of_oreb_home','sum_of_dreb_home', 'sum_of_stl_home', 'sum_of_blk_home','sum_of_to_home', 'sum_of_pf_home']]

# Groups sums of away team stats for the entire data
away_history_totals = df.copy().groupby(by='visitor_team_id').sum()[['away_team_wins','away_team_losses','sum_of_fgm_away','sum_of_fga_away', 'sum_of_fg3m_away', 'sum_of_fg3a_away','sum_of_ftm_away', 'sum_of_fta_away', 'sum_of_oreb_away','sum_of_dreb_away', 'sum_of_stl_away', 'sum_of_blk_away','sum_of_to_away', 'sum_of_pf_away']]

# I reset the index so I can then use the id for the merge in the next step. I tried merging on the index but it wasn't working like I expected it too so this was my work around, not sure if this is best practice or not.
home_history_totals.reset_index(inplace=True)
away_history_totals.reset_index(inplace=True)


# %%
# Grouping removes object data types so I'm merging back into the main df to get the descriptors I need for the data set
home_history_totals = pd.merge(home_history_totals, df[['home_team_id','home_nickname','home_yearfounded','home_arena', 'home_city', 'home_conference']], on=['home_team_id'])


# Grouping removes object data types so I'm merging back into the main df to get the descriptors I need for the data set
away_history_totals = away_history_totals.merge(df[['visitor_team_id','away_nickname', 'away_yearfounded','away_arena', 'away_city', 'away_conference']],on=['visitor_team_id'])


# %%

# I had issues creating several dupes. I think I'm running into a one to many/ many to many issue wasn't sure how to iron it out at the time. I decided to drop dupes for both sets and again reset the index to keep a consistent count
home_history_totals.drop_duplicates(inplace=True)
away_history_totals.drop_duplicates(inplace=True)
home_history_totals.reset_index(drop=True, inplace=True)
away_history_totals.reset_index(drop=True, inplace=True)


# %%
# Combining both sets to get total win numbers for my conference chart
conference_totals = home_history_totals.merge(away_history_totals,
                                              left_on='home_team_id', 
                                              right_on='visitor_team_id')
# %%
# Creating the total wins feature by combining the teams home and away wins
conference_totals['total_wins'] = conference_totals.home_team_wins + conference_totals.away_team_wins
# %%
# Creating a bar chart for each teams total wins and separating them by conference
fig = px.bar(conference_totals.sort_values(by='total_wins', ascending=False),
                                                        x='home_nickname', 
                                                        y='total_wins', 
                                                        color='home_conference')

# This is where I began my tasteful subtle (I think anyway!) Spurs chart colorway. Being from San Antonio I know we had a consistently above average record but I didn't know we would top wins from the span of this data set! This data set at this time spans all seasons from 2003-2020. Spurs represent =D
fig.update_layout(title=dict(text='Total Wins by Team and Conference',
                            y=0.958,x=0.5,
                            xanchor='auto', 
                            yanchor='middle'),
                barmode='group',
                xaxis_title='Team',
                yaxis_title='Total Wins',
                plot_bgcolor='#ebebeb',
                legend_bgcolor='#ebebeb',
                legend_bordercolor='#fa7f72',
                legend_borderwidth=4,
                bargap=0.25,
                bargroupgap=0.15,
                height=800,
                width=1000)

# Plotly express makes it a bit more difficult to change colors. I was able to put this together to effectively separate the bar colors by conference but I feel like there should be an easier way to do it. I think it's much easier graph objects.
fig.for_each_trace(
lambda trace: trace.update(marker=dict(color="#389393")) if trace.name == "West" else trace.update(marker=dict(color="#f5a25d"))
)

fig.update_traces(width=.7)

# %%
# Sorting by wins to order the chart
away_history_totals.sort_values(by='away_team_wins', ascending=False, inplace=True)
home_history_totals.sort_values(by='home_team_wins', ascending=False, inplace=True)
# Creating bar plot with graph objects. Like I mentioned, color is way more intuitive
fig = go.Figure(data=[
    go.Bar(name='Home Wins', 
           x=home_history_totals.home_nickname, 
           y=home_history_totals.home_team_wins, 
           marker_color='#389393'
        ),
    go.Bar(name='Away Wins', 
           x=away_history_totals.away_nickname, 
           y=away_history_totals.away_team_wins, 
           marker_color='#f5a25d'
        ),
])
fig.update_layout(title=dict(text='Wins Per Team by Travel',
                             y=0.94,x=0.5,
                             xanchor='auto', 
                             yanchor='middle'
                        ),
                  barmode='group',
                  plot_bgcolor='#ebebeb',
                  xaxis_title="Team Name",
                  yaxis_title="Total Wins",
                #   bargap=0.25,
                  bargroupgap=0.15,
                  legend_bgcolor='#ebebeb',
                  legend_bordercolor='#fa7f72',
                  legend_borderwidth=4,
                  height=800,
                  width=1000
            )
fig.show()
# %%

# Sorting by wins to order the chart
away_history_totals.sort_values(by='away_team_losses', 
                                    ascending=False, 
                                    inplace=True
                                )
home_history_totals.sort_values(by='home_team_losses', 
                                    ascending=False, 
                                    inplace=True
                                )
# Creating bar plot with graph objects. Like I mentioned, color is way more intuitive
fig = go.Figure(data=[
    go.Bar(name='Home Losses', 
           x=home_history_totals.home_nickname, 
           y=home_history_totals.home_team_losses, 
           marker_color='#389393'
        ),
    go.Bar(name='Away Losses', 
           x=away_history_totals.away_nickname, 
           y=away_history_totals.away_team_losses, 
           marker_color='#f5a25d'
        ),
])
fig.update_layout(title=dict(text='Losses Per Team by Travel',
                             y=0.94,x=0.5,
                             xanchor='auto', 
                             yanchor='middle'
                        ),
                  barmode='group',
                  plot_bgcolor='#ebebeb',
                  legend_bgcolor='#ebebeb',
                  legend_bordercolor='#fa7f72',
                  legend_borderwidth=4,
                  xaxis_title="Team Name",
                  yaxis_title="Total Wins",
                #   bargap=0.25,
                  bargroupgap=0.15,
                  height=800,
                  width=1000
            )

fig.show()

# %%

# players_df = pd.read_pickle('../data/details_df.pkl')
# players_df.head()
# %%
# Creating boards feature to find each players total offensive and defensive rebounds. I really wanted to do a 'Board man gets paid analysis' but I was discouraged because I didn't have enough time.
players_df['total_boards'] = players_df.oreb + players_df.dreb
# %%
# Creating df of sums of stats per player
player_totals = players_df.groupby(by='player_id').sum()
player_totals.reset_index(inplace=True)
# %%

player_totals = player_totals.sort_values(by='total_boards', ascending=False)
# Merge totals back into players df to get the descriptors I need to make sense of the numbers
player_totals = pd.merge(player_totals,players_df[['player_id',
                                                    'player_name',
                                                    'start_position',
                                                    'team_city']], 
                         on=['player_id']
                    )
player_totals.reset_index(inplace=True, drop=True)
player_totals.drop_duplicates(subset=['player_id'],inplace=True)

# %%
# Build App
app = JupyterDash(__name__)
app.layout = html.Div([
    html.P("Select X-axis:"),
    dcc.Checklist(
        # ids to reference in callback section
        id='x-axis', 
        # Add desired values that correspond to df features. You're also able to add your own labels like below in the dropdown.
        options=[{'label': 'Starting Position', 'value':'start_position'}, 
                 {'label': 'Team City', 'value':'team_city'}
        ],
        # Edit value feature to represent the default selector on initial render
        value=['start_position'], 
        # Option to render chart in notebook
        labelStyle={'display': 'inline-block'}

),  
    html.P("Select Y-axis:"),
    dcc.Dropdown(
        id='y-axis', 
        options=[
                {'label':'Rebounds', 'value':'total_boards'},
                {'label':'Field Goals Made', 'value':'fgm'},
                {'label':'Field Goals Attempted', 'value':'fga'}, 
                {'label':'3Pts Made', 'value':'fg3m'},
                {'label':'3Pts Attempted', 'value':'fg3a'},
                {'label':'Free Throws Made', 'value':'ftm'},
                {'label':'Free Throws Attempted', 'value':'fta'},
                {'label':'Offensive Rebounds', 'value':'oreb'},
                {'label':'Defensive Rebounds', 'value':'dreb'}, 
                {'label':'Steals', 'value':'stl'},
                {'label':'Blocks', 'value':'blk'},
                {'label':'Turn Overs', 'value':'to'},
                {'label':'Personal Fouls', 'value':'pf'},
        ],
  
        value='total_boards', 
    ),
    html.P(),
    # Component to actually plot the chart vs the interactive selectors above
    dcc.Graph(id="boxplot"),
])
# Establish callbacks to enable the chart to update when choosing a different option
@app.callback(
    Output("boxplot", "figure"), 
    [Input("x-axis", "value"), 
     Input("y-axis", "value")])
# Function to create the figure to return
def generate_chart(x, y):
    fig = px.box(player_totals, x=x, y=y, hover_name='player_name',points='all', notched=True)
# More #aesthetics
    fig.update_layout(title=dict(text='Position or City Numbers by Stat',
                             y=0.955,x=0.5,
                             xanchor='auto', 
                             yanchor='middle'),
                    barmode='group',
                    plot_bgcolor='#ebebeb',
                    bargap=0.25,
                    bargroupgap=0.15,
                    height=800,
                    width=1500)
    fig.update_traces(marker=dict(color="#389393", line_width=1, line_color='#fa7f72', opacity=0.7,))
    # fig.update_traces(marker=dict(color="#fa7f72", line_width=1, line_color='#fa7f72', opacity=0.8),selector=dict(type='scatter'))
    

    return fig
# Run app and display result inline in the notebook
app.run_server(mode='inline')
# %%
# ! Future work!

# ! seasons_df = df group by season and home team id, visitor team id
# ! reset index in place
# ! seasons_df = seasons_df.merge(df[[home_team_id, visitor team id, season, home_team_wins, away_team_wins, home_conference, away_conference]], on home team id, visitor team id, season )
# !seasons_df.sort_by(by='sum_of_fgm_home', inplace=True)
# ! seasons_df.drop_duplicates(keep='first', inplace=True)
# ! seasons_df.reset_index(drop=True, inplace=True)
# !seasons_df.head()
# 
# %%