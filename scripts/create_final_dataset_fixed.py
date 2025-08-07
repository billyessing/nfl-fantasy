#!/usr/bin/env python3
"""
Create final dataset with robust team name matching.
"""

import pandas as pd
from pathlib import Path

def normalize_team_name(name):
    """Normalize team name for matching"""
    if pd.isna(name):
        return None
    # Convert to lowercase and handle common variations
    name = str(name).strip()
    name = name.replace('-', ' ')  # Handle hyphens
    name = name.replace('  ', ' ')  # Handle double spaces
    return name.lower()

def create_final_dataset_fixed():
    """Create final dataset with robust team name matching"""
    
    print("🎯 CREATING FINAL DATASET (CASE-INSENSITIVE MATCHING)")
    print("=" * 60)
    
    # Load the 8-year matchups data
    data_dir = Path("data/full_seasons_2017_2024")
    matchups_df = pd.read_csv(data_dir / "matchups_simplified.csv")
    
    # Load the actual owners data
    owners_dir = Path("data/actual_owners")
    owners_df = pd.read_csv(owners_dir / "owners_2017_2024_complete.csv")
    
    print(f"📊 Loaded {len(matchups_df)} matchups and {len(owners_df)} owner records")
    
    # Get all unique team names from matchups data
    matchup_teams = set(matchups_df['team1'].unique()) | set(matchups_df['team2'].unique())
    
    # Get all team names from owners data (exclude waiver)
    owner_teams = set(owners_df[owners_df['manager_name'] != 'Waiver']['team_name'].unique())
    
    print(f"\n🔍 TEAM NAME ANALYSIS:")
    print(f"   Matchup data teams: {len(matchup_teams)}")
    print(f"   Owner data teams: {len(owner_teams)}")
    
    # Create normalized mapping
    normalized_to_actual = {}
    team_to_manager = {}
    
    # Build normalized mapping from owners data
    for _, row in owners_df.iterrows():
        if row['manager_name'] == 'Waiver':
            continue
            
        team = row['team_name']
        manager = row['manager_name']
        normalized = normalize_team_name(team)
        
        normalized_to_actual[normalized] = team
        team_to_manager[team] = manager
    
    # Create reverse lookup for matchup teams to owners teams
    matchup_to_owner_team = {}
    
    for matchup_team in matchup_teams:
        normalized_matchup = normalize_team_name(matchup_team)
        
        # Direct match
        if normalized_matchup in normalized_to_actual:
            actual_team = normalized_to_actual[normalized_matchup]
            matchup_to_owner_team[matchup_team] = actual_team
            continue
        
        # Fuzzy matching for common variations
        found_match = False
        for norm_owner, actual_owner in normalized_to_actual.items():
            # Handle common variations
            if (normalized_matchup == norm_owner or 
                normalized_matchup.replace(' ', '') == norm_owner.replace(' ', '') or
                normalized_matchup.replace('four twenty one', 'fourtwenty-one') == norm_owner or
                normalized_matchup.replace('g spot', 'g-spot') == norm_owner or
                normalized_matchup.replace('hide n zeke', 'hide n zeke') == norm_owner):
                
                matchup_to_owner_team[matchup_team] = actual_owner
                found_match = True
                break
        
        if not found_match:
            print(f"   ⚠️  No match found for: '{matchup_team}' (normalized: '{normalized_matchup}')")
    
    print(f"\n📋 TEAM NAME MAPPING:")
    for matchup_team, owner_team in sorted(matchup_to_owner_team.items()):
        manager = team_to_manager[owner_team]
        print(f"   '{matchup_team}' -> '{owner_team}' ({manager})")
    
    # Apply mapping to create final dataset
    def get_manager_name(team_name):
        if pd.isna(team_name):
            return None
        
        # Get the actual team name from owners data
        if team_name in matchup_to_owner_team:
            actual_team = matchup_to_owner_team[team_name]
            return team_to_manager[actual_team]
        else:
            return f"Unknown_{team_name.replace(' ', '_')}"
    
    # Add manager columns
    matchups_final = matchups_df.copy()
    matchups_final['manager1'] = matchups_final['team1'].apply(get_manager_name)
    matchups_final['manager2'] = matchups_final['team2'].apply(get_manager_name)
    matchups_final['winning_manager'] = matchups_final['winner'].apply(get_manager_name)
    
    # Check results
    all_managers = set(matchups_final['manager1'].unique()) | set(matchups_final['manager2'].unique())
    all_managers.discard(None)
    
    known_managers = [m for m in all_managers if not m.startswith('Unknown_')]
    unknown_managers = [m for m in all_managers if m.startswith('Unknown_')]
    
    print(f"\n📊 MAPPING RESULTS:")
    print(f"   Total managers: {len(all_managers)}")
    print(f"   Known managers: {len(known_managers)}")
    print(f"   Known: {sorted(known_managers)}")
    
    if unknown_managers:
        print(f"   Unknown: {sorted(unknown_managers)}")
    
    # Show actual manager evolution from owners data
    print(f"\n🔄 ACTUAL MANAGER TEAM EVOLUTION:")
    manager_evolution = {}
    
    for _, row in owners_df.iterrows():
        if row['manager_name'] == 'Waiver':
            continue
            
        manager = row['manager_name']
        team = row['team_name']
        year = row['year']
        
        if manager not in manager_evolution:
            manager_evolution[manager] = []
        manager_evolution[manager].append((year, team))
    
    for manager, history in sorted(manager_evolution.items()):
        history.sort()
        teams = []
        current_team = None
        
        for year, team in history:
            if team != current_team:
                teams.append(team)
                current_team = team
        
        print(f"   {manager}: {' -> '.join(teams)}")
    
    # Save final dataset
    output_dir = Path("data/final_dataset")
    output_dir.mkdir(exist_ok=True)
    
    matchups_final.to_csv(output_dir / "league_hard_knox_2017_2024_complete.csv", index=False)
    
    # Save the mapping reference
    mapping_data = []
    for matchup_team, owner_team in matchup_to_owner_team.items():
        manager = team_to_manager[owner_team]
        mapping_data.append({
            'matchup_team_name': matchup_team,
            'actual_team_name': owner_team,
            'manager_name': manager
        })
    
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df.to_csv(output_dir / "team_manager_mapping_final.csv", index=False)
    
    # Create comprehensive Excel file
    with pd.ExcelWriter(output_dir / "league_hard_knox_complete_analysis.xlsx") as writer:
        # Main dataset
        matchups_final.to_excel(writer, sheet_name='All_Matchups', index=False)
        
        # Mapping reference
        mapping_df.to_excel(writer, sheet_name='Team_Manager_Mapping', index=False)
        
        # Owners evolution
        owners_clean = owners_df[owners_df['manager_name'] != 'Waiver']
        owners_clean.to_excel(writer, sheet_name='Manager_Evolution', index=False)
        
        # Current active managers (2022-2024, excluding Daniel and Jack)
        active_managers = ['Hayden', 'Michael', 'Phoenix', 'Billy', 'Robbie', 'Nelson', 
                          'Fraser', 'Justin', 'Angus', 'Nic', 'William', 'James']
        
        recent_matchups = matchups_final[
            (matchups_final['season'] >= 2022) &
            matchups_final['manager1'].isin(active_managers) &
            matchups_final['manager2'].isin(active_managers)
        ]
        recent_matchups.to_excel(writer, sheet_name='Current_Era_2022_2024', index=False)
        
        # Season summaries
        for season in sorted(matchups_final['season'].unique()):
            season_data = matchups_final[matchups_final['season'] == season]
            season_data.to_excel(writer, sheet_name=f'Season_{season}', index=False)
    
    print(f"\n💾 FINAL FILES CREATED:")
    print(f"   📄 {output_dir}/league_hard_knox_2017_2024_complete.csv")
    print(f"   📄 {output_dir}/team_manager_mapping_final.csv")
    print(f"   📊 {output_dir}/league_hard_knox_complete_analysis.xlsx")
    
    # Final statistics
    total_matchups = len(matchups_final)
    known_matchups = len(matchups_final[
        ~matchups_final['manager1'].str.startswith('Unknown_') &
        ~matchups_final['manager2'].str.startswith('Unknown_')
    ])
    
    current_era_matchups = len(recent_matchups)
    
    print(f"\n🎉 FINAL DATASET COMPLETE!")
    print(f"   📊 Total matchups (2017-2024): {total_matchups}")
    print(f"   ✅ Matchups with known managers: {known_matchups} ({known_matchups/total_matchups*100:.1f}%)")
    print(f"   🎯 Current era matchups (2022-2024): {current_era_matchups}")
    print(f"   👥 Active managers: {len(active_managers)}")
    print(f"   📅 Historical span: 8 seasons (2017-2024)")
    
    # Show sample
    print(f"\n📋 SAMPLE OF FINAL DATASET:")
    sample = matchups_final[['season', 'week', 'team1', 'manager1', 'team1_score', 
                            'team2', 'manager2', 'team2_score', 'winning_manager']].head(5)
    print(sample.to_string(index=False))
    
    return True

if __name__ == "__main__":
    create_final_dataset_fixed()