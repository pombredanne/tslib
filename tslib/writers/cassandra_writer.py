import json
import pycassa
import pytz


INTERNAL_TIMEZONE = pytz.UTC


class CassandraWriter(object):

    def __init__(self, nodes, keyspace, column_family, queue_size):
        pool = pycassa.ConnectionPool(keyspace=keyspace, server_list=nodes,
            prefill=False)
        self.cf = pycassa.ColumnFamily(pool, column_family)
        self.qs = queue_size

    def write(self, dataframes):
        key_format = '%Y-%m'
        colname_format = '%Y-%m-%dT%H:%M:%SZ'
        i = 0
        with self.cf.batch(queue_size=self.qs) as b:
            for df in dataframes:
                sensor_id = 'pixml-test-%d' % i
                for timestamp, row in df.iterrows():
                    ts_int = timestamp.astimezone(INTERNAL_TIMEZONE)
                    b.insert(
                        ts_int.strftime(sensor_id + ':' + key_format),
                        dict(("%s_%s" % (ts_int.strftime(colname_format), k),
                              str(v)) for k, v in row.to_dict().iteritems())
                    )
                i += 1
