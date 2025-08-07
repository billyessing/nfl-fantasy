import csv
import pandas as pd
from typing import Dict, List
from pathlib import Path
import logging
from models import Owner, Team, Matchup, SeasonRecord, Roster, HeadToHeadRecord, League

class CSVDataStorage:
    """Handles CSV storage and retrieval of fantasy league data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Define CSV file paths
        self.files = {
            'owners': self.data_dir / 'owners.csv',
            'teams': self.data_dir / 'teams.csv', 
            'matchups': self.data_dir / 'matchups.csv',
            'season_records': self.data_dir / 'season_records.csv',
            'rosters': self.data_dir / 'rosters.csv',
            'head_to_head': self.data_dir / 'head_to_head_records.csv'
        }
    
    def save_all_data(self, league_data: Dict):
        """Save all league data to CSV files"""
        try:
            self.save_owners(list(league_data.get('owners', {}).values()))
            self.save_teams(list(league_data.get('teams', {}).values()))
            self.save_matchups(league_data.get('matchups', []))
            self.save_season_records(league_data.get('season_records', []))
            self.save_rosters(league_data.get('rosters', []))
            
            self.logger.info("All data saved to CSV files successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            raise
    
    def save_owners(self, owners: List[Owner]):
        """Save owner data to CSV"""
        if not owners:
            return
            
        with open(self.files['owners'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['owner_id', 'name', 'email'])
            
            for owner in owners:
                writer.writerow([
                    owner.owner_id,
                    owner.name,
                    owner.email or ''
                ])
        
        self.logger.info(f"Saved {len(owners)} owners to {self.files['owners']}")
    
    def save_teams(self, teams: List[Team]):
        """Save team data to CSV"""
        if not teams:
            return
            
        with open(self.files['teams'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['team_id', 'owner_id', 'team_name', 'season', 'division'])
            
            for team in teams:
                writer.writerow([
                    team.team_id,
                    team.owner_id,
                    team.team_name,
                    team.season,
                    team.division or ''
                ])
        
        self.logger.info(f"Saved {len(teams)} teams to {self.files['teams']}")
    
    def save_matchups(self, matchups: List[Matchup]):
        """Save matchup data to CSV"""
        if not matchups:
            return
            
        with open(self.files['matchups'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'matchup_id', 'season', 'week', 'team1_owner_id', 'team2_owner_id',
                'team1_score', 'team2_score', 'winner_owner_id', 'playoff'
            ])
            
            for matchup in matchups:
                writer.writerow([
                    matchup.matchup_id,
                    matchup.season,
                    matchup.week,
                    matchup.team1_owner_id,
                    matchup.team2_owner_id,
                    matchup.team1_score,
                    matchup.team2_score,
                    matchup.winner_owner_id or '',
                    matchup.playoff
                ])
        
        self.logger.info(f"Saved {len(matchups)} matchups to {self.files['matchups']}")
    
    def save_season_records(self, records: List[SeasonRecord]):
        """Save season record data to CSV"""
        if not records:
            return
            
        with open(self.files['season_records'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'owner_id', 'season', 'wins', 'losses', 'ties',
                'points_for', 'points_against', 'final_rank', 'playoff_seed'
            ])
            
            for record in records:
                writer.writerow([
                    record.owner_id,
                    record.season,
                    record.wins,
                    record.losses,
                    record.ties,
                    record.points_for,
                    record.points_against,
                    record.final_rank,
                    record.playoff_seed or ''
                ])
        
        self.logger.info(f"Saved {len(records)} season records to {self.files['season_records']}")
    
    def save_rosters(self, rosters: List[Roster]):
        """Save roster data to CSV"""
        if not rosters:
            return
            
        with open(self.files['rosters'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'roster_id', 'owner_id', 'season', 'week', 'players_json'
            ])
            
            for roster in rosters:
                import json
                writer.writerow([
                    roster.roster_id,
                    roster.owner_id,
                    roster.season,
                    roster.week,
                    json.dumps(roster.players)
                ])
        
        self.logger.info(f"Saved {len(rosters)} rosters to {self.files['rosters']}")
    
    def save_head_to_head_records(self, records: List[HeadToHeadRecord]):
        """Save head-to-head records to CSV"""
        if not records:
            return
            
        with open(self.files['head_to_head'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'owner1_id', 'owner2_id', 'owner1_wins', 'owner2_wins',
                'owner1_points', 'owner2_points', 'total_games'
            ])
            
            for record in records:
                writer.writerow([
                    record.owner1_id,
                    record.owner2_id,
                    record.owner1_wins,
                    record.owner2_wins,
                    record.owner1_points,
                    record.owner2_points,
                    record.total_games
                ])
        
        self.logger.info(f"Saved {len(records)} head-to-head records to {self.files['head_to_head']}")
    
    def load_owners(self) -> List[Owner]:
        """Load owners from CSV"""
        if not self.files['owners'].exists():
            return []
        
        owners = []
        df = pd.read_csv(self.files['owners'])
        
        for _, row in df.iterrows():
            owner = Owner(
                owner_id=row['owner_id'],
                name=row['name'],
                email=row['email'] if pd.notna(row['email']) else None
            )
            owners.append(owner)
        
        return owners
    
    def load_matchups(self) -> List[Matchup]:
        """Load matchups from CSV"""
        if not self.files['matchups'].exists():
            return []
        
        matchups = []
        df = pd.read_csv(self.files['matchups'])
        
        for _, row in df.iterrows():
            matchup = Matchup(
                matchup_id=row['matchup_id'],
                season=int(row['season']),
                week=int(row['week']),
                team1_owner_id=row['team1_owner_id'],
                team2_owner_id=row['team2_owner_id'],
                team1_score=float(row['team1_score']),
                team2_score=float(row['team2_score']),
                winner_owner_id=row['winner_owner_id'] if pd.notna(row['winner_owner_id']) else None,
                playoff=bool(row['playoff'])
            )
            matchups.append(matchup)
        
        return matchups
    
    def load_season_records(self) -> List[SeasonRecord]:
        """Load season records from CSV"""
        if not self.files['season_records'].exists():
            return []
        
        records = []
        df = pd.read_csv(self.files['season_records'])
        
        for _, row in df.iterrows():
            record = SeasonRecord(
                owner_id=row['owner_id'],
                season=int(row['season']),
                wins=int(row['wins']),
                losses=int(row['losses']),
                ties=int(row['ties']),
                points_for=float(row['points_for']),
                points_against=float(row['points_against']),
                final_rank=int(row['final_rank']),
                playoff_seed=int(row['playoff_seed']) if pd.notna(row['playoff_seed']) else None
            )
            records.append(record)
        
        return records
    
    def load_head_to_head_records(self) -> List[HeadToHeadRecord]:
        """Load head-to-head records from CSV"""
        if not self.files['head_to_head'].exists():
            return []
        
        records = []
        df = pd.read_csv(self.files['head_to_head'])
        
        for _, row in df.iterrows():
            record = HeadToHeadRecord(
                owner1_id=row['owner1_id'],
                owner2_id=row['owner2_id'],
                owner1_wins=int(row['owner1_wins']),
                owner2_wins=int(row['owner2_wins']),
                owner1_points=float(row['owner1_points']),
                owner2_points=float(row['owner2_points']),
                total_games=int(row['total_games'])
            )
            records.append(record)
        
        return records
    
    def get_data_summary(self) -> Dict[str, int]:
        """Get summary of data stored in CSV files"""
        summary = {}
        
        for data_type, file_path in self.files.items():
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    summary[data_type] = len(df)
                except Exception as e:
                    self.logger.error(f"Error reading {file_path}: {e}")
                    summary[data_type] = 0
            else:
                summary[data_type] = 0
        
        return summary
    
    def export_to_excel(self, output_file: str = "fantasy_league_data.xlsx"):
        """Export all CSV data to Excel with multiple sheets"""
        try:
            with pd.ExcelWriter(self.data_dir / output_file) as writer:
                for data_type, file_path in self.files.items():
                    if file_path.exists():
                        df = pd.read_csv(file_path)
                        df.to_excel(writer, sheet_name=data_type, index=False)
            
            self.logger.info(f"Data exported to Excel: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            raise