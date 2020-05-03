from py_shoco.structures import Bits, Masks, Offsets


class Encoding(object):
    def __init__(self, bitlist):
        self.bits = Bits(bitlist)
        self.masks = Masks(bitlist)
        self.offsets = Offsets(bitlist)
        self.packed = sum(bitlist) / 8
        self.size = len([bits for bits in bitlist if bits])
        self.unpacked = self.size - 1
        self._hash = tuple(bitlist).__hash__()

    @property
    def header_code(self):
        return ((1 << self.bits.header) - 2) << (8 - self.bits.header)

    @property
    def header_mask(self):
        return self.masks.header << (8 - self.bits.header)

    @property
    def word(self):
        return ((1 << self.bits.header) - 2) << self.offsets.header

    def __hash__(self):
        return self._hash

    def can_encode(self, part, successors, chrs_indices):
        lead_index = chrs_indices.get(part[0], -1)
        if lead_index < 0:
            return False
        if lead_index > (1 << self.bits.header):
            return False
        last_index = lead_index
        last_char = part[0]
        for bits, char in zip(self.bits.consecutive, part[1:]):
            if char not in successors[last_char]:
                return False
            successor_index = successors[last_char].index(char)
            if successor_index > (1 << bits):
                return False
            last_index = successor_index
            last_char = part[0]
            return True
