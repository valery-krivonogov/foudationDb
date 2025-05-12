from   datetime import datetime

import fdb
from   fdb.tuple import pack, unpack
import pandas as pd


fdb.api_version(510)


@fdb.transactional
def get_score(tr, user):
    user_key = pack(('scores', user))
    score = tr.get(user_key)

    if score == None:
        score = 0
        tr.set(user_key, pack((score,)))
        tr.set(pack(('leaderboard', score, user)), b'')
    else:
        score = unpack(score)[0]

    return score


@fdb.transactional
def add(tr, user, increment=1):
    score = get_score(tr, user)
    total = score + increment
    user_key = pack(('scores', user))

    tr.set(user_key, pack((total,)))
    tr.clear(pack(('leaderboard', score, user)))
    tr.set(pack(('leaderboard', total, user)), b'')

    return total


cols = ['trip_id',
        'vendor_id',
        'pickup_datetime',
        'dropoff_datetime',
        'store_and_fwd_flag',
        'rate_code_id',
        'pickup_longitude',
        'pickup_latitude',
        'dropoff_longitude',
        'dropoff_latitude',
        'passenger_count',
        'trip_distance',
        'fare_amount',
        'extra',
        'mta_tax',
        'tip_amount',
        'tolls_amount',
        'ehail_fee',
        'improvement_surcharge',
        'total_amount',
        'payment_type',
        'trip_type',
        'pickup',
        'dropoff',
        'cab_type',
        'precipitation',
        'snow_depth',
        'snowfall',
        'max_temperature',
        'min_temperature',
        'average_wind_speed',
        'pickup_nyct2010_gid',
        'pickup_ctlabel',
        'pickup_borocode',
        'pickup_boroname',
        'pickup_ct2010',
        'pickup_boroct2010',
        'pickup_cdeligibil',
        'pickup_ntacode',
        'pickup_ntaname',
        'pickup_puma',
        'dropoff_nyct2010_gid',
        'dropoff_ctlabel',
        'dropoff_borocode',
        'dropoff_boroname',
        'dropoff_ct2010',
        'dropoff_boroct2010',
        'dropoff_cdeligibil',
        'dropoff_ntacode',
        'dropoff_ntaname',
        'dropoff_puma']

db = fdb.open()
counter, start = 0, datetime.utcnow()

for chunk in pd.read_csv('trips_xaa.csv.gz',
                         header=None,
                         chunksize=10000,
                         names=cols,
                         usecols=['total_amount',
                                  'pickup_ntaname']):
    for x in range(0, len(chunk)):
        add(db,
            chunk.iloc[x].pickup_ntaname,
            chunk.iloc[x].total_amount)
    counter = counter + 1
    print (counter * 10000) / (datetime.utcnow() - start).total_seconds()
