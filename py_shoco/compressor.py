import ctypes

from py_shoco.code import Code
from py_shoco.constants import ENCODING_TYPES

__all__ = ["Compressor"]

class Compressor(object):
    def __init__(self, successor_table, packs):
        self.successor_table = successor_table
        self.chr_ids_by_chr = self.successor_table.chr_ids_by_chr
        self.successor_ids_by_chr_id_and_chr_id = self.successor_table.successor_ids_by_chr_id_and_chr_id
        self.max_successor_len = self.successor_table.max_successor_len
        self.packs = packs

    def compress(self, original, original_length, out, out_length):
        out_offset = 0
        original_offset = 0
        code = Code()

        indices = [0 for _ in range(self.max_successor_len + 1)]
        while original_offset < original_length:
            try:
                if original_offset == original_length:
                    break

                # find the longest string of known successors
                character_index = original[original_offset]

                indices[0] = self.chr_ids_by_chr[character_index]
                last_chr_index = indices[0]
                if last_chr_index < 0:
                    raise ValueError()
                rest = original_length - original_offset
                n_consecutive = 1
                while n_consecutive <= self.max_successor_len:
                    if n_consecutive == rest:
                        break

                    character_index = original[original_offset + n_consecutive]

                    current_index = self.chr_ids_by_chr[character_index]
                    if current_index < 0:  # '\0' is always -1
                        break

                    successor_index = self.successor_ids_by_chr_id_and_chr_id[last_chr_index][current_index]
                    if successor_index < 0:
                        break

                    indices[n_consecutive] = successor_index
                    last_chr_index = current_index
                    n_consecutive += 1

                if n_consecutive < 2:
                    raise ValueError()

                pack_n = self.find_best_encoding(self.packs, indices, n_consecutive)
                if pack_n >= 0:
                    if out_offset + self.packs[pack_n].bytes_packed > out_length:
                        return out_length + 1

                    code.word = self.packs[pack_n].word
                    for i in range(self.packs[pack_n].bytes_unpacked):
                        code.word |= indices[i] << self.packs[pack_n].offsets[i]

                    # if we'd just copy the word, we might write over the end
                    # of the output string
                    bytes = code.get_char_array_from_word()
                    for i in range(self.packs[pack_n].bytes_packed):
                        out[out_offset + i] = ctypes.c_uint8(bytes[i])

                    out_offset += self.packs[pack_n].bytes_packed
                    original_offset += self.packs[pack_n].bytes_unpacked
                else:
                    raise ValueError()
            except ValueError:
                if original[original_offset] & 0x80:
                    # non-ascii case
                    if out_offset + 2 > out_length:
                        return out_length + 1
                    # put in a sentinel byte
                    out[out_offset] = 0x00
                    out_offset += 1
                else:
                    # an ascii byte
                    if out_offset + 1 > out_length:
                        return out_length + 1
                out[out_offset] = original[original_offset]
                out_offset += 1
                original_offset += 1

        return out_offset

    @classmethod
    def find_best_encoding(cls, packs, indices, n_consecutive):
        for i in range(ENCODING_TYPES - 1, -1, -1):
            if n_consecutive >= packs[i].bytes_unpacked and cls.check_indices(packs, indices, i):
                return i
        return -1

    @classmethod
    def check_indices(cls, packs, indices, pack_n):
        count = 0
        for i in range(packs[pack_n].bytes_unpacked):
            if indices[i] > packs[pack_n].masks[i]:
                return False
            count += 1
        return True
