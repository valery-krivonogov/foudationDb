import fdb
from operator import itemgetter
from fdb.tuple import pack, unpack
import json
import uuid
from ast import literal_eval
from flask import jsonify

products = [
    {
      "product_id": '4eae703b-fcee-4f60-ba3c-d9e10ad621e8',
      "title": "Футболка",
      "price": 400.25,
      "size": 48
    },
    {
      "product_id": '1b2cf956-79ec-4da1-a594-0bdda9bd3da4',
      "title": "Футболка",
      "price": 620.00,
      "size": 54
    },
    {
      "product_id": 'ed2832ee-a9ef-4410-a9b8-2894c52d1773',
      "title": "Носки",
      "price": 25,
      "size": 42
    }
]

fdb.api_version(740)
db = fdb.open('/var/fdb/fdb.cluster')

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


# main code
for pr in products:
    add(db,pr)
    prod_key = pack(('products', 'table', pr["product_id"]))
    print(db.get(prod_key))

prods = getProdByNameAndPrice(db,"Футболка", 500)
result = getProdList(db, prods)
print("find jersey:",  result)

prods = getProdByNameAndSize(db,"Носки", 42)
result = getProdList(db, prods)
print("find socks:",  result)

prod_new = products[0]
prod_new["price"] = 300
prod_new["size"]  = 45
update(db,prod_new)
print(db.get(b'\x02products\x00\x02table\x00\x024eae703b-fcee-4f60-ba3c-d9e10ad621e8\x00'))

delete(db,'4eae703b-fcee-4f60-ba3c-d9e10ad621e8')
print(db.get(b'\x02products\x00\x02table\x00\x024eae703b-fcee-4f60-ba3c-d9e10ad621e8\x00'))

print("test OK")
