#!/usr/bin/env python3
"""
Extract actual manager names from owners pages for 2017-2024.
"""

import os
import sys
import re
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from scraper import NFLFantasyScraper
import pandas as pd

load_dotenv(Path(__file__).parent.parent / '.env')

def extract_owners_data():
    """Extract Team and Manager data from owners pages for all years"""
    
    league_id = os.getenv('LEAGUE_ID')
    session_cookie = os.getenv('NFL_SESSION_COOKIE')
    auth_cookie = os.getenv('NFL_AUTH_COOKIE')
    
    print(f"👥 EXTRACTING OWNERS DATA (2017-2024)")
    print("=" * 60)
    
    cookies = {
        '_gads': session_cookie,
        '_gca': auth_cookie,
        '_gpi': 'UID=0000117c27c7b744:T=1754556041:S=ALNI_MbTkEhLx3OA9t3_7qCYz6k6yQ',
        '_gc_id': 'e88a883e9cbfc44ae8a4ceaef5340169'
    }
    
    scraper = NFLFantasyScraper(league_id=league_id, session_cookies=cookies)
    
    if not scraper.init_driver(headless=True):
        print("❌ Failed to initialize WebDriver")
        return False
        
    try:
        all_owners_data = []
        
        # Extract from each year
        for year in range(2017, 2025):  # 2017-2024
            print(f"\n📅 EXTRACTING {year} OWNERS:")
            print("-" * 40)
            
            owners_url = f"https://fantasy.nfl.com/league/{league_id}/history/{year}/owners"
            
            soup = scraper.load_page(owners_url)
            
            if soup:
                # Extract owners data from the page
                year_owners = extract_owners_from_page(soup, year)
                
                if year_owners:
                    all_owners_data.extend(year_owners)
                    print(f"   ✅ {len(year_owners)} owners extracted")
                    
                    for owner in year_owners:
                        print(f"   📋 {owner['team_name']} -> {owner['manager_name']}")
                else:
                    print(f"   ❌ No owners data found")
            else:
                print(f"   ❌ Failed to load page")
            
            time.sleep(2)  # Rate limiting
        
        # Save all owners data
        if all_owners_data:
            owners_df = pd.DataFrame(all_owners_data)
            
            output_dir = Path("data/actual_owners")
            output_dir.mkdir(exist_ok=True)
            
            # Save complete data
            owners_df.to_csv(output_dir / "owners_2017_2024_complete.csv", index=False)
            
            # Save by year
            for year in range(2017, 2025):
                year_data = owners_df[owners_df['year'] == year]
                if not year_data.empty:
                    year_data.to_csv(output_dir / f"owners_{year}.csv", index=False)
            
            print(f"\n📊 EXTRACTION SUMMARY:")
            print(f"   Total records: {len(all_owners_data)}")
            print(f"   Years covered: {sorted(owners_df['year'].unique())}")
            print(f"   Unique teams: {len(owners_df['team_name'].unique())}")
            print(f"   Unique managers: {len(owners_df['manager_name'].unique())}")
            
            print(f"\n📁 Files saved:")
            print(f"   📄 {output_dir}/owners_2017_2024_complete.csv")
            for year in sorted(owners_df['year'].unique()):
                print(f"   📄 {output_dir}/owners_{year}.csv")
            
            # Show unique managers across all years
            print(f"\n👥 ALL MANAGERS FOUND:")
            unique_managers = sorted(owners_df['manager_name'].unique())
            for manager in unique_managers:
                # Show which years this manager appeared
                manager_years = sorted(owners_df[owners_df['manager_name'] == manager]['year'].unique())
                teams = owners_df[owners_df['manager_name'] == manager]['team_name'].unique()
                print(f"   {manager}: {manager_years} (Teams: {', '.join(teams)})")
            
            return True
        else:
            print(f"❌ No owners data extracted")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        scraper.close_driver()

def extract_owners_from_page(soup, year):
    """Extract team and manager data from an owners page"""
    
    owners_data = []
    
    if not soup:
        return owners_data
    
    # Strategy 1: Look for table structure
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:
                # Look for team name and manager name in cells
                team_cell = None
                manager_cell = None
                
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text().strip()
                    
                    # Skip header rows and empty cells
                    if not cell_text or cell_text in ['Team', 'Manager', 'Owner', 'Record', 'Points']:
                        continue
                    
                    # Look for team names (usually have distinctive patterns)
                    if (3 <= len(cell_text) <= 30 and 
                        not cell_text.isdigit() and
                        not re.match(r'^\d+-\d+-\d+$', cell_text) and  # Records
                        not re.match(r'^\d+\.\d+$', cell_text)):  # Points
                        
                        # Check if this looks like a team name
                        if (any(char.isalpha() for char in cell_text) and
                            cell_text not in ['Email', 'Phone', 'Total']):
                            
                            if team_cell is None:
                                team_cell = cell_text
                            elif manager_cell is None and cell_text != team_cell:
                                manager_cell = cell_text
                
                # If we found both team and manager, save it
                if team_cell and manager_cell:
                    owners_data.append({
                        'year': year,
                        'team_name': team_cell,
                        'manager_name': manager_cell
                    })
    
    # Strategy 2: If table parsing didn't work, try text parsing
    if not owners_data:
        page_text = soup.get_text()
        lines = page_text.split('\n')
        
        potential_teams = []
        potential_managers = []
        
        for line in lines:
            line = line.strip()
            
            # Look for potential team/manager names
            if (3 <= len(line) <= 30 and 
                line and 
                not line.isdigit() and
                not re.match(r'^\d+-\d+-\d+$', line) and
                not re.match(r'^\d+\.\d+$', line) and
                line not in ['Team', 'Manager', 'Owner', 'Record', 'Points', 'Email', 'Total']):
                
                # Categorize as team or manager based on patterns
                if any(keyword in line.lower() for keyword in ['g4ng', 'guru', 'falcon', 'kennels', 'creampies']):
                    potential_teams.append(line)
                elif any(char.isupper() for char in line) and len(line.split()) <= 3:
                    potential_managers.append(line)
        
        # Try to pair teams and managers
        for i in range(min(len(potential_teams), len(potential_managers))):
            owners_data.append({
                'year': year,
                'team_name': potential_teams[i],
                'manager_name': potential_managers[i]
            })
    
    # Remove duplicates
    seen = set()
    unique_owners = []
    for owner in owners_data:
        key = (owner['team_name'], owner['manager_name'])
        if key not in seen:
            seen.add(key)
            unique_owners.append(owner)
    
    return unique_owners

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    if extract_owners_data():
        print(f"\n🏆 OWNERS DATA EXTRACTION COMPLETE!")
    else:
        print(f"\n💥 Extraction failed")