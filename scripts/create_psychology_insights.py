#!/usr/bin/env python3
"""
Create advanced psychological insights visualizations for League of Hard Knox.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import math

def create_psychology_insights():
    """Create comprehensive psychological analysis dashboard"""
    
    print("🧠 CREATING PSYCHOLOGICAL INSIGHTS - LEAGUE OF HARD KNOX")
    print("=" * 65)
    
    # Load the datasets
    data_dir = Path("data/final_dataset")
    matchups_df = pd.read_csv(data_dir / "league_hard_knox_2017_2024_complete.csv")
    
    print(f"📊 Loaded {len(matchups_df)} matchups for psychological analysis")
    
    # Filter to active managers
    active_managers = ['Hayden', 'Michael', 'Phoenix', 'Billy', 'Robbie', 'Nelson', 
                      'Fraser', 'Justin', 'Angus', 'Nic', 'William', 'James']
    
    current_matchups = matchups_df[
        matchups_df['manager1'].isin(active_managers) &
        matchups_df['manager2'].isin(active_managers)
    ].copy()
    
    # Create output directory
    viz_dir = Path("visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    print(f"🎯 Creating advanced psychological insights...")
    
    # 1. Performance Psychology Analysis
    psychology_data = analyze_performance_psychology(current_matchups, active_managers)
    
    # 2. Manager DNA Analysis
    dna_data = analyze_manager_dna(current_matchups, active_managers)
    
    # 3. League Evolution Analysis
    evolution_data = analyze_league_evolution(current_matchups)
    
    # 4. Create visualizations
    create_clutch_factor_viz(psychology_data, viz_dir)
    create_momentum_tracker(psychology_data, viz_dir)
    create_consistency_analysis(psychology_data, viz_dir)
    create_manager_dna_radar(dna_data, viz_dir)
    create_league_evolution_viz(evolution_data, viz_dir)
    create_psychology_dashboard(psychology_data, dna_data, evolution_data, viz_dir)
    
    print(f"\\n🎉 PSYCHOLOGICAL INSIGHTS COMPLETE!")
    print(f"📂 Files saved to: {viz_dir}/")
    print(f"🧠 Open psychology_dashboard.html for comprehensive insights")
    
    return True

def analyze_performance_psychology(matchups_df, active_managers):
    """Analyze psychological performance metrics"""
    
    print("   🎯 Analyzing performance psychology...")
    
    psychology_data = []
    
    for manager in active_managers:
        manager_games = matchups_df[
            (matchups_df['manager1'] == manager) | (matchups_df['manager2'] == manager)
        ].copy()
        
        # Get manager's scores and results
        scores = []
        results = []
        playoff_scores = []
        regular_scores = []
        
        for _, row in manager_games.iterrows():
            if row['manager1'] == manager:
                score = row['team1_score']
                won = row['winning_manager'] == manager
            else:
                score = row['team2_score'] 
                won = row['winning_manager'] == manager
            
            scores.append(score)
            results.append(won)
            
            if row['playoff']:
                playoff_scores.append(score)
            else:
                regular_scores.append(score)
        
        # Calculate metrics
        total_games = len(scores)
        wins = sum(results)
        win_pct = (wins / total_games * 100) if total_games > 0 else 0
        
        # Clutch Factor (playoff vs regular season performance)
        regular_avg = np.mean(regular_scores) if regular_scores else 0
        playoff_avg = np.mean(playoff_scores) if playoff_scores else regular_avg
        clutch_factor = ((playoff_avg - regular_avg) / regular_avg * 100) if regular_avg > 0 else 0
        
        # Consistency (inverse of coefficient of variation)
        consistency = (1 / (np.std(scores) / np.mean(scores))) * 10 if np.mean(scores) > 0 and np.std(scores) > 0 else 5
        
        # Momentum (longest winning/losing streaks)
        streaks = calculate_streaks(results)
        max_win_streak = max([s for s in streaks if s > 0] + [0])
        max_lose_streak = abs(min([s for s in streaks if s < 0] + [0]))
        
        # High-pressure games (close games performance)
        close_games = manager_games[abs(manager_games['team1_score'] - manager_games['team2_score']) <= 10]
        close_game_wins = 0
        close_game_total = 0
        
        for _, row in close_games.iterrows():
            close_game_total += 1
            if row['winning_manager'] == manager:
                close_game_wins += 1
        
        close_game_pct = (close_game_wins / close_game_total * 100) if close_game_total > 0 else 50
        
        psychology_data.append({
            'manager': manager,
            'total_games': total_games,
            'wins': wins,
            'win_pct': win_pct,
            'avg_score': np.mean(scores),
            'score_std': np.std(scores),
            'consistency': min(consistency, 10),  # Cap at 10
            'clutch_factor': clutch_factor,
            'playoff_games': len(playoff_scores),
            'playoff_avg': playoff_avg,
            'regular_avg': regular_avg,
            'max_win_streak': max_win_streak,
            'max_lose_streak': max_lose_streak,
            'close_game_wins': close_game_wins,
            'close_game_total': close_game_total,
            'close_game_pct': close_game_pct
        })
    
    return pd.DataFrame(psychology_data)

def calculate_streaks(results):
    """Calculate winning/losing streaks from boolean results"""
    if not results:
        return [0]
    
    streaks = []
    current_streak = 1 if results[0] else -1
    
    for i in range(1, len(results)):
        if results[i] == results[i-1]:
            # Same result, continue streak
            if results[i]:  # Win
                current_streak += 1 if current_streak > 0 else 1
            else:  # Loss
                current_streak -= 1 if current_streak < 0 else 1
        else:
            # Different result, end streak
            streaks.append(current_streak)
            current_streak = 1 if results[i] else -1
    
    streaks.append(current_streak)
    return streaks

def analyze_manager_dna(matchups_df, active_managers):
    """Analyze manager DNA - their playing style archetypes"""
    
    print("   🧬 Analyzing manager DNA...")
    
    dna_data = []
    
    for manager in active_managers:
        manager_games = matchups_df[
            (matchups_df['manager1'] == manager) | (matchups_df['manager2'] == manager)
        ].copy()
        
        # Get manager's scores
        scores = []
        opponent_scores = []
        margins = []
        
        for _, row in manager_games.iterrows():
            if row['manager1'] == manager:
                score = row['team1_score']
                opp_score = row['team2_score']
            else:
                score = row['team2_score']
                opp_score = row['team1_score']
                
            scores.append(score)
            opponent_scores.append(opp_score)
            margins.append(abs(score - opp_score))
        
        # Calculate DNA metrics (0-10 scale)
        avg_score = np.mean(scores)
        score_std = np.std(scores)
        
        # High Scorer (normalized to league average)
        league_avg = matchups_df[['team1_score', 'team2_score']].values.flatten().mean()
        high_scorer = min((avg_score / league_avg - 1) * 10 + 5, 10) if league_avg > 0 else 5
        
        # Consistent (inverse of coefficient of variation)
        consistent = min((1 / (score_std / avg_score)) * 2, 10) if avg_score > 0 and score_std > 0 else 5
        
        # Lucky (wins above expected based on points)
        expected_wins = sum(1 for i, score in enumerate(scores) if score > opponent_scores[i])
        actual_wins = sum(1 for _, row in manager_games.iterrows() if row['winning_manager'] == manager)
        luck_factor = ((actual_wins - expected_wins) / len(scores) * 20 + 5) if len(scores) > 0 else 5
        luck_factor = max(0, min(luck_factor, 10))
        
        # Clutch (playoff performance boost)
        playoff_games = manager_games[manager_games['playoff'] == True]
        regular_games = manager_games[manager_games['playoff'] == False]
        
        if len(playoff_games) > 0 and len(regular_games) > 0:
            playoff_scores = []
            regular_scores = []
            
            for _, row in playoff_games.iterrows():
                if row['manager1'] == manager:
                    playoff_scores.append(row['team1_score'])
                else:
                    playoff_scores.append(row['team2_score'])
            
            for _, row in regular_games.iterrows():
                if row['manager1'] == manager:
                    regular_scores.append(row['team1_score'])
                else:
                    regular_scores.append(row['team2_score'])
            
            clutch = min(((np.mean(playoff_scores) / np.mean(regular_scores) - 1) * 20 + 5), 10) if np.mean(regular_scores) > 0 else 5
        else:
            clutch = 5
        
        clutch = max(0, clutch)
        
        # Volatile (boom/bust tendency)
        volatile = min((score_std / avg_score) * 15, 10) if avg_score > 0 else 5
        
        # Defensive (low points allowed)
        avg_opp_score = np.mean(opponent_scores)
        league_opp_avg = avg_opp_score  # Simplification
        defensive = max(0, min((1 - avg_opp_score / league_opp_avg) * 10 + 5, 10)) if league_opp_avg > 0 else 5
        
        dna_data.append({
            'manager': manager,
            'high_scorer': high_scorer,
            'consistent': consistent,
            'lucky': luck_factor,
            'clutch': clutch,
            'volatile': volatile,
            'defensive': defensive,
            'avg_score': avg_score,
            'games_played': len(scores)
        })
    
    return pd.DataFrame(dna_data)

def analyze_league_evolution(matchups_df):
    """Analyze how the league has evolved over 8 years"""
    
    print("   📈 Analyzing league evolution...")
    
    evolution_data = []
    
    seasons = sorted(matchups_df['season'].unique())
    
    for season in seasons:
        season_data = matchups_df[matchups_df['season'] == season]
        
        # League-wide metrics
        all_scores = pd.concat([season_data['team1_score'], season_data['team2_score']])
        avg_score = all_scores.mean()
        score_std = all_scores.std()
        
        # Parity (how close teams are in performance)
        # Calculate each team's season average
        team_avgs = []
        for manager in season_data['manager1'].unique():
            manager_games = season_data[
                (season_data['manager1'] == manager) | (season_data['manager2'] == manager)
            ]
            
            scores = []
            for _, row in manager_games.iterrows():
                if row['manager1'] == manager:
                    scores.append(row['team1_score'])
                else:
                    scores.append(row['team2_score'])
            
            if scores:
                team_avgs.append(np.mean(scores))
        
        parity = 1 / (np.std(team_avgs) / np.mean(team_avgs)) if team_avgs and np.mean(team_avgs) > 0 else 1
        
        # Competitiveness (percentage of close games)
        close_games = season_data[abs(season_data['team1_score'] - season_data['team2_score']) <= 15]
        competitiveness = len(close_games) / len(season_data) * 100 if len(season_data) > 0 else 0
        
        evolution_data.append({
            'season': season,
            'avg_score': avg_score,
            'score_volatility': score_std,
            'parity': min(parity, 5),  # Cap at 5 for visualization
            'competitiveness': competitiveness,
            'total_games': len(season_data),
            'high_scoring_games': len(season_data[
                (season_data['team1_score'] + season_data['team2_score']) >= 240
            ])
        })
    
    return pd.DataFrame(evolution_data)

def create_clutch_factor_viz(psychology_df, viz_dir):
    """Create clutch factor visualization"""
    
    print("   📊 Creating clutch factor visualization...")
    
    # Sort by clutch factor
    clutch_sorted = psychology_df.sort_values('clutch_factor', ascending=True)
    
    fig = go.Figure()
    
    # Color based on clutch factor
    colors = ['red' if x < 0 else 'green' if x > 5 else 'orange' for x in clutch_sorted['clutch_factor']]
    
    fig.add_trace(go.Bar(
        y=clutch_sorted['manager'],
        x=clutch_sorted['clutch_factor'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{val:.1f}%" for val in clutch_sorted['clutch_factor']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Clutch Factor: %{x:.1f}%<br>Playoff Avg: %{customdata[0]:.1f}<br>Regular Avg: %{customdata[1]:.1f}<extra></extra>',
        customdata=list(zip(clutch_sorted['playoff_avg'], clutch_sorted['regular_avg']))
    ))
    
    fig.update_layout(
        title={
            'text': "🎯 Clutch Factor Analysis<br><sub>Playoff Performance vs Regular Season (%)</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Performance Boost in Playoffs (%)",
        yaxis_title="Manager",
        width=900,
        height=600,
        showlegend=False
    )
    
    # Add reference line at 0
    fig.add_vline(x=0, line_dash="dash", line_color="gray", 
                  annotation_text="No Difference", annotation_position="top")
    
    fig.write_html(viz_dir / "clutch_factor.html")
    print("   ✅ Clutch Factor visualization saved")

def create_momentum_tracker(psychology_df, viz_dir):
    """Create momentum/streaks visualization"""
    
    print("   📊 Creating momentum tracker...")
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Longest Win Streaks', 'Longest Losing Streaks'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Win streaks
    win_sorted = psychology_df.sort_values('max_win_streak', ascending=True)
    fig.add_trace(
        go.Bar(
            y=win_sorted['manager'],
            x=win_sorted['max_win_streak'],
            orientation='h',
            marker_color='green',
            name='Win Streaks',
            text=win_sorted['max_win_streak'],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Losing streaks
    lose_sorted = psychology_df.sort_values('max_lose_streak', ascending=True)
    fig.add_trace(
        go.Bar(
            y=lose_sorted['manager'],
            x=lose_sorted['max_lose_streak'],
            orientation='h',
            marker_color='red',
            name='Lose Streaks',
            text=lose_sorted['max_lose_streak'],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title={
            'text': "🔥 Momentum Analysis - Longest Streaks (2017-2024)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        width=1200,
        height=600,
        showlegend=False
    )
    
    fig.write_html(viz_dir / "momentum_tracker.html")
    print("   ✅ Momentum Tracker visualization saved")

def create_consistency_analysis(psychology_df, viz_dir):
    """Create consistency vs volatility analysis"""
    
    print("   📊 Creating consistency analysis...")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=psychology_df['consistency'],
        y=psychology_df['avg_score'],
        mode='markers+text',
        text=psychology_df['manager'],
        textposition="top center",
        marker=dict(
            size=psychology_df['win_pct'] / 2,  # Size by win percentage
            color=psychology_df['win_pct'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Win %"),
            line=dict(width=1, color='black')
        ),
        hovertemplate='<b>%{text}</b><br>Consistency: %{x:.1f}<br>Avg Score: %{y:.1f}<br>Win %: %{customdata:.1f}%<extra></extra>',
        customdata=psychology_df['win_pct']
    ))
    
    fig.update_layout(
        title={
            'text': "🎯 Consistency vs Performance<br><sub>Bubble size = Win %, Color = Win %</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Consistency Score (10 = Most Consistent)",
        yaxis_title="Average Score",
        width=800,
        height=700
    )
    
    fig.write_html(viz_dir / "consistency_analysis.html")
    print("   ✅ Consistency Analysis visualization saved")

def create_manager_dna_radar(dna_df, viz_dir):
    """Create Manager DNA radar charts"""
    
    print("   📊 Creating Manager DNA radar charts...")
    
    # Create subplots for multiple radar charts
    fig = make_subplots(
        rows=3, cols=4,
        specs=[[{"type": "polar"}] * 4] * 3,
        subplot_titles=[manager for manager in dna_df['manager'][:12]]  # Top 12
    )
    
    categories = ['High Scorer', 'Consistent', 'Lucky', 'Clutch', 'Volatile', 'Defensive']
    
    positions = [(i+1, j+1) for i in range(3) for j in range(4)]
    
    for idx, (_, manager_data) in enumerate(dna_df.iterrows()):
        if idx >= 12:  # Limit to 12 managers
            break
            
        values = [
            manager_data['high_scorer'],
            manager_data['consistent'],
            manager_data['lucky'],
            manager_data['clutch'],
            manager_data['volatile'],
            manager_data['defensive']
        ]
        
        row, col = positions[idx]
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name=manager_data['manager'],
            line_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)]
        ), row=row, col=col)
    
    fig.update_layout(
        title={
            'text': "🧬 Manager DNA - Performance Archetypes",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=1000,
        showlegend=False
    )
    
    # Update polar charts - use update_layout instead
    for i in range(1, 13):  # 12 subplots
        polar_key = f"polar{i}" if i > 1 else "polar"
        fig.update_layout(**{
            polar_key: dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            )
        })
    
    fig.write_html(viz_dir / "manager_dna_radar.html")
    print("   ✅ Manager DNA Radar charts saved")

def create_league_evolution_viz(evolution_df, viz_dir):
    """Create league evolution visualization"""
    
    print("   📊 Creating league evolution visualization...")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Average Scoring Trends', 'League Parity Over Time', 
                       'Competitiveness (Close Games %)', 'High-Scoring Games per Season'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Average scoring
    fig.add_trace(
        go.Scatter(
            x=evolution_df['season'],
            y=evolution_df['avg_score'],
            mode='lines+markers',
            name='Avg Score',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Parity
    fig.add_trace(
        go.Scatter(
            x=evolution_df['season'],
            y=evolution_df['parity'],
            mode='lines+markers',
            name='Parity',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ),
        row=1, col=2
    )
    
    # Competitiveness
    fig.add_trace(
        go.Scatter(
            x=evolution_df['season'],
            y=evolution_df['competitiveness'],
            mode='lines+markers',
            name='Competitiveness',
            line=dict(color='orange', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    
    # High-scoring games
    fig.add_trace(
        go.Bar(
            x=evolution_df['season'],
            y=evolution_df['high_scoring_games'],
            name='High-Scoring Games',
            marker_color='red'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title={
            'text': "📈 League Evolution (2017-2024)<br><sub>How the League of Hard Knox has changed over 8 years</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=800,
        showlegend=False
    )
    
    fig.write_html(viz_dir / "league_evolution.html")
    print("   ✅ League Evolution visualization saved")

def create_psychology_dashboard(psychology_df, dna_df, evolution_df, viz_dir):
    """Create comprehensive psychology dashboard"""
    
    print("   📊 Creating comprehensive psychology dashboard...")
    
    # Create a comprehensive HTML dashboard
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Psychology Insights - League of Hard Knox</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .insight-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }}
        
        .insight-card:hover {{
            transform: translateY(-5px);
        }}
        
        .insight-header {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .insight-content {{
            padding: 20px;
        }}
        
        .viz-link {{
            display: block;
            width: calc(100% - 40px);
            margin: 0 20px 20px;
            padding: 12px;
            background: #667eea;
            color: white;
            text-decoration: none;
            text-align: center;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.3s ease;
        }}
        
        .viz-link:hover {{
            background: #5a67d8;
        }}
        
        .stats-summary {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .highlight-card {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            grid-column: 1 / -1;
        }}
        
        .highlight-card .insight-header {{
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Psychology Insights</h1>
            <p>League of Hard Knox • Advanced Performance Psychology • 2017-2024</p>
        </div>
        
        <div class="stats-summary">
            <h3>🎯 Key Psychology Findings</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{psychology_df['clutch_factor'].max():.1f}%</div>
                    <div class="stat-label">Most Clutch (Playoff Boost)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{psychology_df['max_win_streak'].max()}</div>
                    <div class="stat-label">Longest Win Streak</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{psychology_df['consistency'].max():.1f}</div>
                    <div class="stat-label">Most Consistent</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{dna_df['high_scorer'].max():.1f}/10</div>
                    <div class="stat-label">Highest Scorer DNA</div>
                </div>
            </div>
        </div>
        
        <div class="insights-grid">
            <div class="insight-card highlight-card">
                <div class="insight-header">
                    <h3>🎯 Clutch Factor Analysis</h3>
                </div>
                <div class="insight-content">
                    <p>Who performs better in high-pressure playoff games? This analysis compares each manager's playoff performance to their regular season average.</p>
                    <p><strong>Key Finding:</strong> {psychology_df.loc[psychology_df['clutch_factor'].idxmax(), 'manager']} shows the biggest playoff performance boost at {psychology_df['clutch_factor'].max():.1f}%.</p>
                </div>
                <a href="clutch_factor.html" class="viz-link">View Clutch Analysis</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>🔥 Momentum Tracker</h3>
                </div>
                <div class="insight-content">
                    <p>Analyze winning and losing streaks to understand momentum patterns and psychological resilience.</p>
                    <p><strong>Longest Win Streak:</strong> {psychology_df.loc[psychology_df['max_win_streak'].idxmax(), 'manager']} ({psychology_df['max_win_streak'].max()} games)</p>
                </div>
                <a href="momentum_tracker.html" class="viz-link">View Momentum Analysis</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>📊 Consistency Analysis</h3>
                </div>
                <div class="insight-content">
                    <p>Compare consistency vs performance to identify steady performers vs boom/bust players.</p>
                    <p><strong>Most Consistent:</strong> {psychology_df.loc[psychology_df['consistency'].idxmax(), 'manager']} (Score: {psychology_df['consistency'].max():.1f}/10)</p>
                </div>
                <a href="consistency_analysis.html" class="viz-link">View Consistency Analysis</a>
            </div>
            
            <div class="insight-card highlight-card">
                <div class="insight-header">
                    <h3>🧬 Manager DNA</h3>
                </div>
                <div class="insight-content">
                    <p>Comprehensive personality profiles showing each manager's playing style across 6 key dimensions: High Scorer, Consistent, Lucky, Clutch, Volatile, and Defensive.</p>
                    <p><strong>Most Unique Profile:</strong> Each manager has a distinct DNA fingerprint showing their fantasy football personality.</p>
                </div>
                <a href="manager_dna_radar.html" class="viz-link">View DNA Analysis</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>📈 League Evolution</h3>
                </div>
                <div class="insight-content">
                    <p>Track how the League of Hard Knox has evolved over 8 years - scoring trends, parity, competitiveness.</p>
                    <p><strong>Key Trend:</strong> League competitiveness and parity have {evolution_df['parity'].corr(evolution_df['season']) > 0 and "increased" or "decreased"} over time.</p>
                </div>
                <a href="league_evolution.html" class="viz-link">View Evolution Analysis</a>
            </div>
        </div>
        
        <div style="text-align: center; color: white; margin-top: 40px;">
            <p>🧠 Psychology Insights • 📊 Advanced Analytics • 🏆 League of Hard Knox</p>
        </div>
    </div>
</body>
</html>'''
    
    # Save the HTML file
    with open(viz_dir / "psychology_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("   ✅ Psychology Dashboard saved")

if __name__ == "__main__":
    create_psychology_insights()