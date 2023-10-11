# <span style="color:blue"> BYTES: Meal Tracking Website</span>

## **Video Demo**
[https://youtu.be/0rVggQNrMbM](https://youtu.be/H0qTLFHteRM)

## **Overview**
Ever go back to a restaurant and have no idea what you ordered previously and what you liked? I certainly do!

BYTES is a website that helps users track and rate restaurants, meals and specific dishes to help avoid this issue.

## **Languages and Libraries**

<p>Server Functionality: Python (flask)</p>
<p>Website pages: HTML, CSS and Jinja templating</p>
<p>Webpage Automation: JavaScript</p>
<p>Additional Frameworks: Bootstrap</p>
<p>Database: sqlite3</p>
<p>Password Security: werkzeug.security</p>

## **Database Design**
<p>The database was created in SQL using sqlite3.</p>
<p>The database is relational with a number of different tables that link together. The structure of the database can be seen
here:</p>

<img src="https://github.com/jonnymortemore/Bytes/assets/79447139/d7125d4e-0c12-4c9b-9588-f9f58c4ec89a">


#### Users
This table stores the user information including username and password. It also stores country and city data. It's id field is linked to almost all other tables in the database and used to control what data is provided to users on log-in. It is also used to track the users login for flask sessions.

#### Places
This table tracks the places that users have added. This includes name, address, website as well as a rating and notes field. It's place_id field is used to link meals and dishes to it.

#### Meals
This table tracks specific meals had at places. It tracks the data and rating of the meal as well as linking to the correct 'place_id'.

#### Dishes
This tracks the specific dish information such as name, cost, course and image.

#### Linking
The idea behind this table was to allow the same dish to be rated multiple times within different meals while preserving all previous dish rating and notes. It links to both the dish and meal tables using their respective ID's.

## **Website Stricture**
<img src="https://github.com/jonnymortemore/Bytes/assets/79447139/7868a8da-2597-4f85-8bd4-05f25afdea4a">


## **Account System**
<p>The website has a simple user login system. Viewing and adding data is restricted to logged in accounts which are accessed using a username and password. Their user ID number is then assigned to the flask session to track their login until logged out.</p>
<p>On logging in the user has access to more pages to view, add and edit data.</p>
<p>The user also has access to a account page where they can view their username as well as change password and location. </p>



## **Viewing Data**
<p>Each type of data (places, meals and dishes) have their own seperate page once logged in to the website.</p>
<p>These pages stem from a universal 'data' html page which contains the search headers.</p>
<P>All data can be searched on a number criteria as well as a free search, implemented using javaScript.</p>
<p>From each page you can add new data of that type, which redirects to the add page.</p>
<p>Each element also has an edit button that allows the user to edit that data from an edit page. </p>


## **Adding Data**
<p>The adding page allows users to add new places, meals and dishes</p>
<p>They can either add completely new places, meals and dishes or select places and dishes from a list. This list comprises all places they have already visited, and all dishes from selected places.</p>
<p>The user can add and remove multiple dishes to the page dynamically. This is controlled by javaScript.</p>
<p>On completion, the new data will be added to the database via SQL at the server level. </p>

## **Editing Data**
<p>When a user clicks on an edit button on one of the elements on the data page, they will be redirected to a new 'edit' page displaying the current data they wished to edit.</p>
<p>They can then change any element of that data as they wish. This is then passed to the database via SQL at the server level. </p>

## **Possible Future Improvements**
Initially I had planned to use google maps API to help users select restaurants and add their data much easier. This however quickly exceeded the scope of this project but would be the logical next step if I were to take it forward.

Another possible improvement would be to allow images to be uploaded for places, meals and dishes as currently only image links are allowed. Although possible this makes it much harder to add personal photos to the website. This would however require significant local storage to store such images.


