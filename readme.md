### Запуск сервера foudationDb в docker


Настройка:
```
echo "docker:docker@127.0.0.1:4500,127.0.0.1:4501,127.0.0.1:4502" > fdb.cluster
fdbcli --exec "configure new double ssd"
```

fdb> status details
```
Using cluster file `/var/fdb/fdb.cluster'.

Configuration:
  Redundancy mode        - double
  Storage engine         - ssd-2
  Log engine             - ssd-2
  Encryption at-rest     - disabled
  Coordinators           - 3
  Usable Regions         - 1

Cluster:
  FoundationDB processes - 6
  Zones                  - 6
  Machines               - 6
  Memory availability    - 6.5 GB per process on machine with least available
  Fault Tolerance        - 1 machines
  Server time            - 05/13/25 07:44:46

Data:
  Replication health     - Healthy
  Moving data            - 0.000 GB
  Sum of key-value sizes - 0 MB
  Disk space used        - 944 MB

Operating space:
  Storage server         - 901.5 GB free on most full server
  Log server             - 901.5 GB free on most full server

Workload:
  Read rate              - 9 Hz
  Write rate             - 0 Hz
  Transactions started   - 4 Hz
  Transactions committed - 0 Hz
  Conflict rate          - 0 Hz

Backup and DR:
  Running backups        - 0
  Running DRs            - 0

Process performance details:
  172.26.0.2:4502        (  2% cpu;  4% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )
  172.26.0.3:4501        (  5% cpu;  5% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )
  172.26.0.4:4500        (  4% cpu;  5% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )
  172.26.0.5:4510        (  2% cpu;  5% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )
  172.26.0.6:4511        (  2% cpu;  5% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )
  172.26.0.7:4512        (  2% cpu;  5% machine; 0.000 Gbps;  6% disk IO; 0.1 GB / 6.5 GB RAM  )

Coordination servers:
  fdb-coord-1:4500  (reachable)
  fdb-coord-2:4501  (reachable)
  fdb-coord-3:4502  (reachable)

Client time: 05/13/25 07:44:46

fdb> writemode on
```

### Install python packages
Настройка виртуального окружения
```
microdnf install pip
pip install virtualenv
mkdir ~/rest
cd  ~/rest
python -m venv ~/rest
```

Активация окружения:
```
source ~/rest/bin/activate
```


For fdb: 
```
pip install foundationdb
```

For API:
```
pip install flask
```
Проверка доступности сервера
```
import fdb

fdb.api_version(740)
db = fdb.open('fdb.cluster')
db[b"hello"] = b"world"
print(db.get(b"hello"))
``` 
## Запуск и тестирование сервиса RestAPI

Запуск

python app.py
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 658-990-418
```

###  Проверка сервиса

Список продуктов в базе<br/>
curl -i http://localhost:5000/fdb/api/v1.0/prods

```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.9.21
Date: Wed, 14 May 2025 18:27:07 GMT
Content-Type: application/json
Content-Length: 538
Connection: close

{
  "Result": [
    {
      "price": 620.0,
      "product_id": "1b2cf956-79ec-4da1-a594-0bdda9bd3da4",
      "size": 54,
      "title": "\u0424\u0443\u0442\u0431\u043e\u043b\u043a\u0430"
    },
    {
      "price": 400.25,
      "product_id": "4eae703b-fcee-4f60-ba3c-d9e10ad621e8",
      "size": 48,
      "title": "\u0424\u0443\u0442\u0431\u043e\u043b\u043a\u0430"
    },
    {
      "price": 25,
      "product_id": "ed2832ee-a9ef-4410-a9b8-2894c52d1773",
      "size": 42,
      "title": "\u041d\u043e\u0441\u043a\u0438"
    }
  ]
}
```

Получения сведений о продукте по ключу<br/>

curl -i http://localhost:5000/fdb/api/v1.0/prods/ed2832ee-a9ef-4410-a9b8-2894c52d1773
```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.9.21
Date: Wed, 14 May 2025 18:35:15 GMT
Content-Type: application/json
Content-Length: 179
Connection: close

{
  "Result": [
    {
      "price": 25,
      "product_id": "ed2832ee-a9ef-4410-a9b8-2894c52d1773",
      "size": 42,
      "title": "\u041d\u043e\u0441\u043a\u0438"
    }
  ]
}
```
Создание продукта<br/>

curl -i -H "Content-Type: application/json" -X POST -d '{"price": 24, "size": 39, "title": "\u041d\u043e\u0441\u043a\u0438"}' http://localhost:5000/fdb/api/v1.0/prods
```
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.3 Python/3.9.21
Date: Wed, 14 May 2025 19:03:09 GMT
Content-Type: application/json
Content-Length: 159
Connection: close

{
  "Result": {
    "price": 24,
    "product_id": "318c49e7-a78e-4a17-abcb-930d6ed71ea7",
    "size": 39,
    "title": "\u041d\u043e\u0441\u043a\u0438"
  }
}
```
Удаление продукта<br/>
curl -i -H "Content-Type: application/json" -X DELETE -d '{}' http://localhost:5000/fdb/api/v1.0/prods/318c49e7-a78e-4a17-abcb-930d6ed71ea7
```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.9.21
Date: Wed, 14 May 2025 19:07:14 GMT
Content-Type: application/json
Content-Length: 21
Connection: close

{
  "Result": true
}
```
