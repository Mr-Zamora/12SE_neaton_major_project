"""
Basketball 1-on-1 Simulation Module

This module simulates a 1-on-1 basketball game between two NBA players
using their statistics and the Gemini API for generating play-by-play commentary.
"""

import random
import json
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class BasketballSimulator:
    def __init__(self, player1, player2, target_score=11, make_it_take_it=True):
        """
        Initialize the basketball simulator with two players.
        
        Args:
            player1: Dictionary containing player 1's stats
            player2: Dictionary containing player 2's stats
            target_score: Points needed to win (default: 11)
            make_it_take_it: If True, scorer keeps possession (default: True)
        """
        self.player1 = player1
        self.player2 = player2
        self.target_score = target_score
        self.make_it_take_it = make_it_take_it
        
        # Game state
        self.score = {player1['name']: 0, player2['name']: 0}
        self.possession = None  # Will be set when game starts
        self.game_log = []
        self.game_over = False
        self.winner = None
        
        # Calculate derived stats that might be useful
        self._calculate_derived_stats()
    
    def _calculate_derived_stats(self):
        """Calculate additional stats that might be useful for simulation."""
        for player in [self.player1, self.player2]:
            # Convert height to inches for easier comparison
            height_str = player.get('height', '6\'0"')
            feet, inches = height_str.replace('"', '').split("'")
            player['height_inches'] = int(feet) * 12 + int(inches) if inches else int(feet) * 12
            
            # Calculate offensive rating (simple version)
            player['offensive_rating'] = (
                player.get('points', 10) * 0.4 + 
                player.get('Field Goal Percentage (FG%)', 45) * 0.3 +
                player.get('Three-Point Percentage (3P%)', 33) * 0.3
            )
            
            # Calculate defensive rating (simple version)
            player['defensive_rating'] = (
                player.get('rebounds', 5) * 0.5 + 
                player.get('height_inches', 72) / 84 * 50  # Normalize height impact
            )
            
            # Stamina rating based on MPG
            player['stamina'] = min(100, player.get('Average Minutes Per Game (MPG)', 25) * 2.5)
            
            # Handle missing stats with reasonable defaults
            if 'Steals Per Game (SPG)' not in player:
                player['Steals Per Game (SPG)'] = 0.8  # League average
            if 'Blocks Per Game (BPG)' not in player:
                player['Blocks Per Game (BPG)'] = 0.5  # League average
            if 'Turnovers Per Game (TOV)' not in player:
                player['Turnovers Per Game (TOV)'] = 2.0  # League average
    
    def start_game(self):
        """Start the game by determining initial possession."""
        # Determine who starts with the ball (50/50 chance)
        self.possession = random.choice([self.player1, self.player2])
        
        # Log the game start
        intro = f"Welcome to this 1v1 showdown between {self.player1['name']} and {self.player2['name']}! "
        intro += f"First to {self.target_score} points wins, and we're playing {'make it, take it' if self.make_it_take_it else 'alternating possession'} rules. "
        intro += f"{self.possession['name']} wins the tip and will start with the ball."
        
        self.game_log.append({"type": "intro", "text": intro})
        return intro
    
    def _get_shot_success_probability(self, offensive_player, defensive_player, shot_type):
        """
        Calculate the probability of a successful shot.
        
        Args:
            offensive_player: Player taking the shot
            defensive_player: Player defending
            shot_type: Either 'inside' (1-pointer) or 'outside' (2-pointer)
        
        Returns:
            Float representing probability (0-1) of shot success
        """
        # Base probability from player stats
        if shot_type == 'inside':
            base_prob = offensive_player.get('Field Goal Percentage (FG%)', 45) / 100
        else:  # outside shot
            base_prob = offensive_player.get('Three-Point Percentage (3P%)', 33) / 100
        
        # Defensive impact
        height_diff = defensive_player['height_inches'] - offensive_player['height_inches']
        height_factor = min(0.15, max(-0.05, height_diff * 0.01))  # Taller defender has advantage
        
        # Defensive impact based on position matchup
        def_impact = 0.1  # Base defensive impact
        
        # Adjust for defender's position and stats
        if defensive_player.get('position') in ['C', 'PF'] and shot_type == 'inside':
            def_impact += 0.05  # Big men better at defending inside
        if defensive_player.get('position') in ['SG', 'SF'] and shot_type == 'outside':
            def_impact += 0.05  # Wing players better at defending outside
            
        # Block chance
        block_chance = min(0.15, defensive_player.get('Blocks Per Game (BPG)', 0.5) / 10)
        
        # Calculate final probability
        final_prob = base_prob - (def_impact + height_factor + block_chance/2)
        
        # Ensure probability is within reasonable bounds
        return max(0.2, min(0.9, final_prob))
    
    def _simulate_possession(self):
        """Simulate a single possession in the game."""
        offensive_player = self.possession
        defensive_player = self.player2 if offensive_player == self.player1 else self.player1
        
        # Check if there's a turnover
        turnover_chance = offensive_player.get('Turnovers Per Game (TOV)', 2) / 20  # 10% per turnover
        if random.random() < turnover_chance:
            action = f"{offensive_player['name']} dribbles, but {defensive_player['name']} pokes the ball away! Turnover!"
            self.game_log.append({"type": "turnover", "text": action})
            self.possession = defensive_player
            return {"result": "turnover", "text": action}
        
        # Determine shot type based on player position and tendencies
        inside_shot_tendency = {
            'C': 0.8, 'PF': 0.7, 'SF': 0.6, 'SG': 0.5, 'PG': 0.5
        }.get(offensive_player.get('position', 'SF'), 0.6)
        
        # Adjust based on player's 3P% vs FG%
        three_point_skill = offensive_player.get('Three-Point Percentage (3P%)', 33) / 100
        if three_point_skill > 0.37:  # Good 3-point shooter
            inside_shot_tendency -= 0.1
        
        # Determine if shot is inside or outside
        shot_type = 'inside' if random.random() < inside_shot_tendency else 'outside'
        
        # Get shot success probability
        success_prob = self._get_shot_success_probability(offensive_player, defensive_player, shot_type)
        
        # Check for block
        block_chance = min(0.2, defensive_player.get('Blocks Per Game (BPG)', 0.5) / 5)
        if shot_type == 'inside':
            block_chance *= 1.5  # More likely to block inside shots
        
        if random.random() < block_chance:
            action = self._generate_block_description(offensive_player, defensive_player, shot_type)
            self.game_log.append({"type": "block", "text": action})
            self.possession = defensive_player
            return {"result": "block", "text": action}
        
        # Determine if shot is successful
        shot_successful = random.random() < success_prob
        
        # Generate description
        action = self._generate_shot_description(offensive_player, defensive_player, shot_type, shot_successful)
        
        if shot_successful:
            # Update score
            points = 2 if shot_type == 'outside' else 1
            self.score[offensive_player['name']] += points
            
            # Check if game is over
            if self.score[offensive_player['name']] >= self.target_score:
                # Check if we need to win by 2
                opponent_score = self.score[defensive_player['name']]
                if self.score[offensive_player['name']] >= opponent_score + 2:
                    self.game_over = True
                    self.winner = offensive_player
            
            # Determine next possession
            if not self.make_it_take_it:
                self.possession = defensive_player
            # If make_it_take_it, offensive player keeps possession
            
            # Add score to action
            action += f" Score: {self.player1['name']} {self.score[self.player1['name']]}, {self.player2['name']} {self.score[self.player2['name']]}"
            
            self.game_log.append({"type": "shot_made", "text": action, "points": points})
            return {"result": "shot_made", "text": action, "points": points}
        else:
            # Shot missed, determine rebound
            offensive_rebound_chance = offensive_player.get('rebounds', 5) / (
                offensive_player.get('rebounds', 5) + defensive_player.get('rebounds', 5) * 1.5
            )
            
            # Height advantage in rebounding
            height_diff = offensive_player['height_inches'] - defensive_player['height_inches']
            offensive_rebound_chance += height_diff * 0.005  # Small adjustment for height
            
            # Ensure reasonable bounds
            offensive_rebound_chance = max(0.2, min(0.7, offensive_rebound_chance))
            
            rebound_player = offensive_player if random.random() < offensive_rebound_chance else defensive_player
            
            # Generate rebound description
            rebound_text = f" {rebound_player['name']} grabs the rebound!"
            action += rebound_text
            
            # Update possession
            self.possession = rebound_player
            
            self.game_log.append({"type": "shot_missed", "text": action})
            return {"result": "shot_missed", "text": action}
    
    def _generate_shot_description(self, offensive_player, defensive_player, shot_type, successful):
        """Generate a descriptive text for a shot attempt."""
        # Shot type descriptions
        inside_moves = [
            "drives to the basket",
            "makes a quick move to the hoop",
            "backs down in the post",
            "spins into the lane",
            "cuts to the basket",
            "goes up strong",
            "attempts a layup",
            "tries a floater",
            "goes for a post move"
        ]
        
        outside_moves = [
            "pulls up for a deep shot",
            "steps back for a jumper",
            "creates space for a jump shot",
            "rises up for the long-range shot",
            "attempts a perimeter shot",
            "goes for a fadeaway jumper"
        ]
        
        # Select move based on shot type
        move = random.choice(inside_moves if shot_type == 'inside' else outside_moves)
        
        # Build description
        description = f"{offensive_player['name']} {move}"
        
        # Add defensive context
        if random.random() < 0.7:  # 70% chance to mention defense
            defensive_actions = [
                f"with {defensive_player['name']} contesting",
                f"against tight defense from {defensive_player['name']}",
                f"with {defensive_player['name']} right there",
                f"over {defensive_player['name']}"
            ]
            description += f" {random.choice(defensive_actions)}"
        
        # Add result
        if successful:
            success_phrases = [
                "... and it's good!",
                "... it drops in!",
                "... nothing but net!",
                "... count it!",
                "... and scores!",
                "... and converts!"
            ]
            description += f" {random.choice(success_phrases)}"
        else:
            miss_phrases = [
                "... but misses!",
                "... off the rim!",
                "... but it's no good!",
                "... but can't connect!",
                "... but it rims out!"
            ]
            description += f" {random.choice(miss_phrases)}"
        
        return description
    
    def _generate_block_description(self, offensive_player, defensive_player, shot_type):
        """Generate a descriptive text for a blocked shot."""
        if shot_type == 'inside':
            block_phrases = [
                f"{offensive_player['name']} goes up for the shot, but {defensive_player['name']} BLOCKS it emphatically!",
                f"{defensive_player['name']} meets {offensive_player['name']} at the rim and rejects the shot!",
                f"Great defense! {defensive_player['name']} swats away {offensive_player['name']}'s attempt!",
                f"{offensive_player['name']} drives in but {defensive_player['name']} times it perfectly for the block!"
            ]
        else:
            block_phrases = [
                f"{offensive_player['name']} pulls up, but {defensive_player['name']} gets a piece of it!",
                f"{defensive_player['name']} closes out quickly and blocks {offensive_player['name']}'s jumper!",
                f"Great perimeter defense! {defensive_player['name']} blocks the shot attempt!",
                f"{offensive_player['name']}'s shot is rejected by {defensive_player['name']}!"
            ]
        
        return random.choice(block_phrases)
    
    def simulate_full_game(self):
        """Simulate the entire game until completion."""
        # Start the game
        self.start_game()
        
        # Simulate possessions until game is over
        possession_count = 0
        while not self.game_over and possession_count < 100:  # Safety limit
            possession_count += 1
            
            # Add "checks the ball" action every possession
            check_ball = f"{self.possession['name']} checks the ball at the top of the key."
            self.game_log.append({"type": "check_ball", "text": check_ball})
            
            # Simulate the possession
            self._simulate_possession()
        
        # Generate game conclusion
        if self.winner:
            conclusion = f"Game over! {self.winner['name']} wins {self.score[self.winner['name']]} to {self.score[self.player2['name'] if self.winner == self.player1 else self.player1['name']]}!"
            self.game_log.append({"type": "conclusion", "text": conclusion})
        else:
            conclusion = "The game reached the maximum number of possessions without a winner."
            self.game_log.append({"type": "conclusion", "text": conclusion})
        
        return {
            "game_log": self.game_log,
            "final_score": self.score,
            "winner": self.winner['name'] if self.winner else None
        }
    
    def get_enhanced_commentary(self):
        """
        Use Gemini API to generate enhanced play-by-play commentary
        based on the simulated game log.
        """
        # Prepare the prompt for Gemini
        prompt = f"""
        You are a basketball commentator providing play-by-play commentary for a 1-on-1 basketball game.
        
        Player 1: {json.dumps(self.player1, indent=2)}
        
        Player 2: {json.dumps(self.player2, indent=2)}
        
        Game Rules:
        - First to {self.target_score} points wins (must win by 2)
        - Inside shots (within the arc) are worth 1 point
        - Outside shots (beyond the arc) are worth 2 points
        - {'Make it, take it rules (scorer keeps possession)' if self.make_it_take_it else 'Alternating possession after made baskets'}
        
        Game Log:
        {json.dumps([entry['text'] for entry in self.game_log], indent=2)}
        
        Please provide an engaging, detailed play-by-play commentary of this game, highlighting key moments,
        player strengths/weaknesses, and tactical decisions. Make it sound like an exciting broadcast.
        Include an introduction, the play-by-play narrative, and a conclusion with the final result.
        """
        
        try:
            # Call Gemini API
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            enhanced_commentary = response.text
            
            return enhanced_commentary
        except Exception as e:
            # Fallback if API fails
            print(f"Error calling Gemini API: {e}")
            return "\n".join([entry['text'] for entry in self.game_log])


def simulate_game(player1_data, player2_data, target_score=11, make_it_take_it=True, use_gemini=True):
    """
    Simulate a 1-on-1 basketball game between two players.
    
    Args:
        player1_data: Dictionary with player 1's stats
        player2_data: Dictionary with player 2's stats
        target_score: Points needed to win (default: 11)
        make_it_take_it: If True, scorer keeps possession (default: True)
        use_gemini: If True, use Gemini API for enhanced commentary
    
    Returns:
        Dictionary containing game results and commentary
    """
    # Create simulator
    simulator = BasketballSimulator(player1_data, player2_data, target_score, make_it_take_it)
    
    # Run simulation
    game_result = simulator.simulate_full_game()
    
    # Get enhanced commentary if requested
    if use_gemini:
        try:
            commentary = simulator.get_enhanced_commentary()
            game_result['enhanced_commentary'] = commentary
        except Exception as e:
            print(f"Error getting enhanced commentary: {e}")
            game_result['enhanced_commentary'] = None
    
    return game_result


if __name__ == "__main__":
    # Test the simulator with sample data
    player1 = {
        "name": "Test Player 1",
        "position": "C",
        "points": 20.5,
        "rebounds": 10.2,
        "assists": 2.3,
        "Field Goal Percentage (FG%)": 52.1,
        "Three-Point Percentage (3P%)": 22.5,
        "height": "6'10"
    }
    
    player2 = {
        "name": "Test Player 2",
        "position": "SG",
        "points": 22.1,
        "rebounds": 4.5,
        "assists": 5.7,
        "Field Goal Percentage (FG%)": 45.8,
        "Three-Point Percentage (3P%)": 38.2,
        "height": "6'5"
    }
    
    result = simulate_game(player1, player2, use_gemini=False)
    for entry in result['game_log']:
        print(entry['text'])
