# League of Hard Knox - Fantasy Football Analysis

## Project Overview
Complete 8-year fantasy football league analysis (2017-2024) with head-to-head statistics and manager tracking.

## Key Files

### 📊 Final Datasets
- `data/final_dataset/league_hard_knox_2017_2024_complete.csv` - Complete matchup data with manager names
- `data/final_dataset/team_manager_mapping_final.csv` - Team name to manager mapping
- `data/final_dataset/league_hard_knox_complete_analysis.xlsx` - Comprehensive Excel analysis

### 📈 Analysis Results  
- `data/h2h_analysis/detailed_h2h_records.csv` - Detailed head-to-head records
- `data/h2h_analysis/overall_standings.csv` - Overall manager standings

### 🎨 Interactive Visualizations
- `visualizations/index.html` - **Main dashboard homepage**
- `visualizations/h2h_dashboard.html` - Interactive multi-view dashboard  
- `visualizations/h2h_matrix_heatmap.html` - H2H win percentage heatmap
- `visualizations/overall_standings.html` - 8-year standings chart
- `visualizations/h2h_network.html` - Network analysis of rivalries
- `visualizations/season_performance.html` - Performance trends over time
- `visualizations/rivalry_analysis.html` - Most competitive matchups
- `visualizations/points_analysis.html` - Points for vs against analysis
- `visualizations/matchup_table.html` - Interactive filterable table of all matchups

### 📋 Reference Data
- `data/actual_owners/owners_2017_2024_complete.csv` - Official manager-team mappings by year

## Core Scripts
- `scripts/extract_owners_data.py` - Extract manager data from NFL.com
- `scripts/create_final_dataset_fixed.py` - Create final cleaned dataset
- `scripts/create_h2h_analysis.py` - Generate head-to-head analysis
- `scripts/create_h2h_visualizations.py` - Create interactive visualizations
- `scripts/cleanup_project.py` - Clean up redundant files

## Source Code
- `src/models.py` - Data models (Owner, Matchup classes)
- `src/scraper.py` - Web scraping functionality with Selenium
- `src/storage.py` - CSV/Excel data storage utilities
- `src/analytics.py` - Statistical analysis functions
- `src/extractor.py` - Data extraction utilities

## Key Stats (2017-2024)
- **Total Matchups**: 678
- **Active Managers**: 12  
- **Seasons**: 8 (2017-2024)
- **Top Manager**: Hayden (55.7% win rate)
- **Most Dominant H2H**: Billy vs Phoenix (8-0)
- **Closest Rivalry**: Multiple 50-50 matchups

## Manager Evolution
- **Most Consistent**: Hayden (royalfam - no name changes)
- **Most Changes**: William (4 different team names)
- **Recent Addition**: James (joined 2022 with best recent win %)
