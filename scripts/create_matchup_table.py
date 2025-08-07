#!/usr/bin/env python3
"""
Create interactive table visualization for all matchups with filtering.
"""

import pandas as pd
from pathlib import Path
import json

def create_matchup_table():
    """Create interactive filterable table of all matchups"""
    
    print("📋 CREATING INTERACTIVE MATCHUP TABLE")
    print("=" * 50)
    
    # Load the final dataset
    data_dir = Path("data/final_dataset")
    matchups_df = pd.read_csv(data_dir / "league_hard_knox_2017_2024_complete.csv")
    
    print(f"📊 Loaded {len(matchups_df)} matchups")
    
    # Filter to active managers only
    active_managers = ['Hayden', 'Michael', 'Phoenix', 'Billy', 'Robbie', 'Nelson', 
                      'Fraser', 'Justin', 'Angus', 'Nic', 'William', 'James']
    
    current_matchups = matchups_df[
        matchups_df['manager1'].isin(active_managers) &
        matchups_df['manager2'].isin(active_managers)
    ].copy()
    
    print(f"🎯 Filtered to {len(current_matchups)} matchups between active managers")
    
    # Enhance the data for better table display
    current_matchups['margin'] = abs(current_matchups['team1_score'] - current_matchups['team2_score'])
    current_matchups['total_points'] = current_matchups['team1_score'] + current_matchups['team2_score']
    current_matchups['high_scoring'] = current_matchups['total_points'] >= 240
    current_matchups['blowout'] = current_matchups['margin'] >= 30
    current_matchups['close_game'] = current_matchups['margin'] <= 10
    
    # Add era classification
    def get_era(season):
        if season <= 2019:
            return "Early Era (2017-2019)"
        elif season <= 2021:
            return "Middle Era (2020-2021)" 
        else:
            return "Recent Era (2022-2024)"
    
    current_matchups['era'] = current_matchups['season'].apply(get_era)
    
    # Add week type
    current_matchups['week_type'] = current_matchups['playoff'].apply(
        lambda x: 'Playoff' if x else 'Regular Season'
    )
    
    # Sort by most recent first
    current_matchups = current_matchups.sort_values(['season', 'week'], ascending=[False, False])
    
    # Create the interactive HTML table
    create_interactive_html_table(current_matchups)
    
    print(f"✅ Interactive table created: visualizations/matchup_table.html")
    return True

def create_interactive_html_table(df):
    """Create HTML table with advanced filtering and sorting"""
    
    # Prepare data for JavaScript
    table_data = []
    for _, row in df.iterrows():
        table_data.append({
            'season': int(row['season']),
            'week': int(row['week']),
            'era': row['era'],
            'week_type': row['week_type'],
            'team1': row['team1'],
            'manager1': row['manager1'],
            'team1_score': round(row['team1_score'], 2),
            'team2': row['team2'],
            'manager2': row['manager2'], 
            'team2_score': round(row['team2_score'], 2),
            'winner': row['winner'] if pd.notna(row['winner']) else 'Tie',
            'winning_manager': row['winning_manager'] if pd.notna(row['winning_manager']) else 'Tie',
            'margin': round(row['margin'], 2),
            'total_points': round(row['total_points'], 2),
            'high_scoring': row['high_scoring'],
            'blowout': row['blowout'],
            'close_game': row['close_game']
        })
    
    # Get unique values for filter dropdowns
    seasons = sorted(df['season'].unique(), reverse=True)
    managers = sorted(df['manager1'].unique())
    eras = df['era'].unique()
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matchup Browser - League of Hard Knox</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .controls {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .filter-group label {{
            font-size: 0.9em;
            font-weight: 600;
            color: #495057;
        }}
        
        .filter-group select,
        .filter-group input {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 0.9em;
            min-width: 120px;
        }}
        
        .stats-bar {{
            padding: 15px 30px;
            background: #e9ecef;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .stat {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #495057;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 70vh;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        th {{
            background: #495057;
            color: white;
            padding: 12px 8px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{
            background: #343a40;
        }}
        
        th.sortable::after {{
            content: ' ⇅';
            opacity: 0.5;
        }}
        
        th.sort-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        
        th.sort-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
        
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:nth-child(even) {{
            background-color: #f5f5f5;  /* Light grey instead of light blue-grey */
        }}
        
        tr:hover {{
            background-color: #e3f2fd;
        }}
        
        .score {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .winner {{
            background: #d4edda;
            color: #155724;
            font-weight: bold;
        }}
        
        .high-scoring {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .blowout {{
            background: #ffe6e6;  /* Lighter red background */
            color: #721c24;
        }}
        
        .close-game {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge {{
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .badge-playoff {{
            background: #ffc107;
            color: #212529;
        }}
        
        .badge-regular {{
            background: #6c757d;
            color: white;
        }}
        
        .manager-name {{
            font-weight: 600;
            color: #495057;
        }}
        
        .team-name {{
            font-size: 0.85em;
            color: #6c757d;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }}
        
        .clear-filters {{
            padding: 8px 16px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        
        .clear-filters:hover {{
            background: #c82333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏈 Matchup Browser</h1>
            <p>League of Hard Knox • 2017-2024 • Interactive Matchup Explorer</p>
        </div>
        
        <div class="controls">
            <div class="filter-group">
                <label>Season</label>
                <select id="seasonFilter">
                    <option value="">All Seasons</option>
                    {' '.join([f'<option value="{season}">{season}</option>' for season in seasons])}
                </select>
            </div>
            
            <div class="filter-group">
                <label>Era</label>
                <select id="eraFilter">
                    <option value="">All Eras</option>
                    {' '.join([f'<option value="{era}">{era}</option>' for era in eras])}
                </select>
            </div>
            
            <div class="filter-group">
                <label>Manager</label>
                <select id="managerFilter">
                    <option value="">All Managers</option>
                    {' '.join([f'<option value="{manager}">{manager}</option>' for manager in managers])}
                </select>
            </div>
            
            <div class="filter-group">
                <label>Week Type</label>
                <select id="weekTypeFilter">
                    <option value="">All Weeks</option>
                    <option value="Regular Season">Regular Season</option>
                    <option value="Playoff">Playoff</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>Game Type</label>
                <select id="gameTypeFilter">
                    <option value="">All Games</option>
                    <option value="high_scoring">High Scoring (240+)</option>
                    <option value="blowout">Blowouts (30+ margin)</option>
                    <option value="close_game">Close Games (≤10 margin)</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>Search</label>
                <input type="text" id="searchFilter" placeholder="Team or manager...">
            </div>
            
            <button class="clear-filters" onclick="clearFilters()">Clear All</button>
        </div>
        
        <div class="stats-bar">
            <div class="stat">
                <span class="stat-value" id="totalMatches">{len(table_data)}</span>
                <span class="stat-label">Total Matches</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="avgPoints">0</span>
                <span class="stat-label">Avg Total Points</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="highScoringCount">0</span>
                <span class="stat-label">High Scoring</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="blowoutCount">0</span>
                <span class="stat-label">Blowouts</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="closeGameCount">0</span>
                <span class="stat-label">Close Games</span>
            </div>
        </div>
        
        <div class="table-container">
            <table id="matchupTable">
                <thead>
                    <tr>
                        <th class="sortable" onclick="sortTable('season')">Season</th>
                        <th class="sortable" onclick="sortTable('week')">Week</th>
                        <th>Type</th>
                        <th>Team 1</th>
                        <th>Manager 1</th>
                        <th class="sortable" onclick="sortTable('team1_score')">Score 1</th>
                        <th>Team 2</th>
                        <th>Manager 2</th>
                        <th class="sortable" onclick="sortTable('team2_score')">Score 2</th>
                        <th>Winner</th>
                        <th class="sortable" onclick="sortTable('margin')">Margin</th>
                        <th class="sortable" onclick="sortTable('total_points')">Total</th>
                        <th onclick="resetSorting()" style="cursor: pointer; color: #dc3545;" title="Reset sorting to default">🔄</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
            <div id="noResults" class="no-results" style="display: none;">
                No matchups found matching your filters.
            </div>
        </div>
    </div>
    
    <script>
        const matchupData = {json.dumps(table_data, indent=2)};
        let filteredData = [...matchupData];
        let sortColumn = 'season';
        let sortDirection = 'desc';
        
        function renderTable(data) {{
            const tbody = document.getElementById('tableBody');
            const noResults = document.getElementById('noResults');
            
            if (data.length === 0) {{
                tbody.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }}
            
            tbody.style.display = '';
            noResults.style.display = 'none';
            
            tbody.innerHTML = data.map(match => 
                '<tr class="' + getRowClass(match) + '">' +
                    '<td>' + match.season + '</td>' +
                    '<td>' + match.week + '</td>' +
                    '<td><span class="badge ' + (match.week_type === 'Playoff' ? 'badge-playoff' : 'badge-regular') + '">' + match.week_type + '</span></td>' +
                    '<td><div class="team-name">' + match.team1 + '</div></td>' +
                    '<td><span class="manager-name">' + match.manager1 + '</span></td>' +
                    '<td class="score ' + (match.winning_manager === match.manager1 ? 'winner' : '') + '">' + match.team1_score + '</td>' +
                    '<td><div class="team-name">' + match.team2 + '</div></td>' +
                    '<td><span class="manager-name">' + match.manager2 + '</span></td>' +
                    '<td class="score ' + (match.winning_manager === match.manager2 ? 'winner' : '') + '">' + match.team2_score + '</td>' +
                    '<td><span class="manager-name">' + match.winning_manager + '</span></td>' +
                    '<td>' + match.margin + '</td>' +
                    '<td class="' + (match.high_scoring ? 'high-scoring' : '') + '">' + match.total_points + '</td>' +
                '</tr>'
            ).join('');
            
            updateStats(data);
        }}
        
        function getRowClass(match) {{
            if (match.blowout) return 'blowout';
            if (match.close_game) return 'close-game';
            return '';
        }}
        
        function updateStats(data) {{
            document.getElementById('totalMatches').textContent = data.length;
            
            if (data.length > 0) {{
                const avgPoints = data.reduce((sum, m) => sum + m.total_points, 0) / data.length;
                document.getElementById('avgPoints').textContent = avgPoints.toFixed(1);
                
                document.getElementById('highScoringCount').textContent = 
                    data.filter(m => m.high_scoring).length;
                document.getElementById('blowoutCount').textContent = 
                    data.filter(m => m.blowout).length;
                document.getElementById('closeGameCount').textContent = 
                    data.filter(m => m.close_game).length;
            }} else {{
                document.getElementById('avgPoints').textContent = '0';
                document.getElementById('highScoringCount').textContent = '0';
                document.getElementById('blowoutCount').textContent = '0';
                document.getElementById('closeGameCount').textContent = '0';
            }}
        }}
        
        function applyFilters() {{
            const season = document.getElementById('seasonFilter').value;
            const era = document.getElementById('eraFilter').value;
            const manager = document.getElementById('managerFilter').value;
            const weekType = document.getElementById('weekTypeFilter').value;
            const gameType = document.getElementById('gameTypeFilter').value;
            const search = document.getElementById('searchFilter').value.toLowerCase();
            
            filteredData = matchupData.filter(match => {{
                if (season && match.season.toString() !== season) return false;
                if (era && match.era !== era) return false;
                if (manager && match.manager1 !== manager && match.manager2 !== manager) return false;
                if (weekType && match.week_type !== weekType) return false;
                if (gameType && !match[gameType]) return false;
                if (search && !matchesSearch(match, search)) return false;
                return true;
            }});
            
            sortData();
            renderTable(filteredData);
        }}
        
        function matchesSearch(match, search) {{
            return (
                match.team1.toLowerCase().includes(search) ||
                match.team2.toLowerCase().includes(search) ||
                match.manager1.toLowerCase().includes(search) ||
                match.manager2.toLowerCase().includes(search) ||
                match.winning_manager.toLowerCase().includes(search)
            );
        }}
        
        function sortTable(column) {{
            if (sortColumn === column) {{
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            }} else {{
                sortColumn = column;
                sortDirection = column === 'season' ? 'desc' : 'asc';
            }}
            
            // Update sort indicators
            document.querySelectorAll('th').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            
            const currentTh = event.target;
            currentTh.classList.add(sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
            
            sortData();
            renderTable(filteredData);
        }}
        
        function sortData() {{
            filteredData.sort((a, b) => {{
                let aVal = a[sortColumn];
                let bVal = b[sortColumn];
                
                if (typeof aVal === 'string') {{
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }}
                
                if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
                return 0;
            }});
        }}
        
        function clearFilters() {{
            document.getElementById('seasonFilter').value = '';
            document.getElementById('eraFilter').value = '';
            document.getElementById('managerFilter').value = '';
            document.getElementById('weekTypeFilter').value = '';
            document.getElementById('gameTypeFilter').value = '';
            document.getElementById('searchFilter').value = '';
            applyFilters();
        }}
        
        // Event listeners
        document.getElementById('seasonFilter').addEventListener('change', applyFilters);
        document.getElementById('eraFilter').addEventListener('change', applyFilters);
        document.getElementById('managerFilter').addEventListener('change', applyFilters);
        document.getElementById('weekTypeFilter').addEventListener('change', applyFilters);
        document.getElementById('gameTypeFilter').addEventListener('change', applyFilters);
        document.getElementById('searchFilter').addEventListener('input', applyFilters);
        
        // Initial render
        sortData();
        renderTable(filteredData);
    </script>
</body>
</html>'''
    
    # Save the HTML file
    viz_dir = Path("visualizations")
    with open(viz_dir / "matchup_table.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    create_matchup_table()