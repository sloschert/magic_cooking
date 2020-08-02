import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_app.src.recipe_recommender import recipe_recommender
import json


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chose_ingredients')
def chose_ingredients():

    most_used_ingredients = []
    list_of_ingredients = []

    with open("flask_app/data/most_used_ingredients.txt", "r") as f:
        for line in f:
            most_used_ingredients.append(line.strip())

    with open("flask_app/data/list_of_ingredients.txt", "r") as f:
        for line in f:
            list_of_ingredients.append(line.strip())

    return render_template('chose_ingredients.html', most_used_ingredients=most_used_ingredients, list_of_ingredients=list_of_ingredients)

@app.route('/results')
def results():
    user_input = dict(request.args)
    user_input_values = list(user_input.values()) #   list(user_input.values())
    # unpack the multiple inputs recieved by the jQuery input-fields
    u1 = [i.split(",") for i in user_input_values]
    u2 = []
    for i in u1:
        for j in i:
            u2.append(j)
    # drop empty entry
    try:
        u2.remove("")
        u2.remove("")
    except:
        pass
    user_ingredients = set(u2)
    recommendations = recipe_recommender(user_ingredients)
    #print(recommendations)
    return render_template('results.html', recommendations=recommendations, user_ingredients=list(user_ingredients))

if __name__== '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port='5000')
