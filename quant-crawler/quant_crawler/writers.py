from pyutils import *
import quant_dbi.qdb

from quant_qdb.writer import QdbWriter, QdbStreamWriter, QdbMultiWriter

class QuantDbiWriter(QdbWriter):
    def __init__(self, stream=None, db=None, table=None, **kwargs):
        if stream is not None:
            table = quant_dbi.qdb.stream_to_table(stream)
        elif is_str(db):
            db = getattr(quant_dbi.qdb, db)
        super(QuantDbiWriter, self).__init__(db=db, table=table, **kwargs)

        
class QuantDbiMultiWriter(QdbMultiWriter):
    def __init__(self, streams=None, **kwargs):
        writers = {}
        for k, conf in streams.iteritems():
            w = QuantDbiWriter(**conf)
            writers[k] = w
        super(QuantDbiMultiWriter, self).__init__(writers, **kwargs)

        





