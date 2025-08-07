#!/usr/bin/env python3
"""
Create temporal patterns and league dynamics insights for League of Hard Knox.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from scipy import stats

def create_temporal_dynamics_insights():
    """Create comprehensive temporal patterns and league dynamics analysis"""
    
    print("⏰ CREATING TEMPORAL & DYNAMICS INSIGHTS - LEAGUE OF HARD KNOX")
    print("=" * 70)
    
    # Load the datasets
    data_dir = Path("data/final_dataset")
    matchups_df = pd.read_csv(data_dir / "league_hard_knox_2017_2024_complete.csv")
    
    print(f"📊 Loaded {len(matchups_df)} matchups for temporal analysis")
    
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
    
    print(f"🎯 Creating temporal patterns and league dynamics...")
    
    # 1. Temporal Patterns Analysis
    temporal_data = analyze_temporal_patterns(current_matchups, active_managers)
    
    # 2. League Dynamics Analysis  
    dynamics_data = analyze_league_dynamics(current_matchups, active_managers)
    
    # 3. Create visualizations
    create_week_by_week_heatmap(temporal_data['weekly_performance'], viz_dir)
    create_bad_beats_gallery(temporal_data['bad_beats'], viz_dir)
    create_statement_games_viz(temporal_data['statement_games'], viz_dir)
    create_kryptonite_analysis(dynamics_data['kryptonite'], viz_dir)
    create_parity_index_viz(dynamics_data['parity_evolution'], viz_dir)
    create_luck_vs_skill_analysis(dynamics_data['expected_wins'], viz_dir)
    create_temporal_dashboard(temporal_data, dynamics_data, viz_dir)
    create_dynamics_dashboard(dynamics_data, viz_dir)
    
    print(f"\\n🎉 TEMPORAL & DYNAMICS INSIGHTS COMPLETE!")
    print(f"📂 Files saved to: {viz_dir}/")
    print(f"⏰ Open temporal_dashboard.html for time-based insights")
    print(f"🎮 Open dynamics_dashboard.html for league dynamics")
    
    return True

def analyze_temporal_patterns(matchups_df, active_managers):
    """Analyze temporal patterns in performance"""
    
    print("   ⏰ Analyzing temporal patterns...")
    
    # 1. Week-by-week performance heatmap
    weekly_performance = analyze_weekly_performance(matchups_df, active_managers)
    
    # 2. Bad beats analysis (high scores that lost)
    bad_beats = analyze_bad_beats(matchups_df, active_managers)
    
    # 3. Statement games (big upsets)
    statement_games = analyze_statement_games(matchups_df, active_managers)
    
    return {
        'weekly_performance': weekly_performance,
        'bad_beats': bad_beats,
        'statement_games': statement_games
    }

def analyze_weekly_performance(matchups_df, active_managers):
    """Analyze performance by week across all seasons"""
    
    weekly_data = []
    
    for week in range(1, 18):  # NFL weeks 1-17
        week_games = matchups_df[matchups_df['week'] == week]
        
        for manager in active_managers:
            manager_week_games = week_games[
                (week_games['manager1'] == manager) | 
                (week_games['manager2'] == manager)
            ]
            
            if len(manager_week_games) == 0:
                continue
            
            scores = []
            wins = 0
            
            for _, row in manager_week_games.iterrows():
                if row['manager1'] == manager:
                    score = row['team1_score']
                    if row['winning_manager'] == manager:
                        wins += 1
                else:
                    score = row['team2_score']
                    if row['winning_manager'] == manager:
                        wins += 1
                
                scores.append(score)
            
            avg_score = np.mean(scores) if scores else 0
            win_pct = (wins / len(scores) * 100) if scores else 0
            
            weekly_data.append({
                'manager': manager,
                'week': week,
                'avg_score': avg_score,
                'win_pct': win_pct,
                'games': len(scores),
                'wins': wins
            })
    
    return pd.DataFrame(weekly_data)

def analyze_bad_beats(matchups_df, active_managers):
    """Find games lost despite high scores"""
    
    bad_beats = []
    
    # Calculate league average by season
    season_averages = {}
    for season in matchups_df['season'].unique():
        season_data = matchups_df[matchups_df['season'] == season]
        all_scores = pd.concat([season_data['team1_score'], season_data['team2_score']])
        season_averages[season] = all_scores.mean()
    
    for _, row in matchups_df.iterrows():
        season_avg = season_averages.get(row['season'], 120)
        
        # Check team1
        if (row['manager1'] in active_managers and 
            row['team1_score'] >= season_avg + 20 and  # Well above average
            row['winning_manager'] != row['manager1']):
            
            bad_beats.append({
                'season': row['season'],
                'week': row['week'],
                'manager': row['manager1'],
                'team': row['team1'],
                'score': row['team1_score'],
                'opponent': row['manager2'],
                'opponent_score': row['team2_score'],
                'margin': row['team2_score'] - row['team1_score'],
                'season_avg': season_avg,
                'above_avg': row['team1_score'] - season_avg,
                'playoff': row['playoff']
            })
        
        # Check team2
        if (row['manager2'] in active_managers and 
            row['team2_score'] >= season_avg + 20 and
            row['winning_manager'] != row['manager2']):
            
            bad_beats.append({
                'season': row['season'],
                'week': row['week'],
                'manager': row['manager2'],
                'team': row['team2'],
                'score': row['team2_score'],
                'opponent': row['manager1'],
                'opponent_score': row['team1_score'],
                'margin': row['team1_score'] - row['team2_score'],
                'season_avg': season_avg,
                'above_avg': row['team2_score'] - season_avg,
                'playoff': row['playoff']
            })
    
    return pd.DataFrame(bad_beats).sort_values(['above_avg', 'margin'], ascending=[False, False])

def analyze_statement_games(matchups_df, active_managers):
    """Find biggest upsets (weak teams beating strong ones)"""
    
    # First, calculate season win percentages for context
    season_records = {}
    
    for season in matchups_df['season'].unique():
        season_data = matchups_df[matchups_df['season'] == season]
        season_records[season] = {}
        
        for manager in active_managers:
            manager_games = season_data[
                (season_data['manager1'] == manager) | 
                (season_data['manager2'] == manager)
            ]
            
            wins = len(manager_games[manager_games['winning_manager'] == manager])
            total = len(manager_games)
            win_pct = (wins / total) if total > 0 else 0
            
            season_records[season][manager] = {
                'wins': wins,
                'total': total,
                'win_pct': win_pct
            }
    
    statement_games = []
    
    for _, row in matchups_df.iterrows():
        if row['manager1'] not in active_managers or row['manager2'] not in active_managers:
            continue
            
        season = row['season']
        manager1_record = season_records[season].get(row['manager1'], {'win_pct': 0.5})
        manager2_record = season_records[season].get(row['manager2'], {'win_pct': 0.5})
        
        # Calculate upset factor (difference in win percentages)
        win_pct_diff = abs(manager1_record['win_pct'] - manager2_record['win_pct'])
        
        # Only consider games with significant win percentage differences
        if win_pct_diff >= 0.3:  # 30% difference in win rates
            winner = row['winning_manager']
            if winner in [row['manager1'], row['manager2']]:
                # Determine if this was an upset
                if ((winner == row['manager1'] and manager1_record['win_pct'] < manager2_record['win_pct']) or
                    (winner == row['manager2'] and manager2_record['win_pct'] < manager1_record['win_pct'])):
                    
                    loser = row['manager2'] if winner == row['manager1'] else row['manager1']
                    winner_score = row['team1_score'] if winner == row['manager1'] else row['team2_score']
                    loser_score = row['team2_score'] if winner == row['manager1'] else row['team1_score']
                    
                    statement_games.append({
                        'season': row['season'],
                        'week': row['week'],
                        'winner': winner,
                        'winner_score': winner_score,
                        'loser': loser,
                        'loser_score': loser_score,
                        'margin': winner_score - loser_score,
                        'upset_factor': win_pct_diff,
                        'winner_win_pct': season_records[season][winner]['win_pct'],
                        'loser_win_pct': season_records[season][loser]['win_pct'],
                        'playoff': row['playoff']
                    })
    
    return pd.DataFrame(statement_games).sort_values('upset_factor', ascending=False)

def analyze_league_dynamics(matchups_df, active_managers):
    """Analyze league-wide dynamics and patterns"""
    
    print("   🎮 Analyzing league dynamics...")
    
    # 1. Kryptonite analysis (unexpected dominance patterns)
    kryptonite = analyze_kryptonite_matchups(matchups_df, active_managers)
    
    # 2. Parity evolution over time
    parity_evolution = analyze_parity_evolution(matchups_df, active_managers)
    
    # 3. Expected vs actual wins (luck vs skill)
    expected_wins = analyze_expected_vs_actual_wins(matchups_df, active_managers)
    
    return {
        'kryptonite': kryptonite,
        'parity_evolution': parity_evolution,
        'expected_wins': expected_wins
    }

def analyze_kryptonite_matchups(matchups_df, active_managers):
    """Find matchups where one manager unexpectedly dominates another"""
    
    h2h_records = {}
    
    # Build head-to-head records
    for _, row in matchups_df.iterrows():
        if row['manager1'] not in active_managers or row['manager2'] not in active_managers:
            continue
            
        key1 = (row['manager1'], row['manager2'])
        key2 = (row['manager2'], row['manager1'])
        
        if key1 not in h2h_records:
            h2h_records[key1] = {'wins': 0, 'losses': 0, 'games': 0}
        if key2 not in h2h_records:
            h2h_records[key2] = {'wins': 0, 'losses': 0, 'games': 0}
        
        h2h_records[key1]['games'] += 1
        h2h_records[key2]['games'] += 1
        
        if row['winning_manager'] == row['manager1']:
            h2h_records[key1]['wins'] += 1
            h2h_records[key2]['losses'] += 1
        elif row['winning_manager'] == row['manager2']:
            h2h_records[key1]['losses'] += 1
            h2h_records[key2]['wins'] += 1
    
    # Find kryptonite relationships
    kryptonite_matchups = []
    
    for (manager1, manager2), record in h2h_records.items():
        if record['games'] >= 5:  # Minimum games for significance
            win_pct = record['wins'] / record['games']
            
            # Look for extreme dominance (80%+ win rate)
            if win_pct >= 0.8:
                kryptonite_matchups.append({
                    'dominator': manager1,
                    'victim': manager2,
                    'wins': record['wins'],
                    'losses': record['losses'],
                    'games': record['games'],
                    'dominance': win_pct * 100,
                    'dominance_level': 'Kryptonite' if win_pct >= 0.9 else 'Heavy Favorite'
                })
    
    return pd.DataFrame(kryptonite_matchups).sort_values('dominance', ascending=False)

def analyze_parity_evolution(matchups_df, active_managers):
    """Analyze how competitive balance has changed over time"""
    
    parity_data = []
    
    for season in sorted(matchups_df['season'].unique()):
        season_data = matchups_df[matchups_df['season'] == season]
        
        # Calculate win percentages for each manager
        season_win_pcts = []
        
        for manager in active_managers:
            manager_games = season_data[
                (season_data['manager1'] == manager) | 
                (season_data['manager2'] == manager)
            ]
            
            if len(manager_games) == 0:
                continue
                
            wins = len(manager_games[manager_games['winning_manager'] == manager])
            win_pct = wins / len(manager_games)
            season_win_pcts.append(win_pct)
        
        if season_win_pcts:
            # Calculate parity metrics
            win_pct_std = np.std(season_win_pcts)
            win_pct_range = max(season_win_pcts) - min(season_win_pcts)
            parity_index = 1 - (win_pct_std / 0.5)  # Normalized to 0-1 scale
            
            # Calculate Gini coefficient for inequality
            gini = calculate_gini(season_win_pcts)
            
            parity_data.append({
                'season': season,
                'parity_index': max(0, parity_index),
                'win_pct_std': win_pct_std,
                'win_pct_range': win_pct_range,
                'gini_coefficient': gini,
                'num_managers': len(season_win_pcts)
            })
    
    return pd.DataFrame(parity_data)

def calculate_gini(values):
    """Calculate Gini coefficient for inequality measurement"""
    values = np.array(values)
    values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * values)) / (n * np.sum(values)) - (n + 1) / n

def analyze_expected_vs_actual_wins(matchups_df, active_managers):
    """Analyze luck vs skill using points scored/allowed"""
    
    expected_wins_data = []
    
    for season in sorted(matchups_df['season'].unique()):
        season_data = matchups_df[matchups_df['season'] == season]
        
        for manager in active_managers:
            manager_games = season_data[
                (season_data['manager1'] == manager) | 
                (season_data['manager2'] == manager)
            ]
            
            if len(manager_games) == 0:
                continue
            
            scores_for = []
            scores_against = []
            actual_wins = 0
            
            for _, row in manager_games.iterrows():
                if row['manager1'] == manager:
                    scores_for.append(row['team1_score'])
                    scores_against.append(row['team2_score'])
                    if row['winning_manager'] == manager:
                        actual_wins += 1
                else:
                    scores_for.append(row['team2_score'])
                    scores_against.append(row['team1_score'])
                    if row['winning_manager'] == manager:
                        actual_wins += 1
            
            # Calculate expected wins based on points
            expected_wins = sum(1 for pf, pa in zip(scores_for, scores_against) if pf > pa)
            
            total_games = len(scores_for)
            actual_win_pct = actual_wins / total_games
            expected_win_pct = expected_wins / total_games
            luck_factor = actual_win_pct - expected_win_pct
            
            expected_wins_data.append({
                'season': season,
                'manager': manager,
                'actual_wins': actual_wins,
                'expected_wins': expected_wins,
                'total_games': total_games,
                'actual_win_pct': actual_win_pct * 100,
                'expected_win_pct': expected_win_pct * 100,
                'luck_factor': luck_factor * 100,
                'avg_points_for': np.mean(scores_for),
                'avg_points_against': np.mean(scores_against),
                'point_differential': np.mean(scores_for) - np.mean(scores_against)
            })
    
    return pd.DataFrame(expected_wins_data)

def create_week_by_week_heatmap(weekly_df, viz_dir):
    """Create week-by-week performance heatmap"""
    
    print("   📊 Creating week-by-week heatmap...")
    
    # Create pivot table for heatmap
    heatmap_data = weekly_df.pivot(index='manager', columns='week', values='avg_score')
    heatmap_data = heatmap_data.fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=[f"Week {w}" for w in heatmap_data.columns],
        y=heatmap_data.index,
        colorscale='RdYlGn',
        zmid=120,  # Average score as midpoint
        text=[[f"{val:.1f}" if val > 0 else "" for val in row] for row in heatmap_data.values],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Avg Score: %{z:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "📅 Week-by-Week Performance Heatmap<br><sub>Average scores across all seasons (2017-2024)</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        width=1200,
        height=600,
        xaxis_title="NFL Week",
        yaxis_title="Manager"
    )
    
    fig.write_html(viz_dir / "week_by_week_heatmap.html")
    print("   ✅ Week-by-week heatmap saved")

def create_bad_beats_gallery(bad_beats_df, viz_dir):
    """Create bad beats gallery visualization"""
    
    print("   📊 Creating bad beats gallery...")
    
    if len(bad_beats_df) == 0:
        print("   ⚠️  No bad beats found - skipping")
        return
    
    top_bad_beats = bad_beats_df.head(20)
    
    fig = go.Figure()
    
    # Color by how far above average
    colors = px.colors.sequential.Reds_r
    
    fig.add_trace(go.Bar(
        x=top_bad_beats.index,
        y=top_bad_beats['above_avg'],
        marker=dict(
            color=top_bad_beats['margin'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Loss Margin")
        ),
        text=[f"{row['manager']}<br>{row['season']} W{row['week']}<br>{row['score']:.1f} pts" 
              for _, row in top_bad_beats.iterrows()],
        textposition='outside',
        hovertemplate='<b>%{customdata[0]}</b><br>Season: %{customdata[1]}<br>Week: %{customdata[2]}<br>Score: %{customdata[3]:.1f}<br>vs %{customdata[4]} (%{customdata[5]:.1f})<br>Lost by: %{customdata[6]:.1f}<extra></extra>',
        customdata=list(zip(
            top_bad_beats['manager'],
            top_bad_beats['season'],
            top_bad_beats['week'],
            top_bad_beats['score'],
            top_bad_beats['opponent'],
            top_bad_beats['opponent_score'],
            -top_bad_beats['margin']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': "💔 Bad Beats Gallery<br><sub>Highest scores that still lost (Top 20)</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Ranked Bad Beats",
        yaxis_title="Points Above Season Average",
        width=1200,
        height=700,
        showlegend=False
    )
    
    fig.write_html(viz_dir / "bad_beats_gallery.html")
    print("   ✅ Bad Beats Gallery saved")

def create_statement_games_viz(statement_df, viz_dir):
    """Create statement games visualization"""
    
    print("   📊 Creating statement games visualization...")
    
    if len(statement_df) == 0:
        print("   ⚠️  No statement games found - skipping")
        return
    
    top_statements = statement_df.head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=top_statements['upset_factor'] * 100,
        y=top_statements['margin'],
        mode='markers+text',
        text=[f"{row['winner']}<br>vs {row['loser']}<br>{row['season']} W{row['week']}" 
              for _, row in top_statements.iterrows()],
        textposition="top center",
        marker=dict(
            size=20,
            color=top_statements['margin'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Victory Margin"),
            line=dict(width=2, color='white')
        ),
        hovertemplate='<b>%{customdata[0]} defeats %{customdata[1]}</b><br>Season: %{customdata[2]} Week %{customdata[3]}<br>Score: %{customdata[4]:.1f} - %{customdata[5]:.1f}<br>Upset Factor: %{x:.1f}%<br>Margin: %{y:.1f}<extra></extra>',
        customdata=list(zip(
            top_statements['winner'],
            top_statements['loser'],
            top_statements['season'],
            top_statements['week'],
            top_statements['winner_score'],
            top_statements['loser_score']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': "🎯 Statement Games<br><sub>Biggest upsets based on season records</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Upset Factor (Win % Difference)",
        yaxis_title="Victory Margin",
        width=1000,
        height=700
    )
    
    fig.write_html(viz_dir / "statement_games.html")
    print("   ✅ Statement Games visualization saved")

def create_kryptonite_analysis(kryptonite_df, viz_dir):
    """Create kryptonite matchups visualization"""
    
    print("   📊 Creating kryptonite analysis...")
    
    if len(kryptonite_df) == 0:
        print("   ⚠️  No kryptonite matchups found - skipping")
        return
    
    fig = go.Figure()
    
    colors = ['#FF0000' if x >= 90 else '#FF6B6B' for x in kryptonite_df['dominance']]
    
    fig.add_trace(go.Bar(
        y=[f"{row['dominator']} vs {row['victim']}" for _, row in kryptonite_df.iterrows()],
        x=kryptonite_df['dominance'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{row['wins']}-{row['losses']}" for _, row in kryptonite_df.iterrows()],
        textposition='inside',
        hovertemplate='<b>%{customdata[0]} dominates %{customdata[1]}</b><br>Record: %{customdata[2]}-%{customdata[3]} (%{x:.1f}%)<br>Games: %{customdata[4]}<extra></extra>',
        customdata=list(zip(
            kryptonite_df['dominator'],
            kryptonite_df['victim'],
            kryptonite_df['wins'],
            kryptonite_df['losses'],
            kryptonite_df['games']
        ))
    ))
    
    fig.update_layout(
        title={
            'text': "🧪 Kryptonite Analysis<br><sub>Unexplained dominance patterns (80%+ win rate, 5+ games)</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Dominance Percentage",
        yaxis_title="Matchup",
        width=900,
        height=max(400, len(kryptonite_df) * 50),
        showlegend=False
    )
    
    fig.write_html(viz_dir / "kryptonite_analysis.html")
    print("   ✅ Kryptonite Analysis saved")

def create_parity_index_viz(parity_df, viz_dir):
    """Create parity evolution visualization"""
    
    print("   📊 Creating parity index visualization...")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('League Parity Index Over Time', 'Win Percentage Spread'),
        shared_xaxes=True
    )
    
    # Parity index
    fig.add_trace(
        go.Scatter(
            x=parity_df['season'],
            y=parity_df['parity_index'],
            mode='lines+markers',
            name='Parity Index',
            line=dict(color='blue', width=3),
            marker=dict(size=10),
            hovertemplate='Season: %{x}<br>Parity Index: %{y:.3f}<br>(1.0 = Perfect Parity)<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Win percentage range
    fig.add_trace(
        go.Scatter(
            x=parity_df['season'],
            y=parity_df['win_pct_range'],
            mode='lines+markers',
            name='Win % Range',
            line=dict(color='red', width=3),
            marker=dict(size=10),
            hovertemplate='Season: %{x}<br>Win % Range: %{y:.3f}<br>(Lower = More Competitive)<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title={
            'text': "⚖️ League Parity Evolution (2017-2024)<br><sub>How competitive balance has changed over time</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=800,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Season", row=2, col=1)
    fig.update_yaxes(title_text="Parity Index", row=1, col=1)
    fig.update_yaxes(title_text="Win % Range", row=2, col=1)
    
    fig.write_html(viz_dir / "parity_evolution.html")
    print("   ✅ Parity Evolution visualization saved")

def create_luck_vs_skill_analysis(expected_df, viz_dir):
    """Create luck vs skill analysis"""
    
    print("   📊 Creating luck vs skill analysis...")
    
    fig = go.Figure()
    
    # Aggregate across all seasons for overall view
    manager_totals = expected_df.groupby('manager').agg({
        'luck_factor': 'mean',
        'point_differential': 'mean',
        'total_games': 'sum'
    }).reset_index()
    
    fig.add_trace(go.Scatter(
        x=manager_totals['point_differential'],
        y=manager_totals['luck_factor'],
        mode='markers+text',
        text=manager_totals['manager'],
        textposition="top center",
        marker=dict(
            size=manager_totals['total_games'] / 5,  # Scale by total games
            color=manager_totals['luck_factor'],
            colorscale='RdYlGn',
            cmid=0,
            showscale=True,
            colorbar=dict(title="Luck Factor (%)"),
            line=dict(width=2, color='black')
        ),
        hovertemplate='<b>%{text}</b><br>Avg Point Differential: %{x:.1f}<br>Luck Factor: %{y:.1f}%<br>Total Games: %{customdata}<extra></extra>',
        customdata=manager_totals['total_games']
    ))
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Average Luck")
    fig.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="Average Skill")
    
    fig.update_layout(
        title={
            'text': "🍀 Luck vs Skill Analysis<br><sub>Expected wins (based on points) vs actual wins</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Average Point Differential (Skill)",
        yaxis_title="Luck Factor (% above/below expected)",
        width=900,
        height=700,
        annotations=[
            dict(x=0.02, y=0.98, xref='paper', yref='paper', text='Lucky & Good', showarrow=False, font=dict(size=12)),
            dict(x=0.02, y=0.02, xref='paper', yref='paper', text='Unlucky but Good', showarrow=False, font=dict(size=12)),
            dict(x=0.98, y=0.98, xref='paper', yref='paper', text='Lucky but Bad', showarrow=False, font=dict(size=12), xanchor='right'),
            dict(x=0.98, y=0.02, xref='paper', yref='paper', text='Unlucky & Bad', showarrow=False, font=dict(size=12), xanchor='right')
        ]
    )
    
    fig.write_html(viz_dir / "luck_vs_skill.html")
    print("   ✅ Luck vs Skill Analysis saved")

def create_temporal_dashboard(temporal_data, dynamics_data, viz_dir):
    """Create temporal patterns dashboard"""
    
    print("   📊 Creating temporal patterns dashboard...")
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Temporal Patterns - League of Hard Knox</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
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
            background: linear-gradient(45deg, #2196F3, #1976D2);
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
            background: #2196F3;
            color: white;
            text-decoration: none;
            text-align: center;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.3s ease;
        }}
        
        .viz-link:hover {{
            background: #1976D2;
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
            color: #2196F3;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .highlight-card {{
            background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
            grid-column: 1 / -1;
        }}
        
        .highlight-card .insight-header {{
            background: linear-gradient(45deg, #FF9800, #F57C00);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Temporal Patterns</h1>
            <p>League of Hard Knox • Time-Based Performance Analysis • 2017-2024</p>
        </div>
        
        <div class="stats-summary">
            <h3>🕐 Time-Based Insights</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(temporal_data['bad_beats'])}</div>
                    <div class="stat-label">Bad Beats Recorded</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(temporal_data['statement_games'])}</div>
                    <div class="stat-label">Statement Games</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">17</div>
                    <div class="stat-label">Weeks Analyzed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">8</div>
                    <div class="stat-label">Seasons Tracked</div>
                </div>
            </div>
        </div>
        
        <div class="insights-grid">
            <div class="insight-card highlight-card">
                <div class="insight-header">
                    <h3>📅 Week-by-Week Performance</h3>
                </div>
                <div class="insight-content">
                    <p>Heatmap showing average performance across all 17 NFL weeks. Discover which managers start strong, finish strong, or have consistent performance patterns throughout the season.</p>
                    <p><strong>Pattern Analysis:</strong> Identify early-season performers vs late-season surges across 8 years of data.</p>
                </div>
                <a href="week_by_week_heatmap.html" class="viz-link">View Weekly Patterns</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>💔 Bad Beats Gallery</h3>
                </div>
                <div class="insight-content">
                    <p>The most heartbreaking losses - high-scoring performances that still resulted in defeats. See who has been the unluckiest with great scores.</p>
                    <p><strong>Worst Bad Beat:</strong> {temporal_data['bad_beats'].iloc[0]['manager'] if len(temporal_data['bad_beats']) > 0 else 'None'} scoring {temporal_data['bad_beats'].iloc[0]['score']:.1f} points but still losing</p>
                </div>
                <a href="bad_beats_gallery.html" class="viz-link">View Bad Beats</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>🎯 Statement Games</h3>
                </div>
                <div class="insight-content">
                    <p>Biggest upsets where underdog teams defeated heavily favored opponents. These are the games that define seasons and create legendary moments.</p>
                    <p><strong>Top Upset:</strong> {temporal_data['statement_games'].iloc[0]['winner'] if len(temporal_data['statement_games']) > 0 else 'None'} shocking {temporal_data['statement_games'].iloc[0]['loser'] if len(temporal_data['statement_games']) > 0 else 'No upsets'}</p>
                </div>
                <a href="statement_games.html" class="viz-link">View Statement Games</a>
            </div>
        </div>
        
        <div style="text-align: center; color: white; margin-top: 40px;">
            <p>⏰ Temporal Analysis • 📊 Pattern Recognition • 🏆 League of Hard Knox</p>
        </div>
    </div>
</body>
</html>'''
    
    # Save the HTML file
    with open(viz_dir / "temporal_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("   ✅ Temporal Dashboard saved")

def create_dynamics_dashboard(dynamics_data, viz_dir):
    """Create league dynamics dashboard"""
    
    print("   📊 Creating league dynamics dashboard...")
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>League Dynamics - League of Hard Knox</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%);
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
            background: linear-gradient(45deg, #9C27B0, #673AB7);
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
            background: #9C27B0;
            color: white;
            text-decoration: none;
            text-align: center;
            border-radius: 8px;
            font-weight: 500;
            transition: background 0.3s ease;
        }}
        
        .viz-link:hover {{
            background: #673AB7;
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
            color: #9C27B0;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .highlight-card {{
            background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
            grid-column: 1 / -1;
        }}
        
        .highlight-card .insight-header {{
            background: linear-gradient(45deg, #4CAF50, #388E3C);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 League Dynamics</h1>
            <p>League of Hard Knox • Competitive Balance & Patterns • 2017-2024</p>
        </div>
        
        <div class="stats-summary">
            <h3>⚖️ League Balance Metrics</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(dynamics_data['kryptonite'])}</div>
                    <div class="stat-label">Kryptonite Matchups</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{dynamics_data['parity_evolution']['parity_index'].mean():.3f}</div>
                    <div class="stat-label">Avg Parity Index</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(dynamics_data['expected_wins']['manager'].unique())}</div>
                    <div class="stat-label">Managers Analyzed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{dynamics_data['expected_wins']['luck_factor'].std():.1f}%</div>
                    <div class="stat-label">Luck Variance</div>
                </div>
            </div>
        </div>
        
        <div class="insights-grid">
            <div class="insight-card highlight-card">
                <div class="insight-header">
                    <h3>🧪 Kryptonite Analysis</h3>
                </div>
                <div class="insight-content">
                    <p>Discover mysterious dominance patterns where certain managers inexplicably dominate others despite overall records. These matchups defy logic and create guaranteed outcomes.</p>
                    <p><strong>Top Kryptonite:</strong> {dynamics_data['kryptonite'].iloc[0]['dominator'] if len(dynamics_data['kryptonite']) > 0 else 'None'} dominates {dynamics_data['kryptonite'].iloc[0]['victim'] if len(dynamics_data['kryptonite']) > 0 else 'N/A'}</p>
                </div>
                <a href="kryptonite_analysis.html" class="viz-link">View Kryptonite Matchups</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>⚖️ Parity Evolution</h3>
                </div>
                <div class="insight-content">
                    <p>Track how competitive balance has evolved over 8 years. Has the league become more or less competitive? Which seasons had the most parity?</p>
                    <p><strong>Trend:</strong> League parity has {('increased' if dynamics_data['parity_evolution']['parity_index'].corr(dynamics_data['parity_evolution']['season']) > 0 else 'decreased')} over time</p>
                </div>
                <a href="parity_evolution.html" class="viz-link">View Parity Trends</a>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <h3>🍀 Luck vs Skill</h3>
                </div>
                <div class="insight-content">
                    <p>Separate luck from skill using expected wins based on points scored. Who wins more than they should? Who has been unlucky despite good performance?</p>
                    <p><strong>Analysis:</strong> Compare point differential (skill) with actual vs expected wins (luck) across all managers.</p>
                </div>
                <a href="luck_vs_skill.html" class="viz-link">View Luck Analysis</a>
            </div>
        </div>
        
        <div style="text-align: center; color: white; margin-top: 40px;">
            <p>🎮 League Dynamics • ⚖️ Competitive Balance • 🏆 League of Hard Knox</p>
        </div>
    </div>
</body>
</html>'''
    
    # Save the HTML file
    with open(viz_dir / "dynamics_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("   ✅ League Dynamics Dashboard saved")

if __name__ == "__main__":
    create_temporal_dynamics_insights()