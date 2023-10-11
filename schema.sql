--table on users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    hash TEXT NOT NULL
);
--information about places. type = takeaway/restaurant/food vendor
CREATE TABLE places (
    place_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    placeName TEXT,
    placeType TEXT,
    placeAddress1 TEXT,
    placeAddress2 TEXT,
    placeCity TEXT,
    placePostcode TEXT,
    placeCountry TEXT,
    placeCuisine TEXT,
    placeWebsite TEXT,
    placeImg TEXT,
    placeRating INTEGER DEFAULT 0,
    placeVisited INTEGER DEFAULT 1,
    placeNotes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);


--specific meal occassions, linked with places
--meal_occasion = breakfast/luch/dinner
--type = sit down meal / takeaway etc
CREATE TABLE meals (
    meal_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    place_id INTEGER NOT NULL,
    mealDate DATE,
    mealType TEXT,
    mealOccasion TEXT,
    mealRating INTEGER DEFAULT 0,
    mealNotes TEXT,
    mealImg TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(place_id) REFERENCES places(place_id)
);
--information about specific plates had at places
--course = starter / main / side / dessert / drink
CREATE TABLE dishes (
    dish_id INTEGER PRIMARY KEY,
    place_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dishName TEXT,
    dishCourse TEXT,
    dishCuisine TEXT,
    dishCurrency TEXT,
    dishCost INTEGER DEFAULT 0,
    dishImg TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(place_id) REFERENCES places(place_id)
);
--Links meal_id with specific plates from that meal. Rating of that plate during that specific meal
CREATE TABLE linking (
    linking_id INTEGER PRIMARY KEY,
    meal_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    dishRating INTEGER DEFAULT 0,
    dishNotes TEXT,
    FOREIGN KEY(meal_id) REFERENCES meals(meal_id),
    FOREIGN KEY(dish_id) REFERENCES dishes(dish_id)
);

--to add test user
INSERT INTO users (username, country, city, hash) VALUES ("jonny", "australia", "melbourne", "1");

--trying to get all the dishes with unified rating and notes from linking automatically
SELECT linking.meal_id, linking.dish_id,
AVG(linking.dishRating) AS average,
COUNT(linking.dishRating) AS visits, GROUP_CONCAT(linking.dishNotes, " ") AS notes,
dishes.*
FROM linking
JOIN dishes
ON linking.dish_id = dishes.dish_id
WHERE dishes.place_id = 1
AND dishes.user_id = 1;

--places sort with most recent meal date joined
SELECT places.*, MAX(meals.mealDate) AS recent
FROM places
INNER JOIN meals
ON places.place_id = meals.place_id
WHERE places.user_id = ?
GROUP BY places.place_id;

-- get linking from dish_id and get matching meal dates with meal_id and user_id
SELECT linking.dishRating, linking.dishNotes, meals.mealDate
FROM linking
JOIN meals
ON linking.meal_id = meals.meal_id
WHERE linking.dish_id = ?
AND meals.user_id = ?;