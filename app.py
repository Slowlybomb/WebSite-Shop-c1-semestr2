"""
My system has two kinds of user: regular ones, and administrators.
To login as admin use this super save password and creative user id: Password: '123' User_id: 'admin'
"""

# I found about flash here: https://flask.palletsprojects.com/en/2.3.x/patterns/flashing/
# and https://stackoverflow.com/questions/40949746/how-to-display-flashing-message-without-reloading-the-page-in-flask
from flask import Flask, render_template, session, redirect, url_for, g, request, flash 
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationFrom, LoginForm, CatalogForm, PaintForm, ChangePasswordForm, OrderForm, ChangeUserForm, AddProductForm
from functools import wraps
from werkzeug.utils import secure_filename
import os
from random import randint


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "XYU"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)
    g.paint_type = session.get("paint_type", None)

    db = get_db()
    admin_username = 'admin'
    hashed_password = generate_password_hash('123')
    admin_exists = db.execute("SELECT 1 FROM users WHERE user_id = ?", (admin_username,)).fetchone()
    if not admin_exists:
        db.execute("INSERT INTO users (user_id, password, is_admin) VALUES (?, ?, 1)", (admin_username, hashed_password))
        db.commit()

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

def initialize():
    db = get_db()
    admin_username = 'admin'
    password = "123"
    hashed_password = generate_password_hash(password)
    admin_exists = db.execute("SELECT 1 FROM users WHERE user_id = ?", (admin_username,)).fetchone()
    if not admin_exists:
        db.execute("INSERT INTO users (user_id, password, is_admin) VALUES (?, ?, 1)", (admin_username, hashed_password))
        db.commit()
    close_db(None)

@app.route("/", method=['POST'])
def index():
    g.url = session.get("url", "index")
    return render_template("index.html")


@app.route("/paints", methods=['GET', 'POST'])
def paints():
    g.url = session.get("url", "paints")
    form = CatalogForm()
    db = get_db()
    if form.validate_on_submit():
        paint_type = form.paint_type.data
        search = form.search.data
        if paint_type == "all" or not paint_type:
            paints = db.execute("SELECT * FROM paints WHERE paint_name LIKE ?;", ('%' + search + '%',)).fetchall()
        else:
            paints = db.execute("""SELECT * FROM paints WHERE paint_type = ? AND paint_name LIKE ?;""", (paint_type, '%' + search + '%')).fetchall()
    else:
        paints = db.execute("SELECT * FROM paints;").fetchall()
    return render_template("paints.html", paints=paints, form=form)

# --- PAINT function ---

@app.route("/paint/<int:paint_id>", methods=['GET', 'POST'])
def paint(paint_id):
    form = PaintForm()
    db = get_db()
    paint = db.execute("""
                SELECT * FROM paints
                WHERE paint_id = ?;""", (paint_id,)).fetchone()
    recommendations = recommendation(paint)
    if recommendations:
        return render_template("paint.html", paint=paint, form=form, recommendations=recommendations)
    return render_template("paint.html", paint=paint, form=form)


def recommendation(paint):
    db = get_db()
    paint_name = paint['paint_name']
    paint_name_parts = paint_name.split(",")
    if paint_name_parts:
        try:
            city = paint_name_parts[-2].strip()
            recommendations = db.execute("""
                        SELECT * FROM paints
                        WHERE paint_name LIKE ?
                        AND paint_name NOT LIKE ?;""", ('%' + city + '%', paint_name)).fetchall()
            return recommendations
        except:
            return
    return



# --- CART functions ---

@app.route("/cart",  methods=["GET", "POST"])
def cart():
    if g.user == None:
        return redirect(url_for("login"))
    if "cart" not in session:
        session["cart"] = {}
    names = {}
    db = get_db()
    for cart_id in session["cart"]:
        print(cart_id)
        print(session["cart"][cart_id])
        paint_id = session["cart"][cart_id]["paint_id"]
        paint = db.execute(
            "SELECT * FROM paints WHERE paint_id = ?;", (paint_id,)).fetchone()
        name = paint["paint_name"]
        paint_type = paint["paint_type"]
        names[paint_id] = name
        price = price_calculator(paint_type, session["cart"][cart_id]["quantity"], session["cart"][cart_id]["size"])
        session["cart"][cart_id]["price"] = price
    return render_template("cart.html", cart=session["cart"], names=names)

def price_calculator(paint_type, quantity, paint_size):
    quantity = int(quantity)
    price = 0
    if paint_type == "card":
        price = quantity * 4
    elif paint_type == "paint":
        if paint_size == "500x400mm":
            price = quantity * 200
        elif paint_size == "350x350mm":
            price = quantity * 150
        elif paint_size == "A1":
            price = quantity * 800
        elif paint_size == "A2":
            price = quantity * 600
        elif paint_size == "A3":
            price = quantity * 300
    elif paint_type == "print":
        if paint_size == "500x400mm":
            price = quantity * 30
        elif paint_size == "350x350mm":
            price = quantity * 15
        elif paint_size == "A1":
            price = quantity * 90
        elif paint_size == "A2":
            price = quantity * 70
        elif paint_size == "A3":
            price = quantity * 60
    return price


@app.route("/add_to_cart/<int:paint_id>", methods=['GET', 'POST'])
def add_to_cart(paint_id):
    form = PaintForm()
    paint_size = form.paint_size.data
    quantity = form.quantity.data
    # You said to write comment for code that I proud. It is cart_id. I find it really good solution for database problem. I saves me from creating 1000 objects in db.
    cart_id = str(paint_id) + "_" + str(paint_size)
    if "cart" not in session:
        session["cart"] = {}
    if cart_id not in session["cart"]:
        session["cart"][cart_id] = {"paint_id": paint_id,"quantity": quantity, "size": paint_size}
    else:
        session["cart"][cart_id]["quantity"] += int(quantity)
    return redirect(url_for("cart"))


@app.route("/remove_from_cart/<cart_id>")
def remove_from_cart(cart_id):
    session["cart"].pop(cart_id)
    return redirect(url_for("cart"))


@app.route("/increase_quantity/<cart_id>")
def increase_quantity(cart_id):
    session["cart"][cart_id]["quantity"] += 1
    return redirect(url_for("cart"))


@app.route("/decrease_quantity/<cart_id>")
def decrease_quantity(cart_id):
    if session["cart"][cart_id]["quantity"] > 1:
        session["cart"][cart_id]["quantity"] -= 1
    return redirect(url_for("cart"))
# --- End of CART functions ---

# # --- Order ---

@app.route("/order", methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()
    if form.validate_on_submit():
        db = get_db()
        order_details = ""
        total_price = 0
        for cart_id in session["cart"]:
            list = cart_id.split("_")
            paint_id = list[0]
            paint_size = list[1]
            paint = db.execute(
            "SELECT * FROM paints WHERE paint_id = ?;", (paint_id,)).fetchone()
            paint_name = paint["paint_name"]
            quantity = session["cart"][cart_id]["quantity"]
            price = session["cart"][cart_id]["price"]
            total_price += price
            row = str(paint_id) + "|" + str(paint_name) + "|"  + str(paint_size) + "|"  + str(quantity)+ "|"  + str(price)+ "\n"
            order_details += row
  
            
        customer_name = form.customer_name.data
        customer_surname = form.customer_surname.data
        customer_email = form.customer_email.data
        order_address = form.address.data
        comments = form.comments.data      
        user_id = g.user
        db.execute("""INSERT INTO orders (customer_name, user_id,customer_surname, customer_email, order_address, comments, order_details, total_price) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                   (customer_name, user_id,  customer_surname, customer_email, order_address, comments, order_details, total_price))
        db.commit()
        session.pop('cart', None)
        
        return render_template('order_confirmation.html', total_price=total_price)
        
    return render_template('order_page.html', form=form)


# --- End of Order ---


# --- Account functions ---

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationFrom()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        db = get_db()
        conflict_user = db.execute(
            """
            SELECT * FROM users
            WHERE user_id = ?;""", (user_id, )).fetchone()
        if conflict_user is not None:
            form.user_id.errors.append("User name already taken")
        else:
            db.execute("""
                       INSERT INTO users (user_id, password)
                       VALUES (?, ?);""",
                       (user_id, generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,)).fetchone()
        
        if user is None:
            form.user_id.errors.append("No such user name!")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect password!")
        else:
            session.clear()
            session["user_id"] = user_id
            session["is_admin"] = user["is_admin"] if "is_admin" in user.keys() else None
            return redirect(url_for("index"))
    return render_template("login.html", form=form)



@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        newPassword = form.newPassword.data
        oldPassword = form.oldPassword.data
        user_id = session["user_id"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

        if user and check_password_hash(user["password"], oldPassword):
            hashed_new_password = generate_password_hash(newPassword)
            db.execute("UPDATE users SET password = ? WHERE user_id = ?", (hashed_new_password, user_id))
            db.commit()
            flash("Your password was successfully changed.", "success")
        else:
            flash("Old password is incorrect.", "error")

    return redirect(url_for("account"))


@app.route("/change_username", methods=["GET", "POST"])
def change_username():
    form = ChangeUserForm()
    if form.validate_on_submit():
        password = form.password.data
        newName = form.newName.data
        user_id = session["user_id"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

        if user and check_password_hash(user["password"], password):
            db.execute("UPDATE users SET user_id = ? WHERE user_id = ?",(newName, user_id))
            session["user_id"] = newName
            flash("Your username was successfully changed.")
            #I also have to update user_id in order)))
            db.execute("""
                        UPDATE orders
                        SET user_id = ?
                        WHERE user_id = ?;
                        """, (newName, user_id))
            db.commit()
        else:
            flash("Password is incorrect.")
    return redirect(url_for("account"))


# I think this part is to bulky
@app.route("/account_orders")
@login_required
def account_orders():
    user_id = session.get("user_id")
    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY order_id DESC;", (user_id,)
    ).fetchall()

    orders_with_details = []
    for order in orders:
        order_dict = dict(order)
        parsed_order_details = []

        details = order_dict['order_details'].split("\n")
        for detail in details:
            if detail:
                parts = detail.split("|")
                if len(parts) >= 5:
                    parsed_order_details.append({
                        # I had strange problem with index, so I had to create dictionary with all details
                        'paint_id': parts[0],
                        'paint_name': parts[1],
                        'paint_size': parts[2],
                        'quantity': parts[3],
                        'price': parts[4]
                    })
        order_dict['parsed_order_details'] = parsed_order_details
        orders_with_details.append(order_dict)

    return render_template("account_orders.html", orders=orders_with_details)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/account")
def account():
    change_pass_form = ChangePasswordForm()
    ch_user_form = ChangeUserForm()
    return render_template("account.html", ChangePasswordForm=change_pass_form, ChangeUserForm=ch_user_form)


# --- END Account functions ---

# --- ADMIN FUNCTIONS ---
@app.route("/admin", methods=['GET', 'POST'])
@admin_required
def admin():
    add_product_form = AddProductForm()
    return render_template('admin_dashboard.html',add_product_form=add_product_form)


@app.route("/addProductForm", methods=['GET', 'POST'])
@admin_required
def addProductForm():
    
    form = AddProductForm()
    print(form.paint_name.data,form.paint_type.data,form.paint_description.data)
    if form.validate_on_submit():
        image = form.image.data
        paint_name = form.paint_name.data
        paint_city = form.paint_city.data
        paint_type = form.paint_type.data
        paint_description = form.paint_description.data
        if paint_city:
            paint_name+= ", " + paint_city.capitalize() + ", " + paint_type.capitalize()
        # START OF snapped code.
        # code for photo snapped from here: https://flask-wtf.readthedocs.io/en/0.15.x/form/
        image = form.image.data
        # secure_filename:https://medium.com/@sujathamudadla1213/what-is-the-use-of-secure-filename-in-flask-9eef4c71503b
        img_name = secure_filename(image.filename)
        image.save(os.path.join(os.getcwd(), 'static/img', img_name))
        # END of snapped code
        db = get_db()
        db.execute(
            "INSERT INTO paints (paint_name, paint_type, paint_description, img_name) VALUES (?, ?, ?, ?)",
            (paint_name, paint_type, paint_description, img_name)
        )
        db.commit()
        flash('Product successfully added!', 'success')
    return render_template("admin_dashboard.html", add_product_form=form)

@app.route("/seeOrderAdmin", methods=['GET', 'POST'])
@admin_required
def seeOrderAdmin():
    db = get_db()
    orders = db.execute("""
            SELECT * FROM orders""").fetchall()
    orders_with_details = []
    for order in orders:
        order_dict = dict(order)
        parsed_order_details = []

        details = order_dict['order_details'].split("\n")
        for detail in details:
            if detail:
                parts = detail.split("|")
                if len(parts) >= 5:
                    parsed_order_details.append({
                        # I had strange problem with index, so I had to create dictionary with all details
                        'paint_id': parts[0],
                        'paint_name': parts[1],
                        'paint_size': parts[2],
                        'quantity': parts[3],
                        'price': parts[4]
                    })
        order_dict['parsed_order_details'] = parsed_order_details
        orders_with_details.append(order_dict)
    return render_template("admin_orders.html", orders=orders_with_details)

@app.route("/removeOrder/<int:order_id>", methods=['GET', 'POST'])
@admin_required
def removeOrder(order_id):
    db = get_db()
    db.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
    db.commit()
    flash('Order removed successfully.', 'success')
    return redirect(url_for('seeOrderAdmin'))

@app.route("/removePaint/<int:paint_id>", methods=['GET', 'POST'])
@admin_required
def removePaint(paint_id):
    db = get_db()
    db.execute("DELETE FROM paints WHERE paint_id = ?", (paint_id,))
    db.commit()
    flash('Paint removed successfully.', 'success')
    return redirect(url_for('paints'))


@app.route("/Users")
@admin_required
def Users():
    db = get_db()
    users = db.execute("""
            SELECT * FROM users""").fetchall()
    return render_template("users.html", users=users)

@app.route("/removeUser/<user_id>", methods=['GET', 'POST'])
@admin_required
def removeUser(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    db.commit()
    flash('User removed successfully.', 'success')
    return redirect(url_for('Users'))

@app.route("/removeRandomUser", methods=['GET', 'POST'])
@admin_required
def removeRandomUser():
    db = get_db()
    users = db.execute("SELECT user_id FROM users").fetchall()
    if users:
        random_index = randint(0, len(users) - 1)
        user_id = users[random_index]['user_id']
        db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        db.commit()
        message = 'User '+(user_id)+' removed successfully.'
        flash(message, 'success')
    else:
        flash('No users to remove.', 'error')
    return redirect(url_for('Users'))
# --- END ADMIN functions ---