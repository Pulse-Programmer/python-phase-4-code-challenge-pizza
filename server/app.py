#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    if restaurants:
        body = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]
        status = 200
    else:
        body = {"error": "No restaurants found"}
        status = 404

    return make_response(body, status)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        body = restaurant.to_dict()
        status = 200
    else:
        body = {"error": "Restaurant not found"}
        status = 404
        
    return make_response(body, status)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        body = {"message": "Restaurant deleted"}
        status = 204
    else:
        body = {"error": "Restaurant not found"}
        status = 404
        
    return make_response(body, status)

#GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    if pizzas:
        body = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
        status = 200
    else:
        body = {"error": "No pizzas found"}
        status = 404

    return make_response(body, status)

#POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizzas():
    data = request.get_json()
    if data:
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if price and pizza_id and restaurant_id:
            try:
                restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
                db.session.add(restaurant_pizza)
                db.session.commit()
                body = restaurant_pizza.to_dict()
                status = 201
            except ValueError:
                body = {"errors": ["validation errors"]}
                status = 400
        else:
            body = {"errors": ["validation errors"]}  # "error": "Missing required fields"
            status = 400
    else:
        body = {"errors": ["validation errors"]}    # "error": "Missing JSON data"
        status = 400

    return make_response(body, status)
    



if __name__ == "__main__":
    app.run(port=5555, debug=True)
