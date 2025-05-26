# Entry point for NBA Player Stat Viewer & Simulator

import json
from flask import Flask, render_template, request, abort
import os

app = Flask(__name__)

# Load player data from players.json
with open(os.path.join(os.path.dirname(__file__), 'players.json'), encoding='utf-8') as f:
    players = json.load(f)

# Helper: get player by id
def get_player(player_id):
    for player in players:
        if str(player['id']) == str(player_id):
            return player
    return None

# Helper: get team logo as SVG
def get_team_logo(team_name):
    # Check for specific teams to use their official colors
    team_colors = {
        'New York Knicks': 'F58426',  # Knicks Orange
        'Dallas Mavericks': '0053BC',  # Mavericks Blue
        'Houston Rockets': 'CE1141',   # Rockets Red
        'Minnesota Timberwolves': '0C2340'  # Timberwolves Midnight Blue
    }
    
    # Use the team's color if defined, otherwise generate a consistent color
    if team_name in team_colors:
        color = team_colors[team_name]
    else:
        import hashlib
        color = hashlib.md5(team_name.encode()).hexdigest()[:6]
    
    # Get the first letter of the team name
    first_letter = team_name[0].upper()
    
    # Create a simple SVG logo
    svg = f'''
    <svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
        <rect width="50" height="50" rx="25" fill="#{color}" opacity="0.8"/>
        <text x="25" y="32" font-family="Arial, sans-serif" font-size="24" 
              font-weight="bold" text-anchor="middle" fill="white">{first_letter}</text>
    </svg>
    '''
    return svg.strip()

# Register the function to be available in templates
app.jinja_env.globals.update(get_team_logo=get_team_logo)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/players')
def list_players():
    return render_template('players.html', players=players)

@app.route('/player/<player_id>')
def player_detail(player_id):
    player = get_player(player_id)
    if not player:
        abort(404)
    return render_template('player_detail.html', player=player)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    result = None
    if request.method == 'POST':
        id1 = request.form.get('player1')
        id2 = request.form.get('player2')
        p1 = get_player(id1)
        p2 = get_player(id2)
        if p1 and p2:
            result = {'player1': p1, 'player2': p2}
    return render_template('compare.html', players=players, result=result)

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    sim_result = None
    ai_commentary = get_ai_commentary()
    if request.method == 'POST':
        id1 = request.form.get('player1')
        id2 = request.form.get('player2')
        p1 = get_player(id1)
        p2 = get_player(id2)
        if p1 and p2:
            # Dummy simulation: pick winner by higher points
            winner = p1 if p1['points'] >= p2['points'] else p2
            sim_result = {'player1': p1, 'player2': p2, 'winner': winner}
    return render_template('simulate.html', players=players, sim_result=sim_result, ai_commentary=ai_commentary)

def get_ai_commentary():
    return 'AI commentary will be added here.'

if __name__ == '__main__':
    app.run(debug=True)
