import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics import pairwise_distances

def playlist_score(songs):
    CLIENT_ID = os.environ.get("CLIENT_ID", None)
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
    n = len(songs)
    sum = {}
    sum['acousticness'] = 0
    sum['danceability'] = 0
    sum['energy'] = 0
    sum['instrumentalness'] = 0
    sum['liveness'] = 0
    sum['loudness'] = 0
    sum['speechiness'] = 0
    sum['tempo'] = 0
    sum['valence'] = 0
    for song in songs:
        results = sp.search(q='artist:' + song['artist'] + ' track:' + song['title'], type='track')
        if results['tracks']['items']:
            trackId = results['tracks']['items'][0]['id']
            sum['acousticness'] += sp.audio_features(trackId)[0]['acousticness']/n
            sum['danceability'] += sp.audio_features(trackId)[0]['danceability']/n
            sum['energy'] += sp.audio_features(trackId)[0]['energy']/n
            sum['instrumentalness'] += sp.audio_features(trackId)[0]['instrumentalness']/n
            sum['liveness'] += sp.audio_features(trackId)[0]['liveness']/n
            sum['loudness'] += sp.audio_features(trackId)[0]['loudness']/n
            sum['speechiness'] += sp.audio_features(trackId)[0]['speechiness']/n
            sum['tempo'] += sp.audio_features(trackId)[0]['tempo']/(n*160)
            sum['valence'] += sp.audio_features(trackId)[0]['valence']/n
    res = []
    for key, value in sum.items():
        res.append(value)
    return res

def compare_playlist(playlist1, playlist2):
    return pairwise_distances([playlist1],[playlist2])[0][0]



