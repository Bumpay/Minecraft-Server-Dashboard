from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sse import sse
import requests

app = Flask(__name__)
app.config['REDIS_URL'] = 'redis://localhost'
app.register_blueprint(sse, url_prefix='/stream')

API_URL = 'http://127.0.0.1:8000'
SERVER = 'mc-vanilla-plus'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/server/<action>')
def server_control(action):
    if action in ['start', 'stop', 'restart']:
        response = requests.post(f'{API_URL}/servers/{SERVER}/{action}')
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Invalid action'}), 400


@app.route('/players')
def players():
    response = requests.get(f'{API_URL}/servers/{SERVER}/players')
    return jsonify(response.json())


@app.route('/status')
def status():
    response = requests.get(f'{API_URL}/servers/{SERVER}/status')
    return jsonify(response.json())


@app.route('/resource-usage')
def resource_usage():
    response = requests.get(f'{API_URL}/servers/{SERVER}/metrics')
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(debug=True)
