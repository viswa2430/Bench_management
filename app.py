from flask import Flask, render_template, request, redirect, url_for
import json, os

app = Flask(__name__)

CONSULTANTS_FILE = 'data/consultants.json'
ROLES_FILE = 'data/roles.json'

# Helper functions
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
    required_skills = set(role['skills'])
    available_consultants = [c for c in consultants if c['available']]
    for c in available_consultants:
        c['score'] = len(set(c['skills']).intersection(required_skills))
    sorted_consultants = sorted(available_consultants, key=lambda x: x['score'], reverse=True)
    return sorted_consultants[:3]

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    user_type = request.form['user_type']
    if user_type == 'recruiter':
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('add_consultant'))

@app.route('/add_consultant', methods=['GET', 'POST'])
def add_consultant():
    if request.method == 'POST':
        name = request.form['name']
        skills = request.form['skills'].split(',')
        available = True
        consultants = load_data(CONSULTANTS_FILE)
        consultants.append({'name': name, 'skills': [s.strip() for s in skills], 'available': available})
        save_data(CONSULTANTS_FILE, consultants)
        return redirect(url_for('add_consultant'))
    return render_template('add_consultant.html')

@app.route('/dashboard')
def dashboard():
    consultants = load_data(CONSULTANTS_FILE)
    total = len(consultants)
    available_count = len([c for c in consultants if c['available']])
    utilization = (total - available_count)/total*100 if total > 0 else 0
    return render_template('dashboard.html', consultants=consultants, total=total,
                           available_count=available_count, utilization=utilization)

@app.route('/roles', methods=['GET', 'POST'])
def roles():
    roles_data = load_data(ROLES_FILE)
    if request.method == 'POST':
        role_name = request.form['role_name']
        skills = [s.strip() for s in request.form['skills'].split(',')]
        roles_data.append({'role_name': role_name, 'skills': skills})
        save_data(ROLES_FILE, roles_data)
        return redirect(url_for('roles'))
    matches = {}
    for role in roles_data:
        matches[role['role_name']] = match_candidates(role)
    return render_template('roles.html', roles=roles_data, matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
