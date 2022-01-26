from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import json

import raw_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///16homework.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone
        }


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order = db.relationship("Order")
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        }


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id
        }


db.drop_all()
db.create_all()

users_list = []
for user_data in raw_data.users:
    new_user = User(id=user_data["id"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    age=user_data["age"],
                    email=user_data["email"],
                    role=user_data["role"],
                    phone=user_data["phone"])

    users_list.append(new_user)

orders_list = []
for order_data in raw_data.orders:
    new_order = Order(
        id=order_data["id"],
        name=order_data["name"],
        description=order_data["description"],
        start_date=order_data["start_date"],
        end_date=order_data["end_date"],
        address=order_data["address"],
        price=order_data["price"],
        customer_id=order_data["customer_id"],
        executor_id=order_data["executor_id"])

    orders_list.append(new_order)

offers_list = []
for offer_data in raw_data.offers:
    new_offer = Offer(
        id=offer_data["id"],
        order_id=offer_data["order_id"],
        executor_id=offer_data["executor_id"])
    offers_list.append(new_offer)

    db.session.add_all(users_list)
    db.session.add_all(orders_list)
    db.session.add_all(offers_list)
    db.session.commit()


@app.route("/users/", methods=["GET", "POST"])
def users():
    if request.method == "GET":
        result = []
        for usr in User.query.all():
            result.append(usr.to_dict())
        return json.dumps(result), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "POST":
        user_data = json.load(request.data)
        new_user = User(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    age=user_data["age"],
                    email=user_data["email"],
                    role=user_data["role"],
                    phone=user_data["phone"])
        db.session.add(new_user)
        db.session.commit()

        return "Пользователь добавлен", 201


@app.route("/users/<int:uid>", methods=["GET", "POST", "PUT", "DELETE"])
def get_user(uid: int):
    if request.method == "GET":
        return json.dumps(User.query.get(uid).to_dict()), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "DELETE":
        usr = User.query.get(uid)
        db.session.delete(usr)
        db.session.commit()
        return "Пользователь удален", 204
    elif request.method == "PUT":
        user_data = json.loads(request.data)
        usr = User.query.get(uid)
        usr.first_name = user_data["first_name"]
        usr.last_name = user_data["last_name"]
        usr.age = user_data["age"]
        usr.email = user_data["email"]
        usr.role = user_data["role"]
        usr.phone = user_data["phone"]
        db.session.add(usr)
        db.session.commit()
        return "Изменения сохранены", 204


@app.route("/oders/", methods=["GET", "POST"])
def orders():
    if request.method == "GET":
        result = []
        for order in Order.query.all():
            result.append(order.to_dict())
        return json.dumps(result), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "POST":
        order_data = json.load(request.data)
        new_order = Order(
            name=order_data["name"],
            description=order_data["description"],
            start_date=order_data["start_date"],
            end_date=order_data["end_date"],
            address=order_data["address"],
            price=order_data["price"],
            customer_id=order_data["customer_id"],
            executor_id=order_data["executor_id"])
        db.session.add(new_order)
        db.session.commit()
        return "Заказ добавлен", 201


@app.route("/orders/<int:uid>", methods=["GET", "POST", "PUT", "DELETE"])
def get_order(uid: int):
    if request.method == "GET":
        return json.dumps(Order.query.get(uid).to_dict()), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "DELETE":
        order = Order.query.get(uid)
        db.session.delete(order)
        db.session.commit()
        return "Заказ удален", 204
    elif request.method == "PUT":
        order_data = json.loads(request.data)
        order = Order.query.get(uid)
        order.name = order_data["name"],
        order.description = order_data["description"]
        order.start_date = order_data["start_date"]
        order.end_date = order_data["end_date"]
        order.address = order_data["address"]
        order.price = order_data["price"]
        order.customer_id = order_data["customer_id"]
        order.executor_id = order_data["executor_id"]
        db.session.add(order)
        db.session.commit()
        return "Изменения сохранены", 204


@app.route("/offers/", methods=["GET", "POST"])
def offers():
    if request.method == "GET":
        result = []
        for offer in Offer.query.all():
            result.append(offer.to_dict())
        return json.dumps(result), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "POST":
        offer_data = json.load(request.data)
        new_offer = User(
            order_id=offer_data["order_id"],
            executor_id=offer_data["executor_id"])
        db.session.add(new_offer)
        db.session.commit()

        return "Предложение добавлено", 201


@app.route("/offers/<int:uid>", methods=["GET", "POST", "PUT", "DELETE"])
def get_offer(uid: int):
    if request.method == "GET":
        return json.dumps(Offer.query.get(uid).to_dict()), 200, {"Content-type": 'application/json; charset=utf-8'}
    elif request.method == "DELETE":
        offer = Offer.query.get(uid)
        db.session.delete(offer)
        db.session.commit()
        return "Предложение удалено", 204
    elif request.method == "PUT":
        offer_data = json.loads(request.data)
        offer = Offer.query.get(uid)
        offer.order_id = offer_data["order_id"]
        offer.executor_id = offer_data["executor_id"]
        db.session.add(offer)
        db.session.commit()
        return "Изменения сохранены", 204


if __name__ == '__main__':
    app.run()
