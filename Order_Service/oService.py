from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import requests, os
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
CORS(app)
db = SQLAlchemy(app)

USER_SERVICE_URL = "http://user_service:5001/users"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product = db.Column(db.String(100), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product": self.product
        }

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(os.path.join(os.getcwd(), 'Order_Service/static'), path)  # Corrected path

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Corrected path

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Microservices"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    result = [order.to_json() for order in orders]
    return jsonify(result)

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify(order.to_json())
    return jsonify({'error': 'Order not found'}), 404

@app.route('/order', methods=['POST'])
def create_order():
    data = request.json
    user_id = data.get('user_id')

    # Verify user exists in User Service
    user_response = requests.get(f"{USER_SERVICE_URL}/{user_id}")
    if user_response.status_code != 200:
        return jsonify({'error': 'User not found'}), 404

    new_order = Order(user_id=user_id, product=data['product'])
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order created', 'order': new_order.to_json()}), 201

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    data = request.json
    order.product = data.get('product', order.product)  # Update product if provided

    db.session.commit()
    return jsonify({'message': 'Order updated', 'order': order.to_json()})

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)
