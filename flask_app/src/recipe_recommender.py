import pandas as pd
from numpy import sum as numpySum
from sklearn.preprocessing import MultiLabelBinarizer

def recipe_recommender(user_input:set, max_recipes=7):
    """
    INPUT:
    user input (set)
    maximal number of recipes that will be returned
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
            # else:
            #     print(i, "not in series")
        len_union = len(union)
        if len_union == 0:
            len_union = 0.001
        jaccard = intersection / len_union

        # intersection_over_recipe_length = intersection/len(all_ingredients)
        # print("Übereinstimmung / Rezeptlänge", intersection_over_recipe_length)


        # intersection over recipe-length penalizes large recipes stronger than
        # jaccard does.
        # Example: User has onion, cream and noodles; recipe consists out of
        # conion and cream .
        # jaccard: 0,66
        # intersection over recipe-length : 1
        # Problem: very short recipes with e.g. 1 ingredient.
        # --> Solution:
        # #
        if len(all_ingredients) > 2 and intersection == len(all_ingredients):
            jaccard = 1

        return jaccard


    DEFAULT_ING = ["Salz", "Pfeffer", "Wasser", "Meersalz"]
    len_user_ingredients = len(user_input)

    # Read data from csv
    recipes = pd.read_csv("flask_app/data/recipes_4170.csv", converters={'ingredients': eval, 'categories': eval}, index_col=0)
    # One hit encode ingredients
    mlb = MultiLabelBinarizer()
    df_onehot = pd.DataFrame(mlb.fit_transform(recipes["ingredients"]), columns=mlb.classes_, index=recipes.index)

    # Delete default ingredients (salt etc.)
    # 1) from one hot encoded:
    df_onehot = df_onehot.drop(DEFAULT_ING, 1)
    # 2) from recipes df:
    def discard_defaults(a):
        for i in DEFAULT_ING:
            a.discard(i)
    recipes.ingredients.apply(discard_defaults)

    # Create list of most used ingredients
    most_used_ingredients = df_onehot.mean().sort_values(ascending=False).head(20)
    # # Save as file
    # with open("../most_used_ingredients.txt", "w") as f:
    #     for i in sorted(most_used_ingredients.index):
    #         f.write(i)
    #         f.write("\n")

    # # Search recipes with similar ingredients
    df_onehot["number_of_ingredients"] = 0
    df_onehot["number_of_ingredients"] = df_onehot.apply(numpySum, 1)
    df_onehot["jaccard"] = df_onehot.apply(calc_jaccard_index, 1)

    top_recipes = df_onehot.jaccard.sort_values(ascending=False)[:max_recipes]
    print(top_recipes)

    list_of_series = []
    for i in top_recipes.index:
        list_of_series.append(recipes.loc[i])
    list_of_lists = []
    for i in list_of_series:
        list_of_lists.append([i.name, i.description, i.ingredients, i.url])

    return list_of_lists
