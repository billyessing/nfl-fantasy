# GitHub Pages Deployment Guide

## Quick Setup

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add NFL fantasy league dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/nfl-fantasy.git
   git branch -M main
   git push -u origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your GitHub repository
   - Click **Settings** tab
   - Scroll to **Pages** section
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/docs`
   - Click **Save**

3. **Access your dashboard:**
   - URL will be: `https://YOUR_USERNAME.github.io/nfl-fantasy/`
   - Main dashboard: `https://YOUR_USERNAME.github.io/nfl-fantasy/index.html`

## What's Included

- **Main Dashboard** (`index.html`) - Homepage with links to all visualizations
- **H2H Matrix** (`h2h_matrix_heatmap.html`) - Win percentage heatmap
- **Standings** (`overall_standings.html`) - 8-year standings
- **Interactive Dashboard** (`h2h_dashboard.html`) - Multi-view dashboard
- **Matchup Browser** (`matchup_table.html`) - Filterable table of all games
- **Network Analysis** (`h2h_network.html`) - Rivalry visualization
- **Season Trends** (`season_performance.html`) - Performance over time
- **Points Analysis** (`points_analysis.html`) - Scoring analysis
- **Rivalries** (`rivalry_analysis.html`) - Most competitive matchups

## Updating the Dashboard

To update visualizations after running new analysis:

```bash
# Copy updated visualizations
cp visualizations/* docs/

# Commit changes
git add docs/
git commit -m "Update dashboard with latest data"
git push
```

GitHub Pages will automatically update within a few minutes.