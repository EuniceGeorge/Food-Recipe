import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='naijacrave',
            user='root',
            password=' '
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

def add_ingredient(connection, ingredient_name):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO ingredients (ingredient_name) VALUES (%s)"
        cursor.execute(query, (ingredient_name,))
        connection.commit()
        print(f"Ingredient '{ingredient_name}' added successfully!")
    except Error as e:
        print(f"Error adding ingredient: {e}")

def add_recipe(connection):
    try:
        cursor = connection.cursor()
        
        # Add recipe name
        recipe_name = input("Enter recipe name: ")
        query = "INSERT INTO recipe (recipe_name) VALUES (%s)"
        cursor.execute(query, (recipe_name,))
        recipe_id = cursor.lastrowid
        
        # Add ingredients
        while True:
            ingredient = input("Enter an ingredient (or press enter to finish): ")
            if not ingredient:
                break
            
            # Check if ingredient exists, if not add it
            cursor.execute("SELECT ingredient_id FROM ingredients WHERE ingredient_name = %s", (ingredient,))
            result = cursor.fetchone()
            if result:
                ingredient_id = result[0]
            else:
                add_ingredient(connection, ingredient)
                cursor.execute("SELECT LAST_INSERT_ID()")
                ingredient_id = cursor.fetchone()[0]
            
            # Link ingredient to recipe
            cursor.execute("INSERT INTO ingredient_recipe (recipe_id, ingredient_id) VALUES (%s, %s)", 
                           (recipe_id, ingredient_id))
        
        # Add directions
        print("Enter cooking directions (press Enter twice to finish):")
        directions = []
        while True:
            line = input()
            if line:
                directions.append(line)
            else:
                break
        directions_text = "\n".join(directions)
        cursor.execute("INSERT INTO directions (recipe_id, direction) VALUES (%s, %s)", 
                       (recipe_id, directions_text))
        
        connection.commit()
        print(f"Recipe '{recipe_name}' added successfully!")
    except Error as e:
        print(f"Error adding recipe: {e}")

def search_recipes(connection):
    ingredients = input("Enter ingredients to search (comma-separated): ").split(',')
    ingredients = [ing.strip() for ing in ingredients]
    
    try:
        cursor = connection.cursor(dictionary=True)
        placeholders = ', '.join(['%s'] * len(ingredients))
        query = f"""
        SELECT DISTINCT r.recipe_name, d.direction
        FROM recipe r
        JOIN ingredient_recipe ir ON r.recipe_id = ir.recipe_id
        JOIN ingredients i ON ir.ingredient_id = i.ingredient_id
        JOIN directions d ON r.recipe_id = d.recipe_id
        WHERE i.ingredient_name IN ({placeholders})
        """
        cursor.execute(query, tuple(ingredients))
        recipes = cursor.fetchall()
        
        if recipes:
            print("\nMatching Recipes:")
            for recipe in recipes:
                print(f"\nRecipe: {recipe['recipe_name']}")
                print(f"Directions: {recipe['direction']}")
        else:
            print("No matching recipes found.")
    except Error as e:
        print(f"Error searching recipes: {e}")

def main_menu():
    connection = create_connection()
    if not connection:
        return

    while True:
        print("\n--- Naija Crave Recipe Console ---")
        print("1. Add a new recipe")
        print("2. Search recipes by ingredients")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            add_recipe(connection)
        elif choice == '2':
            search_recipes(connection)
        elif choice == '3':
            print("Thank you for using Naija Crave Recipe Console. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    if connection.is_connected():
        connection.close()

if __name__ == '__main__':
    main_menu()