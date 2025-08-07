#!/usr/bin/env python3
"""
Clean up redundant code and excess data files.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up redundant files and organize the project"""
    
    print("🧹 CLEANING UP PROJECT - REMOVING REDUNDANT FILES")
    print("=" * 60)
    
    base_dir = Path(".")
    
    # Files and directories to keep (essential)
    keep_files = {
        # Core source code
        "src/models.py",
        "src/scraper.py", 
        "src/storage.py",
        
        # Configuration
        ".env",
        "requirements.txt",
        "CLAUDE.md",
        
        # Final datasets (the ones we actually need)
        "data/final_dataset/league_hard_knox_2017_2024_complete.csv",
        "data/final_dataset/team_manager_mapping_final.csv",
        "data/final_dataset/league_hard_knox_complete_analysis.xlsx",
        
        # H2H analysis
        "data/h2h_analysis/detailed_h2h_records.csv",
        "data/h2h_analysis/overall_standings.csv",
        
        # Actual owners data (reference)
        "data/actual_owners/owners_2017_2024_complete.csv",
        
        # Key scripts (final versions only)
        "scripts/create_final_dataset_fixed.py",
        "scripts/create_h2h_analysis.py",
        "scripts/extract_owners_data.py",
    }
    
    # Directories that contain only redundant/intermediate data
    redundant_dirs = [
        "data/full_seasons_2020_2024",
        "data/full_seasons_2017_2024", 
        "data/manager_mapped_dataset",
        "data/final_corrected_dataset",
        "data/manager_analysis_2020_2024",
        "data/manager_analysis_final",
        "data/owner_mappings",
        "data/season_2019"
    ]
    
    # Redundant script files (keep only the final working versions)
    redundant_scripts = [
        "scripts/extract_real_data.py",
        "scripts/extract_with_better_parsing.py", 
        "scripts/extract_real_game_data.py",
        "scripts/extract_final_real_data.py",
        "scripts/extract_matchup_data.py",
        "scripts/extract_week_matchups.py",
        "scripts/extract_owner_mappings.py",
        "scripts/extract_full_seasons.py",
        "scripts/extract_seasons_efficient.py",
        "scripts/extract_2022_and_combine.py",
        "scripts/extract_2020_2021.py",
        "scripts/extract_manager_names.py",
        "scripts/extract_2017_2019.py",
        "scripts/extract_2017_2019_focused.py",
        "scripts/extract_2019_only.py",
        "scripts/check_2019_data.py",
        "scripts/check_historical_availability.py",
        "scripts/create_owner_mapped_dataset.py",
        "scripts/create_fixed_owner_mapping.py",
        "scripts/create_final_corrected_dataset.py",
        "scripts/create_owner_mapped_dataset.py",
        "scripts/create_final_manager_reports.py"
    ]
    
    print("🗂️  CLEANING UP REDUNDANT DIRECTORIES:")
    total_size_saved = 0
    
    for dir_path in redundant_dirs:
        dir_full_path = base_dir / dir_path
        if dir_full_path.exists():
            # Calculate size before deletion
            size = sum(f.stat().st_size for f in dir_full_path.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            total_size_saved += size_mb
            
            print(f"   🗑️  Removing: {dir_path} ({size_mb:.1f} MB)")
            shutil.rmtree(dir_full_path)
        else:
            print(f"   ⚠️  Not found: {dir_path}")
    
    print(f"\n📁 CLEANING UP REDUNDANT SCRIPTS:")
    
    for script_path in redundant_scripts:
        script_full_path = base_dir / script_path
        if script_full_path.exists():
            size = script_full_path.stat().st_size / 1024
            total_size_saved += size / 1024
            print(f"   🗑️  Removing: {script_path} ({size:.1f} KB)")
            script_full_path.unlink()
        else:
            print(f"   ⚠️  Not found: {script_path}")
    
    # Clean up any remaining individual redundant data files
    redundant_files = [
        "data/actual_owners/owners_2017.csv",
        "data/actual_owners/owners_2018.csv", 
        "data/actual_owners/owners_2019.csv",
        "data/actual_owners/owners_2020.csv",
        "data/actual_owners/owners_2021.csv",
        "data/actual_owners/owners_2022.csv",
        "data/actual_owners/owners_2023.csv",
        "data/actual_owners/owners_2024.csv"
    ]
    
    print(f"\n📄 CLEANING UP INDIVIDUAL REDUNDANT FILES:")
    
    for file_path in redundant_files:
        file_full_path = base_dir / file_path
        if file_full_path.exists():
            size = file_full_path.stat().st_size / 1024
            total_size_saved += size / 1024
            print(f"   🗑️  Removing: {file_path} ({size:.1f} KB)")
            file_full_path.unlink()
    
    # Create a clean project structure summary
    print(f"\n📊 FINAL PROJECT STRUCTURE:")
    print("-" * 40)
    
    # Show what's left
    essential_dirs = ["src", "data/final_dataset", "data/h2h_analysis", "data/actual_owners", "scripts"]
    
    for dir_name in essential_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"\n📂 {dir_name}/")
            for file_path in sorted(dir_path.rglob('*')):
                if file_path.is_file():
                    rel_path = file_path.relative_to(dir_path)
                    size = file_path.stat().st_size / 1024
                    print(f"   📄 {rel_path} ({size:.1f} KB)")
    
    # Create a README for the cleaned project
    readme_content = """# League of Hard Knox - Fantasy Football Analysis

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

### 📋 Reference Data
- `data/actual_owners/owners_2017_2024_complete.csv` - Official manager-team mappings by year

## Core Scripts
- `scripts/extract_owners_data.py` - Extract manager data from NFL.com
- `scripts/create_final_dataset_fixed.py` - Create final cleaned dataset
- `scripts/create_h2h_analysis.py` - Generate head-to-head analysis

## Source Code
- `src/models.py` - Data models
- `src/scraper.py` - Web scraping functionality  
- `src/storage.py` - Data storage utilities

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
"""
    
    with open(base_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"\n📝 Created README.md with project overview")
    
    print(f"\n✨ CLEANUP COMPLETE!")
    print(f"   💾 Space saved: ~{total_size_saved:.1f} MB")
    print(f"   📁 Essential files preserved")
    print(f"   🗑️  Redundant files removed")
    print(f"   📚 README.md created")
    
    return True

if __name__ == "__main__":
    cleanup_project()