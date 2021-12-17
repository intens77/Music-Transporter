from spotipy import SpotifyOAuth, Spotify
from vk_api import VkApi
from vk_api.audio import VkAudio


def auth_handler():
    key = input('Enter authentication code: ')
    remember_device = True
    return key, remember_device


def log_in_vk(vk_login, vk_password):
    vk_session = VkApi(vk_login, vk_password, auth_handler=auth_handler)
    vk_session.auth()
    return vk_session


def get_vk_audio_dict(vk_login, vk_password):
    vk_session = log_in_vk(vk_login, vk_password)
    music_list = VkAudio(vk_session).get()
    audio_dict = dict()
    for item in music_list[::-1]:
        artist = item['artist'].lower()
        track_title = item['title'].lower()
        if artist in audio_dict.keys():
            if track_title in audio_dict[artist]:
                continue
            else:
                audio_dict[artist].add(track_title)
        else:
            audio_dict[artist] = {track_title}
    return audio_dict


def log_in_spotify(spotify_client_id, spotify_client_secret):
    redirected_uri = 'https://github.com/intens77'
    scope = ('user-library-read', 'playlist-read-private, playlist-modify-private',
             'playlist-modify-public', 'user-read-private', 'user-library-modify')
    sp_oauth = SpotifyOAuth(spotify_client_id, spotify_client_secret, redirected_uri,
                            scope=scope, cache_path=None)
    code = sp_oauth.get_auth_response(open_browser=False)
    token = sp_oauth.get_access_token(code, as_dict=False, check_cache=False)
    client = Spotify(auth=token)
    return client


def get_spotify_audio_dict(spotify_client):
    audio_dict = dict()
    spotify_saved_tracks = spotify_client.current_user_saved_tracks()['items']
    for item in spotify_saved_tracks:
        artist = item['track']['artists'][0]['name'].lower()
        track_title = item['track']['name'].lower()
        if artist in audio_dict.keys():
            if track_title in audio_dict[artist]:
                continue
            else:
                audio_dict[artist].add(track_title)
        else:
            audio_dict[artist] = {track_title}
    return audio_dict


def find_unsaved_tracks(vk_tracks, spotify_tracks):
    tracks = vk_tracks
    for artist in tracks.keys():
        if artist in spotify_tracks.keys():
            tracks[artist] = tracks[artist] | spotify_tracks[artist]
    return tracks


def save_music(spotify_client, tracks):
    errors = dict()
    for artist in tracks.keys():
        for track in tracks[artist]:
            try:
                music = spotify_client.search(f'{artist} {track}', type='track')
                spotify_client.current_user_saved_tracks_add(tracks=music['tracks']['items'][0]['id'].split())
            except:
                if artist in errors.keys():
                    errors[artist].add(track)
                else:
                    errors[artist] = {track}


def main():
    vk_login = input('please, enter your vk login or phone number: ')
    vk_password = input('please, enter your vk password: ')
    spotify_client_id = input('please, enter your spotify client id: ')
    spotify_client_secret = input('please, enter your spotify client secret: ')
    vk_tracks = get_vk_audio_dict(vk_login, vk_password)
    spotify_client = log_in_spotify(spotify_client_id, spotify_client_secret)
    spotify_tracks = get_spotify_audio_dict(spotify_client)
    unsaved_tracks = find_unsaved_tracks(vk_tracks, spotify_tracks)
    save_music(spotify_client, unsaved_tracks)


if __name__ == '__main__':
    main()
