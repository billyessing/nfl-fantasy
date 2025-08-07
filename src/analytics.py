import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging
from models import HeadToHeadRecord, Owner, Matchup, SeasonRecord
from storage import CSVDataStorage

class FantasyAnalytics:
    """Analytics engine for fantasy league data"""
    
    def __init__(self, storage: CSVDataStorage):
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        
    def calculate_head_to_head_records(self) -> List[HeadToHeadRecord]:
        """Calculate all-time head-to-head records between owners"""
        matchups = self.storage.load_matchups()
        owners = self.storage.load_owners()
        
        # Create mapping of owner IDs to names
        owner_names = {owner.owner_id: owner.name for owner in owners}
        
        # Track head-to-head stats
        h2h_stats = defaultdict(lambda: {
            'wins': 0, 'losses': 0, 'points_for': 0.0, 'points_against': 0.0, 'games': 0
        })
        
        for matchup in matchups:
            # Skip if no clear winner
            if not matchup.winner_owner_id:
                continue
                
            owner1 = matchup.team1_owner_id
            owner2 = matchup.team2_owner_id
            
            # Create consistent pairing key (alphabetical order)
            pair_key = tuple(sorted([owner1, owner2]))
            
            # Update stats for both owners
            if matchup.winner_owner_id == owner1:
                # Owner1 won
                h2h_stats[(owner1, owner2)]['wins'] += 1
                h2h_stats[(owner2, owner1)]['losses'] += 1
            else:
                # Owner2 won
                h2h_stats[(owner2, owner1)]['wins'] += 1
                h2h_stats[(owner1, owner2)]['losses'] += 1
            
            # Update points
            h2h_stats[(owner1, owner2)]['points_for'] += matchup.team1_score
            h2h_stats[(owner1, owner2)]['points_against'] += matchup.team2_score
            h2h_stats[(owner2, owner1)]['points_for'] += matchup.team2_score
            h2h_stats[(owner2, owner1)]['points_against'] += matchup.team1_score
            
            # Update game counts
            h2h_stats[(owner1, owner2)]['games'] += 1
            h2h_stats[(owner2, owner1)]['games'] += 1
        
        # Convert to HeadToHeadRecord objects
        records = []
        processed_pairs = set()
        
        for (owner1, owner2), stats in h2h_stats.items():
            pair_key = tuple(sorted([owner1, owner2]))
            
            if pair_key in processed_pairs:
                continue
            
            processed_pairs.add(pair_key)
            
            # Get stats for both directions
            stats1 = h2h_stats[(owner1, owner2)]
            stats2 = h2h_stats[(owner2, owner1)]
            
            record = HeadToHeadRecord(
                owner1_id=owner1,
                owner2_id=owner2,
                owner1_wins=stats1['wins'],
                owner2_wins=stats2['wins'],
                owner1_points=stats1['points_for'],
                owner2_points=stats2['points_for'],
                total_games=stats1['games']
            )
            records.append(record)
        
        # Save the calculated records
        self.storage.save_head_to_head_records(records)
        self.logger.info(f"Calculated {len(records)} head-to-head records")
        
        return records
    
    def get_owner_win_percentages(self) -> Dict[str, float]:
        """Calculate win percentage for each owner across all seasons"""
        season_records = self.storage.load_season_records()
        owners = self.storage.load_owners()
        
        owner_names = {owner.owner_id: owner.name for owner in owners}
        win_percentages = {}
        
        # Aggregate wins/losses across all seasons
        owner_totals = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0})
        
        for record in season_records:
            owner_totals[record.owner_id]['wins'] += record.wins
            owner_totals[record.owner_id]['losses'] += record.losses
            owner_totals[record.owner_id]['ties'] += record.ties
        
        # Calculate win percentages
        for owner_id, totals in owner_totals.items():
            total_games = totals['wins'] + totals['losses'] + totals['ties']
            if total_games > 0:
                # Count ties as half wins
                adjusted_wins = totals['wins'] + (totals['ties'] * 0.5)
                win_percentage = (adjusted_wins / total_games) * 100
                win_percentages[owner_names.get(owner_id, owner_id)] = round(win_percentage, 1)
        
        return win_percentages
    
    def get_points_leaders(self, season: Optional[int] = None) -> Dict[str, Dict]:
        """Get points leaders (total, average, highest single game)"""
        matchups = self.storage.load_matchups()
        owners = self.storage.load_owners()
        
        if season:
            matchups = [m for m in matchups if m.season == season]
        
        owner_names = {owner.owner_id: owner.name for owner in owners}
        
        # Track points stats
        points_stats = defaultdict(lambda: {
            'total_points': 0.0, 'games': 0, 'highest_game': 0.0, 'scores': []
        })
        
        for matchup in matchups:
            # Team 1 stats
            points_stats[matchup.team1_owner_id]['total_points'] += matchup.team1_score
            points_stats[matchup.team1_owner_id]['games'] += 1
            points_stats[matchup.team1_owner_id]['scores'].append(matchup.team1_score)
            if matchup.team1_score > points_stats[matchup.team1_owner_id]['highest_game']:
                points_stats[matchup.team1_owner_id]['highest_game'] = matchup.team1_score
            
            # Team 2 stats
            points_stats[matchup.team2_owner_id]['total_points'] += matchup.team2_score
            points_stats[matchup.team2_owner_id]['games'] += 1
            points_stats[matchup.team2_owner_id]['scores'].append(matchup.team2_score)
            if matchup.team2_score > points_stats[matchup.team2_owner_id]['highest_game']:
                points_stats[matchup.team2_owner_id]['highest_game'] = matchup.team2_score
        
        # Calculate averages and format results
        results = {}
        for owner_id, stats in points_stats.items():
            owner_name = owner_names.get(owner_id, owner_id)
            avg_points = stats['total_points'] / stats['games'] if stats['games'] > 0 else 0
            
            results[owner_name] = {
                'total_points': round(stats['total_points'], 1),
                'average_points': round(avg_points, 1),
                'highest_game': round(stats['highest_game'], 1),
                'games_played': stats['games']
            }
        
        return results
    
    def get_championship_history(self) -> Dict[int, str]:
        """Get championship winners by season"""
        season_records = self.storage.load_season_records()
        owners = self.storage.load_owners()
        
        owner_names = {owner.owner_id: owner.name for owner in owners}
        champions = {}
        
        # Group by season and find rank 1
        season_groups = defaultdict(list)
        for record in season_records:
            season_groups[record.season].append(record)
        
        for season, records in season_groups.items():
            # Find champion (rank 1)
            champion_record = min(records, key=lambda x: x.final_rank)
            if champion_record.final_rank == 1:
                champions[season] = owner_names.get(champion_record.owner_id, champion_record.owner_id)
        
        return champions
    
    def get_playoff_performance(self) -> Dict[str, Dict]:
        """Analyze playoff performance for each owner"""
        matchups = self.storage.load_matchups()
        owners = self.storage.load_owners()
        
        owner_names = {owner.owner_id: owner.name for owner in owners}
        
        # Track playoff stats
        playoff_stats = defaultdict(lambda: {
            'appearances': set(), 'wins': 0, 'losses': 0, 'points': 0.0
        })
        
        playoff_matchups = [m for m in matchups if m.playoff]
        
        for matchup in playoff_matchups:
            # Track appearances by season
            playoff_stats[matchup.team1_owner_id]['appearances'].add(matchup.season)
            playoff_stats[matchup.team2_owner_id]['appearances'].add(matchup.season)
            
            # Track wins/losses
            if matchup.winner_owner_id == matchup.team1_owner_id:
                playoff_stats[matchup.team1_owner_id]['wins'] += 1
                playoff_stats[matchup.team2_owner_id]['losses'] += 1
            elif matchup.winner_owner_id == matchup.team2_owner_id:
                playoff_stats[matchup.team2_owner_id]['wins'] += 1
                playoff_stats[matchup.team1_owner_id]['losses'] += 1
            
            # Track points
            playoff_stats[matchup.team1_owner_id]['points'] += matchup.team1_score
            playoff_stats[matchup.team2_owner_id]['points'] += matchup.team2_score
        
        # Format results
        results = {}
        for owner_id, stats in playoff_stats.items():
            owner_name = owner_names.get(owner_id, owner_id)
            total_games = stats['wins'] + stats['losses']
            win_pct = (stats['wins'] / total_games * 100) if total_games > 0 else 0
            avg_points = stats['points'] / total_games if total_games > 0 else 0
            
            results[owner_name] = {
                'appearances': len(stats['appearances']),
                'wins': stats['wins'],
                'losses': stats['losses'],
                'win_percentage': round(win_pct, 1),
                'average_points': round(avg_points, 1)
            }
        
        return results
    
    def get_rivalry_analysis(self, min_games: int = 5) -> List[Dict]:
        """Analyze the most competitive rivalries"""
        h2h_records = self.storage.load_head_to_head_records()
        owners = self.storage.load_owners()
        
        owner_names = {owner.owner_id: owner.name for owner in owners}
        
        rivalries = []
        
        for record in h2h_records:
            if record.total_games >= min_games:
                # Calculate competitiveness metrics
                total_wins = record.owner1_wins + record.owner2_wins
                win_diff = abs(record.owner1_wins - record.owner2_wins)
                competitiveness = 1 - (win_diff / total_wins) if total_wins > 0 else 0
                
                avg_points_diff = abs(
                    (record.owner1_points / record.total_games) - 
                    (record.owner2_points / record.total_games)
                ) if record.total_games > 0 else 0
                
                rivalry = {
                    'owner1': owner_names.get(record.owner1_id, record.owner1_id),
                    'owner2': owner_names.get(record.owner2_id, record.owner2_id),
                    'total_games': record.total_games,
                    'owner1_wins': record.owner1_wins,
                    'owner2_wins': record.owner2_wins,
                    'competitiveness_score': round(competitiveness, 3),
                    'avg_points_diff': round(avg_points_diff, 1),
                    'series_leader': owner_names.get(
                        record.owner1_id if record.owner1_wins > record.owner2_wins else record.owner2_id,
                        'Tied'
                    )
                }
                rivalries.append(rivalry)
        
        # Sort by competitiveness score (higher = more competitive)
        rivalries.sort(key=lambda x: x['competitiveness_score'], reverse=True)
        
        return rivalries
    
    def generate_summary_stats(self) -> Dict:
        """Generate comprehensive league summary statistics"""
        owners = self.storage.load_owners()
        matchups = self.storage.load_matchups()
        season_records = self.storage.load_season_records()
        
        # Basic counts
        total_owners = len(owners)
        total_matchups = len(matchups)
        seasons_played = len(set(record.season for record in season_records))
        
        # Points stats
        all_scores = []
        for matchup in matchups:
            all_scores.extend([matchup.team1_score, matchup.team2_score])
        
        highest_score = max(all_scores) if all_scores else 0
        lowest_score = min(all_scores) if all_scores else 0
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Championship counts
        championships = self.get_championship_history()
        
        return {
            'league_overview': {
                'total_owners': total_owners,
                'seasons_played': seasons_played,
                'total_matchups': total_matchups,
                'total_games': total_matchups
            },
            'scoring': {
                'highest_score_ever': round(highest_score, 1),
                'lowest_score_ever': round(lowest_score, 1),
                'average_score': round(avg_score, 1)
            },
            'championships': championships,
            'most_championships': max(
                [(owner, list(championships.values()).count(owner)) for owner in set(championships.values())],
                key=lambda x: x[1]
            ) if championships else ('N/A', 0)
        }