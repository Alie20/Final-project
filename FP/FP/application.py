from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
app=Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db =SQL("sqlite:///electronics.db")


@app.route("/")
def index():
    return render_template("front.html")


@app.route("/register" , methods=["GET","POST"])
def register():
    if request.method=="POST":
        session.clear()
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") :
            return apology("sorry complete the information")

        else:
            username = request.form.get("username")
            password = request.form.get("password")
            confirm = request.form.get("confirmation")

            username_data = db.execute("SELECT username FROM info WHERE username = :username",
                                       username=request.form.get("username"))
            print(username_data)
            if len(username_data) != 0:
                return apology("username is already taken")

            else:
                if password == confirm:
                    print("hello")
                    hash1 = generate_password_hash(password)
                    db.execute("INSERT INTO info (username,hash) VALUES(:username,:hash1)", username=username, hash1=hash1)
                    rows = db.execute("SELECT * FROM info WHERE username = :username",
                                      username=request.form.get("username"))

                    session["user_id"] = rows[0]["id"]
                    flash("You have been registered ")
                    return redirect(url_for('home'))
                else:
                    return apology("sorry not same password")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM info WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect ("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
@login_required

def home():

    if request.method == "POST":
        if  request.form.get("ard") or  request.form.get("node") or request.form.get("rasp") or  request.form.get("ard"):

            ard=request.form.get("ard")
            node=request.form.get("node")
            rasp=request.form.get("rasp")
            stepper=request.form.get("stepper")

            y={}
            y["ard"]=ard
            y["node"]=node
            y["rasp"]=rasp
            y["stepper"]=stepper

            print(session["user_id"])

            username=db.execute("SELECT username FROM info WHERE id=:id",id=session["user_id"])
            name = username[0]['username']

            data = db.execute("SELECT * FROM data WHERE username=:username", username=name)
            print(data)

            if not data:
                db.execute("INSERT INTO data (username,stepper,Arduino,rasp,node) VALUES(:username,:stepper,:Arduino,:rasp,:node)",
                    username=name, stepper=y["stepper"],Arduino=y["ard"],rasp=y["rasp"],node=y["node"])
                x=db.execute("SELECT * FROM data WHERE username=:username",username=name)
                print(x)
                return render_template("data.html",x=x)
            else:
                db.execute("UPDATE data SET stepper =:stepper , Arduino =:Arduino , rasp =:rasp , node =:node  WHERE username= :username",
                                username = name,
                                stepper = y["stepper"],
                                Arduino = y["ard"],
                                rasp = y["rasp"],
                                node = y["node"])
                x=db.execute("SELECT * FROM data WHERE username=:username",username=name)
                print(x)
                return render_template("data.html",x=x)







        else:
            return apology("you should eneter no.of parts that you want to buy")


    else:
        return render_template("home.html")


@app.route("/data" , methods =["GET", "POST"])
@login_required

def data():
    if request.method =="POST":
        if request.form.get("ok") == "ok":
            username=db.execute("SELECT username FROM info WHERE id=:id",id=session["user_id"])
            name = username[0]['username']
            f=db.execute("SELECT * FROM data WHERE username=:username",username=name)
            return render_template("final.html",f=f)
        elif request.form.get("cancel") == "cancel":
            username=db.execute("SELECT username FROM info WHERE id=:id",id=session["user_id"])
            name = username[0]['username']

            db.execute("INSERT INTO data (username,stepper,Arduino,rasp,node) VALUES(:username,:stepper,:Arduino,:rasp,:node)",
            username=name, stepper=y["stepper"],Arduino=y["ard"],rasp=y["rasp"],node=y["node"])
            x=db.execute("SELECT * FROM data WHERE username=:username",username=name)
            return render_template("home.html")
    return render_template("home.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
