# Entry point for NBA Player Stat Viewer & Simulator

import json
from flask import Flask, render_template, request, abort, jsonify
import os
from basketball_sim import simulate_game
from player_enhancer import enhance_player_data

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
    ai_commentary = None
    target_score = 11  # Default target score
    
    if request.method == 'POST':
        id1 = request.form.get('player1')
        id2 = request.form.get('player2')
        p1 = get_player(id1)
        p2 = get_player(id2)
        
        # Get target score if provided
        if request.form.get('target_score'):
            try:
                target_score = int(request.form.get('target_score'))
            except ValueError:
                pass  # Use default if invalid
        
        if p1 and p2:
            # Run the advanced simulation
            game_result = simulate_game(p1, p2, target_score=target_score)
            
            # Extract winner from game result
            winner_name = game_result.get('winner')
            winner = p1 if winner_name == p1['name'] else p2
            
            # Get enhanced player data from the simulation
            enhanced_p1 = game_result.get('enhanced_player1', p1)
            enhanced_p2 = game_result.get('enhanced_player2', p2)
            
            sim_result = {
                'player1': p1, 
                'player2': p2,
                'enhanced_player1': enhanced_p1,
                'enhanced_player2': enhanced_p2, 
                'winner': winner,
                'final_score': game_result.get('final_score'),
                'game_log': game_result.get('game_log')
            }
            
            # Get AI commentary from the simulation
            ai_commentary = game_result.get('enhanced_commentary')
    
    return render_template('simulate.html', players=players, sim_result=sim_result, 
                           ai_commentary=ai_commentary, target_score=target_score)

def get_ai_commentary():
    """This function is now deprecated as commentary is generated in the simulation"""
    return 'AI commentary is now generated as part of the simulation.'

# API endpoint to get simulation results as JSON
@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    data = request.json
    if not data or 'player1_id' not in data or 'player2_id' not in data:
        return jsonify({'error': 'Missing player IDs'}), 400
    
    p1 = get_player(data['player1_id'])
    p2 = get_player(data['player2_id'])
    
    if not p1 or not p2:
        return jsonify({'error': 'Player not found'}), 404
    
    target_score = data.get('target_score', 11)
    
    # Run simulation with enhanced player data
    game_result = simulate_game(p1, p2, target_score=target_score)
    
    return jsonify(game_result)

# SQL Injection demonstration endpoint (for educational purposes only)
@app.route('/error_test')
def error_test():
    username = request.args.get('username', '')
    
    # WARNING: This is intentionally vulnerable to SQL injection
    # DO NOT use this pattern in production code
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    # We're not actually executing the query, just showing it
    result = {
        'query': query,
        'warning': 'This endpoint demonstrates SQL injection vulnerability. DO NOT use this pattern in production.',
        'proper_way': 'Use parameterized queries instead: cursor.execute("SELECT * FROM users WHERE username = ?", (username,))'
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
