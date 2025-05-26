"""
Player Enhancer Module

This module enhances player data by calculating derived attributes from existing statistics.
These derived attributes are used to improve the realism of the basketball simulation.
"""

def enhance_player_data(player):
    """
    Enhance player data with derived attributes based on existing statistics.
    
    Args:
        player: Dictionary containing player stats
        
    Returns:
        Enhanced player dictionary with additional derived attributes
    """
    # Create a copy of the player dict to avoid modifying the original
    enhanced_player = player.copy()
    
    # Calculate scoring efficiency (composite of shooting percentages)
    enhanced_player['scoring_efficiency'] = (
        player.get('Field Goal Percentage (FG%)', 45) * 0.5 +
        player.get('Three-Point Percentage (3P%)', 33) * 0.3 +
        player.get('Free Throw Percentage (FT%)', 75) * 0.2
    )
    
    # Estimate usage rate based on points and assists
    enhanced_player['usage_rate'] = min(100, (
        player.get('points', 10) * 2 + 
        player.get('assists', 3) * 1.5
    ))
    
    # Position-based defensive estimates
    position = player.get('position', 'SF')
    if any(pos in position for pos in ['C', 'PF']):
        # Big men tend to block more shots but get fewer steals
        enhanced_player['estimated_blocks'] = 1.2 + (player.get('rebounds', 5) * 0.1)
        enhanced_player['estimated_steals'] = 0.8
        # Estimate offensive vs defensive rebounds
        enhanced_player['offensive_rebounds'] = player.get('rebounds', 5) * 0.35
        enhanced_player['defensive_rebounds'] = player.get('rebounds', 5) * 0.65
    elif any(pos in position for pos in ['PG', 'SG']):
        # Guards tend to get more steals but fewer blocks
        enhanced_player['estimated_steals'] = 1.2 + (player.get('assists', 3) * 0.1)
        enhanced_player['estimated_blocks'] = 0.3
        # Guards get fewer offensive rebounds
        enhanced_player['offensive_rebounds'] = player.get('rebounds', 3) * 0.2
        enhanced_player['defensive_rebounds'] = player.get('rebounds', 3) * 0.8
    else:
        # Small forwards are balanced
        enhanced_player['estimated_steals'] = 1.0
        enhanced_player['estimated_blocks'] = 0.7
        enhanced_player['offensive_rebounds'] = player.get('rebounds', 4) * 0.25
        enhanced_player['defensive_rebounds'] = player.get('rebounds', 4) * 0.75
    
    # Calculate stamina factor based on minutes per game
    enhanced_player['stamina'] = 0.9 + (
        player.get('Average Minutes Per Game (MPG)', 25) / 40
    ) * 0.2
    
    # Estimate clutch performance (based on FT% and TS%)
    enhanced_player['clutch_rating'] = (
        player.get('Free Throw Percentage (FT%)', 75) * 0.6 +
        player.get('True Shooting Percentage (TS%)', 55) * 0.4
    ) / 100
    
    # Estimate shot distribution (2PT vs 3PT tendency)
    fg_pct = player.get('Field Goal Percentage (FG%)', 45)
    tp_pct = player.get('Three-Point Percentage (3P%)', 33)
    
    # If 3P% is close to FG%, player likely takes more 3s
    if (fg_pct - tp_pct) < 8:
        enhanced_player['three_point_tendency'] = 0.6  # 60% of shots are 3s
    elif (fg_pct - tp_pct) < 15:
        enhanced_player['three_point_tendency'] = 0.4  # 40% of shots are 3s
    else:
        enhanced_player['three_point_tendency'] = 0.2  # 20% of shots are 3s
    
    # Estimate defensive impact based on position and rebounds
    enhanced_player['defensive_impact'] = (
        player.get('rebounds', 5) * 0.5 +
        enhanced_player['estimated_blocks'] * 2 +
        enhanced_player['estimated_steals'] * 1.5
    ) / 10
    
    return enhanced_player
