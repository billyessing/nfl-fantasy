from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Owner:
    """Represents a fantasy league owner (consistent across team name changes)"""
    owner_id: str
    name: str
    email: Optional[str] = None
    
@dataclass 
class Team:
    """Represents a team in a specific season (owner may change team names)"""
    team_id: str
    owner_id: str  # Links to Owner - this stays constant
    team_name: str  # This can change season to season
    season: int
    division: Optional[str] = None
    
@dataclass
class Player:
    """NFL player information"""
    player_id: str
    name: str
    position: str
    nfl_team: str
    
@dataclass
class Matchup:
    """Weekly head-to-head matchup between two teams"""
    matchup_id: str
    season: int
    week: int
    team1_owner_id: str  # Use owner_id instead of team_id
    team2_owner_id: str  # Use owner_id instead of team_id
    team1_score: float
    team2_score: float
    winner_owner_id: Optional[str] = None
    playoff: bool = False
    
@dataclass
class Roster:
    """Team roster for a specific week"""
    roster_id: str
    owner_id: str  # Use owner_id for consistency
    season: int
    week: int
    players: List[Dict[str, any]]  # player_id, position, points, starter status
    
@dataclass
class SeasonRecord:
    """Season-long record for an owner"""
    owner_id: str  # Track by owner, not team name
    season: int
    wins: int
    losses: int
    ties: int
    points_for: float
    points_against: float
    final_rank: int
    playoff_seed: Optional[int] = None
    
@dataclass
class HeadToHeadRecord:
    """All-time head-to-head record between two owners"""
    owner1_id: str
    owner2_id: str
    owner1_wins: int
    owner2_wins: int
    owner1_points: float
    owner2_points: float
    total_games: int
    
@dataclass
class League:
    """League information"""
    league_id: str
    name: str
    seasons: List[int]
    owners: List[Owner]
    scoring_settings: Dict[str, any]