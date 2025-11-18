from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from functools import wraps
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = "super_secret_key"

CONSULTANTS_FILE = 'data/consultants.json'
ROLES_FILE = 'data/roles.json'


# ---------------------------
# Helper Functions
# ---------------------------
def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        return json.load(f)


def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)


def match_candidates(role):
    consultants = load_data(CONSULTANTS_FILE)
    required = set(role['skills'])
    available = [c for c in consultants if c['available']]

    for c in available:
        c['score'] = len(set(c['skills']).intersection(required))

    sorted_list = sorted(available, key=lambda x: x['score'], reverse=True)
    return sorted_list[:3]


# ---------------------------
# Access Control Decorators
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_type' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


def recruiter_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_type') != 'recruiter':
            return render_template('access_denied.html', message="❌ Only recruiters can access this page.")
        return f(*args, **kwargs)
    return decorated


def consultant_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_type') != 'consultant':
            return render_template('access_denied.html', message="❌ Only consultants can access this page.")
        return f(*args, **kwargs)
    return decorated


# ---------------------------
# Login / Logout
# ---------------------------
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    user_type = request.form['user_type']
    session['user_type'] = user_type

    if user_type == "recruiter":
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('add_consultant'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------------------
# Consultant Area
# ---------------------------
@app.route('/add_consultant', methods=['GET', 'POST'])
@login_required
@consultant_only
def add_consultant():
    if request.method == 'POST':
        name = request.form['name']
        skills = [s.strip() for s in request.form['skills'].split(',')]
        consultants = load_data(CONSULTANTS_FILE)

        consultants.append({
            'name': name,
            'skills': skills,
            'available': True
        })

        save_data(CONSULTANTS_FILE, consultants)
        return redirect(url_for('add_consultant'))

    return render_template('add_consultant.html')


# ---------------------------
# Recruiter Dashboard
# ---------------------------
@app.route('/dashboard')
@login_required
@recruiter_only
def dashboard():
    consultants = load_data(CONSULTANTS_FILE)
    total = len(consultants)
    available = len([c for c in consultants if c['available']])

    utilization = (total - available) / total * 100 if total > 0 else 0

    return render_template('dashboard.html',
                           consultants=consultants,
                           total=total,
                           available_count=available,
                           utilization=utilization)


# ---------------------------
# Recruiter: Roles & Matching
# ---------------------------
@app.route('/roles', methods=['GET', 'POST'])
@login_required
@recruiter_only
def roles():
    roles_data = load_data(ROLES_FILE)

    if request.method == 'POST':
        role_name = request.form['role_name']
        skills = [s.strip() for s in request.form['skills'].split(',')]
        roles_data.append({'role_name': role_name, 'skills': skills})
        save_data(ROLES_FILE, roles_data)
        return redirect(url_for('roles'))

    matches = {role['role_name']: match_candidates(
        role) for role in roles_data}

    return render_template('roles.html', roles=roles_data, matches=matches)


# ---------------------------
# Recruiter: Assign Consultant
# ---------------------------
@app.route('/assign/<role_name>/<consultant_name>', methods=['POST'])
@login_required
@recruiter_only
def assign_consultant(role_name, consultant_name):
    consultant_name = unquote(consultant_name)
    consultants = load_data(CONSULTANTS_FILE)

    for c in consultants:
        if c['name'] == consultant_name:
            c['available'] = False  # Mark as assigned
            break

    save_data(CONSULTANTS_FILE, consultants)
    return redirect(url_for('roles'))


# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
