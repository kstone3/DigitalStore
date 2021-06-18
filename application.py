#Imports date stuff so you can get current date
from datetime import date

# import the Flask web framework so that we can take advantage of
# its libraries for rendering database info for display on web pages
# AND for inserting info into databases from info submitted through
# forms on web pages (dynamic web pages)
from flask import Flask, render_template, request
# import the cs50 library so we can use the connection making abstraction
from cs50 import SQL

#Flask stuff, don't change
app = Flask(__name__)

#Sets up database connection
conn = SQL("sqlite:///data.db")

#Method for index.html
@app.route("/")
def index():
    #Rows is a list of dicts, this applies to all methods
    rows = conn.execute("SELECT * FROM items")
    #This tells the webpage where to go after submitting the form
    return render_template("index.html", rows=rows)

#Method to add an item
@app.route('/addItem', methods=['GET', 'POST'])
def addItem():
    #Sends you to the failure page if you didn't input one of the fields
    #request.form.get() gets the value with the name in the get() from the form with the action specified as this method
    #The @app.route() tells the html how to identify this method
    if not request.form.get("name") or not request.form.get("price") or not request.form.get("numInStock") or not request.form.get("seller"):
        return render_template("failureToAdd.html")
    #Inserts new item into the database
    #An INSERT statement in SQL returns the id as a number
    id = conn.execute("INSERT INTO items (name, price, seller, datePosted, numInStock) VALUES (?,?,?,?,?)", request.form.get("name"), request.form.get("price"), request.form.get("seller"), date.today(), request.form.get("numInStock"))
    rows = conn.execute("SELECT * FROM items WHERE id = ?", id)
    return render_template("addSuccess.html", rows=rows)

#Method to delete an item
@app.route("/deleteItem", methods=['GET', 'POST'])
def deleteItem():
    #Sends you to the failure page if you didn't input one of the fields
    if not request.form.get("name") or not request.form.get("seller") or not request.form.get("datePosted"):
        return render_template("failureToDelete.html")
    #A SELECT statement in SQL does not return the id as a number
    #So you have to SELECT the id, but it gets returned as a dict inside a list and unwrap it later
    id = conn.execute("SELECT id FROM items WHERE name = ? and seller = ? and datePosted = ?", request.form.get("name"), request.form.get("seller"), request.form.get("datePosted"))
    #id[0]gets the first item from the list and .get('id') selects the item from the dict with a key of 'id'
    rows = conn.execute("SELECT * FROM items WHERE id = ?", id[0].get('id'))
    #Actually deletes the item from the database
    conn.execute("DELETE FROM items WHERE id = ?", id[0].get('id'))
    return render_template("deleteSuccess.html", rows=rows)

#Method to find the item you want to change the stock of
@app.route("/changeNumInStockQuery", methods=['GET', 'POST'])
def changeNumInStockQuery():
    if not request.form.get("name") or not request.form.get("seller") or not request.form.get("datePosted"):
        return render_template("failureToChangeNumInStock.html")
    rows = conn.execute("SELECT * FROM items WHERE name = ? and seller = ? and datePosted = ?", request.form.get("name"), request.form.get("seller"), request.form.get("datePosted"))
    return render_template("changeNumInStock.html", rows=rows)

#Method to actually change the number in stock
@app.route("/changeNumInStock", methods=['GET', 'POST'])
def changeNumInStock():
    conn.execute("UPDATE items SET numInStock = ? WHERE id = ?", request.form.get("numInStockChange"), request.form.get("id"))
    rows = conn.execute("SELECT * FROM items WHERE id = ?", request.form.get("id"))
    return render_template("changeNumInStockSuccess.html", rows=rows)

#Method to buy an item
@app.route("/buyItem", methods=['GET', 'POST'])
def buyItem():
    #Gets the stock of the item so I can decrease it by one later in the method
    stock = conn.execute("SELECT numInStock FROM items WHERE id = ?", request.form.get("id"))
    #If there are none in stock then it sends you to the failure to buy page
    if stock[0].get('numInStock') == "None" or stock[0].get('numInStock') <= 0:
        return render_template("failureToBuy.html")
    #Stock variable works the same as the id variable
    conn.execute("UPDATE items SET numInStock = ? WHERE id = ?", (stock[0].get('numInStock')-1), request.form.get("id"))
    rows = conn.execute("SELECT * FROM items WHERE id = ?", request.form.get("id"))
    return render_template("itemBoughtSuccess.html", rows=rows)

#Method to search for items to buy
@app.route("/queryItems", methods=['GET', 'POST'])
def queryItems():
    name = request.form.get("name")
    price = request.form.get("price")
    date = request.form.get("datePosted")
    seller = request.form.get("seller")

    #If you don't enter a value for one of these fields, then it sets it to a % sign.
    #This will make it so that the SQL SELECT statement will basically ignore that field in selecting the items you want
    if(name == ""):
        name = '%'
    if(price == ""):
        price = '%'
    if(date == ""):
        date = '%'
    if(seller == ""):
        seller = '%'

    #Makes it so that you search for items with a name like the one you entered
    #For example if there are a bunch of items like Light Blue T-Shirt and Red T-Shirt,
    #and you enter T-Shirt, it will select all items with T-Shirt in the name and will return Light Blue T-Shirt
    name = '%' + name + '%'

    rows = conn.execute("SELECT * FROM items WHERE name LIKE ? AND price LIKE ? AND datePosted LIKE ? AND seller like ?", name, price, date, seller)
    return render_template("queryItems.html", rows=rows)