import unicodedata
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

import iris

app = Flask(__name__)

# ----------------------------------------------------------------
### ECHO
# ----------------------------------------------------------------

@app.route("/", methods=["GET"])
def get_info():
    """
    It returns a JSON object with a single key-value pair
    :return: A JSON object with the version number of the API.
    """
    info = {'version':'1.0.6'}
    return jsonify(info)

# ----------------------------------------------------------------
### IRIS KAFKA
# ----------------------------------------------------------------


connection = iris.createConnection("iris", 1972, "USER", "SuperUser", "SYS", sharedmemory = False)

@app.route("/kafka/", methods=["POST"])
def post_kafka():
    """
    It sends X messages to the Kafka topic 'test'.
    """
    if not request.json:
        return jsonify({'message': 'No input data provided'}), 400
    if 'round' not in request.json:
        return jsonify({'message': 'No round var provided'}), 400

    irisInstance = iris.IRIS(connection)

    service = irisInstance.classMethodObject("EnsLib.PEX.Director","dispatchCreateBusinessService","FlaskService")

    service.invokeObject("ProcessInput",request.json['round'])

    return jsonify({'message': f"{request.json['round']} round(s) of kafka sended"}), 200

# ----------------------------------------------------------------
### SIMPLE CRUD
# ----------------------------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  content = db.Column(db.String(120), nullable=False)

  def serialize(self):
    return {
      'id': self.id,
      'title': self.title,
      'content': self.content
    }

  def __init__(self, title, content):
    self.title = title
    self.content = content

db.create_all()

## get item by id
@app.route("/items/<int:id>", methods=["GET"])
def get_item(id):
    item = Item.query.get(id)
    if item is None:
        return jsonify({'message': 'Item not found'}), 404
    return jsonify(item.serialize())

#get all items
@app.route("/items/", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify([item.serialize() for item in items])

#post item
@app.route("/items/", methods=["POST"])
def post_item():
    if not request.json or not 'title' in request.json or not 'content' in request.json:
        return jsonify({'message': 'No input data provided'}), 400
    item = Item(request.json['title'], request.json['content'])
    db.session.add(item)
    db.session.commit()
    return jsonify(item.serialize()), 201

#put item
@app.route("/items/<int:id>", methods=["PUT"])
def put_item(id):
    item = Item.query.get(id)
    if item is None:
        return jsonify({'message': 'Item not found'}), 404
    if not request.json:
        return jsonify({'message': 'No input data provided'}), 400
    if 'title' in request.json and type(request.json['title']) is not str:
        return jsonify({'message': 'Title must be a string'}), 400
    if 'content' in request.json and type(request.json['content']) is not str:
        return jsonify({'message': 'Content must be a string.'}), 400
    item.title = request.json.get('title', item.title)
    item.content = request.json.get('content', item.content)
    db.session.commit()
    return jsonify(item.serialize())

#delete item
@app.route("/items/<int:id>", methods=["DELETE"])
def delete_item(id):
    item = Item.query.get(id)
    if item is None:
        return jsonify({'message': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})

@app.route('/items/<id>', methods=['PATCH'])
def patch_item(id):
    """
    It updates the content of the item with the id provided.
    """
    body = request.get_json()
    item = Item.query.get(id)
    if 'title' in body:
        item.title = body['title']
    if 'content' in body:
        item.content = body['content']
    db.session.commit()
    return jsonify({'message': 'Item updated'}), 200


# ----------------------------------------------------------------
### MAIN PROGRAM
# ----------------------------------------------------------------

if __name__ == '__main__':
    app.run('0.0.0.0', port = "80")