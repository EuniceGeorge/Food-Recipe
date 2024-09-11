import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

app = Flask(__name__)
#mysql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://naijacrave:crave@localhost/naijacrave'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_name = db.Column(db.String(255), unique=True, nullable=False)
    recipes = db.relationship('Recipe', secondary='ingredient_recipe',back_populates='ingredients')

class Recipe(db.Model):
    __tablename__ = 'recipe'
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.String(255), unique=True, nullable=False)
    ingredients = db.relationship('Ingredient', secondary='ingredient_recipe', back_populates='recipes')
    directions = db.relationship('Direction', back_populates='recipe')

class IngredientRecipe(db.Model):
    __tablename__ = 'ingredient_recipe'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), primary_key=True)

class Direction(db.Model):
    __tablename__ = 'directions'
    direction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    direction = db.Column(db.Text, nullable=False)
    recipe = db.relationship('Recipe', back_populates='directions')

recipe_dict = {}
def add_recipe():
    recipe_name = input("Enter recipe title: ")
    recipe_exist = Recipe.query.filter_by(recipe_name=recipe_name).first()
    if recipe_exist:
        print(f"Recipe '{recipe_name}' already exist")
        return
    else:
        new_recipe = Recipe(recipe_name=recipe_name)
        db.session.add(new_recipe)
        db.session.flush()#to assign a new ID to a recipe

    ingredients_input = input("Enter ingredients (comma-separated): ").split(',')
    ingredient_list = []
    for ingredient_name in ingredients_input:
        ingredient_name = ingredient_name.strip()
        ingredient_exist = Ingredient.query.filter_by(ingredient_name=ingredient_name).first()
        if ingredient_exist:
            print(f"Ingredient '{ingredient_name}' already exist")
            new_recipe.ingredients.append(ingredient_exist)
            #if ingredient exist, it is appended without inserting it as a new record. it skips the insertion and directly associates the existing ingredient with the new recipe.
        else:
            ingredient = Ingredient(ingredient_name=ingredient_name)
            db.session.add(ingredient)
            new_recipe.ingredients.append(ingredient)
            ingredient_list.append(ingredient_name)

    direction_input = input("Enter cooking instructions(separate with ';'): ").split(';')
    direction_list = []
    for direction_text in direction_input:
        direction_text = direction_text.strip()
        if direction_text:
            direction = Direction(direction=direction_text, recipe=new_recipe)
            db.session.add(direction)
            direction_list.append(direction_text)

    db.session.commit()

    recipe_dict[recipe_name] = {
            "ingredients": ingredient_list,
            "directions": direction_list
            }

    print(f"Recipe '{recipe_name}' added successfully!")

def search_recipes():
    search_item = input("Enter ingredients to search (comma-separated): ").split(',')
    search_item = [ing.strip().lower() for ing in search_item]

    # Search for recipes that contain any of the entered ingredients
    recipes = Recipe.query.join(Recipe.ingredients).filter(
            or_(Recipe.ingredients for ing in search_item)).all()

    if recipes:
        print("\nMatching Recipes:")
        for recipe in recipes:
            print("\n" + "=" * 50)
            print(f"\nRecipe: {recipe.recipe_name}")
            print(f"\nIngredients: {', '.join([ing.ingredient_name for ing in recipe.ingredients])}")
            print("\nDirections: ")
            for i, direct in enumerate(recipe.directions, 1):
                print(f"{i}. {direct.direction}")

            print("=" * 50)

    else:
        print("No matching recipes found.")

def main_menu():
    while True:
        print("\n--- Naija Crave Recipe Console ---")
        print("1. Add a new recipe")
        print("2. Search recipes by ingredients")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            add_recipe()
        elif choice == '2':
            search_recipes()
        elif choice == '3':
            print("Thank you for using Naija Crave Recipe Console. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    with app.app_context():
        main_menu()
