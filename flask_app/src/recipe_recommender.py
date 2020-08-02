import pandas as pd
from numpy import sum as numpySum
from sklearn.preprocessing import MultiLabelBinarizer

def recipe_recommender(user_input:set, max_recipes=15):
    """
    INPUT:
    user_input - set, ingredients the user is searching for
    max_recipes - Maximal number of recipes that will be returned

    OUTPUT:
    List of lists with the {max_recipes} most similar recipes, based on user ingredients
    """

    def calc_jaccard_index(a:pd.Series):
        """
        Function to be called by df.apply, to be applied on all one hit encoded rows. Calculates the Jaccard index
        (divides the size of intersection by the size of the union).
        Takes into account the "user_input" with ingredients the user is searching for.

        INPUT:
        Pandas Series

        RETURNS:
        Jaccard Index (integer between 0 and 1)
        """

        all_ingredients = recipes.loc[ a.name ].ingredients  # ingredients for each onehotencoded row (recipe)
        union = user_input.union(all_ingredients) # union of user ingredients and recipe ingredients
        intersection = 0 # intersection between user and recipe ingredients
        for i in user_input:
            if i in a:
                intersection = intersection + a[i]

        len_union = len(union)
        if len_union == 0:
            len_union = 0.001
        jaccard = intersection / len_union
        # Alpha punishes ingredients NOT in common. A higher Alpha makes recipes shorter and better fits.
        ALPHA = 0.07
        jaccard = jaccard - (len(all_ingredients) - intersection) * ALPHA
        return jaccard

    DEFAULT_ING = ["Salz", "Pfeffer", "Wasser"]
    recipes = pd.read_csv("flask_app/data/recipes5_4170_translated.csv", converters={'ingredients': eval, 'categories': eval}, index_col=0)
    ## Read data from pickle-file
    #recipes = pd.read_pickle("flask_app/data/recipes4_4170.pickle")

    mlb = MultiLabelBinarizer()
    recipes_onehot = pd.DataFrame(mlb.fit_transform(recipes["ingredients"]), columns=mlb.classes_, index=recipes.index)

    # Delete default ingredients (salt etc.)
    # 1) from one hot encoded:
    recipes_onehot = recipes_onehot.drop(DEFAULT_ING, 1)
    # 2) from recipes df:
    def discard_defaults(a):
        for i in DEFAULT_ING:
            a.discard(i)
    recipes.ingredients.apply(discard_defaults)

    ## Create and save list of most used ingredients
    # most_used_ingredients = recipes_onehot.mean().sort_values(ascending=False).head(20)
    # with open("../most_used_ingredients.txt", "w") as f:
    #     for i in sorted(most_used_ingredients.index):
    #         f.write(i)
    #         f.write("\n")

    recipes_onehot["number_of_ingredients"] = recipes_onehot.apply(numpySum, 1)
    recipes_onehot["jaccard"] = recipes_onehot.apply(calc_jaccard_index, 1)

    top_recipes = recipes_onehot.jaccard.sort_values(ascending=False)[:max_recipes]
    print("Top recipes:\n\n", top_recipes)

    if top_recipes[0] != 0.0:
        list_of_series = []
        for i in top_recipes.index:
            list_of_series.append(recipes.loc[i])
        list_of_lists = []
        for c, i in enumerate(list_of_series):
            list_of_lists.append([i.name, i.description, i.ingredients, i.url, top_recipes[c].round(2)])
        return list_of_lists
    else:
        return None
