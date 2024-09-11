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
    ingredient_name = db.Column(db.String(255), nullable=False)
    recipes = db.relationship('Recipe', secondary='ingredient_recipe', back_populates='ingredients')

def __repr__(self):
        return f'<Ingredient {self.ingredient_name}>'

class Recipe(db.Model):
    __tablename__ = 'recipe'
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.String(255), nullable=False)
    ingredients = db.relationship('Ingredient', secondary='ingredient_recipe', back_populates='recipes')
    directions = db.relationship('Direction', back_populates='recipe')

    def __repr__(self):
        return f'<Recipe {self.recipe_name}>'

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

    def __repr__(self):
     return f'<Direction {self.direction}>'
"""    
def add_recipe():
    recipe_name = input("Enter recipe title: ")
    new_recipe = Recipe(recipe_name=recipe_name)
    db.session.add(new_recipe)
    db.session.flush()#to assign a new ID to a recipe

    ingredients_input = input("Enter ingredients (comma-separated): ").split(',')
    for ingredient_name in ingredients_input:
        ingredient_name = ingredient_name.strip()
        ingredient = Ingredient(ingredient_name=ingredient_name)
        db.session.add(ingredient)

        new_recipe.ingredients.append(ingredient)

    direction_input = input("Enter cooking instructions(separate with ';'): ").split(';')
    for direction_text in direction_input:
        direction_text = direction_text.strip()
        if direction_text:
            direction = Direction(direction=direction_text, recipe=new_recipe)
            db.session.add(direction)

    db.session.commit()
    print(f"Recipe '{recipe_name}' added successfully!")

def search_recipes():
    search_item = input("Enter ingredients to search (comma-separated): ").split(',')
    search_item = [ing.strip().lower() for ing in search_item]

    # Search for recipes that contain any of the entered ingredients
    recipes = Recipe.query.join(Recipe.ingredients).filter(
        or_(*[func.lower(Recipe.ingredients).like(f'%{ing}%') for ing in search_item])
    ).all()

    if recipes:
        print("\nMatching Recipes:")
        for recipe in recipes:
            print(f"\nRecipe: {recipe.recipe_name}")
            print(f"Ingredients: {', '.join([ing.ingredient_name for ing in recipe.ingredients])}")
            print(f"Direction: {recipe.directions}")
    else:
        print("No matching recipes found.")

def search_recipes():
    search_item = input("Enter ingredient (separated by ','): ").split(',')
    if search_item:
        recipes = Recipe.query.join(Recipe.ingredients).filter(
                or_(
                    Recipe.recipe_name.ilike(f'%{search_item}%'),
                    Ingredient.ingredient_name.ilike(f'%{search_item}%')
                    )
                ).distinct().all()
    else:
        recipes = Recipe.query.all()

    if not recipes:
        print("No response")
        return

    for recipe in recipes:
        print("\n" + "=" * 20)

        print("\ningredient:")
        for ing in recipe.ingredients:
            print(f"- {ing.ingredient_name}")

        print("\nDirections: ")
        for i, direct in enumerate(recipe.directions, 1):
            print(f"{i}. {direct.direction}")

        print("=" * 20)

        print(f"\nTotal recipes found: {len(recipes)}")

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
        main_menu()"""
