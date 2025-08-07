#!/usr/bin/env python3
"""
Create comprehensive head-to-head analysis using actual manager names.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

def create_h2h_analysis():
    """Create comprehensive H2H analysis with actual manager names"""
    
    print("🥊 HEAD-TO-HEAD ANALYSIS - LEAGUE OF HARD KNOX (2017-2024)")
    print("=" * 70)
    
    # Load the final dataset
    data_dir = Path("data/final_dataset")
    matchups_df = pd.read_csv(data_dir / "league_hard_knox_2017_2024_complete.csv")
    
    print(f"📊 Analyzing {len(matchups_df)} matchups across 8 seasons")
    
    # Filter to current active managers only (exclude Daniel and Jack who left)
    active_managers = ['Hayden', 'Michael', 'Phoenix', 'Billy', 'Robbie', 'Nelson', 
                      'Fraser', 'Justin', 'Angus', 'Nic', 'William', 'James']
    
    current_matchups = matchups_df[
        matchups_df['manager1'].isin(active_managers) &
        matchups_df['manager2'].isin(active_managers)
    ]
    
    print(f"🎯 Focusing on {len(current_matchups)} matchups between current active managers")
    
    # Calculate H2H records
    h2h_records = defaultdict(lambda: defaultdict(lambda: {
        'wins': 0, 'losses': 0, 'points_for': 0, 'points_against': 0, 'games': 0
    }))
    
    for _, row in current_matchups.iterrows():
        manager1 = row['manager1']
        manager2 = row['manager2']
        winner = row['winning_manager']
        
        if manager1 == manager2:
            continue
            
        # Update records
        if winner == manager1:
            h2h_records[manager1][manager2]['wins'] += 1
            h2h_records[manager2][manager1]['losses'] += 1
        elif winner == manager2:
            h2h_records[manager2][manager1]['wins'] += 1
            h2h_records[manager1][manager2]['losses'] += 1
        
        # Update points and games
        h2h_records[manager1][manager2]['points_for'] += row['team1_score']
        h2h_records[manager1][manager2]['points_against'] += row['team2_score']
        h2h_records[manager1][manager2]['games'] += 1
        
        h2h_records[manager2][manager1]['points_for'] += row['team2_score']
        h2h_records[manager2][manager1]['points_against'] += row['team1_score']
        h2h_records[manager2][manager1]['games'] += 1
    
    # Calculate overall records
    overall_records = {}
    for manager in active_managers:
        total_wins = sum(h2h_records[manager][opp]['wins'] for opp in h2h_records[manager])
        total_losses = sum(h2h_records[manager][opp]['losses'] for opp in h2h_records[manager])
        total_points_for = sum(h2h_records[manager][opp]['points_for'] for opp in h2h_records[manager])
        total_points_against = sum(h2h_records[manager][opp]['points_against'] for opp in h2h_records[manager])
        total_games = sum(h2h_records[manager][opp]['games'] for opp in h2h_records[manager])
        
        win_pct = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
        avg_points_for = total_points_for / total_games if total_games > 0 else 0
        avg_points_against = total_points_against / total_games if total_games > 0 else 0
        
        overall_records[manager] = {
            'wins': total_wins,
            'losses': total_losses,
            'win_pct': win_pct,
            'points_for': total_points_for,
            'points_against': total_points_against,
            'avg_for': avg_points_for,
            'avg_against': avg_points_against,
            'games': total_games
        }
    
    # Sort by win percentage, then by wins
    sorted_managers = sorted(overall_records.items(), 
                           key=lambda x: (x[1]['win_pct'], x[1]['wins']), 
                           reverse=True)
    
    print(f"\n🏆 OVERALL STANDINGS (Current Active Managers):")
    print("-" * 70)
    
    for rank, (manager, record) in enumerate(sorted_managers, 1):
        print(f"{rank:2d}. {manager:8s}: {record['wins']:2d}-{record['losses']:2d} "
              f"({record['win_pct']:5.1f}%) | Avg: {record['avg_for']:6.1f}-{record['avg_against']:6.1f}")
    
    # Most dominant H2H records
    print(f"\n🔥 MOST DOMINANT H2H RECORDS (5+ games):")
    print("-" * 70)
    
    dominant_records = []
    for manager1 in h2h_records:
        for manager2, record in h2h_records[manager1].items():
            games = record['games']
            if games >= 5:
                win_pct = (record['wins'] / games * 100) if games > 0 else 0
                if record['wins'] >= record['losses'] * 2:  # At least 2:1 ratio
                    dominant_records.append((manager1, manager2, record['wins'], record['losses'], win_pct, games))
    
    dominant_records.sort(key=lambda x: (x[4], x[2]), reverse=True)
    
    for record in dominant_records[:10]:
        manager1, manager2, wins, losses, win_pct, games = record
        avg_for = h2h_records[manager1][manager2]['points_for'] / games
        avg_against = h2h_records[manager1][manager2]['points_against'] / games
        print(f"   {manager1:8s} vs {manager2:8s}: {wins:2d}-{losses:2d} ({win_pct:5.1f}%) | "
              f"Avg: {avg_for:6.1f}-{avg_against:6.1f} ({games} games)")
    
    # Closest rivalries
    print(f"\n⚔️  CLOSEST RIVALRIES (7+ games, within 2 games):")
    print("-" * 70)
    
    close_rivalries = []
    processed_pairs = set()
    
    for manager1 in h2h_records:
        for manager2, record in h2h_records[manager1].items():
            pair = tuple(sorted([manager1, manager2]))
            if pair in processed_pairs:
                continue
            processed_pairs.add(pair)
            
            games = record['games']
            if games >= 7:
                wins1 = record['wins']
                wins2 = record['losses']
                diff = abs(wins1 - wins2)
                
                if diff <= 2:
                    # Get reverse record
                    wins2_actual = h2h_records[manager2][manager1]['wins']
                    close_rivalries.append((manager1, manager2, wins1, wins2_actual, games, diff))
    
    close_rivalries.sort(key=lambda x: (x[5], -x[4]))  # Sort by difference, then games desc
    
    for rivalry in close_rivalries:
        manager1, manager2, wins1, wins2, games, diff = rivalry
        avg_for1 = h2h_records[manager1][manager2]['points_for'] / games
        avg_against1 = h2h_records[manager1][manager2]['points_against'] / games
        print(f"   {manager1:8s} vs {manager2:8s}: {wins1:2d}-{wins2:2d} ({games} games, diff: {diff}) | "
              f"Avg: {avg_for1:6.1f}-{avg_against1:6.1f}")
    
    # Highest scoring matchups
    print(f"\n🚀 HIGHEST SCORING REGULAR MATCHUPS (avg 240+ combined):")
    print("-" * 70)
    
    high_scoring = []
    processed_pairs = set()
    
    for manager1 in h2h_records:
        for manager2, record in h2h_records[manager1].items():
            pair = tuple(sorted([manager1, manager2]))
            if pair in processed_pairs:
                continue
            processed_pairs.add(pair)
            
            games = record['games']
            if games >= 3:
                combined_avg = (record['points_for'] + record['points_against']) / games
                if combined_avg >= 240:
                    avg_for = record['points_for'] / games
                    avg_against = record['points_against'] / games
                    high_scoring.append((manager1, manager2, combined_avg, avg_for, avg_against, games))
    
    high_scoring.sort(key=lambda x: x[2], reverse=True)
    
    for matchup in high_scoring[:8]:
        manager1, manager2, combined, avg_for, avg_against, games = matchup
        print(f"   {manager1:8s} vs {manager2:8s}: {combined:6.1f} avg combined | "
              f"{avg_for:6.1f}-{avg_against:6.1f} ({games} games)")
    
    # Manager head-to-head matrix
    print(f"\n📊 DETAILED HEAD-TO-HEAD BREAKDOWN:")
    print("-" * 70)
    
    for manager, (total_wins, total_losses) in [(m, (r['wins'], r['losses'])) for m, r in sorted_managers[:6]]:
        print(f"\n🏆 {manager.upper()} ({total_wins}-{total_losses}, {overall_records[manager]['win_pct']:.1f}%):")
        
        # Sort opponents by record against them
        opponents = []
        for opp, record in h2h_records[manager].items():
            if record['games'] > 0:
                opponents.append((opp, record['wins'], record['losses'], record['games'],
                                record['points_for']/record['games'], record['points_against']/record['games']))
        
        opponents.sort(key=lambda x: (x[1]/x[3], x[1]), reverse=True)
        
        for opp, wins, losses, games, avg_for, avg_against in opponents:
            win_pct = wins/games*100 if games > 0 else 0
            print(f"   vs {opp:8s}: {wins:2d}-{losses:2d} ({win_pct:5.1f}%) | {avg_for:6.1f}-{avg_against:6.1f}")
    
    # Era analysis
    print(f"\n📅 ERA ANALYSIS:")
    print("-" * 70)
    
    eras = {
        'Early Era (2017-2019)': current_matchups[current_matchups['season'] <= 2019],
        'Middle Era (2020-2021)': current_matchups[(current_matchups['season'] >= 2020) & (current_matchups['season'] <= 2021)],
        'Recent Era (2022-2024)': current_matchups[current_matchups['season'] >= 2022]
    }
    
    for era_name, era_data in eras.items():
        if len(era_data) == 0:
            continue
            
        era_records = defaultdict(lambda: {'wins': 0, 'losses': 0})
        
        for _, row in era_data.iterrows():
            manager1, manager2, winner = row['manager1'], row['manager2'], row['winning_manager']
            if winner == manager1:
                era_records[manager1]['wins'] += 1
                era_records[manager2]['losses'] += 1
            elif winner == manager2:
                era_records[manager2]['wins'] += 1
                era_records[manager1]['losses'] += 1
        
        era_standings = []
        for manager in active_managers:
            wins = era_records[manager]['wins']
            losses = era_records[manager]['losses']
            if wins + losses > 0:
                win_pct = wins / (wins + losses) * 100
                era_standings.append((manager, wins, losses, win_pct))
        
        era_standings.sort(key=lambda x: (x[3], x[1]), reverse=True)
        
        print(f"\n{era_name} Top 5:")
        for rank, (manager, wins, losses, win_pct) in enumerate(era_standings[:5], 1):
            print(f"   {rank}. {manager:8s}: {wins:2d}-{losses:2d} ({win_pct:5.1f}%)")
    
    # Save detailed analysis
    output_dir = Path("data/h2h_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # Create detailed records DataFrame
    detailed_records = []
    for manager1 in h2h_records:
        for manager2, record in h2h_records[manager1].items():
            if record['games'] > 0:
                detailed_records.append({
                    'manager': manager1,
                    'opponent': manager2,
                    'wins': record['wins'],
                    'losses': record['losses'],
                    'games': record['games'],
                    'win_pct': record['wins'] / record['games'] * 100,
                    'avg_points_for': record['points_for'] / record['games'],
                    'avg_points_against': record['points_against'] / record['games'],
                    'total_points_for': record['points_for'],
                    'total_points_against': record['points_against']
                })
    
    detailed_df = pd.DataFrame(detailed_records)
    detailed_df.to_csv(output_dir / "detailed_h2h_records.csv", index=False)
    
    # Overall standings
    standings_df = pd.DataFrame([
        {
            'rank': rank,
            'manager': manager,
            'wins': record['wins'],
            'losses': record['losses'],
            'games': record['games'],
            'win_pct': record['win_pct'],
            'avg_points_for': record['avg_for'],
            'avg_points_against': record['avg_against'],
            'total_points_for': record['points_for'],
            'total_points_against': record['points_against']
        }
        for rank, (manager, record) in enumerate(sorted_managers, 1)
    ])
    standings_df.to_csv(output_dir / "overall_standings.csv", index=False)
    
    print(f"\n💾 Analysis saved to: {output_dir}/")
    print(f"   📄 detailed_h2h_records.csv")
    print(f"   📄 overall_standings.csv")
    
    print(f"\n🎉 HEAD-TO-HEAD ANALYSIS COMPLETE!")
    print(f"   📊 {len(current_matchups)} matchups analyzed")
    print(f"   👥 {len(active_managers)} active managers")
    print(f"   📅 8 seasons (2017-2024)")
    
    return True

if __name__ == "__main__":
    create_h2h_analysis()