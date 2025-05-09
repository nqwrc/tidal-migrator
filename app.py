import csv
import io
from pathlib import Path
import sys
import webbrowser
import tidalapi
import yaml
from flask import Flask, redirect, render_template, url_for, request, session as flask_session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for Flask session

global tidal_sessions
account_sessions_file = 'account_sessions.yml'
tidal_sessions = {}  # username -> tidalapi.Session

def load_account_sessions():
    try:
        with open(account_sessions_file, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def save_account_sessions(sessions):
    with open(account_sessions_file, 'w') as f:
        yaml.dump(sessions, f)

def open_tidal_session(config=None, username=None):
    account_sessions = load_account_sessions()
    previous_session = account_sessions.get(username) if username else None

    if config:
        session = tidalapi.Session(config=config)
    else:
        session = tidalapi.Session()
    if previous_session:
        try:
            if session.load_oauth_session(token_type=previous_session['token_type'],
                                          access_token=previous_session['access_token'],
                                          refresh_token=previous_session['refresh_token']):
                return session
        except Exception as e:
            print("Error loading previous Tidal Session: \n" + str(e))

    login_data, future = session.login_oauth()
    print('Login with the webbrowser: ' + login_data.verification_uri_complete)
    url = login_data.verification_uri_complete
    if not url.startswith('https://'):
        url = 'https://' + url
    webbrowser.open(url)
    future.result()
    # Get username from Tidal session
    username = session.user.username
    account_sessions[username] = {
        'session_id': session.session_id,
        'token_type': session.token_type,
        'access_token': session.access_token,
        'refresh_token': session.refresh_token
    }
    save_account_sessions(account_sessions)
    return session

def transfer_all_favorites_to_another_account(source_session: tidalapi.Session, category: str, target_session: tidalapi.Session):
    errors = []
    type_map = {
        'tracks': ('tracks', 'add_track'),
        'albums': ('albums', 'add_album'),
        'artists': ('artists', 'add_artist'),
        'videos': ('videos', 'add_video'),
        'playlists': ('playlists', 'add_playlist'),
    }
    if category not in type_map:
        return [f"Unknown favorite category: {category}"]
    get_method, add_method = type_map[category]
    try:
        favorites = getattr(source_session.user.favorites, get_method)()
    except Exception as e:
        return [f"Failed to fetch favorites: {e}"]
    for fav in favorites:
        try:
            getattr(target_session.user.favorites, add_method)(fav.id)
        except Exception as e:
            errors.append(str(e))
    return errors

@app.route('/')
def index():
    account_sessions = load_account_sessions()
    usernames = list(account_sessions.keys())
    current_user = flask_session.get('current_user')
    return render_template('index.html', usernames=usernames, current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global tidal_sessions
    if request.method == 'POST':
        username = request.form.get('username')
        if username and username in load_account_sessions():
            # Switch to existing account
            session = open_tidal_session(username=username)
        else:
            # New login
            session = open_tidal_session()
            username = session.user.username
        tidal_sessions[username] = session
        flask_session['current_user'] = username
        return redirect(url_for('post_login'))
    else:
        # GET: show account selection
        account_sessions = load_account_sessions()
        usernames = list(account_sessions.keys())
        return render_template('index.html', usernames=usernames, current_user=flask_session.get('current_user'))

@app.route('/switch_account', methods=['POST'])
def switch_account():
    username = request.form.get('username')
    if username in load_account_sessions():
        flask_session['current_user'] = username
        return redirect(url_for('post_login'))
    return "Account not found", 400

@app.route('/post_login')
def post_login():
    username = flask_session.get('current_user')
    if not username:
        return redirect(url_for('index'))
    session = open_tidal_session(username=username)

    tracks = session.user.favorites.tracks()
    albums = session.user.favorites.albums()
    videos = session.user.favorites.videos()
    artists = session.user.favorites.artists()
    playlists = session.user.favorites.playlists()

    account_sessions = load_account_sessions()
    usernames = list(account_sessions.keys())

    return render_template('post_login.html',
                           tracks=tracks,
                           albums=albums,
                           artists=artists,
                           videos=videos,
                           playlists=playlists,
                           usernames=usernames,
                           current_user=username)

@app.route('/transfer_all_favorites', methods=['POST'])
def transfer_all_favorites():
    global tidal_sessions
    source_username = request.form.get('source_user')
    categories = request.form.getlist('categories')
    target_username = flask_session.get('current_user')
    if not (source_username and categories and target_username):
        return "Missing data for transfer", 400
    if source_username not in tidal_sessions:
        tidal_sessions[source_username] = open_tidal_session(username=source_username)
    if target_username not in tidal_sessions:
        tidal_sessions[target_username] = open_tidal_session(username=target_username)
    source_session = tidal_sessions[source_username]
    target_session = tidal_sessions[target_username]
    all_errors = []
    for category in categories:
        errors = transfer_all_favorites_to_another_account(source_session, category, target_session)
        if errors:
            all_errors.extend([f"{category}: {err}" for err in errors])
    if all_errors:
        return f"Errors during transfer: {', '.join(all_errors)}"
    else:
        return redirect(url_for('post_login'))

@app.route('/logout')
def logout():
    flask_session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
