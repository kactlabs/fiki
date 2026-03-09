#!/usr/bin/env python3
"""
Character Fix - Removes special characters from recipe markdown filenames
Usage: python character_fix.py
"""

import os
import glob
import re
import unicodedata


def remove_accents(text):
    """Remove accents and diacritics from text"""
    # Normalize to NFD (decomposed form) and filter out combining characters
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def sanitize_filename(filename):
    """Convert filename to ASCII-safe format without special characters"""
    # Split into parts: number prefix and name
    match = re.match(r'^(\d{3}-)(.+)(\.md)$', filename)
    if not match:
        return filename
    
    prefix, name, extension = match.groups()
    
    # Remove accents and convert to ASCII
    name = remove_accents(name)
    
    # Remove any remaining special characters, keep only alphanumeric and hyphens
    name = re.sub(r'[^\w\s-]', '', name.lower())
    
    # Replace spaces with hyphens and remove multiple hyphens
    name = re.sub(r'[-\s]+', '-', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    return f"{prefix}{name}{extension}"


def fix_filenames():
    """Find and rename all recipe files with special characters"""
    print("=" * 60)
    print("🔧 Character Fix - Removing special characters from filenames")
    print("=" * 60)
    print()
    
    # Get all recipe files
    pattern = '[0-9][0-9][0-9]-*.md'
    files = glob.glob(pattern)
    
    if not files:
        print("📄 No recipe files found")
        return
    
    print(f"📄 Found {len(files)} recipe file(s)")
    print()
    
    renamed_count = 0
    
    for old_filename in sorted(files):
        new_filename = sanitize_filename(old_filename)
        
        if old_filename != new_filename:
            try:
                # Check if target filename already exists
                if os.path.exists(new_filename):
                    print(f"⚠️  Skipping: {old_filename}")
                    print(f"   Target already exists: {new_filename}")
                    print()
                    continue
                
                # Rename the file
                os.rename(old_filename, new_filename)
                print(f"✅ Renamed:")
                print(f"   {old_filename}")
                print(f"   → {new_filename}")
                print()
                renamed_count += 1
                
            except Exception as e:
                print(f"❌ Error renaming {old_filename}: {e}")
                print()
        else:
            print(f"✓  OK: {old_filename}")
    
    print("=" * 60)
    print(f"✨ Renamed {renamed_count} file(s)")
    print("=" * 60)
    
    # Update index.md if any files were renamed
    if renamed_count > 0:
        print()
        print("📚 Updating index.md...")
        try:
            import subprocess
            import sys
            
            result = subprocess.run([sys.executable, "indexer.py"], 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=30)
            if result.returncode == 0:
                print("✅ Index updated successfully!")
            else:
                print(f"⚠️  Warning: indexer.py returned error code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⚠️  Warning: indexer.py timed out")
        except FileNotFoundError:
            print("⚠️  Warning: indexer.py not found")
        except Exception as e:
            print(f"⚠️  Warning: Could not run indexer.py: {e}")
        print("=" * 60)


def main():
    """Main function"""
    fix_filenames()


if __name__ == "__main__":
    main()
