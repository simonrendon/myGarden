# myGarden
myGarden is a Python CLI application that I developed using Python 3.9 and the SQLite 3 database framework. It consists of an SQLite database of many different plants, and allows users to create their own gardens, compare the size of their gardens with others, and provides many different tools for navigating the relational database.

The setup of the tables in the database are as follows:
CREATE TABLE IF NOT EXISTS Plant 
       (Scientific_name TEXT NOT NULL, 
          Common_name	TEXT NOT NULL UNIQUE,  
          requiredWater TEXT NOT NULL CHECK(requiredWater IN ('low', 'medium', 'high')), 
          requiredLight TEXT NOT NULL CHECK(requiredLight IN ('low', 'medium', 'high')), 
          floweringTime TEXT DEFAULT 'does not flower', 
          whenToPlant	TEXT DEFAULT 'anytime', 
          minZone	INTEGER, 
          maxZone	INTEGER, 
          edible	TEXT NOT NULL CHECK(edible IN ('Y', 'N')), 
          type 	TEXT NOT NULL, 
          harvestTime	TEXT, 
          PRIMARY KEY(Scientific_name))

CREATE TABLE IF NOT EXISTS Users ( 
         Username TEXT,
         Password TEXT NOT NULL, 
         gardenZone	INTEGER NOT NULL CHECK(gardenZone BETWEEN 1 and 13), 
         PRIMARY KEY(Username)

CREATE TABLE IF NOT EXISTS ALLPLANTS ( 
         Username	TEXT NOT NULL, 
         plantName	TEXT NOT NULL, 
         FOREIGN KEY(plantName) REFERENCES Plant(Scientific_name) ON DELETE SET NULL,
         FOREIGN KEY(Username) REFERENCES Users(Username) ON DELETE SET NULL;
)


The final version of the myGarden app was built and finished on November 30, 2020. The app was built in Python 3.9 using the command line interface on JetBrain’s PyCharm IDE. 
Upon running, the user is presented with a sign-in screen which prompts for the username and password, which are then queried with the Users table to ensure they exist. If either the username or password does not exist, then the user is offered whether to create an account or exit. If they choose to create an account, they are prompted to enter the values for the Users table (username, password, garden zone), and the following values are inserted into the table. After signing in, the username is saved as a global variable and the user is presented with a menu consisting of 9 options:

Search for plants by type (1)
This option prompts the user for a Plant type ‘?’, and then performs the query 
SELECT * FROM Plant WHERE type=?;
Which then displays all the Plants that are of that type, given that they are in the list of [Fruit, Vegetable, Herb, Succulent, Flower]. This is done with the typesearch(db) function.

Search for plants in your planting zone (2)
This option uses the zonesearch(db) function, which uses the global variable ‘user’ to find the plants in a user’s USDA planting zone. It performs the nested query
SELECT Common_name, type, minZone, maxZone FROM Plant P, Users U 
                 WHERE minZone<=U.gardenZone AND maxZone>=U.gardenZone AND U.Username=?
with the ‘?’ placeholder being the user variable. Then, to retrieve the zone as a variable, the following query is done:
SELECT gardenZone FROM Users WHERE Username=?
In order to print the user’s zone, followed by all the plants returned by the first query.

Search for plants by common name (3)
This option calls the namesearch(db) function, which prompts the user to enter a plant’s common name and returns all those matching the search using the query:
SELECT * FROM Plant WHERE Common_name LIKE ?

See what fruits or veggies you can plant today (4)
This option calls the cropsearch(db) function, which asks the user for the current month before performing the nested query
SELECT Common_name, type, whenToPlant FROM 
      (SELECT * FROM Plant P, Users U 
      WHERE minZone<=U.gardenZone AND maxZone>=U.gardenZone
      AND U.Username=?) t
      WHERE t.edible='Y' AND t.whenToPlant LIKE ?
Issue: although the whenToPlant value is a range of months, this search only finds the columns that contain the name exactly, and not within the range.



See which flowers are in bloom currently (5)
This calls the inbloom(db) function, which prompts the user to enter the current season before performing the 2 queries, with ‘?’ being the season
SELECT Common_name FROM Plant WHERE floweringTime LIKE ?
       AND type='Flower'
SELECT COUNT(*) FROM Plant WHERE floweringTime LIKE ?
       AND type='Flower'
It prints “these x flowers are blooming” , with x being the count of flowers, before printing the list of flowers. 

Add a plant to your garden (6)
This calls the addtogarden(db), which prompts the user for the common name of the plant to add to the garden, which performs the first query to search for the plant, and if it exists, performs the 2nd SQL script to insert it into the ALLPLANTS table, with the first placeholder being the username, and the second one the plant’s common name. Finally, it performs the final query to print all the current plants in the user’s garden after insertion
SELECT COUNT(*) FROM Plant WHERE Common_name=?
INSERT INTO ALLPLANTS(Username, plantName) VALUES(?,?)
SELECT Plantname FROM ALLPLANTS WHERE Username=?

Show the amount of plants in each user's garden (7)
This calls the showdb(db) function, which performs an inner join on ALLPLANTS and Users to generate the amount of plants each user has in their garden, grouping by username and ordering by the amount of plants.
SELECT U.Username, COUNT(A.plantName) 
FROM ALLPLANTS A INNER JOIN Users U ON A.Username=U.Username 
GROUP BY U.Username ORDER BY COUNT(A.plantName) DESC

Update a record in your garden (8)
This calls the updategarden(db) function, which prompts the user for the plant name that they wish to delete from their garden. After searching for whether the plant exists, it performs the script:
DELETE FROM ALLPLANTS WHERE Username=? AND plantName=?
Which then deletes the record from the ALLPLANTS table, before printing the rest of the garden after deletion.

Change your login credentials (9)
This prompts the user to enter whether they’d like to update their password or their garden zone, and based on the choice, performs either one of the two scripts, updating the Users table:
UPDATE Users SET Password=? WHERE Username=?
UPDATE Users SET gardenZone=? WHERE Username=?

Please choose an option or press 0 to exit: 
Finally, pressing 0 exits the menu and closes the program.
