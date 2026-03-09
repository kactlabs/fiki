#!/usr/bin/env python3
"""
Food Wiki Generator - Creates random food recipe markdown files
Usage: python business.py <number_of_recipes>
Example: python business.py 3
"""

import sys
import os
import re
import subprocess
import unicodedata
from llm import get_llm


def remove_accents(text):
    """Remove accents and diacritics from text"""
    # Normalize to NFD (decomposed form) and filter out combining characters
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def sanitize_filename(name):
    """Convert recipe name to valid filename format without special characters"""
    # Remove accents and convert to ASCII
    name = remove_accents(name)
    
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s-]', '', name.lower())
    
    # Replace spaces with hyphens
    name = re.sub(r'[-\s]+', '-', name)
    
    return name.strip('-')


def load_existing_dishes():
    """Load existing dish names from unique_dishes.txt"""
    if not os.path.exists('unique_dishes.txt'):
        return []
    
    try:
        with open('unique_dishes.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"⚠️  Warning: Could not read unique_dishes.txt: {e}")
        return []


def save_dish_name(dish_name):
    """Append dish name to unique_dishes.txt"""
    try:
        with open('unique_dishes.txt', 'a', encoding='utf-8') as f:
            f.write(f"{dish_name}\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not save to unique_dishes.txt: {e}")


def generate_recipe(llm, recipe_number, existing_dishes):
    """Generate a single random recipe using LLM"""
    
    # Build exclusion list for prompt
    exclusion_text = ""
    if existing_dishes:
        exclusion_text = f"\n\nDo NOT generate recipes for these dishes (already created):\n" + "\n".join(f"- {dish}" for dish in existing_dishes)
    
    prompt = f"""Generate a complete, detailed recipe for a random international dish. 
The recipe should follow this EXACT markdown format:

/ [Home](index.md)

# [Dish Name] ([Origin/Description])

[Brief 1-2 sentence description of the dish]

---

## Ingredients

### [Category 1]
- [amount] **[ingredient]**
- [amount] **[ingredient]**

### [Category 2]
- [amount] **[ingredient]**

### [Additional categories as needed]

---

## [Dish Name] Sauce (if applicable)

Mix the following:

- [amount] **[ingredient]**
- [amount] **[ingredient]**

---

## Recipe Steps

### 1. [Step Title]
[Detailed instructions for this step]

---

### 2. [Step Title]
[Detailed instructions for this step]

---

[Continue with all necessary steps]

---

## Optional: [Variation Name]

- [Optional variation instructions]

---

Generate a unique, authentic recipe from any world cuisine. Make it detailed and practical.
Do NOT include any explanatory text before or after the recipe. Output ONLY the markdown recipe.{exclusion_text}"""

    try:
        print(f"🍳 Generating recipe {recipe_number}...")
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"❌ Error generating recipe {recipe_number}: {e}")
        return None


def extract_recipe_name(recipe_content):
    """Extract the dish name from the recipe markdown"""
    # Look for the first # heading
    match = re.search(r'^#\s+(.+?)(?:\s+\(|$)', recipe_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return f"recipe-{os.urandom(4).hex()}"


def get_next_index():
    """Get the next available index number by checking existing files"""
    import glob
    
    pattern = '[0-9][0-9][0-9]-*.md'
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    # Extract all index numbers
    indices = []
    for filename in existing_files:
        match = re.match(r'^(\d{3})-', filename)
        if match:
            indices.append(int(match.group(1)))
    
    # Return next index after the highest
    return max(indices) + 1 if indices else 1


def save_recipe(recipe_content, index):
    """Save recipe to a numbered markdown file"""
    # Extract recipe name for filename
    recipe_name = extract_recipe_name(recipe_content)
    filename = f"{index:03d}-{sanitize_filename(recipe_name)}.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(recipe_content)
        print(f"✅ Created: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return None


def main():
    """Main function to generate multiple recipes"""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python business.py <number_of_recipes>")
        print("Example: python business.py 3")
        sys.exit(1)
    
    try:
        num_recipes = int(sys.argv[1])
        if num_recipes <= 0:
            raise ValueError("Number must be positive")
    except ValueError as e:
        print(f"❌ Error: Please provide a valid positive number")
        sys.exit(1)
    
    print("=" * 60)
    print(f"🍽️  Food Wiki Generator - Creating {num_recipes} recipe(s)")
    print("=" * 60)
    print()
    
    # Load existing dishes to avoid duplicates
    existing_dishes = load_existing_dishes()
    if existing_dishes:
        print(f"📋 Loaded {len(existing_dishes)} existing dish(es) to avoid duplicates")
        print()
    
    # Initialize LLM
    try:
        llm = get_llm()
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        sys.exit(1)
    
    # Generate recipes
    created_files = []
    next_index = get_next_index()
    
    for i in range(num_recipes):
        recipe_content = generate_recipe(llm, i + 1, existing_dishes)
        
        if recipe_content:
            # Extract dish name before saving
            dish_name = extract_recipe_name(recipe_content)
            
            # Check if this dish already exists (case-insensitive)
            if any(dish_name.lower() == existing.lower() for existing in existing_dishes):
                print(f"⚠️  Skipping duplicate: {dish_name}")
                print()
                continue
            
            filename = save_recipe(recipe_content, next_index)
            if filename:
                created_files.append(filename)
                # Save dish name to tracking file
                save_dish_name(dish_name)
                existing_dishes.append(dish_name)
                next_index += 1  # Increment for next recipe
        
        print()  # Blank line between recipes
    
    # Summary
    print("=" * 60)
    print(f"✨ Successfully created {len(created_files)} recipe file(s):")
    for filename in created_files:
        print(f"   📄 {filename}")
    print("=" * 60)
    
    # Update index.md automatically
    if created_files:
        print()
        print("📚 Updating index.md...")
        try:
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


if __name__ == "__main__":
    main()
