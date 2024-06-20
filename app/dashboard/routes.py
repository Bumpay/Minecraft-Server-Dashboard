from flask import render_template, redirect, url_for, request, session, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, jwt_required

from . import dashboard

load_dotenv()

users = {
    os.getenv('ADMIN_USERNAME'): os.getenv('ADMIN_PASSWORD')
}


@dashboard.route('/')
def index():
    return redirect(url_for('dashboard.login'))


@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return jsonify({'message': 'Could not verify'}), 401

        if users.get(auth.username) == auth.password:
            access_token = create_access_token(identity={'username': auth.username})
            session['access_token'] = access_token
            return jsonify({"token": access_token})
        return jsonify({"message": "Invalid credentials"}), 401

    return render_template('login.html')


@dashboard.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
