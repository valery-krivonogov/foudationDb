#!flask/bin/python
import fdb
from operator import itemgetter
from fdb.tuple import pack, unpack
import json
from flask import Flask, jsonify, abort, make_response, request
import uuid
from ast import literal_eval



app = Flask(__name__)

api_root = '/fdb/api/v1.0/prods'

products = [
    {
      "product_id": '4eae703b-fcee-4f60-ba3c-d9e10ad621e8',
      "title": "Футболка",
      "price": 400.25,
      "size": 42
    },
    {
      "product_id": 'cab5f2cf-83b5-40e8-929a-45963c7dba29',
      "title": "Футболка",
      "price": 200,
      "size": 43
    }
]

####################################################################################################
#                                             DB                                                   #
####################################################################################################

def connectDB():
    fdb.api_version(740)
    return fdb.open('/var/fdb/fdb.cluster')

db = connectDB()

@fdb.transactional
def add(tr, prod):
    prod_key = pack(('products', 'table', prod["product_id"]))
    ind1_key = pack(('products', 'ind1',  prod["title"], prod["price"], prod["product_id"]))
    ind2_key = pack(('products', 'ind2',  prod["title"], prod["size"],  prod["product_id"]))
    buf =  json.dumps(prod).encode()
    tr.set(prod_key, buf)
    tr.set(ind1_key, b'')
    tr.set(ind2_key, b'')

@fdb.transactional
def delete(tr, product_id):
    prod_key = pack(('products', 'table', product_id))
    buf = tr.get(prod_key)
    prod = literal_eval(buf.decode('utf-8'))
    ind1_key = pack(('products', 'ind1',  prod["title"], prod["price"], product_id))
    ind2_key = pack(('products', 'ind2',  prod["title"], prod["size"],  product_id))
    tr.clear(ind1_key)
    tr.clear(ind2_key)
    tr.clear(prod_key)

@fdb.transactional
def update(tr, prod_new):
    prod_key = pack(('products', 'table', prod_new["product_id"]))
    # удаление старых индексов
    buf = tr.get(prod_key)
    prod = literal_eval(buf.decode('utf-8'))
    ind1_key = pack(('products', 'ind1',  prod["title"], prod["price"], prod["product_id"]))
    ind2_key = pack(('products', 'ind2',  prod["title"], prod["size"],  prod["product_id"]))
    tr.clear(ind1_key)
    tr.clear(ind2_key)
    # формирование новых индексов
    ind1_key = pack(('products', 'ind1',  prod_new["title"], prod_new["price"], prod_new["product_id"]))
    ind2_key = pack(('products', 'ind2',  prod_new["title"], prod_new["size"],  prod_new["product_id"]))
    tr.set(ind1_key, b'')
    tr.set(ind2_key, b'')
    # обновление записи
    buf =  json.dumps(prod_new).encode()
    tr.set(prod_key, buf)

@fdb.transactional
def getProdByNameAndPrice(tr, title, price):
    res = []
    iterator = tr.get_range_startswith(pack(('products', 'ind1', title, )), reverse=False)
    for key, _ in iterator:
        ind = unpack(key)
        if ind[3] < price:
            res.append(ind[4])
    return res

@fdb.transactional
def getProdByNameAndSize(tr, title, size):
    res = []
    iterator = tr.get_range_startswith(pack(('products', 'ind2', title, )), reverse=False)
    for key, _ in iterator:
        ind = unpack(key)
        if ind[3] == size:
            res.append(ind[4])
    return res

@fdb.transactional
def getProdList(tr, prodIsList):
    res = []
    for rec in prodIsList:
        prod_key = pack(('products', 'table', rec))
        buf = tr.get(prod_key)
        prod = literal_eval(buf.decode('utf-8'))
        res.append(prod)
    return res

@fdb.transactional
def getProdAll(tr):
    res = []
    iterator = tr.get_range_startswith(pack(('products', 'table',  )), reverse=False)
    for key, _ in iterator:
        ind = unpack(key)
        res.append(ind[2])
    return res

@fdb.transactional
def getProdById(tr, prod_id):
    res = []
    iterator = tr.get_range_startswith(pack(('products', 'table', prod_id  )), reverse=False)
    for key, _ in iterator:
        ind = unpack(key)
        res.append(ind[2])
    return res

####################################################################################################
#                                             REST API                                             #
####################################################################################################

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route(api_root, methods=['GET'])
def get_all_prod():
    prods = getProdAll(db)
    result = getProdList(db, prods)
    return jsonify({'Result': result})

@app.route(api_root+'/<string:prod_id>', methods=['GET'])
def get_prod(prod_id):
    prods = getProdById(db, prod_id)
    if len(prods) == 0:
        abort(404)
    result = getProdList(db, prods)
    return jsonify({'Result': result})

@app.route(api_root+'/getProdNamePrice/<string:title>/<int:price>', methods=['GET'])
def getProdNamePrice(title,price):
    prods = getProdByNameAndPrice(db,title, price)
    if len(prods) == 0:
        abort(404)
    result = getProdList(db, prods)
    return jsonify({'Result': result})

@app.route(api_root+'/getProdNameSize/<string:title>/<int:size>', methods=['GET'])
def getProdNameSize(title,size):
    prods = getProdByNameAndSize(db,title, price)
    if len(prods) == 0:
        abort(404)
    result = getProdList(db, prods)
    return jsonify({'Result': result})


@app.route(api_root, methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    pr = {
      "product_id": str(uuid.uuid4()),
      "title": request.json['title'],
      "price": request.json['price'],
      "size":  request.json['size']
    }
    add(db,pr)
    return jsonify({'Result': pr}), 201

@app.route(api_root+'/<string:prod_id>', methods=['PUT'])
def update_task(prod_id):
    prod = list(filter(lambda t: t['product_id'] == prod_id, products))
    prod[0]['title']       = request.json.get('title', prod[0]['title'])
    prod[0]['description'] = request.json.get('description', prod[0]['description'])
    prod[0]['done']        = request.json.get('done', prod[0]['done'])
   
    # update 
    return jsonify({'task': task[0]})

@app.route(api_root+'/<string:prod_id>', methods=['DELETE'])
def delete_task(prod_id):
    delete(db,prod_id)
    return jsonify({'Result': True})

if __name__ == '__main__':
    db = connectDB()
    app.run(debug=True)