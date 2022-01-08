import os
import time
import json
import flask
import pandas as pd
import firebase_admin
from firebase_admin import db, credentials, storage
from pydub import AudioSegment

# Fetch credentials.
cred = None
if 'DYNO' in os.environ:
  json_data = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
  json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
  cred = credentials.Certificate(json_data)
else:
  cred = credentials.Certificate('private-key.json')

# And initialize the app.
firebase_admin.initialize_app(cred, {
  'databaseURL': 'https://toacametru-default-rtdb.firebaseio.com',
  'storageBucket': 'toacametru.appspot.com',
})

# Load the model.
from src.solver import Solver
solver = Solver()

# Initialize the Flask app.
app = flask.Flask(__name__, template_folder='templates', static_folder='static')

# The app must use https for recording to work!
# Only trigger SSLify if the app is running on Heroku,
# acc. https://stackoverflow.com/questions/15116312/redirect-http-to-https-on-flaskheroku/22137608.
from flask_sslify import SSLify
if 'DYNO' in os.environ:
  sslify = SSLify(app)

@app.route('/record', methods=['GET', 'POST'])
def record():
  print(f"request={flask.request.method}")
  if flask.request.method == 'GET':
    print("GET!")
    return {'success' : True}
  if flask.request.method == 'POST':
    # Fetch the file.
    file = flask.request.files['audio']
    
    # Fetch the IP.
    ip = flask.request.environ.get('HTTP_X_REAL_IP', flask.request.remote_addr)

    # Create a directory if we don't have one.
    if not os.path.exists('recordings'):
      os.mkdir('recordings')

    # Build the filepath.
    filename = f'{ip}-{int(time.time())}-{file.filename}'
    wavFilepath = os.path.join(app.root_path, 'recordings', f'{filename}.wav')
    mp3Filepath = os.path.join(app.root_path, 'recordings', f'{filename}.mp3')
    file.save(wavFilepath)

    # Convert to mp3.
    AudioSegment.from_wav(wavFilepath).export(mp3Filepath, format='mp3')

    # Predict the tone.
    statistics = solver.analyze(mp3Filepath)
    print(statistics)
    
    # Store the recording.
    storage.bucket().blob(f'recordings/{filename}.mp3').upload_from_filename(mp3Filepath);

    # And return the result.
    # TODO: return the db key.
    return {'statistics' : statistics, 'success' : True}

# Set up the main route
@app.route('/', methods=['GET', 'POST'])
def main():
  if flask.request.method == 'GET':
    return(flask.render_template('index.html'))

  if flask.request.method == 'POST':
    return None

if __name__ == '__main__':
  app.run()
