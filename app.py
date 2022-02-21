from flask import Flask, render_template, request, session
from pymongo import MongoClient
import re
import retrieve
import razorpay
from dotenv import load_dotenv
import os

load_dotenv()
key=os.getenv('key')
mongo_client=os.getenv('mongo_client')
app = Flask(__name__)
app.secret_key = key
client = MongoClient(mongo_client)
app.db = client.clickbait

@app.route('/')
def login_template():
    session['name'] = None
    session['email']=None
    return render_template('signin.html')


@app.route('/register')
def sign_up():
    return render_template('signup.html')


@app.route('/login', methods=['POST'])
def login():
    user_email = request.form['email']
    user_password = request.form['password']
    if app.db.user_details.find_one({"mail": user_email, "pass": user_password}):
        session['name'] = retrieve.name(user_email)
        session['email'] = user_email
        id, price, quantity, desc, product_name, image = retrieve.home_products()
        return render_template("home.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                               image=image)
    else:
        return render_template("signin.html", msg="a")


@app.route('/new_user', methods=['POST'])
def head_to_homepage():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    if name and email and password:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(regex, email):
            if app.db.user_details.find_one({"mail": email}) is None:
                session['name'] = name
                session['email'] = email
                app.db.user_details.insert_one({"name": name, "mail": email, "pass": password})
                id, price, quantity, desc, product_name, image = retrieve.home_products()
                return render_template("home.html", id=id, price=price, quantity=quantity, desc=desc,
                                       product_name=product_name, image=image)
    return render_template("signup.html", msg="a")


@app.route("/home/page", methods=['GET'])
def home_page():
    id, price, quantity, desc, product_name, image = retrieve.home_products()
    return render_template("home.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/clothing", methods=['GET'])
def clothing():
    id, price, quantity, desc, product_name, image = retrieve.product_details("clothing")
    return render_template("clothing.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/laptops", methods=['GET'])
def laptops():
    id, price, quantity, desc, product_name, image = retrieve.product_details("laptop")
    return render_template("laptops.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/mobiles", methods=['GET'])
def mobiles():
    id, price, quantity, desc, product_name, image = retrieve.product_details("mobile")
    return render_template("mobiles.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/shoes", methods=['GET'])
def shoes():
    id, price, quantity, desc, product_name, image = retrieve.product_details("shoes")
    return render_template("shoes.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/watches", methods=['GET'])
def watches():
    id, price, quantity, desc, product_name, image = retrieve.product_details("watch")
    return render_template("watches.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/contacts", methods=['GET'])
def contacts():
    return render_template("contact.html")


@app.route("/home/about", methods=['GET'])
def about():
    return render_template("about.html")


@app.route("/home/tnc", methods=['GET'])
def tnc():
    return render_template("tnc.html")


@app.route('/home/product/<id>', methods=['GET'])
def product(id):
    price, quantity, desc, product_name, image = retrieve.find_product(id)
    session['price']=price
    session['product_name']=product_name
    session['desc']=desc
    session['image']=image
    session['id']=id
    session['quantity']=quantity
    return render_template("product.html", id=id, price=price, quantity=quantity, desc=desc, product_name=product_name,
                           image=image)


@app.route("/home/orders", methods=['GET'])
def orders():
    products=retrieve.check_order(session['email'])
    if products==0:
        return render_template("orders.html",
                               message="You haven't made any purchases yet!! Do surf through our products and get the "
                                       "products that your eyes wants",
                               name=session['name'], email=session['email'])
    else:
        desc, product_name, image, count= retrieve.user_products(session['email'])
        return render_template("orders.html", desc=desc, product_name=product_name, image=image, count=count)


@app.route("/home/contacts/feedback", methods=['POST'])
def feedback():
    feedback = request.form['feedback']
    app.db.user_feedback.insert_one({"Feedback": feedback, "Given_from": session['email']})
    return render_template("contact.html", message="Thank you for your feedback!!")


@app.route("/home/contacts/product/payment", methods=['GET'])
def payment():
    if retrieve.get_quantity(session['id']):
        global payment
        client = razorpay.Client(auth=("rzp_test_aTSY11mldUwe2k", "W0PgGm9UCWuTl9gJbQDklvCg"))
        data = { "amount": session['price']*100, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)
        return render_template("pay.html",payment=payment,product_name=session['product_name'],image="https://image.shutterstock.com/image-vector/vector-illustration-word-clickbait-red-260nw-1668982222.jpg")
    else:
        return render_template("product.html", id=session['id'], price=session['price'], quantity=session['quantity'], desc=session['desc'], product_name=session['product_name'],
                           image=session['image'],message="The product is currently out of stock, Please come again later")


@app.route("/home/product/payment/successful", methods=['GET'])
def payment_success():
    retrieve.update_details(session['id'], session['desc'], session['product_name'],
                           session['image'],session['email'])
    session['quantity']=session['quantity']-1
    return render_template("product.html",id=session['id'], price=session['price'], quantity=session['quantity'], desc=session['desc'], product_name=session['product_name'],
                           image=session['image'], message="Your order has been placed successfully!!")