from fileinput import close
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo_client=os.getenv('mongo_client')

def product_details(product):
    product_name = []
    id = []
    image = []
    price = []
    quantity = []
    desc = []
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    results = app.db.products.find({"product_type": product})
    for result in results:
        for key, value in result.items():
            if key == "id":
                id.append(value)
            elif key == "Price":
                price.append(value)
            elif key == "quantity":
                quantity.append(value)
            elif key == "desc":
                desc.append(value)
            elif key == "Product_name":
                product_name.append(value)
            elif key == "image":
                image.append(value)
    return id, price, quantity, desc, product_name, image


def home_products():
    product_name = []
    id = []
    image = []
    price = []
    quantity = []
    desc = []
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    products = ["mobile", "laptop", "shoes", "watch", "clothing"]
    for product in products:
        result = app.db.products.find_one({"product_type": product})
        for key, value in result.items():
            if key == "id":
                id.append(value)
            elif key == "Price":
                price.append(value)
            elif key == "quantity":
                quantity.append(value)
            elif key == "desc":
                desc.append(value)
            elif key == "Product_name":
                product_name.append(value)
            elif key == "image":
                image.append(value)
    return id, price, quantity, desc, product_name, image


def find_product(id):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    product = app.db.products.find_one({"id": id})
    for key, value in product.items():
        if key == "Price":
            price = value
        elif key == "quantity":
            quantity = value
        elif key == "desc":
            desc = value
        elif key == "Product_name":
            product_name = value
        elif key == "image":
            image = value
    return price, quantity, desc, product_name, image


def name(email):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    user = app.db.user_details.find_one({"mail": email})
    for key, value in user.items():
        if key == "name":
            return value


def user_products(email):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    products = app.db.order_details.find({})
    desc = []
    product_name = []
    image = []
    count = 1
    try:
        for key,value in products.items():
            if key == "desc":
                desc.append(value)
            elif key == "product_name":
                product_name.append(value)
            elif key == "image":
                image.append(value)
    except:
        desc = []
        product_name = []
        image = []
        count=0
        for product in products:
            if product["mail"]==email:
                count+=1
                for key, value in product.items():
                    if key == "desc":
                        desc.append(value)
                    elif key == "product_name":
                        product_name.append(value)
                    elif key == "image":
                        image.append(value)
    finally:
        return desc, product_name, image,count


def check_order(email):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    result = app.db.order_details.find_one({"mail": email})
    if result is None:
        return 0
    else:
        return 1


def get_quantity(id):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    product=app.db.products.find_one({"id":id})
    if product['quantity']>=1:
        return 1
    else:
        return 0


def update_details(id,desc,product_name,image,email):
    app = Flask(__name__)
    client = MongoClient(mongo_client)
    app.db = client.clickbait
    product=app.db.products.find_one({"id":id})
    app.db.products.update_one({"id":id},{"$set": { 'quantity': (product['quantity']-1) }})
    app.db.order_details.insert_one({"mail": email, "desc": desc, "product_name": product_name,"image":image})