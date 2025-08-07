import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from models import Owner, Matchup, SeasonRecord, Roster
from scraper import NFLFantasyScraper
import logging

class FantasyDataExtractor:
    """Extracts and processes fantasy league data from NFL.com"""
    
    def __init__(self, scraper: NFLFantasyScraper):
        self.scraper = scraper
        self.logger = logging.getLogger(__name__)
        self.owner_mapping = {}  # Maps team names to consistent owner IDs
        
    def extract_all_league_data(self, seasons: List[int]) -> Dict:
        """Extract complete league data for specified seasons"""
        league_data = {
            'owners': {},
            'teams': {},
            'matchups': [],
            'season_records': [],
            'rosters': []
        }
        
        # First, build owner mapping from all seasons
        self._build_owner_mapping(seasons)
        
        for season in seasons:
            self.logger.info(f"Extracting data for season {season}")
            
            # Extract season standings to get records
            standings = self.scraper.extract_season_standings(season)
            season_records = self._process_season_standings(standings, season)
            league_data['season_records'].extend(season_records)
            
            # Extract matchups for each week (typically 17 regular season weeks + playoffs)
            for week in range(1, 18):  # Regular season weeks
                matchups = self._extract_weekly_matchups(season, week)
                league_data['matchups'].extend(matchups)
            
            # Extract playoff matchups if available
            playoff_matchups = self._extract_playoff_matchups(season)
            league_data['matchups'].extend(playoff_matchups)
        
        # Convert owner mapping to Owner objects
        for owner_id, owner_info in self.owner_mapping.items():
            league_data['owners'][owner_id] = Owner(
                owner_id=owner_id,
                name=owner_info['name'],
                email=owner_info.get('email')
            )
        
        return league_data
    
    def _build_owner_mapping(self, seasons: List[int]):
        """Build mapping of team names to consistent owner IDs across seasons"""
        owner_names_seen = set()
        
        for season in seasons:
            standings = self.scraper.extract_season_standings(season)
            
            for standing in standings:
                team_name = standing.get('team_name', '').strip()
                if not team_name:
                    continue
                
                # Extract owner name from team name (usually format: "Team Name (Owner Name)")
                owner_name = self._extract_owner_name_from_team(team_name)
                
                if owner_name and owner_name not in owner_names_seen:
                    owner_id = self._generate_owner_id(owner_name)
                    self.owner_mapping[owner_id] = {
                        'name': owner_name,
                        'team_names': {season: team_name}
                    }
                    owner_names_seen.add(owner_name)
                elif owner_name:
                    # Find existing owner and add team name for this season
                    for owner_id, owner_info in self.owner_mapping.items():
                        if owner_info['name'] == owner_name:
                            owner_info['team_names'][season] = team_name
                            break
    
    def _extract_owner_name_from_team(self, team_name: str) -> str:
        """Extract owner name from team name"""
        # Common formats:
        # "Team Name (Owner Name)"
        # "Owner Name's Team"
        # "Team Name - Owner Name"
        
        # Try parentheses format first
        paren_match = re.search(r'\(([^)]+)\)', team_name)
        if paren_match:
            return paren_match.group(1).strip()
        
        # Try possessive format
        poss_match = re.search(r"(.+)'s\s+", team_name)
        if poss_match:
            return poss_match.group(1).strip()
        
        # Try dash separator
        dash_match = re.search(r'(.+)\s*-\s*(.+)', team_name)
        if dash_match:
            # Use the shorter part as owner name
            part1, part2 = dash_match.groups()
            return part1.strip() if len(part1) < len(part2) else part2.strip()
        
        # If no pattern matches, use the whole team name
        return team_name.strip()
    
    def _generate_owner_id(self, owner_name: str) -> str:
        """Generate consistent owner ID from name"""
        # Remove special characters and convert to lowercase
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', owner_name.lower())
        return '_'.join(clean_name.split())
    
    def _process_season_standings(self, standings: List[Dict], season: int) -> List[SeasonRecord]:
        """Convert standings data to SeasonRecord objects"""
        season_records = []
        
        for standing in standings:
            team_name = standing.get('team_name', '')
            owner_name = self._extract_owner_name_from_team(team_name)
            owner_id = self._generate_owner_id(owner_name)
            
            # Parse record (format: "10-4-0" or "10-4")
            record = standing.get('record', '0-0-0')
            wins, losses, ties = self._parse_record(record)
            
            season_record = SeasonRecord(
                owner_id=owner_id,
                season=season,
                wins=wins,
                losses=losses,
                ties=ties,
                points_for=float(standing.get('points_for', 0)),
                points_against=float(standing.get('points_against', 0)),
                final_rank=standing.get('rank', 0)
            )
            season_records.append(season_record)
        
        return season_records
    
    def _parse_record(self, record_str: str) -> Tuple[int, int, int]:
        """Parse win-loss-tie record string"""
        try:
            parts = record_str.split('-')
            wins = int(parts[0]) if len(parts) > 0 else 0
            losses = int(parts[1]) if len(parts) > 1 else 0
            ties = int(parts[2]) if len(parts) > 2 else 0
            return wins, losses, ties
        except (ValueError, IndexError):
            return 0, 0, 0
    
    def _extract_weekly_matchups(self, season: int, week: int) -> List[Matchup]:
        """Extract matchup data for a specific week"""
        matchups = []
        
        # Build URL for weekly matchups (this would need to be customized based on actual NFL.com structure)
        url = self.scraper.get_league_url(season, f'schedule?week={week}')
        soup = self.scraper.load_page(url, '.matchup')
        
        if not soup:
            self.logger.warning(f"Could not load matchups for {season} week {week}")
            return matchups
        
        # Extract matchup elements (this would need to be customized based on HTML structure)
        matchup_elements = soup.find_all('div', class_='matchup') or soup.find_all('tr', class_='matchup-row')
        
        for i, elem in enumerate(matchup_elements):
            matchup = self._parse_matchup_element(elem, season, week, i)
            if matchup:
                matchups.append(matchup)
        
        return matchups
    
    def _parse_matchup_element(self, elem: BeautifulSoup, season: int, week: int, index: int) -> Optional[Matchup]:
        """Parse individual matchup element from HTML"""
        try:
            # This would need to be customized based on actual HTML structure
            # Looking for team names and scores
            
            team_elements = elem.find_all('div', class_='team') or elem.find_all('td', class_='team')
            score_elements = elem.find_all('div', class_='score') or elem.find_all('td', class_='score')
            
            if len(team_elements) >= 2 and len(score_elements) >= 2:
                team1_name = team_elements[0].get_text().strip()
                team2_name = team_elements[1].get_text().strip()
                
                team1_score = self._extract_score(score_elements[0].get_text())
                team2_score = self._extract_score(score_elements[1].get_text())
                
                # Map team names to owner IDs
                team1_owner_id = self._get_owner_id_from_team_name(team1_name, season)
                team2_owner_id = self._get_owner_id_from_team_name(team2_name, season)
                
                winner_owner_id = None
                if team1_score > team2_score:
                    winner_owner_id = team1_owner_id
                elif team2_score > team1_score:
                    winner_owner_id = team2_owner_id
                
                return Matchup(
                    matchup_id=f"{season}_{week}_{index}",
                    season=season,
                    week=week,
                    team1_owner_id=team1_owner_id,
                    team2_owner_id=team2_owner_id,
                    team1_score=team1_score,
                    team2_score=team2_score,
                    winner_owner_id=winner_owner_id,
                    playoff=week > 17
                )
        
        except Exception as e:
            self.logger.error(f"Error parsing matchup element: {e}")
        
        return None
    
    def _extract_score(self, score_text: str) -> float:
        """Extract numeric score from text"""
        try:
            # Remove non-numeric characters except decimal point
            cleaned = re.sub(r'[^\d.]', '', score_text)
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def _get_owner_id_from_team_name(self, team_name: str, season: int) -> str:
        """Get owner ID from team name for a specific season"""
        owner_name = self._extract_owner_name_from_team(team_name)
        return self._generate_owner_id(owner_name)
    
    def _extract_playoff_matchups(self, season: int) -> List[Matchup]:
        """Extract playoff matchup data"""
        playoff_matchups = []
        
        # Playoff weeks typically start at week 15-17 depending on league settings
        playoff_weeks = [15, 16, 17]  # Championship typically week 17
        
        for week in playoff_weeks:
            weekly_matchups = self._extract_weekly_matchups(season, week)
            for matchup in weekly_matchups:
                matchup.playoff = True
            playoff_matchups.extend(weekly_matchups)
        
        return playoff_matchups
    
    def extract_roster_data(self, season: int, week: int) -> List[Roster]:
        """Extract roster data for all teams in a specific week"""
        rosters = []
        
        # This would require navigating to each team's roster page
        # Implementation would depend on NFL.com structure
        self.logger.info(f"Roster extraction for {season} week {week} - placeholder")
        
        return rosters