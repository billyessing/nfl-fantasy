#!/usr/bin/env python3
"""
Create interactive H2H visualizations for League of Hard Knox.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

def create_h2h_visualizations():
    """Create comprehensive H2H visualizations"""
    
    print("📊 CREATING H2H VISUALIZATIONS - LEAGUE OF HARD KNOX")
    print("=" * 60)
    
    # Load the datasets
    data_dir = Path("data/final_dataset")
    matchups_df = pd.read_csv(data_dir / "league_hard_knox_2017_2024_complete.csv")
    
    h2h_dir = Path("data/h2h_analysis") 
    detailed_h2h_df = pd.read_csv(h2h_dir / "detailed_h2h_records.csv")
    standings_df = pd.read_csv(h2h_dir / "overall_standings.csv")
    
    print(f"📈 Loaded {len(matchups_df)} matchups and H2H analysis data")
    
    # Filter to current active managers
    active_managers = ['Hayden', 'Michael', 'Phoenix', 'Billy', 'Robbie', 'Nelson', 
                      'Fraser', 'Justin', 'Angus', 'Nic', 'William', 'James']
    
    current_matchups = matchups_df[
        matchups_df['manager1'].isin(active_managers) &
        matchups_df['manager2'].isin(active_managers)
    ]
    
    # Create output directory
    viz_dir = Path("visualizations")
    viz_dir.mkdir(exist_ok=True)
    
    print(f"🎨 Creating visualizations...")
    
    # 1. H2H Matrix Heatmap
    create_h2h_matrix_heatmap(detailed_h2h_df, active_managers, viz_dir)
    
    # 2. Overall Standings Chart
    create_standings_chart(standings_df, viz_dir)
    
    # 3. Head-to-Head Win Percentages Network
    create_h2h_network(detailed_h2h_df, active_managers, viz_dir)
    
    # 4. Season-by-Season Performance
    create_season_performance(current_matchups, active_managers, viz_dir)
    
    # 5. Points Distribution
    create_points_analysis(current_matchups, active_managers, viz_dir)
    
    # 6. Rivalry Analysis
    create_rivalry_analysis(detailed_h2h_df, active_managers, viz_dir)
    
    # 7. Interactive Dashboard
    create_interactive_dashboard(detailed_h2h_df, standings_df, current_matchups, active_managers, viz_dir)
    
    print(f"\n🎉 VISUALIZATIONS COMPLETE!")
    print(f"📂 Files saved to: {viz_dir}/")
    print(f"🌐 Open h2h_dashboard.html in your browser for interactive experience")
    
    return True

def create_h2h_matrix_heatmap(detailed_h2h_df, active_managers, viz_dir):
    """Create H2H win percentage matrix heatmap"""
    
    print("   📊 Creating H2H Matrix Heatmap...")
    
    # Create matrix
    matrix = pd.DataFrame(index=active_managers, columns=active_managers)
    
    for _, row in detailed_h2h_df.iterrows():
        if row['manager'] in active_managers and row['opponent'] in active_managers:
            matrix.loc[row['manager'], row['opponent']] = row['win_pct']
    
    # Fill diagonal with None (can't play yourself)
    for manager in active_managers:
        matrix.loc[manager, manager] = None
    
    # Convert to numeric
    matrix = matrix.astype(float)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=active_managers,
        y=active_managers,
        colorscale='RdYlGn',
        zmid=50,
        zmin=0,
        zmax=100,
        text=[[f"{val:.1f}%" if not pd.isna(val) else "" for val in row] for row in matrix.values],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='<b>%{y} vs %{x}</b><br>Win %: %{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Head-to-Head Win Percentages (2017-2024)<br><sub>League of Hard Knox - Row vs Column</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Opponent",
        yaxis_title="Manager",
        width=800,
        height=700,
        font=dict(size=12)
    )
    
    fig.write_html(viz_dir / "h2h_matrix_heatmap.html")
    print("   ✅ H2H Matrix Heatmap saved")

def create_standings_chart(standings_df, viz_dir):
    """Create overall standings bar chart"""
    
    print("   📊 Creating Overall Standings Chart...")
    
    # Sort by rank
    standings_sorted = standings_df.sort_values('rank')
    
    fig = go.Figure()
    
    # Add wins
    fig.add_trace(go.Bar(
        name='Wins',
        x=standings_sorted['manager'],
        y=standings_sorted['wins'],
        marker_color='green',
        text=standings_sorted['wins'],
        textposition='inside'
    ))
    
    # Add losses  
    fig.add_trace(go.Bar(
        name='Losses',
        x=standings_sorted['manager'],
        y=standings_sorted['losses'],
        marker_color='red',
        text=standings_sorted['losses'],
        textposition='inside'
    ))
    
    fig.update_layout(
        title={
            'text': "Overall Standings - 8 Year Record (2017-2024)<br><sub>League of Hard Knox</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Manager",
        yaxis_title="Games",
        barmode='stack',
        width=1000,
        height=600,
        font=dict(size=12),
        hovermode='x unified'
    )
    
    # Add win percentage annotations
    for i, row in standings_sorted.iterrows():
        fig.add_annotation(
            x=row['manager'],
            y=row['wins'] + row['losses'] + 2,
            text=f"{row['win_pct']:.1f}%",
            showarrow=False,
            font=dict(size=11, color="black")
        )
    
    fig.write_html(viz_dir / "overall_standings.html")
    print("   ✅ Overall Standings Chart saved")

def create_h2h_network(detailed_h2h_df, active_managers, viz_dir):
    """Create network visualization of H2H relationships"""
    
    print("   📊 Creating H2H Network Visualization...")
    
    # Filter for significant matchups (5+ games)
    significant_h2h = detailed_h2h_df[detailed_h2h_df['games'] >= 5].copy()
    
    # Create positions in a circle
    import math
    n = len(active_managers)
    positions = {}
    for i, manager in enumerate(sorted(active_managers)):
        angle = 2 * math.pi * i / n
        positions[manager] = (math.cos(angle), math.sin(angle))
    
    # Create edges and node traces
    edge_trace = []
    for _, row in significant_h2h.iterrows():
        if row['manager'] in active_managers and row['opponent'] in active_managers:
            x0, y0 = positions[row['manager']]
            x1, y1 = positions[row['opponent']]
            
            # Color based on win percentage
            if row['win_pct'] >= 70:
                color = 'green'
                width = 4
            elif row['win_pct'] >= 55:
                color = 'lightgreen'
                width = 3
            elif row['win_pct'] <= 30:
                color = 'red'
                width = 4
            elif row['win_pct'] <= 45:
                color = 'lightcoral'
                width = 3
            else:
                color = 'gray'
                width = 2
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=width, color=color),
                hoverinfo='none',
                showlegend=False
            ))
    
    # Create node trace
    node_x = [positions[manager][0] for manager in sorted(active_managers)]
    node_y = [positions[manager][1] for manager in sorted(active_managers)]
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=sorted(active_managers),
        textposition="middle center",
        marker=dict(
            size=50,
            color='lightblue',
            line=dict(width=2, color='darkblue')
        ),
        textfont=dict(size=10),
        hoverinfo='text',
        hovertext=[f"{manager}" for manager in sorted(active_managers)]
    )
    
    fig = go.Figure(data=edge_trace + [node_trace])
    
    fig.update_layout(
        title={
            'text': "Head-to-Head Network (5+ Games)<br><sub>Green=Dominant, Red=Dominated, Gray=Even</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=100),
        annotations=[ dict(
            text="Line thickness and color indicate dominance level",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002,
            xanchor='left', yanchor='bottom',
            font=dict(size=12)
        )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=800,
        height=800
    )
    
    fig.write_html(viz_dir / "h2h_network.html")
    print("   ✅ H2H Network Visualization saved")

def create_season_performance(matchups_df, active_managers, viz_dir):
    """Create season-by-season performance chart"""
    
    print("   📊 Creating Season Performance Chart...")
    
    # Calculate season records
    season_records = []
    
    for season in sorted(matchups_df['season'].unique()):
        season_data = matchups_df[matchups_df['season'] == season]
        
        for manager in active_managers:
            wins = len(season_data[season_data['winning_manager'] == manager])
            losses = len(season_data[
                ((season_data['manager1'] == manager) | (season_data['manager2'] == manager)) &
                (season_data['winning_manager'] != manager) &
                (season_data['winning_manager'].notna())
            ])
            
            if wins + losses > 0:
                season_records.append({
                    'season': season,
                    'manager': manager,
                    'wins': wins,
                    'losses': losses,
                    'win_pct': wins / (wins + losses) * 100 if wins + losses > 0 else 0
                })
    
    season_df = pd.DataFrame(season_records)
    
    fig = go.Figure()
    
    # Add trace for each manager
    for manager in sorted(active_managers):
        manager_data = season_df[season_df['manager'] == manager].sort_values('season')
        
        fig.add_trace(go.Scatter(
            x=manager_data['season'],
            y=manager_data['win_pct'],
            mode='lines+markers',
            name=manager,
            line=dict(width=2),
            marker=dict(size=8),
            hovertemplate=f'<b>{manager}</b><br>Season: %{{x}}<br>Win %: %{{y:.1f}}%<br>Record: %{{customdata}}<extra></extra>',
            customdata=[f"{row['wins']}-{row['losses']}" for _, row in manager_data.iterrows()]
        ))
    
    fig.update_layout(
        title={
            'text': "Season-by-Season Win Percentage (2017-2024)<br><sub>League of Hard Knox</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Season",
        yaxis_title="Win Percentage (%)",
        width=1200,
        height=700,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left", 
            x=1.01
        )
    )
    
    # Add reference line at 50%
    fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                  annotation_text="50% (Even)", annotation_position="bottom right")
    
    fig.write_html(viz_dir / "season_performance.html")
    print("   ✅ Season Performance Chart saved")

def create_points_analysis(matchups_df, active_managers, viz_dir):
    """Create points scoring analysis"""
    
    print("   📊 Creating Points Analysis...")
    
    # Calculate average points for/against
    points_data = []
    
    for manager in active_managers:
        manager_matchups = matchups_df[
            (matchups_df['manager1'] == manager) | (matchups_df['manager2'] == manager)
        ]
        
        points_for = []
        points_against = []
        
        for _, row in manager_matchups.iterrows():
            if row['manager1'] == manager:
                points_for.append(row['team1_score'])
                points_against.append(row['team2_score'])
            else:
                points_for.append(row['team2_score'])
                points_against.append(row['team1_score'])
        
        points_data.append({
            'manager': manager,
            'avg_points_for': np.mean(points_for),
            'avg_points_against': np.mean(points_against),
            'total_games': len(points_for)
        })
    
    points_df = pd.DataFrame(points_data)
    
    # Create scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=points_df['avg_points_for'],
        y=points_df['avg_points_against'],
        mode='markers+text',
        text=points_df['manager'],
        textposition="top center",
        marker=dict(
            size=points_df['total_games'] / 3,  # Scale by number of games
            color=points_df['avg_points_for'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Avg Points For")
        ),
        hovertemplate='<b>%{text}</b><br>Avg For: %{x:.1f}<br>Avg Against: %{y:.1f}<br>Games: %{customdata}<extra></extra>',
        customdata=points_df['total_games']
    ))
    
    # Add diagonal line (equal points for/against)
    min_val = min(points_df['avg_points_for'].min(), points_df['avg_points_against'].min()) - 5
    max_val = max(points_df['avg_points_for'].max(), points_df['avg_points_against'].max()) + 5
    
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Equal Points',
        showlegend=True
    ))
    
    fig.update_layout(
        title={
            'text': "Points For vs Points Against (2017-2024)<br><sub>Bubble size = Games played</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Average Points For",
        yaxis_title="Average Points Against",
        width=800,
        height=700
    )
    
    fig.write_html(viz_dir / "points_analysis.html")
    print("   ✅ Points Analysis saved")

def create_rivalry_analysis(detailed_h2h_df, active_managers, viz_dir):
    """Create rivalry analysis showing closest matchups"""
    
    print("   📊 Creating Rivalry Analysis...")
    
    # Find closest rivalries (most games, closest records)
    rivalries = []
    processed = set()
    
    for _, row in detailed_h2h_df.iterrows():
        manager1, manager2 = row['manager'], row['opponent']
        
        if (manager1 in active_managers and manager2 in active_managers and
            row['games'] >= 5 and (manager1, manager2) not in processed and
            (manager2, manager1) not in processed):
            
            # Get reverse record
            reverse = detailed_h2h_df[
                (detailed_h2h_df['manager'] == manager2) & 
                (detailed_h2h_df['opponent'] == manager1)
            ]
            
            if not reverse.empty:
                wins1, wins2 = row['wins'], reverse.iloc[0]['wins']
                games = row['games']
                diff = abs(wins1 - wins2)
                
                rivalries.append({
                    'matchup': f"{manager1} vs {manager2}",
                    'manager1': manager1,
                    'manager2': manager2,
                    'wins1': wins1,
                    'wins2': wins2,
                    'games': games,
                    'difference': diff,
                    'competitiveness': 1 / (diff + 1),  # Higher = more competitive
                })
                
                processed.add((manager1, manager2))
                processed.add((manager2, manager1))
    
    rivalry_df = pd.DataFrame(rivalries)
    rivalry_df = rivalry_df.sort_values(['difference', 'games'], ascending=[True, False])
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    top_rivalries = rivalry_df.head(10)
    
    fig.add_trace(go.Bar(
        y=top_rivalries['matchup'],
        x=top_rivalries['games'],
        orientation='h',
        marker=dict(
            color=top_rivalries['competitiveness'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Competitiveness")
        ),
        text=[f"{row['wins1']}-{row['wins2']}" for _, row in top_rivalries.iterrows()],
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Games: %{x}<br>Record: %{text}<br>Difference: %{customdata}<extra></extra>',
        customdata=top_rivalries['difference']
    ))
    
    fig.update_layout(
        title={
            'text': "Top 10 Rivalries (5+ Games)<br><sub>Sorted by competitiveness</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Total Games Played",
        yaxis_title="Matchup",
        width=800,
        height=600,
        margin=dict(l=150)
    )
    
    fig.write_html(viz_dir / "rivalry_analysis.html")
    print("   ✅ Rivalry Analysis saved")

def create_interactive_dashboard(detailed_h2h_df, standings_df, matchups_df, active_managers, viz_dir):
    """Create comprehensive interactive dashboard"""
    
    print("   📊 Creating Interactive Dashboard...")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('H2H Win Percentage Matrix', 'Overall Standings', 
                       'Manager Performance Over Time', 'Points Distribution'),
        specs=[[{"type": "heatmap"}, {"type": "bar"}],
               [{"type": "scatter", "colspan": 2}, None]],
        row_heights=[0.5, 0.5],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # 1. H2H Matrix (top-left)
    matrix = pd.DataFrame(index=active_managers, columns=active_managers)
    for _, row in detailed_h2h_df.iterrows():
        if row['manager'] in active_managers and row['opponent'] in active_managers:
            matrix.loc[row['manager'], row['opponent']] = row['win_pct']
    
    for manager in active_managers:
        matrix.loc[manager, manager] = None
    
    matrix = matrix.astype(float)
    
    fig.add_trace(
        go.Heatmap(
            z=matrix.values,
            x=active_managers,
            y=active_managers,
            colorscale='RdYlGn',
            zmid=50,
            showscale=False,
            text=[[f"{val:.0f}%" if not pd.isna(val) else "" for val in row] for row in matrix.values],
            texttemplate="%{text}",
            textfont={"size": 8}
        ),
        row=1, col=1
    )
    
    # 2. Standings (top-right)
    standings_sorted = standings_df.sort_values('rank')
    
    fig.add_trace(
        go.Bar(
            x=standings_sorted['manager'],
            y=standings_sorted['win_pct'],
            name='Win %',
            marker_color='steelblue',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Performance over time (bottom, full width)
    season_records = []
    for season in sorted(matchups_df['season'].unique()):
        season_data = matchups_df[matchups_df['season'] == season]
        for manager in active_managers:
            wins = len(season_data[season_data['winning_manager'] == manager])
            total = len(season_data[
                (season_data['manager1'] == manager) | (season_data['manager2'] == manager)
            ])
            if total > 0:
                season_records.append({
                    'season': season,
                    'manager': manager,
                    'win_pct': wins / total * 100
                })
    
    season_df = pd.DataFrame(season_records)
    
    # Add top 5 managers only for clarity
    top_5_managers = standings_sorted.head(5)['manager'].tolist()
    
    for manager in top_5_managers:
        manager_data = season_df[season_df['manager'] == manager]
        fig.add_trace(
            go.Scatter(
                x=manager_data['season'],
                y=manager_data['win_pct'],
                mode='lines+markers',
                name=manager,
                showlegend=True
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "League of Hard Knox - H2H Dashboard (2017-2024)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=1000,
        showlegend=True,
        legend=dict(x=1.02, y=0.5)
    )
    
    fig.write_html(viz_dir / "h2h_dashboard.html")
    print("   ✅ Interactive Dashboard saved")

if __name__ == "__main__":
    # Install required packages
    try:
        import plotly
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "plotly", "kaleido"])
        import plotly.graph_objects as go
        import plotly.express as px
    
    create_h2h_visualizations()