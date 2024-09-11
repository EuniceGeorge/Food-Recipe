import sqlite3
from dataclasses import dataclass

@dataclass
class Ingredient:
    id: int
    name: str

@dataclass
class Recipe:
    id: int
    name: str
    ingredients: list[Ingredient]

class RecipeDatabase:
    def __init__(self, db_name="recipe_finder.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients (id),
            PRIMARY KEY (recipe_id, ingredient_id)
        )
        ''')
        self.conn.commit()

    def add_ingredient(self, name):
        self.cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (name,))
        self.conn.commit()

    def add_recipe(self, name, ingredients):
        self.cursor.execute("INSERT OR IGNORE INTO recipes (name) VALUES (?)", (name,))
        recipe_id = self.cursor.lastrowid
        for ingredient in ingredients:
            self.add_ingredient(ingredient)
            self.cursor.execute("SELECT id FROM ingredients WHERE name=?", (ingredient,))
            ingredient_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)", (recipe_id, ingredient_id))
        self.conn.commit()

    def find_recipes(self, ingredients):
        placeholders = ','.join(['?'] * len(ingredients))
        query = f'''
        SELECT r.id, r.name, COUNT(DISTINCT ri.ingredient_id) as ingredient_count
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE i.name IN ({placeholders})
        GROUP BY r.id
        HAVING ingredient_count >= ?
        ORDER BY ingredient_count DESC
        '''
        self.cursor.execute(query, ingredients + [3])  # Minimum 3 ingredients
        return [Recipe(id=row[0], name=row[1], ingredients=self.get_recipe_ingredients(row[0])) for row in self.cursor.fetchall()]

    def get_recipe_ingredients(self, recipe_id):
        self.cursor.execute('''
        SELECT i.id, i.name
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = ?
        ''', (recipe_id,))
        return [Ingredient(id=row[0], name=row[1]) for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()

def main():
    db = RecipeDatabase()

    # Add some sample recipes
    db.add_recipe("French Toast", ["bread", "egg", "milk", "cinnamon"])
    db.add_recipe("Onion Soup", ["onion", "bread", "cheese", "broth"])
    db.add_recipe("Grilled Cheese", ["bread", "cheese", "butter"])

    while True:
        print("\nRecipe Finder")
        print("1. Find recipes")
        print("2. Add a new recipe")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            ingredients = []
            while len(ingredients) < 3:
                ingredient = input(f"Enter ingredient {len(ingredients) + 1} (or 'done' if finished): ").lower()
                if ingredient == 'done':
                    break
                ingredients.append(ingredient)
            
            if len(ingredients) < 3:
                print("You need to enter at least 3 ingredients to find recipes.")
            else:
                recipes = db.find_recipes(ingredients)
                if recipes:
                    print("\nFound recipes:")
                    for recipe in recipes:
                        print(f"- {recipe.name}")
                        print(f"  Ingredients: {', '.join(ingredient.name for ingredient in recipe.ingredients)}")
                else:
                    print("No recipes found with these ingredients.")

        elif choice == '2':
            name = input("Enter the recipe name: ")
            ingredients = []
            while True:
                ingredient = input("Enter an ingredient (or 'done' if finished): ").lower()
                if ingredient == 'done':
                    break
                ingredients.append(ingredient)
            db.add_recipe(name, ingredients)
            print("Recipe added successfully!")

        elif choice == '3':
            break

        else:
            print("Invalid choice. Please try again.")

    db.close()

if __name__ == "__main__":
    main()
