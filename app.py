from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from datetime import date

app = Flask(__name__)
app.config["TEMPLATE_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///bytes.db")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/places")
@login_required
def places():
    # check if any places exist from database (compared to user)
    count = db.execute(
        "SELECT COUNT(*) AS count FROM places WHERE user_id = ?;", session["user_id"]
    )
    if count[0]["count"] == 0:
        # No places
        return render_template("places.html", type="places", data="false")
    else:
        # render places
        # get places
        places = db.execute(
            "SELECT places.*, MAX(meals.mealDate) AS recent FROM places INNER JOIN meals ON places.place_id = meals.place_id WHERE places.user_id = ? GROUP BY places.place_id;",
            session["user_id"],
        )
        distinctPlaces = db.execute(
            "SELECT DISTINCT placeName FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        cuisine = db.execute(
            "SELECT DISTINCT dishCuisine FROM dishes WHERE dishes.user_id = ?;",
            session["user_id"],
        )
        city = db.execute(
            "SELECT DISTINCT placeCity FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        country = db.execute(
            "SELECT DISTINCT placeCountry FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        # get meals
        meals = []
        combinedDishes = []
        for row in places:
            meals.append(
                db.execute("SELECT * FROM meals WHERE place_id = ? AND user_id = ?;", row["place_id"], session["user_id"])
            )
            # get all the dishes or the place
            tempDishes = db.execute(
                "SELECT * FROM dishes WHERE place_id = ? AND user_id = ?;", row["place_id"], session["user_id"]
            )
            # for each of these dishes loop through and find times eaten and average
            for dish in tempDishes:
                # times eaten
                temp = db.execute(
                    "SELECT COUNT(*) AS eaten, AVG(dishRating) AS average, GROUP_CONCAT(dishNotes) AS notes FROM linking WHERE dish_id = ?;",
                    dish["dish_id"],
                )
                dish["eaten"] = temp[0]["eaten"]
                # average rating
                dish["average"] = int(temp[0]["average"])
                # notes - concatinate notes
                dish["notes"] = temp[0]["notes"]
            combinedDishes.append(tempDishes)
        # loop through meals and create dishes
        mealDishes = []
        for i in range(len(meals)):
            for row in meals[i]:
                mealDishes.append(
                    db.execute(
                        "SELECT * FROM linking JOIN dishes ON linking.dish_id = dishes.dish_id WHERE meal_id = ?;",
                        row["meal_id"],
                    )
                )
        # print(mealDishes)
        return render_template(
            "places.html",
            type="places",
            data="true",
            mealDishes=mealDishes,
            combinedDishes=combinedDishes,
            meals=meals,
            places=places,
            dPlaces=distinctPlaces,
            cuisine=cuisine,
            city=city,
            country=country,
        )


@app.route("/meals")
@login_required
def meals():
    # check if any places exist from database (compared to user)
    count = db.execute(
        "SELECT COUNT(*) AS count FROM meals WHERE user_id = ?;", session["user_id"]
    )
    if count[0]["count"] == 0:
        # No places
        return render_template("meals.html", type="meals", data="false")
    else:
        # render places
        # get meal information from SQL
        meals = db.execute(
            "SELECT * FROM meals JOIN places ON meals.place_id = places.place_id WHERE meals.user_id = ?;",
            session["user_id"],
        )
        places = db.execute(
            "SELECT DISTINCT placeName FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        cuisine = db.execute(
            "SELECT DISTINCT dishCuisine FROM dishes WHERE dishes.user_id = ?;",
            session["user_id"],
        )
        # get dish information from meal using meal_id and join on rating and notes
        dishes = []
        for row in meals:
            dishes.append(
                db.execute(
                    "SELECT * FROM linking JOIN dishes ON linking.dish_id = dishes.dish_id WHERE meal_id = ?;",
                    row["meal_id"],
                )
            )

        return render_template(
            "meals.html",
            type="meals",
            data="true",
            dishes=dishes,
            meals=meals,
            places=places,
            cuisine=cuisine,
        )


@app.route("/existing/place", methods=["GET", "POST"])
def existingPlace():
    if request.method == "POST":
        name = request.get_json()
        print(name)
        info = db.execute(
            "SELECT * FROM places WHERE place_id = ? AND user_id = ?;",
            name["id"],
            session["user_id"],
        )
        dishes = db.execute(
            "SELECT * FROM dishes WHERE place_id = ? AND user_id = ?;",
            name["id"],
            session["user_id"],
        )
        return {"place": info, "dishes": dishes}


@app.route("/existing/dish", methods=["GET", "POST"])
def existingDish():
    if request.method == "POST":
        name = request.get_json()
        dishes = db.execute(
            "SELECT * FROM dishes JOIN linking ON dishes.dish_id = linking.dish_id WHERE dishes.dish_id = ? AND dishes.user_id = ?;",
            name["id"],
            session["user_id"],
        )
        return dishes


@app.route("/dishes")
@login_required
def dishes():
    # check if any places exist from database (compared to user)
    count = db.execute(
        "SELECT COUNT(*) AS count FROM dishes WHERE user_id = ?;", session["user_id"]
    )
    if count[0]["count"] == 0:
        # No dishes
        return render_template("dishes.html", type="dishes", data="false")
    else:
        # render dishes
        # get dishes info as dictionary
        dishes = db.execute(
            "SELECT * FROM dishes JOIN places ON dishes.place_id = places.place_id WHERE dishes.user_Id = ?;",
            session["user_id"],
        )
        cuisine = db.execute(
            "SELECT DISTINCT dishCuisine FROM dishes WHERE dishes.user_id = ?;",
            session["user_id"],
        )
        places = db.execute(
            "SELECT DISTINCT placeName FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        # print(places)
        # loop through dishes and get number of times eaten and average rating from SQL
        for row in dishes:
            # times eaten
            temp = db.execute(
                "SELECT COUNT(*) AS eaten, AVG(dishRating) AS average, GROUP_CONCAT(dishNotes) AS notes FROM linking WHERE dish_id = ?;",
                row["dish_id"],
            )
            row["eaten"] = temp[0]["eaten"]
            # average rating
            row["average"] = int(temp[0]["average"])
            # notes - concatinate notes
            row["notes"] = temp[0]["notes"]
        return render_template(
            "dishes.html",
            type="dishes",
            data="true",
            dishes=dishes,
            cuisine=cuisine,
            places=places,
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # post
        # check entered username
        if not request.form.get("username"):
            return render_template("register.html", error="please enter a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", error="please enter a password")

        elif not request.form.get("confirmation"):
            return render_template(
                "register.html", error="please confirm your password"
            )

        # check passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", error="passwords do not match")

        # check city filled in
        elif not request.form.get("city"):
            return render_template("register.html", error="please enter a city name")

        # check country filled in
        elif not request.form.get("country"):
            return render_template("register.html", error="please enter a country")

        # check username doesn't exist
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get("username").lower(),
        )
        if len(rows) != 0:
            return render_template(
                "register.html", error="sorry this username already exists"
            )

        # save username and password using SQL
        db.execute(
            "INSERT INTO users (username, hash, city, country) VALUES (?, ?, ?, ?);",
            request.form.get("username").lower(),
            generate_password_hash(request.form.get("password")),
            request.form.get("city").capitalize(),
            request.form.get("country"),
        )
        return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # post
        # Forget any user_id
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            # Ensure username was submitted
            if not request.form.get("username"):
                return render_template("login.html", error="Must include username")

            # Ensure password was submitted
            elif not request.form.get("password"):
                return render_template("login.html", error="Must provide password")
            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )
            print(rows)

            # Ensure username exists and password is correct
            if len(rows[0]) == 0 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return render_template(
                    "login.html", error="Incorrect password or username"
                )

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            return render_template("home.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # check add type
    if request.method == "GET":
        requestType = request.args["add-type"]
        print(requestType)
        # find if meals empty
        # if not populate a dictionary with all user meals and pass
        # find user country and city
        user_info = db.execute(
            "SELECT city, country FROM users WHERE id = ?;", session["user_id"]
        )
        distinctPlaces = db.execute(
            "SELECT DISTINCT placeName, place_id FROM places WHERE user_id = ?;",
            session["user_id"],
        )
        # print(user_info)
        return render_template(
            "add.html",
            type=requestType,
            city=user_info[0]["city"],
            country=user_info[0]["country"],
            places=distinctPlaces,
        )
    else:
        # post
        form_dict = request.form
        print(form_dict)
        # create seperate dictionaries
        placeColDict = split_dictionary(form_dict, 0, 13)
        mealColDict = split_dictionary(form_dict, 14, 19)
        dishColDict = split_dictionary(form_dict, 29, len(form_dict))

        # if placeExisting / dish/Existing not selected will be 'NotPicked'

        # check for issues
        # places
        if placeColDict["placeName"] == "":
            return error("Woah your place needs a name!!")

        # check place doesn't already exist
        check = db.execute(
            "SELECT COUNT(*) AS count FROM places WHERE placeName = ? AND placeCity = ? AND placePostcode = ? AND user_id = ?;",
            placeColDict["placeName"],
            placeColDict["placeCity"],
            placeColDict["placePostcode"],
            session["user_id"],
        )
        if check[0]["count"] != 0 and placeColDict["placeExisting"] == "NotPicked":
            return error(
                "This location already exists! Please select it from the list when adding a new meal!"
            )

        # check place rating between 0 and 5
        try:
            if (
                int(placeColDict["placeRating"]) < 0
                or int(placeColDict["placeRating"]) > 5
            ):
                return error(
                    "Oops something went wrong with your place rating there, please try again"
                )
        except:
            return error("Oops there was an error! - place")

        # meal
        # check date exists
        if mealColDict["mealDate"] == "":
            return error("Woah your meal date looks wrong there, how did that happen?!")

        # check meal rating between 0 and 5
        try:
            if int(mealColDict["mealRating"]) < 0 or int(mealColDict["mealRating"]) > 5:
                return error(
                    "Oops something went wrong with your place rating there, please try again"
                )
        except:
            return error("Oops there was an error! - meal")

        # dish issues
        # check dishName
        for key in dishColDict.keys():
            # find existing key and get value
            if "dishExisting" in key:
                existing = dishColDict[key]
            if "dishName" in key:
                # check dishName not empty
                if dishColDict[key] == "":
                    return error("Oops one of your dishes wasn't named correctly")

                # check if dish doesn't already exist
                check = db.execute(
                    "SELECT COUNT(*) AS count FROM dishes WHERE dishName = ? AND user_id = ?;",
                    dishColDict[key],
                    session["user_id"],
                )
                # If count is not 0 an existing not 'NotPicked' means they adding an already existing dish not drop drop down
                if check[0]["count"] != 0 and existing == "NotPicked":
                    return error(
                        "This dish already exists at this establishment. Please select it from the list next time!"
                    )

            # check rating
            if "dishRating" in key:
                try:
                    if int(dishColDict[key]) < 0 or int(dishColDict[key]) > 5:
                        return error(
                            "Oops something went wrong with one of your dish ratings there, please try again"
                        )
                except:
                    return error("Oops there was an error! - dish")

        # ADD DATA
        # places
        # check if picked from a list or new place
        if placeColDict["placeExisting"] == "NotPicked":
            place_id = db.execute(
                "INSERT INTO places (user_id, placeVisited) VALUES (?, ?);",
                session["user_id"],
                1,
            )
        else:
            # if existing - pick get place Id from the placeExisting key
            place_id = placeColDict["placeExisting"]

        # loop through rest of values and update to table where placename and user_id match
        for key in placeColDict.keys():
            if key != "placeExisting":
                db.execute(
                    "UPDATE places SET ? = ? WHERE place_id = ?",
                    key,
                    placeColDict[key],
                    place_id,
                )

        # meal
        meal_id = db.execute(
            "INSERT INTO meals (user_Id, place_id) VALUES (?, ?);",
            session["user_id"],
            place_id,
        )
        for key in mealColDict.keys():
            db.execute(
                "UPDATE meals SET ? = ? WHERE meal_id = ?",
                key,
                mealColDict[key],
                meal_id,
            )

        # dishes
        dishNum = " "
        for key in dishColDict.keys():
            # find number in string - UPDATE
            newDishNum = key[0 : key.index("d")]
            # set key name or check if key matches
            print(newDishNum)
            if dishNum != newDishNum:
                # insert into dishes
                # if doesn't exist
                if dishColDict[newDishNum + "dishExisting"] == "NotPicked":
                    dish_id = db.execute(
                        "INSERT INTO dishes (user_Id, place_id) VALUES (?, ?);",
                        session["user_id"],
                        place_id,
                    )
                else:
                    # If dish exists already
                    dish_id = dishColDict[newDishNum + "dishExisting"]

                # insert into linking
                linking_id = db.execute(
                    "INSERT INTO linking (meal_id, dish_id) VALUES (?, ?);",
                    meal_id,
                    dish_id,
                )

                dishNum = newDishNum

            # update column so that it match the SQL database (remove the dish number from key name)
            column = key[key.index("d") : len(key)]
            print(column)
            # set dish information
            # check if for linking or dishes
            if "dishRating" in key or "dishNotes" in key:
                db.execute(
                    "UPDATE linking SET ? = ? WHERE linking_id = ?",
                    column,
                    dishColDict[key],
                    linking_id,
                )
            elif "dishCost" in key:
                # find the cost times value by 10 to get an integer
                print(dishColDict[key])
                new_cost = int(float(dishColDict[key]) * 100)
                print(new_cost)
                db.execute(
                    "UPDATE dishes SET ? = ? WHERE dish_id = ?",
                    column,
                    new_cost,
                    dish_id,
                )
            else:
                if "dishExisting" not in key:
                    db.execute(
                        "UPDATE dishes SET ? = ? WHERE dish_id = ?",
                        column,
                        dishColDict[key],
                        dish_id,
                    )

        return render_template("home.html")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        type = request.args["type"]
        id = request.args["id"]
        # check type - dish / meal / place
        # use id to find info from SQL
        # pass sql data to render_template to build Edit page
        if type == "dish":
            info = db.execute(
                "SELECT * FROM dishes WHERE dish_id = ? AND user_id = ?;",
                id,
                session["user_id"],
            )
            linkedDishes = db.execute(
                "SELECT linking.dishRating, linking.dishNotes, linking.linking_id, meals.mealDate FROM linking JOIN meals ON linking.meal_id = meals.meal_id WHERE linking.dish_id = ? AND meals.user_id = ?;",
                id,
                session["user_id"],
            )
            return render_template(
                "edit.html", type=type, info=info[0], linked=linkedDishes
            )
        elif type == "meal":
            info = db.execute(
                "SELECT * FROM meals WHERE meal_id = ? AND user_id = ?;",
                id,
                session["user_id"],
            )
            return render_template("edit.html", type=type, info=info[0])
        elif type == "place":
            info = db.execute(
                "SELECT * FROM places WHERE place_id = ? AND user_id = ?;",
                id,
                session["user_id"],
            )
            return render_template("edit.html", type=type, info=info[0])
        else:
            return render_template("home.html")
    else:
        # post
        dict = request.form
        print(dict)
        for key in dict.keys():
            if "place" in key:
                db.execute(
                    "UPDATE places SET ? = ? WHERE place_id = ?",
                    key,
                    dict[key],
                    dict["place_id"],
                )

            elif "meal" in key:
                db.execute(
                    "UPDATE meals SET ? = ? WHERE meal_id = ?",
                    key,
                    dict[key],
                    dict["meal_id"],
                )
            elif "dish" in key:
                if "Rating" in key or "Notes" in key:
                    id = key[len(key) - 1 :]
                    linkingKey = key[: len(key) - 2]
                    print(id)
                    db.execute(
                        "UPDATE linking SET ? = ? WHERE linking_id = ?",
                        linkingKey,
                        dict[key],
                        id,
                    )
                elif "Cost" in key:
                    print(dict[key])
                    newCost = int(float(dict[key]) * 100)
                    print(newCost)
                    db.execute(
                        "UPDATE dishes SET ? = ? WHERE dish_id = ?",
                        key,
                        newCost,
                        dict["dish_id"],
                    )
                else:
                    db.execute(
                        "UPDATE dishes SET ? = ? WHERE dish_id = ?",
                        key,
                        dict[key],
                        dict["dish_id"],
                    )
            else:
                return error("error while editing! Sorry!")

        return render_template("home.html")


@app.route("/account", methods=["GET"])
@login_required
def account():
    account = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    return render_template("account.html", account=account[0])


@app.route("/account/location", methods=["POST"])
@login_required
def location_update():
    dict = request.form
    print(dict)
    for key in dict:
        db.execute(
            "UPDATE users SET ? = ? WHERE id = ?;", key, dict[key], session["user_id"]
        )
    return redirect("/account")


@app.route("/account/password", methods=["POST"])
@login_required
def password_update():
    dict = request.form
    print(dict)

    # Ensure password was submitted
    if not request.form.get("password"):
        return render_template("account.html", error="please enter a password")

    elif not request.form.get("confirmation"):
        return render_template("account", error="please confirm your password")

    # check passwords match
    elif request.form.get("password") != request.form.get("confirmation"):
        return render_template("account.html", error="passwords do not match")

    # check password
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Ensure username exists and password is correct
    if len(rows[0]) == 0 or not check_password_hash(
        rows[0]["hash"], request.form.get("password")
    ):
        return render_template("account.html", error="Incorrect password")

    # update password
    db.execute(
        "UPDATE users SET hash = ? WHERE id = ?;",
        generate_password_hash(request.form.get("password")),
        session["user_id"],
    )

    return redirect("/account")


@app.route("/about")
def about():
    return render_template("about.html")


def error(message):
    return render_template("error.html", error=message)


def split_dictionary(input_dict, start, end):
    new_dict = {}
    i = 0
    for k, v in input_dict.items():
        i += 1
        if i >= start and i <= end:
            new_dict[k] = v

    return new_dict
