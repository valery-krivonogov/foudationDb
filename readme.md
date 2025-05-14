```
echo "docker:docker@127.0.0.1:4500,127.0.0.1:4501,127.0.0.1:4502" > fdb.cluster
fdbcli --exec "configure new double ssd"
```

fdb> status
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
  Server time            - 05/13/25 07:44:05

Data:
  Replication health     - Healthy
  Moving data            - 0.000 GB
  Sum of key-value sizes - 0 MB
  Disk space used        - 944 MB

Operating space:
  Storage server         - 901.5 GB free on most full server
  Log server             - 901.5 GB free on most full server

Workload:
  Read rate              - 13 Hz
  Write rate             - 0 Hz
  Transactions started   - 8 Hz
  Transactions committed - 0 Hz
  Conflict rate          - 0 Hz

Backup and DR:
  Running backups        - 0
  Running DRs            - 0

Client time: 05/13/25 07:44:05

fdb> status details

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

microdnf install pip

For fdb: 
pip install foundationdb

For API:
pip install virtualenv


mkdir ~/rest
cd  ~/rest
python -m venv ~/rest

```
import fdb

# Must run api_version() before anything else 740 is the newest version (does NOT match the version of the client installed)
fdb.api_version(740)

db = fdb.open('fdb.cluster')
db[b"hello"] = b"world"
print(db.get(b"hello"))
``` 