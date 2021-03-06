from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool,  CategoricalColorMapper, WheelZoomTool, Legend, Select
from bokeh.io import curdoc
from bokeh.layouts import widgetbox, row, column
#from bokeh.palettes import Category20_17
from bokeh.palettes import Set1
from bokeh.models.widgets import CheckboxGroup
from bokeh.embed import file_html
from bokeh.resources import CDN


import ast
import pandas as pd

# # Define the callback: update_plot

def update_plot(attr, old, new):
    # Read the current value off the slider and 2 dropdowns: yr, x, y
#     x = x_select.value
#     y = y_select.value
    clustered_by = cluster_select.value
        
    # Label axes of plot
#     p.xaxis.axis_label = x
#     p.yaxis.axis_label = y
    
    # Set new_data
    new_data = source.data
#     new_data['x'] = df.loc['genres_top' in checkbox_genres.active, x]
#     new_data['y'] = df.loc['genres_top' in checkbox_genres.active, y]
#     new_data['x'] = df[x]
#     new_data['y'] = df[y]
    source.data = new_data
    
    # Set the range of all axes
#     p.x_range.start = min(df[x])
#     p.x_range.end = max(df[x])
#     p.y_range.start = min(df[y])
#     p.y_range.end = max(df[y])
    
    # Update what tracks are clustered by ### TO-DO
    p.legend = clustered_by
    p.color = dict(field=clustered_by, transform=color_mapper)
    # Update clusters
#     cluster_plot.x = source_clusters[x]
#     cluster_plot.y = source_clusters[y] 
    
    # Add title to plot
#     p.title.text = '{} vs. {}'.format(y,x)

# Read track info
df = pd.read_csv('tracks_with_kmeans.csv', index_col='track_id')
df['genres_all'] = df['genres_all'].map(ast.literal_eval)
df['genres_all'].apply(lambda row : ', '.join(map(str, row)))

# Read cluster info 
# track_genres = pd.read_csv('clusters.csv', index_col=0)
# source_clusters = ColumnDataSource(data=track_genres)
audio_cols = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'tempo', 'valence']
unique_genres = df['MainGenre'].unique().tolist()


# # Create a dropdown Select widget for the x data: x_select
# x_select = Select(
#     options=audio_cols,
#     value='acousticness',
#     title='x-axis data'
# )

# # Attach the update_plot callback to the 'value' property of x_select
# x_select.on_change('value', update_plot)

# # Create a dropdown Select widget for the y data: y_select
# y_select = Select(
#     options=audio_cols,
#     value='energy',
#     title='y-axis data'
# )

# Create a dropdown Select widget for the KMeans Data
cluster_select = Select(
    options=['MainGenre', 'KMeansLabel'],
    value='MainGenre',
    title='Categorized by:'
)
cluster_select.on_change('value', update_plot)

# Attach the update_plot callback to the 'value' property of y_select
# y_select.on_change('value', update_plot)

# Create a checkbox for genres
# checkbox_genres = CheckboxGroup(
#         labels=unique_genres, active=list(range(0,len(unique_genres))
#                                          )
# )
# checkbox_genres.on_change('active', update_plot)
# Create data source
source = ColumnDataSource(data={
    'x' : df['x'],
    'y' : df['y'],
    'track' : df['track'],
    'artist' : df['artist'],
    'album' : df['album'],
    'MainGenre' : df['MainGenre'],
    'genres_all' : df['genres_all'],
    'KMeansLabel' : df['KMeansLabel']
})

# Create Color Mapper
color_mapper = CategoricalColorMapper(factors=unique_genres, palette=Set1[9])

# Add hover tool
hover = HoverTool(tooltips={'Artist':'@artist',
                                     'Track':'@track',
                                     'Album':'@album',
                                     'Main Genre':'@MainGenre',
                                     'All Genres':'@genres_all',
                                     'KMeans Genre':'@KMeansLabel'}
                 )

# Add hover for clusters
# hover_cluster = HoverTool(tooltips={'Cluster':'@cluster',
#                                     'Method':'@method',
#                                    '(x,y)':'($x, $y)'}
#                          )
# Create figure
p = figure(x_axis_label='Dimension 1', y_axis_label='Dimension 2', 
           x_range = (min(df['x']), max(df['x'])), 
           y_range = (min(df['y']), max(df['y'])),
           plot_height=600, plot_width=800, 
           tools=['wheel_zoom', hover])

# Plot Clusters
# cluster_plot = p.circle(x=x_select.value, y=y_select.value, source=source_clusters, fill_alpha=0.1, size=100,
#         color=dict(field='cluster', transform=color_mapper))

# Plot Points
p.circle(x='x', 
         y='y', 
         source=source, 
         fill_alpha=0.25, 
         legend='MainGenre', 
         color = dict(field='MainGenre', transform=color_mapper)
        )

### Trick to locate legend outside of plot
new_legend = p.legend[0]
p.legend[0].plot = None
p.add_layout(new_legend, 'right')

p.toolbar.active_inspect = [hover]


# # Create layout and add to current document
#layout = column(p, widgetbox(x_select, y_select))
#layout = row(checkbox_genres, layout)
layout = column(p, widgetbox(cluster_select))
curdoc().add_root(layout)
#curdoc().title = "{} vs. {}".format(y_select.value, x_select.value)
output_file('FeatureDistribution.html')
save(layout, filename='FeatureDistribution.html')
html = file_html(layout, CDN, "FeatureDistribution")

show(layout)
