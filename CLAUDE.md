# NFL Fantasy League Data Scraper - Claude Context

## Project Overview

This is a Python application that scrapes historical fantasy football data from NFL.com and generates comprehensive analytics for fantasy leagues. The project was built to analyze the "League of Hard Knox" fantasy league with 12 teams across multiple seasons.

## Current Status

**✅ COMPLETED FEATURES:**
- Web scraping engine with Chrome WebDriver and session cookie authentication
- Data extraction for team rosters and league standings
- Owner-centric data model that handles team name changes across seasons
- CSV and Excel data storage with proper data structures
- Complete analytics engine with win percentages, head-to-head records, points analysis
- Successfully extracted 12 teams from League of Hard Knox (2023-2024 seasons)
- Clean, organized project structure with proper documentation

**✅ REAL DATA EXTRACTED:**
- Successfully extracts actual game records (7-7-0, 10-4-0, etc.) and points (628.0, 779.9, etc.)
- Working for completed seasons 2023-2024 with real fantasy performance data
- Analytics working on real data: win percentages, points leaders, championships

**⚠️ CURRENT LIMITATIONS:**
- Limited to a subset of teams (3 out of 12 total league members extracted so far)
- No individual matchup data yet (weekly head-to-head games)
- No visualization dashboard yet (data is exported to Excel)

## Key Technical Details

### Authentication Method
- Uses session cookies extracted from browser dev tools
- Primary cookies: `_gads`, `_gca`, `_gpi`, `_gc_id`
- League ID: 5224652 for League of Hard Knox
- Authentication is working successfully

### Data Structure Discovered
- ❌ Wrong URL: `https://fantasy.nfl.com/league/{league_id}?season={year}&view=standings` (returns 0-0-0 records)
- ✅ Correct URL: `https://fantasy.nfl.com/league/{league_id}/history/{year}/standings` (returns real data)
- Real data found via text parsing: records like "7-7-0", "10-4-0" and points like "779.86", "737.46"
- Completed seasons have actual game results, current season shows placeholder data

### Core Architecture
```
src/
├── models.py      # Owner, Team, Matchup, SeasonRecord data classes
├── scraper.py     # Chrome WebDriver + NFL.com interaction
├── extractor.py   # HTML parsing and data extraction logic  
├── storage.py     # CSV/Excel file management
└── analytics.py   # Win %, head-to-head, points analysis
```

### League Data Extracted
**Teams (12 total):**
- Bijan Mustardson, Slippery Gypsies, royalfam, The Guru, Bad Newz Kennels
- Captain Falcon, L G4ng, Creampies, YungSauvages, King JuJu, JerrysWrld, LetsRide

**Data Files Created:**
- `data/league_of_hard_knox_real/owners.csv` - Team owner mappings
- `data/league_of_hard_knox_real/season_records.csv` - Season standings
- `data/league_of_hard_knox_real/league_of_hard_knox_data.xlsx` - Excel export

## Usage Instructions

### Quick Start
```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Test connectivity 
python main.py

# Full data extraction
python scripts/extract_with_better_parsing.py
```

### Configuration Required
- Copy `.env.example` to `.env`
- Add NFL.com session cookies from browser dev tools
- League ID already configured (5224652)

## Next Development Priorities

1. **Extract Actual Game Data** - Currently getting team rosters but need matchup scores
2. **Build Visualization Dashboard** - Charts, graphs, interactive reports  
3. **Improve Error Handling** - Better retry logic and graceful failures
4. **Historical Data Expansion** - Try to get more seasons of data

## Key Insights for Future Development

### Matchup Data Challenge
The current extraction gets team standings but shows 0-0-0 records, indicating either:
- Games haven't been played yet (current season)
- Need different URL patterns for historical game data
- Matchup data might be on separate pages (schedule view vs standings view)

### NFL.com Structure Notes
- Uses heavy JavaScript rendering (requires Selenium, not just requests)
- Different URL patterns for different data types
- Authentication required for private league access
- Rate limiting recommended (2 second delays implemented)

### Data Model Design
- Owner-centric design handles team name changes across seasons
- Separation of Owner (persistent) vs Team (seasonal) entities
- Designed for head-to-head matchup analysis and historical tracking

## Files to Understand the Project

**Core Logic:**
- `src/scraper.py` - Web scraping and NFL.com interaction
- `src/extractor.py` - Data parsing and processing
- `src/analytics.py` - Statistical calculations and insights

**Working Examples:**
- `scripts/extract_with_better_parsing.py` - Successful data extraction
- `main.py` - Simple connectivity test

**Data:**
- `data/league_of_hard_knox_real/` - Successfully extracted league data

This project demonstrates a complete end-to-end fantasy sports analytics pipeline with real-world data extraction challenges and solutions.