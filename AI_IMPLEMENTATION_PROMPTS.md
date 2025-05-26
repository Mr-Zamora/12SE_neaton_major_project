# AI Implementation Prompts

This document provides detailed prompts for implementing each AI enhancement from AI_ENHANCEMENTS.md.

## 1. Player Profile Enhancements

### 1.1 AI-Generated Player Bios
```
Create a concise NBA scouting report for {player_name}, a {position} for the {team}. 

Key Stats:
- {points} PPG, {assists} APG, {rebounds} RPG
- Shooting: {fg_pct}% FG, {3p_pct}% 3P, {ft_pct}% FT
- Efficiency: {ts_pct}% TS

Write a 3-4 sentence bio that:
1. Describes their playing style and role
2. Highlights their key strengths and skills
3. Mentions any notable statistical achievements
4. Uses an engaging, scouting report style

Keep it under 100 words and avoid generic phrases. Focus on what makes this player unique based on their stats.
```

### 1.2 Player Archetype Classification
```
Classify this NBA player into one of these archetypes based on their stats:
- 3&D Wing: Strong defense and 3pt shooting
- Floor General: High assists, low turnovers
- Volume Scorer: High PPG, lower efficiency
- Two-Way Star: Strong both offensively and defensively
- Stretch Big: Big with outside shooting
- Rim Protector: High blocks and rebounds
- 3-Level Scorer: Efficient from all areas
- Playmaker: High assists and scoring
- 3-Point Specialist: Elite 3pt shooting
- Defensive Anchor: Elite defender, lower offensive role

Player: {player_name}
Position: {position}
Stats: {points} PPG, {assists} APG, {rebounds} RPG, {fg_pct}% FG, {3p_pct}% 3P, {blocks} BPG, {steals} SPG

Return a JSON object with:
{
  "archetype": "Most fitting archetype",
  "confidence": "High/Medium/Low",
  "explanation": "2-3 sentences explaining the classification"
}
```

## 2. Comparison Page Features

### 2.1 Head-to-Head Analysis
```
Compare these two NBA players and highlight 2-3 key statistical differences:

{player1_name} ({player1_team}) vs {player2_name} ({player2_team}})

Player 1 Stats:
- {p1_ppg} PPG, {p1_apg} APG, {p1_rpg} RPG
- {p1_fg}% FG, {p1_3p}% 3P, {p1_ft}% FT
- {p1_ts}% TS, {p1_mpg} MPG

Player 2 Stats:
- {p2_ppg} PPG, {p2_apg} APG, {p2_rpg} RPG
- {p2_fg}% FG, {p2_3p}% 3P, {p2_ft}% FT
- {p2_ts}% TS, {p2_mpg} MPG

Return a JSON object with:
{
  "comparisons": [
    {
      "category": "Category name",
      "winner": "Player1/Player2/Even",
      "difference": "X% or X more/less",
      "explanation": "1-2 sentences explaining the difference"
    },
    ...
  ]
}
```

### 2.2 Role-Based Comparison
```
Analyze how these two NBA players with similar stats fulfill different roles:

{player1_name} ({player1_position}): {player1_stats}
{player2_name} ({player2_position}): {player2_stats}

For each player, describe:
1. Their primary role on the court
2. How their stats reflect their playing style
3. What makes them unique compared to the other player
4. Which team needs they might fit better

Keep each analysis to 100 words or less and focus on the differences in how they contribute to winning.
```

## 3. Team Analysis

### 3.1 Team Composition Analysis
```
Analyze this NBA team's composition based on player stats:

Team: {team_name}
Players: 
{formatted_player_list}

Provide a 3-part analysis:
1. Offensive Strengths/Weaknesses
2. Defensive Strengths/Weaknesses
3. Overall Team Identity

For each, include:
- 2-3 specific statistical insights
- How they compare to league averages
- Any notable gaps or imbalances

Format as markdown with clear section headers. Keep each section under 150 words.
```

### 3.2 Lineup Optimizer
```
Given this roster of players, suggest the best 5-player lineup:

{formatted_roster}

Consider:
- Positional balance
- Offensive/defensive balance
- Statistical complementarity
- Floor spacing
- Playmaking

Return a JSON object with:
{
  "lineup": ["PG", "SG", "SF", "PF", "C"],
  "reasoning": {
    "offense": "2-3 sentences",
    "defense": "2-3 sentences",
    "synergy": "How the players complement each other"
  },
  "potential_weaknesses": "1-2 potential issues"
}
```

## 4. Interactive Features

### 4.1 Player Similarity Finder
```
Find the 3 most similar players to {target_player} from this list:

{formatted_player_list}

Compare based on these weighted stats:
- Scoring (30%): Points per game, TS%
- Playmaking (25%): Assists, assist-to-turnover ratio
- Rebounding (15%): Total rebounds per game
- Defense (20%): Steals, blocks
- Efficiency (10%): FG%, 3P%, FT%

Return a JSON array of player objects with similarity scores and explanations:
[
  {
    "player": "Player Name",
    "similarity_score": 0-100,
    "key_similarities": ["stat1", "stat2", ...],
    "key_differences": ["stat1", "stat2", ...]
  },
  ...
]
```

### 4.2 "What Makes Them Special"
```
Analyze this NBA player's stats and identify their most distinctive attribute:

{player_name}
{formatted_stats}

Return a JSON object with:
{
  "attribute": "Name of the most distinctive attribute",
  "stat_value": "The numerical value",
  "percentile": "How they rank (top X%)",
  "explanation": "2-3 sentences explaining why this is special",
  "comparison": "How this compares to league/position average"
}
```

## 5. Simulation Enhancements

### 5.1 Contextual Commentary
```
Generate a single sentence of basketball commentary for this game situation:

Game: {team1} vs {team2}
Score: {score}
Time: {time_remaining}
Situation: {game_situation}

Player with ball: {ball_handler} ({ball_handler_stats})
Defender: {defender} ({defender_stats})

Consider:
- Player tendencies
- Game context
- Recent plays
- Matchups

Make it sound like a real NBA commentator. Be concise (max 15 words).
```

### 5.2 "Keys to Victory"
```
After a simulated game between {team1} and {team2}, analyze the box score and identify 3 key factors that decided the game:

{formatted_box_score}

For each factor:
1. Name the factor (e.g., "Three-point shooting")
2. Provide the relevant stats
3. Explain its impact
4. Note any surprising elements

Format as a numbered list with 1-2 sentences per factor. Keep it analytical but accessible.
```

## 6. Educational Features

### 6.1 Stat Explainer
```
Explain the basketball statistic "{stat_name}" in simple terms.

Include:
1. Definition (1 sentence)
2. How it's calculated (1-2 sentences)
3. What makes a good/bad value
4. Example using {player_name} ({player_value} {stat_name})
5. How it compares to league average
6. Why it matters for evaluating players

Keep each section brief. Use markdown for formatting. Target a casual basketball fan.
```

### 6.2 Basketball IQ Quiz
```
Generate a multiple-choice basketball knowledge question based on these player stats:

{formatted_player_stats}

Requirements:
- Must be answerable using only the provided stats
- Include 4 plausible answer choices
- Focus on comparing players/teams
- Avoid trivial questions
- Include difficulty level (Beginner/Intermediate/Advanced)

Return as JSON:
{
  "question": "Clear, concise question",
  "options": ["A. ...", "B. ...", ...],
  "correct_answer": "Letter of correct answer",
  "explanation": "2-3 sentence explanation",
  "difficulty": "Beginner/Intermediate/Advanced"
}
```

## Implementation Notes

1. **Caching**: Cache all AI responses with appropriate cache keys based on input parameters
2. **Error Handling**: Implement fallback content for each AI feature
3. **Rate Limiting**: Add rate limiting to prevent API abuse
4. **Testing**: Create test cases for each prompt with expected outputs
5. **Localization**: Consider adding language support for international users
6. **Accessibility**: Ensure all AI-generated content is accessible (alt text, ARIA labels, etc.)
