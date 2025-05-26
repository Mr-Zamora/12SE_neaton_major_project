import os
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import re

def create_default_logo():
    # Create a default logo for missing teams
    default_logo = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#1d428a"/>
        <text x="50" y="60" font-family="Arial" font-size="40" fill="white" text-anchor="middle">NBA</text>
    </svg>"""
    
    os.makedirs('static/team_logos', exist_ok=True)
    with open('static/team_logos/default.png', 'wb') as f:
        f.write(default_logo.encode())
    print("Created default logo")

def download_logos():
    # Create the team_logos directory if it doesn't exist
    os.makedirs('static/team_logos', exist_ok=True)
    
    # NBA teams and their abbreviations
    teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans',
        'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic',
        'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
        'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    # Base URL for team logos (using a more reliable source)
    base_url = "https://www.nba.com/.element/img/team/logos/{team}_logo.svg"
    
    # Download each team's logo
    for team_name in teams:
        try:
            # Convert team name to filename format (lowercase with underscores)
            filename = f"static/team_logos/{team_name.lower().replace(' ', '_')}.svg"
            
            # Skip if file already exists
            if os.path.exists(filename):
                print(f"Skipping {team_name} - file exists")
                continue
                
            # Format team name for URL (e.g., 'Los Angeles Lakers' -> 'lakers')
            team_slug = team_name.lower().split()[-1]
            if team_name == 'New York Knicks':
                team_slug = 'knicks'
            elif team_name == 'Golden State Warriors':
                team_slug = 'warriors'
                
            # Download the logo
            url = base_url.format(team=team_slug)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Save the logo
            with open(filename, 'wb') as f:
                f.write(response.content)
                
            print(f"Downloaded {team_name} logo to {filename}")
            
        except Exception as e:
            print(f"Error downloading {team_name} logo: {e}")
            # Create a simple SVG logo for the team
            team_svg = f"""<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <rect width="100" height="100" fill="#1d428a" rx="10"/>
                <text x="50" y="60" font-family="Arial" font-size="12" fill="white" text-anchor="middle">{team_name.upper()}</text>
            </svg>"""
            with open(filename, 'w') as f:
                f.write(team_svg)
            print(f"Created simple logo for {team_name}")
    
    # Create default logo if it doesn't exist
    if not os.path.exists('static/team_logos/default.png'):
        create_default_logo()

if __name__ == "__main__":
    download_logos()
