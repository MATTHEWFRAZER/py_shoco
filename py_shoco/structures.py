class Structure(object):
    def __init__(self, datalist):
        self.datalist = list(datalist)

    @property
    def header(self):
        return self.datalist[0]

    @property
    def lead(self):
        return self.datalist[1]

    @property
    def successors(self):
        return self.datalist[2:]

    @property
    def consecutive(self):
        return self.datalist[1:]


class Bits(Structure):
    def __init__(self, bitlist):
        Structure.__init__(self, bitlist)

class Masks(Structure):
    def __init__(self, bitlist):
        Structure.__init__(self, [((1 << bits) -1) for bits in bitlist])

class Offsets(Structure):
    def __init__(self, bitlist):
        inverse = self.accumulate(bitlist)
        offsets = [32 - offset for offset in inverse]
        Structure.__init__(self, offsets)

    @staticmethod
    def accumulate(seq):
        total = 0
        for elem in seq:
            total += elem
            yield total