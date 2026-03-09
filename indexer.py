#!/usr/bin/env python3
"""
Food Wiki Indexer - Updates index.md with all recipe links
Usage: python indexer.py
"""

import os
import glob
import re


def extract_dish_info(filepath):
    """Extract dish name and description from markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract dish name from first # heading
        name_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        dish_name = name_match.group(1).strip() if name_match else os.path.basename(filepath)
        
        # Remove extra brackets from format like "Name ([Origin])" -> "Name (Origin)"
        dish_name = re.sub(r'\(\[(.+?)\]\)', r'(\1)', dish_name)
        
        # Extract first description paragraph (after the heading)
        desc_match = re.search(r'^#.+?\n\n(.+?)(?:\n\n|---)', content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Limit description length
        if len(description) > 100:
            description = description[:97] + "..."
        
        return dish_name, description
    except Exception as e:
        print(f"⚠️  Warning: Could not read {filepath}: {e}")
        return os.path.basename(filepath), ""


def get_all_recipe_files():
    """Get all numbered recipe markdown files (e.g., 001-*.md)"""
    pattern = '[0-9][0-9][0-9]-*.md'
    files = glob.glob(pattern)
    return sorted(files)


def generate_index_content(recipe_files):
    """Generate the index.md content with all recipe links"""
    
    content = "# Food Wiki\n\n"
    content += "Welcome to the Food Wiki! Explore delicious recipes from around the world.\n\n"
    content += "---\n\n"
    content += "## Recipes\n\n"
    
    if not recipe_files:
        content += "*No recipes available yet. Run `python business.py <number>` to generate recipes.*\n"
    else:
        for filepath in recipe_files:
            dish_name, description = extract_dish_info(filepath)
            
            # Extract the index number from filename (e.g., 001 from 001-dish.md)
            index_match = re.match(r'^(\d{3})-', filepath)
            index_num = int(index_match.group(1)) if index_match else 0
            
            # Create simple list entry: index. dish name (no dash)
            content += f"{index_num}. [{dish_name}]({filepath})\n"
    
    content += "\n---\n\n"
    content += f"*Total Recipes: {len(recipe_files)}*\n"
    
    return content


def update_index():
    """Update index.md with all recipe links"""
    print("=" * 60)
    print("📚 Food Wiki Indexer")
    print("=" * 60)
    print()
    
    # Get all recipe files
    recipe_files = get_all_recipe_files()
    print(f"📄 Found {len(recipe_files)} recipe file(s)")
    
    if recipe_files:
        for f in recipe_files:
            print(f"   • {f}")
        print()
    
    # Generate index content
    index_content = generate_index_content(recipe_files)
    
    # Write to index.md
    try:
        with open('index.md', 'w', encoding='utf-8') as f:
            f.write(index_content)
        print("✅ Successfully updated index.md")
    except Exception as e:
        print(f"❌ Error writing index.md: {e}")
        return False
    
    print("=" * 60)
    return True


def main():
    """Main function"""
    success = update_index()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
