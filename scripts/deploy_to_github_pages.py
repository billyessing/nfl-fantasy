#!/usr/bin/env python3
"""
Deploy visualizations to GitHub Pages docs folder.
"""

import shutil
from pathlib import Path
import subprocess
import sys

def deploy_to_docs():
    """Copy visualizations to docs folder for GitHub Pages"""
    
    print("📂 DEPLOYING TO GITHUB PAGES")
    print("=" * 40)
    
    # Paths
    viz_dir = Path("visualizations")
    docs_dir = Path("docs")
    
    if not viz_dir.exists():
        print("❌ Error: visualizations folder not found")
        return False
    
    # Create docs directory if it doesn't exist
    docs_dir.mkdir(exist_ok=True)
    
    # Copy all files from visualizations to docs
    print(f"📋 Copying files from {viz_dir} to {docs_dir}")
    
    copied_files = []
    for file_path in viz_dir.glob("*.html"):
        dest_path = docs_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        copied_files.append(file_path.name)
        print(f"   ✅ {file_path.name}")
    
    print(f"\n🎉 Successfully copied {len(copied_files)} files to docs/")
    
    # Show next steps
    print("\n📋 NEXT STEPS:")
    print("1. git add .")
    print('2. git commit -m "Deploy dashboard to GitHub Pages"')
    print("3. git push")
    print("\n🌐 Your dashboard will be available at:")
    print("   https://YOUR_USERNAME.github.io/REPO_NAME/")
    
    return True

if __name__ == "__main__":
    success = deploy_to_docs()
    sys.exit(0 if success else 1)