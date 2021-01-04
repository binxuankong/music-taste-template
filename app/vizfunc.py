import pygal
from pygal.style import Style

custom_style = Style(background = 'transparent')

def plot_genre_chart(top_genres):
    try:
        chart_dict = {}
        for timeframe in ['Short', 'Medium', 'Long']:
            pie_chart = pygal.Pie(style=custom_style)
            percent_formatter = lambda x: '{:.2f}%'.format(x)
            pie_chart.value_formatter = percent_formatter
            df = top_genres.loc[top_genres['timeframe'] == timeframe][:10]
            for _, row in df.iterrows():
                genre = row['genre']
                points = row['points'] * 100 / df['points'].sum()
                pie_chart.add(genre, points)
            chart_dict[timeframe] = pie_chart.render_data_uri()
        return chart_dict
    except:
        return None

def plot_mood_gauge(features):
    try:
        music_moods = {'valence': 'Happy', 'danceability': 'Danceable', 'energy': 'Energy', 'acousticness': 'Acoustic', \
                       'instrumentalness': 'Instrumental', 'liveness': 'Live Music', }
        gauge_dict = {}
        for timeframe in ['Short', 'Medium', 'Long']:
            gauge = pygal.SolidGauge(half_pie=True, inner_radius=0.70, style=custom_style)
            percent_formatter = lambda x: '{:.2f}%'.format(x)
            gauge.value_formatter = percent_formatter
            gauge.legend_at_bottom = True
            gauge.legend_at_bottom_columns = 3
            feats = features[timeframe][0]
            for mood in music_moods:
                gauge.add(music_moods[mood], feats[mood] * 100)
            gauge_dict[timeframe] = gauge.render_data_uri()
        return gauge_dict
    except:
        return None