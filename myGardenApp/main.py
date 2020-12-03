import sqlite3
from sqlite3 import Error


class DB:
    # SQLite Data types:
    #    NULL
    #    INTEGER: signed integer, max 8 bytes.
    #    REAL: floating point value, 8-byte
    #    TEXT: text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).
    #    BLOB: blob of data, stored exactly as it was input.

    # "__init__" in python is similar to constructors in Java, and will execute each time you are creating a new object
    # "Self" parameter references the current instance of the class, similar to "this" in Java

    # Create the connection
    def __init__(self, dbFileName):

        try:
            self.dbFileName = dbFileName
            self.conn = sqlite3.connect(self.dbFileName + '.db')
            self.cur = self.conn.cursor()
            print("DB initialized in the current directory.")
        except Error as e:
            print(e)

    # executed Insert, update or delete
    def exec(self, command):
        self.cur.execute(command)
        self.conn.commit()

    # executed Insert, update, or delete with parameters
    def exec2(self, command, values):
        self.cur.execute(command, values)
        self.conn.commit()

    # execute select command
    def fetch(self, command):
        self.cur.execute(command)
        return self.cur.fetchall()

    # execute select with parameters
    def fetch2(self, command, values):
        self.cur.execute(command, values)
        return self.cur.fetchall()

    # close the connection
    def close(self):
        self.conn.close()


# global variables to store the session's username and password
user = ''
pw = ''

"""                                                typesearch
    This function searches the database and returns the plants that are the same type as specified by user input.
"""


def typesearch(db):
    plantType = input("Enter the type of plant from the following list [Fruit, Vegetable, Herb, Succulent, Flower]: ")

    # perform query to select plants by type
    try:
        rows = db.fetch2("SELECT * FROM Plant WHERE type=?;", (plantType,))
    except Error as e:
        print(e)
        return

    # print all the records found
    for row in rows:
        print(row)


"""                                                 zonesearch
    This function takes in the user's username and performs a query to retrieve all the plants that may be in
    that user's zone
"""


def zonesearch(db):
    try:
        rows = db.fetch2("SELECT Common_name, type, minZone, maxZone FROM Plant P, Users U \
                          WHERE minZone<=U.gardenZone AND maxZone>=U.gardenZone AND U.Username=?", (user,))
        zone = db.fetch2("SELECT gardenZone FROM Users WHERE Username=?", (user,))
    except Error as e:
        print(e)
        return

    # print the plant name, the type, and zone
    print("Plants in zone " + str(zone[0][0]) + ": ")
    for row in rows:
        print(row[0] + ", " + row[1] + ", Zones " + str(row[2]) + "-" + str(row[3]))


"""                                                 namesearch
    This function searches plants by common name.
"""


def namesearch(db):
    # ask the user to input the plant's name
    query = input("Enter the name of the plant you'd like to find: ")
    try:
        rows = db.fetch2("SELECT * FROM Plant WHERE Common_name LIKE ?", ('%' + query + '%',))
    except Error as e:
        print(e)
        return

    # check if plant is not found
    if not rows:
        print("Plant not found.")
        return

    # print the plant record
    print("Scientific name:     Common name:    Water:    Light:     When to Plant: Time to flower:   Found between zones: \
    Edible?(Y/N):      Type:     Harvesting Time:")
    for row in rows:
        print('      '.join(map(str, row)))
    print("")


"""                                                 showcrops
    This function lists all of the edible plants in a user's garden zone that can be planted currently. It prompts the user
    for a month in 3 char format before searching the database to find all the plants using a nested query. Finally, 
    it lists the common name, type (fruit or vegetable), and the window of when the crop can be planted.
"""


def showcrops(db):
    month = input("What month is it again? Enter in 3 letter format (e.g. Feb, Mar, etc): ")
    try:
        rows = db.fetch2("SELECT Common_name, type, whenToPlant FROM \
                            (SELECT * FROM Plant P, Users U \
                             WHERE minZone<=U.gardenZone AND maxZone>=U.gardenZone AND U.Username=?) t\
                             WHERE t.edible='Y' AND t.whenToPlant LIKE ?", (user, '%' + month + '%'))
    except Error as e:
        print(e)
        return

    # print the plant name, the type, and zone
    print("Crops you can plant now: ")
    for row in rows:
        print(row[0] + ", " + row[1] + ", " + str(row[2]))
    print("")


"""                                                 inbloom
    This function performs a query on the database to return all of the flowers in the Plant table that are in bloom in
    the current season. It first prompts the user for the season before performing a LIKE search on the flowers in the
    database.
"""


def inbloom(db):
    # prompt the user for the current season
    season = input("Enter the current season: ")

    # then, perform the query on the floweringTime and count the amount of flowers that fit the query
    try:
        rows = db.fetch2("SELECT Common_name, floweringTime FROM Plant WHERE floweringTime LIKE ? \
                         AND type='Flower'", ('%' + season + '%',))
        count = db.fetch2("SELECT COUNT(*) FROM Plant WHERE floweringTime LIKE ? \
                         AND type='Flower'", ('%' + season + '%',))
    except Error as e:
        print(e)
        return

    # check if there are any flowers at all
    if count[0][0] < 1:
        print("There are no flowers in bloom right now.")
        return

    # print all the flowers in bloom
    print("These " + str(count[0][0]) + " flowers are currently in bloom: ")
    for row in rows:
        print(row[0] + " blooms during: " + row[1])


"""                                                 addtogarden
    This function allows a user to insert a new plant into their garden. It prompts the user to enter the plant's common
    name before searching if the plant currently exists in the Plant table. If it does, the plant's name is inserted 
    into ALLPLANTS, where it can be recorded in a user's garden. Finally, it lists all the records in the garden after
    insertion. It allows for multiple inputs at a time until the user specifies not to.
"""


def addtogarden(db):
    cont = ''  # flag determining whether the function should continue

    # continue inserting plants as the user wishes
    while cont != 'N':
        # prompt the user to search for a plant
        plant = input("Enter the name of the plant you'd like to add: ")

        # check if the plant exists by performing a SELECT query on the common name
        try:
            check = db.fetch2("SELECT COUNT(*) FROM Plant WHERE Common_name=?", (plant,))
        except Error as e:
            print(e)
            return

        # then check if the plant was found
        if check[0][0] < 1:
            print("Plant not found")

        # if it was, then insert the plant's name and the user's name into the ALLPLANTS table
        elif check[0][0] == 1:
            try:
                db.exec2("INSERT INTO ALLPLANTS(Username, plantName) VALUES(?,?)", (user, plant))
            except Error as e:
                print(e)
                return
            print(plant + " has been added to your garden.")

        # finally display the user's garden after insertion
        try:
            rows = db.fetch2("SELECT Plantname FROM ALLPLANTS WHERE Username=?", (user,))
        except Error as e:
            print(e)
            return

        print("Plants currently in your garden: ")
        for row in rows:
            print(row)

        # ask the user if they would like to add another plant
        cont = input("Would you like to add another plant? (Y/N) ")


"""                                                 showdb
    This function prints a listing of the amount of plants in all user's gardens, sorted in descending order. It performs
    an inner join between the ALLPLANTS and Users tables on Usernames, and then counts the plants that are under each
    user.
"""


def showdb(db):
    # perform an inner join between the Users and ALLPLANTS tables on the usernames, then group the listing by User
    # and count the plants each one has
    try:
        rows = db.fetch("SELECT U.Username, COUNT(A.plantName) FROM ALLPLANTS A INNER JOIN Users U ON A.Username=U.Username \
                         GROUP BY U.Username ORDER BY COUNT(A.plantName) DESC")

    except Error as e:
        print(e)
        return

    # print the username and count
    print('Username: Plant count: ')
    for row in rows:
        print(row[0] + "     " + str(row[1]))


"""                                                 updategarden
    This function queries all the plants in a user's garden and then prompts the user to delete a plant using the common
    name. It first checks if the plant exists in the garden before performing the deletion. Finally, the function lists
    the contents of the user's new garden after deletion.
"""


def updategarden(db):
    # gather all the plants in the user's garden
    try:
        rows = db.fetch2("SELECT plantName FROM ALLPLANTS WHERE Username=?", (user,))
    except Error as e:
        print(e)
        return

    # print all the plants then prompt the user for the common name of the plant to remove
    [print(row[0]) for row in rows]
    plant = input("Enter the name of the plant you'd like to remove: ")

    # check if the plant exists in the garden first
    if plant not in [row[0] for row in rows]:
        print("Plant not found.")

    # then delete the entry if it exists
    try:
        db.exec2("DELETE FROM ALLPLANTS WHERE Username=? AND plantName=?", (user, plant))
    except Error as e:
        print(e)

    print("Plant successfully removed.")

    # then print all the plants again
    print("Plants in your garden now: ")
    try:
        rows = db.fetch2("SELECT plantName FROM ALLPLANTS WHERE Username=?", (user,))
    except Error as e:
        print(e)
        return

    for row in rows:
        print(row[0])


"""                                                 updateUser
    This function prompts the user to either update their password or their garden zone. The username has a primary
    key constraint so it cannot be updated. The Users table is then updated with the new value of either password
    or gardenZone.
    Note: the function currently does not check for other kinds of input.
"""


def updateUser(db):
    change = input("Would you like to change your password or garden zone?")

    if change == 'password':
        newval = input("Enter your new password: ")
        try:
            db.exec2("UPDATE Users SET Password=? WHERE Username=?", (newval, user))
        except Error as e:
            print(e)
            return
        print("Password changed successfully. Please sign in.")
        signIn(db)

    elif change == 'garden zone':
        newval = input("Enter your new zone: ")
        try:
            db.exec2("UPDATE Users SET gardenZone=? WHERE Username=?", (newval, user))
        except Error as e:
            print(e)
            return
        print("Garden zone changed successfully")


"""                                                 createUser
    This function creates a user taking in variables after prompting for input and then adds those following values to
    the Users table. After creating the user, they are then required to sign in.
"""


def createUser(db):
    # prompt the user to enter the username, password, and their gardening zone
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    zone = input("Enter your garden zone (1-13): ")

    # then enter the data into the Users table
    try:
        db.exec2("INSERT INTO Users(Username, Password, gardenZone) VALUES(?, ?, ?);", (username, password, zone))
    except Error as e:
        print(e)

    # finally prompt the user to sign in with their new credentials
    print("User created successfully. Please sign in.")
    signIn(db)


"""                                                 signIn
    This function allows the user to sign in and saves the user credentials for the session using two global variables.
    It prompts the user for a username and password, then performs a query to verify the existence of the user credentials.
    If the user isn't found, a prompt appears that asks whether or not to exit the program or create a new account. 
    If create an account is selected, the function calls createUser to then create the account. 
    Note: The user and password are global variables, meaning one user can be signed in per session.
"""


def signIn(db):
    global user
    global pw
    print("Please sign in: ")
    user = input("Username: ")
    pw = input("Password: ")

    try:
        check = db.fetch2("SELECT * FROM Users WHERE Username=? AND Password=?", (user, pw))
    except Error as e:
        print(e)
        return

    if not check:
        ans = input("ERROR: User not found. Please press (x) key to exit or (c) key to create an account.")
        if ans.upper() == "X":
            exit()
        elif ans.upper() == "C":
            createUser(db)
            return
        else:
            print("ERROR: wrong input.")
            return
    elif check:
        print("User successfully signed in.")


"""                                     chooseOption(db) 
    This function allows the user to loop through the menu selecting from a list of options to perform 
    whichever action on the database. The user selects an option from the list displayed and is prompted
    to enter an input. The corresponding function for the input number is then performed, unless the input
    is incorrect, then the loop continues and the user is prompted again.                                 
"""


def chooseOption(db):
    option = ''
    options = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    # continously loop through the options until 0 is found
    while option not in options:

        # display the menu of options
        print("Select from the list of options:\nSearch for plants by type (1)")
        print("Search for plants in your planting zone (2)\nSearch for plants by common name (3)")
        print("See what fruits or veggies you can plant today (4)")
        print("See which flowers are in bloom currently (5)\nAdd a plant to your garden (6)")
        print("Show the amount of plants in each user's garden (7)\nUpdate a record in your garden (8)")
        print("Change your login credentials (9)")

        option = input("Please choose an option or press 0 to exit: \n")

        if option == '1':
            typesearch(db)
        elif option == '2':
            zonesearch(db)
        elif option == '3':
            namesearch(db)
        elif option == '4':
            showcrops(db)
        elif option == '5':
            inbloom(db)
        elif option == '6':
            addtogarden(db)
        elif option == '7':
            showdb(db)
        elif option == '8':
            updategarden(db)
        elif option == '9':
            updateUser(db)
        elif option == '0':
            return 0
        else:
            print("Please select an option from the menu.")


def main():
    db = DB('garden')

    # welcome the user and prompt them to sign in
    print("Welcome to myGarden!")
    signIn(db)

    # make the loop to choose an option
    while chooseOption(db) != 0:
        chooseOption(db)

    print("Goodbye!")
    # at the end close connection to the Database
    db.close()


if __name__ == '__main__':
    main()
