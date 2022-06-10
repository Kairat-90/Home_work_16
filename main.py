from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import data
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(300))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def main():
    db.create_all()
    insert_data()
    app.run(debug=True, port=8080)


def insert_data():
    users = data.users()
    new_users = []
    for user in users:
        new_users.append(
            User(
                id=user['id']
                , first_name=user['first_name']
                , last_name=user['last_name']
                , age=user['age']
                , email=user['email']
                , role=user['role']
                , phone=user['phone']
            )
        )

        with db.session.begin():
            db.session.add_all(new_users)

    orders = data.orders()
    new_orders = []
    for order in orders:
        new_orders.append(
            Order(
                id=order['id']
                , name=order['name']
                , description=order['description']
                , start_date=datetime.strptime(order['start_date'], '%m/%d/%Y')
                , end_date=datetime.strptime(order['end_date'], '%m/%d/%Y')
                , address=order['address']
                , price=order['price']
                , customer_id=order['customer_id']
                , executor_id=order['executor_id']
            )
        )

        with db.session.begin():
            db.session.add_all(new_orders)

    offers = data.offers()
    new_offers = []
    for offer in offers:
        new_offers.append(
            Offer(
                id=offer['id']
                , order_id=offer['order_id']
                , executor_id=offer['executor_id']
            )
        )

        with db.session.begin():
            db.session.add_all(new_offers)


@app.route('/users', methods=["GET", "POST"])
def page_users():
    if request.method == 'GET':
        data = []
        for user in User.query.all():
            data.append({
                'id': user.id
                , 'first_name': user.first_name
                , 'last_name': user.last_name
                , 'age': user.age
                , 'email': user.email
                , 'role': user.role
                , 'phone': user.phone
            })
        return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        new_users = User(
            first_name=data['first_name']
            , last_name=data['last_name']
            , age=data['age']
            , email=data['email']
            , role=data['role']
            , phone=data['phone']
        )

        with db.session.begin():
            db.session.add(new_users)


        return '', 200


@app.route('/users/<int:uid>', methods=["GET", "PUT", 'DELETE'])
def user_id(uid):
    if request.method == 'GET':
        user = User.query.get(uid)
        if user is None:
            return 'user not found'
        return jsonify({
            'id': user.id
            , 'first_name': user.first_name
            , 'last_name': user.last_name
            , 'age': user.age
            , 'email': user.email
            , 'role': user.role
            , 'phone': user.phone
        })

    elif request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(uid)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.age = data['age']
        user.email = data['email']
        user.role = data['role']
        user.phone = data['phone']

        db.session.add(user)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        user = Order.query.get(uid)
        db.session.delete(user)
        db.session.commit()

        return '', 203

@app.route('/orders', methods=['GET', 'POST'])
def page_orders():
    if request.method == 'GET':
        data = []
        for order in Order.query.all():
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            data.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executor
            })
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        new_order = Order(
            name=data['name']
            , description=data['description']
            , start_date=datetime.strptime(data['start_date'], '%m/%d/%Y')
            , end_date=datetime.strptime(data['end_date'], '%m/%d/%Y')
            , address=data['address']
            , price=data['price']
            , customer_id=data['customer_id']
            , executor_id=data['executor_id']
        )

        db.session.add(new_order)
        db.session.commit()

        return '', 200


@app.route('/orders/<int:uid>', methods=["GET", "PUT", 'DELETE'])
def order_id(uid):
    if request.method == 'GET':
        order = Order.query.get(uid)
        customer = User.query.get(order.customer_id).first_name if User.query.get(
            order.customer_id) else order.customer_id
        executor = User.query.get(order.executor_id).first_name if User.query.get(
            order.executor_id) else order.executor_id
        if order is None:
            return 'order not found'
        return jsonify({
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "address": order.address,
            "price": order.price,
            "customer_id": customer,
            "executor_id": executor
        })
    elif request.method == 'PUT':
        data = request.get_json()
        order = Order.query.get(uid)
        order.name = data['name']
        order.description = data['description']
        order.address = data['address']
        order.price = data['price']
        order.executor_id = data['executor_id']

        db.session.add(order)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        order = Order.query.get(uid)
        db.session.delete(order)
        db.session.commit()

        return '', 203

@app.route('/offers', methods=["GET", "POST"])
def page_offers():
    if request.method == 'GET':
        data = []
        for offer in Offer.query.all():
            data.append({
                'id': offer.id
                , 'order_id': offer.order_id
                , 'executor_id': offer.executor_id
            })
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        new_offer = Offer(
            order_id=data['order_id']
            , executor_id=data['executor_id']
        )
        with db.session.begin():
            db.session.add(new_offer)

        return '', 200


@app.route('/offers/<int:uid>', methods=["GET", "PUT", 'DELETE'])
def offer_id(uid):
    if request.method == 'GET':
        offer = Offer.query.get(uid)
        if offer is None:
            return 'offer not found'
        return jsonify({
            'id': offer.id
            , 'order_id': offer.order_id
            , 'executor_id': offer.executor_id
        })

    elif request.method == 'PUT':
        data = request.get_json()
        offer = Offer.query.get(uid)
        offer.order_id = data['order_id']
        offer.executor_id = data['executor_id']

        db.session.add(offer)
        db.session.commit()

        return '', 203

    elif request.method == 'DELETE':
        offer = Order.query.get(uid)
        db.session.delete(offer)
        db.session.commit()

        return '', 203


if __name__ == '__main__':
    main()