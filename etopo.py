from numpy import memmap

class Earth(object):
    base = 'ETOPO2v2c_i2_LSB'
    datatypes = { '2_BYTE_INTEGER' : 'int16' }

    def __init__(self):
        with open(self.base + '.hdr', 'r') as h:
            header = dict([tuple(l.strip().split()) for l in h.readlines()])
        
        self.data = memmap(self.base + '.bin',
                           dtype=self.datatypes[header['NUMBERTYPE']],
                           mode='r',
                           shape=tuple([int(header[key])
                                            for key in 'NCOLS','NROWS']))
        self.bad = int(header['NODATA_VALUE'])

    def sample(self, latitude, longitude):
        value = self.data[int(latitude*30)][int(longitude*30)]
        return value if value != self.bad else None