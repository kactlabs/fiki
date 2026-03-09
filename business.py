#!/usr/bin/env python3
"""
Food Wiki Generator - Creates random food recipe markdown files
Usage: python business.py <number_of_recipes>
Example: python business.py 3
"""

import sys
import os
import re
from llm import get_llm


def sanitize_filename(name):
    """Convert recipe name to valid filename format"""
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s-]', '', name.lower())
    # Replace spaces with hyphens
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-')


def generate_recipe(llm, recipe_number):
    """Generate a single random recipe using LLM"""
    
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
Do NOT include any explanatory text before or after the recipe. Output ONLY the markdown recipe."""

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
    
    # Initialize LLM
    try:
        llm = get_llm()
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        sys.exit(1)
    
    # Generate recipes
    created_files = []
    for i in range(1, num_recipes + 1):
        recipe_content = generate_recipe(llm, i)
        
        if recipe_content:
            filename = save_recipe(recipe_content, i)
            if filename:
                created_files.append(filename)
        
        print()  # Blank line between recipes
    
    # Summary
    print("=" * 60)
    print(f"✨ Successfully created {len(created_files)} recipe file(s):")
    for filename in created_files:
        print(f"   📄 {filename}")
    print("=" * 60)


if __name__ == "__main__":
    main()
