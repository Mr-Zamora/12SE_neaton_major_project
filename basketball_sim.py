"""
Basketball 1-on-1 Simulation Module

This module simulates a 1-on-1 basketball game between two NBA players
using their statistics and the Gemini API for generating play-by-play commentary.
Enhanced with derived player attributes for more realistic gameplay.
"""

import random
import json
import google.generativeai as genai
from config import GEMINI_API_KEY
from player_enhancer import enhance_player_data

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
        # Enhance player data with derived attributes
        self.player1 = enhance_player_data(player1)
        self.player2 = enhance_player_data(player2)
        self.target_score = target_score
        self.make_it_take_it = make_it_take_it
        
        # Game state
        self.score = {player1['name']: 0, player2['name']: 0}
        self.possession = None  # Will be set when game starts
        self.game_log = []
        self.game_over = False
        self.winner = None
        
        # Calculate additional derived stats that might be useful
        self._calculate_derived_stats()
    
    def _calculate_derived_stats(self):
        """Calculate additional stats that might be useful for simulation."""
        for player in [self.player1, self.player2]:
            # Convert height to inches for easier comparison
            height_str = player.get('height', '6\'0"')
            feet, inches = height_str.replace('"', '').split("'")
            player['height_inches'] = int(feet) * 12 + int(inches) if inches else int(feet) * 12
            
            # Calculate offensive rating (enhanced version using derived stats)
            player['offensive_rating'] = (
                player.get('points', 10) * 0.3 + 
                player.get('scoring_efficiency', 45) * 0.4 +
                player.get('usage_rate', 20) * 0.3
            )
            
            # Calculate defensive rating (enhanced version using derived stats)
            player['defensive_rating'] = (
                player.get('defensive_impact', 5) * 0.6 + 
                player.get('height_inches', 72) / 84 * 40  # Normalize height impact
            )
            
            # Handle missing stats with reasonable defaults
            if 'Steals Per Game (SPG)' not in player:
                player['Steals Per Game (SPG)'] = player.get('estimated_steals', 0.8)
            if 'Blocks Per Game (BPG)' not in player:
                player['Blocks Per Game (BPG)'] = player.get('estimated_blocks', 0.5)
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
        # Base probability from shooting percentages and derived stats
        if shot_type == 'inside':
            # Inside shots use FG% as base
            base_probability = offensive_player.get('Field Goal Percentage (FG%)', 45) / 100
            # Adjust for height advantage/disadvantage
            height_factor = 1 + (offensive_player.get('height_inches', 72) - 
                                defensive_player.get('height_inches', 72)) / 100
            base_probability *= height_factor
        else:  # outside shot
            # Outside shots use 3P% as base and consider three_point_tendency
            base_probability = offensive_player.get('Three-Point Percentage (3P%)', 33) / 100
            # Players who take more threes tend to be better at them in game situations
            tendency_bonus = offensive_player.get('three_point_tendency', 0.3) * 0.1
            base_probability += tendency_bonus
        
        # Adjust for offensive vs defensive ratings
        offensive_rating = offensive_player.get('offensive_rating', 50)
        defensive_rating = defensive_player.get('defensive_rating', 50)
        rating_factor = 1 + (offensive_rating - defensive_rating) / 200
        
        # Adjust for defensive impact specifically for this shot type
        if shot_type == 'inside':
            defense_impact = defensive_player.get('estimated_blocks', 0.5) * 0.05
        else:
            defense_impact = defensive_player.get('estimated_steals', 0.8) * 0.03
        
        # Calculate final probability
        final_probability = base_probability * rating_factor - defense_impact
        
        # Clamp to reasonable range
        return max(0.1, min(0.9, final_probability))
    
    def _simulate_possession(self):
        """Simulate a single possession in the game."""
        offensive_player = self.possession
        defensive_player = self.player2 if offensive_player == self.player1 else self.player1
        
        # Determine if there's a turnover
        turnover_chance = offensive_player.get('Turnovers Per Game (TOV)', 2.0) / 15
        steal_chance = defensive_player.get('estimated_steals', 0.8) / 10
        
        if random.random() < (turnover_chance + steal_chance):
            # Turnover occurred
            if random.random() < (steal_chance / (turnover_chance + steal_chance)):
                # It was a steal
                turnover_text = f"{defensive_player['name']} steals the ball from {offensive_player['name']}!"
            else:
                # It was an unforced turnover
                turnover_options = [
                    f"{offensive_player['name']} loses control of the ball and turns it over.",
                    f"{offensive_player['name']} steps out of bounds, turning the ball over.",
                    f"{offensive_player['name']} makes a bad pass that goes out of bounds.",
                    f"{offensive_player['name']} is called for traveling, turning the ball over."
                ]
                turnover_text = random.choice(turnover_options)
            
            self.game_log.append({"type": "turnover", "text": turnover_text})
            
            # Change possession
            self.possession = defensive_player
            return
        
        # Determine shot type (inside or outside) using three_point_tendency
        outside_shot_chance = offensive_player.get('three_point_tendency', 0.3)
            
        shot_type = 'outside' if random.random() < outside_shot_chance else 'inside'
        
        # Determine if shot is blocked
        block_chance = 0
        if shot_type == 'inside':
            # Inside shots can be blocked
            block_chance = defensive_player.get('estimated_blocks', 0.5) / 10
            # Height advantage increases block chance
            if defensive_player.get('height_inches', 72) > offensive_player.get('height_inches', 72):
                height_diff = defensive_player.get('height_inches', 72) - offensive_player.get('height_inches', 72)
                block_chance += height_diff / 200
        
        if random.random() < block_chance:
            # Shot is blocked
            block_text = self._generate_block_description(offensive_player, defensive_player, shot_type)
            self.game_log.append({"type": "block", "text": block_text})
            
            # 50% chance the blocker gains possession, otherwise ball stays with shooter
            if random.random() < 0.5:
                self.possession = defensive_player
            
            return
        
        # Calculate shot success probability
        success_prob = self._get_shot_success_probability(offensive_player, defensive_player, shot_type)
        
        # Adjust for clutch situations (close game in late stages)
        score_diff = abs(self.score[offensive_player['name']] - self.score[defensive_player['name']])
        close_game = score_diff <= 2
        near_end = max(self.score[offensive_player['name']], self.score[defensive_player['name']]) >= (self.target_score - 3)
        
        if close_game and near_end:
            # Clutch situation - adjust based on clutch_rating
            clutch_factor = offensive_player.get('clutch_rating', 0.5) * 0.2
            success_prob = success_prob * (1 + clutch_factor)
        
        # Adjust for stamina
        stamina_factor = offensive_player.get('stamina', 1.0) * 0.1
        success_prob = success_prob * (0.95 + stamina_factor)
        
        # Determine if shot is successful
        shot_successful = random.random() < success_prob
        
        # Generate description of the shot
        shot_description = self._generate_shot_description(
            offensive_player, defensive_player, shot_type, shot_successful
        )
        
        # Log the shot
        shot_type_log = "shot_made" if shot_successful else "shot_missed"
        self.game_log.append({"type": shot_type_log, "text": shot_description})
        
        if shot_successful:
            # Update score
            points = 2 if shot_type == 'outside' else 1
            self.score[offensive_player['name']] += points
            
            # Check if game is over
            if self.score[offensive_player['name']] >= self.target_score:
                self.game_over = True
                self.winner = offensive_player['name']
                
                # Generate conclusion text
                conclusion = f"Game over! {offensive_player['name']} wins {self.score[offensive_player['name']]}-{self.score[defensive_player['name']]}!"
                self.game_log.append({"type": "conclusion", "text": conclusion})
            
            # If make-it-take-it rules, offensive player keeps possession
            if not self.make_it_take_it:
                self.possession = defensive_player
        else:
            # Shot missed, determine who gets the rebound using derived offensive/defensive rebound stats
            if shot_type == 'inside':
                # Inside shots have different rebound dynamics
                off_rebound_chance = offensive_player.get('offensive_rebounds', 2) / (
                    offensive_player.get('offensive_rebounds', 2) + 
                    defensive_player.get('defensive_rebounds', 5)
                )
            else:
                # Outside shots tend to have longer rebounds
                off_rebound_chance = offensive_player.get('offensive_rebounds', 1) / (
                    offensive_player.get('offensive_rebounds', 1) + 
                    defensive_player.get('defensive_rebounds', 4) * 1.2
                )
            
            # Adjust for height
            height_advantage = (offensive_player.get('height_inches', 72) - 
                               defensive_player.get('height_inches', 72)) / 100
            off_rebound_chance += height_advantage
            
            # Clamp to reasonable range
            off_rebound_chance = max(0.2, min(0.8, off_rebound_chance))
            
            if random.random() < off_rebound_chance:
                # Offensive rebound
                rebound_text = f"{offensive_player['name']} grabs their own miss!"
                self.game_log.append({"type": "rebound", "text": rebound_text})
                # Possession stays with offensive player
            else:
                # Defensive rebound
                rebound_text = f"{defensive_player['name']} secures the defensive rebound."
                self.game_log.append({"type": "rebound", "text": rebound_text})
                # Change possession
                self.possession = defensive_player
    
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
        # Initialize game
        self.game_log = []
        self.score = {self.player1['name']: 0, self.player2['name']: 0}
        self.possession = random.choice([self.player1, self.player2])
        self.winner = None
        
        # Start the game with an introduction
        intro = f"Welcome to this 1v1 showdown between {self.player1['name']} and {self.player2['name']}! "
        intro += f"First to {self.target_score} points wins, and we're playing {'make it, take it' if self.make_it_take_it else 'alternating possession'} rules. "
        intro += f"{self.possession['name']} wins the tip and will start with the ball."
        self.game_log.append({"type": "intro", "text": intro})
        
        # Track fatigue
        fatigue = {self.player1['name']: 0, self.player2['name']: 0}
        
        # Simulate possessions until target score is reached
        possession_count = 0
        alternate_possession = not self.make_it_take_it
        
        while max(self.score.values()) < self.target_score and possession_count < 100:  # Safety limit
            possession_count += 1
            
            # Get current players
            offensive_player = self.possession
            defensive_player = self.player2 if offensive_player == self.player1 else self.player1
            
            # Add "checks the ball" action every possession
            check_ball = f"{offensive_player['name']} checks the ball at the top of the key."
            self.game_log.append({"type": "check_ball", "text": check_ball})
            
            # Apply fatigue effects (players get tired as game progresses)
            fatigue_factor = 1.0 - (fatigue[offensive_player['name']] * 0.01 * (1.0 / offensive_player.get('stamina', 1.0)))
            
            # Determine if there's a turnover
            turnover_chance = 0.05 + (offensive_player.get('Turnovers Per Game (TOV)', 2.0) / 40)
            if random.random() < turnover_chance:
                turnover_text = f"{offensive_player['name']} loses control of the ball! Turnover to {defensive_player['name']}."
                self.game_log.append({"type": "turnover", "text": turnover_text})
                self.possession = defensive_player
                continue
            
            # Determine shot type based on player position and tendencies
            shot_type_odds = 0.7  # Base chance for inside shot
            if offensive_player['position'] in ['PG', 'SG', 'SF']:
                shot_type_odds = 0.5  # Guards and wings take more outside shots
            
            # Adjust based on three-point percentage
            three_pt_pct = offensive_player.get('Three-Point Percentage (3P%)', 30.0)
            if three_pt_pct > 35:  # Good three-point shooters
                shot_type_odds -= 0.1
            
            shot_type = 'inside' if random.random() < shot_type_odds else 'outside'
            
            # Calculate success probability
            success_prob = self._get_shot_success_probability(offensive_player, defensive_player, shot_type)
            
            # Apply fatigue factor
            success_prob *= fatigue_factor
            
            # Determine if shot is successful
            shot_successful = random.random() < success_prob
            
            # Generate description and update game state
            shot_description = self._generate_shot_description(offensive_player, defensive_player, shot_type, shot_successful)
            
            if shot_successful:
                # Award points
                points = 1 if shot_type == 'inside' else 2
                self.score[offensive_player['name']] += points
                
                # Add to game log
                shot_text = f"{shot_description} {offensive_player['name']} scores! "
                shot_text += f"Score: {offensive_player['name']} {self.score[offensive_player['name']]}, {defensive_player['name']} {self.score[defensive_player['name']]}."
                self.game_log.append({"type": "shot_made", "text": shot_text})
                
                # Check if game is over
                if self.score[offensive_player['name']] >= self.target_score:
                    self.winner = offensive_player
                    break
                
                # Determine next possession
                if not alternate_possession:  # Make it, take it
                    pass  # Keep possession
                else:
                    self.possession = defensive_player
            else:
                # Shot missed, defensive player gets rebound
                rebound_text = f"{shot_description} {defensive_player['name']} grabs the rebound."
                self.game_log.append({"type": "shot_missed", "text": rebound_text})
                self.possession = defensive_player
            
            # Increase fatigue
            fatigue[offensive_player['name']] += 0.5
            fatigue[defensive_player['name']] += 0.3
        
        # Generate game conclusion
        if self.winner:
            loser = self.player2 if self.winner == self.player1 else self.player1
            conclusion = f"Game over! {self.winner['name']} wins {self.score[self.winner['name']]} to {self.score[loser['name']]}!"
            self.game_log.append({"type": "conclusion", "text": conclusion})
        else:
            conclusion = "The game reached the maximum number of possessions without a winner."
            self.game_log.append({"type": "conclusion", "text": conclusion})
        
        # Return game result
        return {
            "game_log": self.game_log,
            "final_score": self.score,
            "winner": self.winner['name'] if self.winner else None,
            "player1": self.player1,
            "player2": self.player2
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
        
        Format your response with the following requirements:
        1. Use HTML formatting for better readability
        2. DO NOT use headings like "Game Summary", "Introduction:", etc. at the beginning of the commentary
        3. Start directly with the play-by-play narrative without any headers
        4. Use <h3> tags only for meaningful section headings if needed (First Half, Second Half, etc.)
        5. Use <p> tags for paragraphs
        6. Use <strong> or <b> tags to emphasize important moments, player names, and scores
        7. Use <br> tags for line breaks within paragraphs where appropriate
        8. Create a clear structure with game progression and conclusion
        9. Include statistics and highlight key plays in a visually distinct way
        10. For the final score, make it stand out with bold formatting
        
        Include an introduction, the play-by-play narrative organized by game progression, and a conclusion with the final result.
        """
        
        try:
            # Call Gemini API
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            enhanced_commentary = response.text
            
            # If the response doesn't contain HTML formatting, add basic formatting
            if '<' not in enhanced_commentary and '>' not in enhanced_commentary:
                # Split by double newlines to identify paragraphs
                paragraphs = enhanced_commentary.split('\n\n')
                formatted_text = []
                
                # Process each paragraph
                for i, para in enumerate(paragraphs):
                    # Check if paragraph looks like a section header (short and ends with colon)
                    if len(para) < 50 and para.strip().endswith(':') and i > 0:  # Skip first paragraph headers
                        # Skip if it contains "Game Summary" or "Introduction"
                        if "game summary" not in para.lower() and "introduction" not in para.lower():
                            formatted_text.append(f"<h3>{para}</h3>")
                    else:
                        # Highlight player names, scores, and key terms
                        for player_name in [self.player1['name'], self.player2['name']]:
                            para = para.replace(player_name, f"<strong>{player_name}</strong>")
                        
                        # Highlight score mentions
                        import re
                        para = re.sub(r'(\d+)-(\d+)', r'<strong>\1-\2</strong>', para)
                        
                        # Add paragraph tags
                        formatted_text.append(f"<p>{para}</p>")
                
                enhanced_commentary = "\n\n".join(formatted_text)
            
            return enhanced_commentary
        except Exception as e:
            # Fallback if API fails
            print(f"Error calling Gemini API: {e}")
            fallback_text = ""
            for entry in self.game_log:
                if entry['type'] == 'intro':
                    fallback_text += f"<p>{entry['text']}</p>\n"
                elif entry['type'] == 'conclusion':
                    fallback_text += f"<p><strong>{entry['text']}</strong></p>\n"
                elif entry['type'] in ['shot_made', 'shot_missed', 'block', 'turnover']:
                    fallback_text += f"<p>{entry['text']}</p>\n"
            return fallback_text


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
    # Create simulator (player enhancement happens in the constructor)
    simulator = BasketballSimulator(player1_data, player2_data, target_score, make_it_take_it)
    
    # Run simulation
    game_result = simulator.simulate_full_game()
    
    # Add enhanced player attributes to the result for display
    game_result['enhanced_player1'] = simulator.player1
    game_result['enhanced_player2'] = simulator.player2
    
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
