# %%
from IPython.display import display
# from IPython.display import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, PowerTransformer
from sklearn.metrics import plot_confusion_matrix
from sklearn.pipeline import Pipeline





# %%
df = pd.read_pickle('../data/main_df.pkl')
df.shape
# %%
# Splitting data 
df_train, df_validation = train_test_split(df, test_size=0.10, random_state=42)
# %%
df_train.columns
# %%
# Base model resuled in ~92
# While this does make the best model out the box, I feel like it kinda doesn't make sense to build a model this way, or any of the below for that matter. This is all historical data where all of the statistics are already gathered and completed so if I feed it data of how many points the home team scored vs the away team, yea, I'd imagine the model will predict who the correct winner is. 
# I don't know if this is right or not, but I think the better approach would be to take individual player stats, then reference them with the players they play with at every point of the game, and also cross reference that with the players they're playing against at every point of the game. Then with those numbers we'd be able to get a better accuracy of what the outcome will be based on who's available on the roster for that game, play times, and the relationship of stats between players. Also to include the point of the game at which players come on and off. This would encapsulate the effect of starters vs role players vs bench warmers coming on and off to give super stars a break or if it's a blow out and they just put the bench in towards the end of the 4th.
# I initially I wanted to do my EDA on whole team stats because I thought it was more approachable and carried that over to the model. Really though, I don't think I would've been able to flesh this out as much as I'd like within the one week time frame we had so I'm gonna roll with what I got!
features_for_modeling = ['fg_pct_home','ft_pct_home','fg3_pct_home','ast_home','reb_home','fg_pct_away','ft_pct_away','fg3_pct_away','ast_away','reb_away','sum_of_fga_home','sum_of_fg3m_home','sum_of_fg3a_home','sum_of_ftm_home','sum_of_fta_home','sum_of_oreb_home','sum_of_dreb_home','sum_of_stl_home','sum_of_blk_home','sum_of_to_home', 'sum_of_pf_home','sum_of_fgm_away','sum_of_fga_away','sum_of_fg3m_away','sum_of_fg3a_away','sum_of_ftm_away','sum_of_fta_away','sum_of_oreb_away','sum_of_dreb_away','sum_of_stl_away','sum_of_blk_away','sum_of_to_away','sum_of_pf_away']
# %%
# Base model resulted in ~82
# I wanted to see how the model would perform if I remove the sums of the stats and only use percentages
features_for_modeling_pct = ['fg_pct_home','ft_pct_home','fg3_pct_home','fg_pct_away','ft_pct_away','fg3_pct_away']
# %%
# Base model resulted in ~82
# Then I wanted to see how it would perform using only what I called secondary stats. Not sure if that's the right name for them but my thinking was that these are stats that don't directly translate to points on the board, except maybe for assists but still.
# Decided to use these features because I thought it was more interesting to see that the model could do just as well on stats like assists and rebounds as it does with percentages of field goals made.
features_for_modeling_secondary = ['ast_home','reb_home','ast_away','reb_away','sum_of_oreb_home','sum_of_dreb_home','sum_of_stl_home','sum_of_blk_home','sum_of_to_home','sum_of_pf_home','sum_of_oreb_away','sum_of_dreb_away','sum_of_stl_away','sum_of_blk_away','sum_of_to_away','sum_of_pf_away']
# %%
# Establishing the secondary features
X = df_train[features_for_modeling_secondary]
y = df_train['home_team_wins']
X.shape, y.shape
# %%
# Splitting training set as a train test
X_train, X_test, y_train , y_test = train_test_split(X, y, test_size=0.20, random_state=42)
# %%
# Running through a few base models to set what performs well
classifiers = [KNeighborsClassifier(),
               RandomForestClassifier(), 
            #    SVC(gamma="auto"), 
               AdaBoostClassifier(), 
               GradientBoostingClassifier()]
# Loop through each classifier and output score
for classifier in classifiers:
    pipe = Pipeline(steps=[('classifier', classifier)])
    pipe.fit(X_train, y_train)
    print(f'{classifier} Score: {round(pipe.score(X_test, y_test), 4)}')
# %%
# Settled on gboost as the one I wanted to work with and made a grid to go through options. Adjusting these options to most of my time and didn't want to include all of the params in the final just because it would take to long to run to output a clean notebook.
# I also went through this process with random forest because it also performed well during the run but while I was going through it, the scores were slightly lower while also being much more overfit so I decided to drop it after tuning several parameters.
gboost_param_grid={'max_depth': [3],
            'max_leaf_nodes': [2, 3],
            'min_samples_leaf': [1, 2],
            'n_estimators': [450],
            'subsample': [0.25,0.5],
       #      Unsure if verbose and random_state are needed here but tossed them in for good measure. I wasn't able to get any consistent progress information during training unfortunately so I just left it here
            'verbose': [1],
            'random_state':[42]
}
# %%
# Initializing gridsearch and fitting, and outputting the results and grabbing the best estimator
gridsearch = GridSearchCV(estimator=GradientBoostingClassifier(), param_grid=gboost_param_grid, 
                          scoring='precision', cv=5, verbose=1,n_jobs=-1)
gridsearch.fit(X_train, y_train)
display(gridsearch.best_estimator_)
display(gridsearch.best_score_)
gridbest = gridsearch.best_estimator_
 # %%
#  Using the best estimator to refit and and ouput the results
display(gridbest.fit(X_train, y_train))
display(gridbest.score(X_train, y_train), gridbest.score(X_test, y_test))
# %%
# Outputting confusion matrices for both train and test
display(plot_confusion_matrix(gridbest, X_train, y_train, cmap='bone'))
display(plot_confusion_matrix(gridbest, X_test, y_test, cmap='bone'))

# %%
# Running model on validation set and outputting results and confusion matrix
X_valid = df_validation[features_for_modeling_secondary]
y_valid = df_validation['home_team_wins']
display(gridbest.score(X_valid, y_valid))
display(plot_confusion_matrix(gridbest, X_valid, y_valid, cmap='bone'))
# %%
# Showing features ranked by importance for the model
fig = px.bar(x=X_train[features_for_modeling_secondary].columns,
       y=sorted(pipe[0].feature_importances_, reverse=True),
       title='Most Important Features',
       labels={'x':'Features',
               'y':'Importance'})
fig.update_traces(marker=dict(color="#389393", line_width=1, line_color='#fa7f72'))

# %%
# Tbh I don't fully understand the roc curve stuff and got a bit confused around here. What I think I'm doing is anyway is grabbing my false positive ans true positives from my model and plotting them to make a curve
y_scores = gridbest.decision_function(X_train)
fpr, tpr, thresh = roc_curve(y_train, y_scores)

# Calculate the ROC (Reciever Operating Characteristic) AUC (Area Under the Curve)
rocauc = auc(fpr, tpr)
print('Train ROC AUC Score: ', rocauc)
# %%
fig = px.area(
    x=fpr, y=tpr,
    title=f'ROC Curve (AUC={auc(fpr, tpr):.4f})',
    labels=dict(x='False Positive Rate', y='True Positive Rate'),
#     marker=dict(color='fa7f72'),

    width=700, height=500
)
fig.add_shape(
    type='line', line=dict(dash='dash'),
    x0=0, x1=1, y0=0, y1=1
)

fig.update_yaxes(scaleanchor="x", scaleratio=1)
fig.update_xaxes(constrain='domain', tickvals=[0,0.25,0.5,0.75,1])

fig.show()

# %%