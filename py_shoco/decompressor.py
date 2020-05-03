import ctypes

from py_shoco.code import Code

__all__ = ["Decompressor"]

from py_shoco.constants import MAX_LEADING_CHARACTER_BITS


class Decompressor(object):
    def __init__(self, decompression_successor_table, packs, min_char):
        self.chr_by_chr_id = decompression_successor_table.chr_by_chr_id
        self.chrs_by_chr_and_successor_id = decompression_successor_table.chrs_by_chr_and_successor_id
        self.packs = packs
        self.min_char = min_char

    def decompress(self, original, original_length, out, out_length):
        out_offset = 0
        original_offset = 0
        code = Code()

        while original_offset < original_length:
            mark = self.decode_header(original[original_offset])
            if mark < 0:
                if out_offset >= out_length:
                    return out_length + 1

                # ignore the sentinel value for non-ascii chars
                if original[original_offset] == 0x00:
                    original_offset += 1
                    if original_offset >= original_length:
                        return -1
                out[out_offset] = original[original_offset]
                out_offset += 1
                original_offset += 1
            else:
                if out_offset + self.packs[mark].bytes_unpacked > out_length:
                    return out_length + 1
                elif original_offset + self.packs[mark].bytes_packed > original_length:
                    return -1

                # This should be OK as well, but it fails with emscripten.
                # Test this with new versions of emcc.
                character_array = code.get_char_array_from_word()
                for i in range(self.packs[mark].bytes_packed):
                    character_array[i] = original[original_offset + i]
                code.reset_all_from_char_array(character_array)

                # unpack the leading char
                offset = self.packs[mark].offsets[0]
                mask = self.packs[mark].masks[0]

                last_chr = self.chr_by_chr_id[(code.word >> offset) & mask]
                out[out_offset] = ctypes.c_uint8(ord(last_chr))
                for i in range(1, self.packs[mark].bytes_unpacked):
                    offset = self.packs[mark].offsets[i]
                    mask = self.packs[mark].masks[i]
                    last_chr = self.chrs_by_chr_and_successor_id[ord(last_chr) - self.min_char][(code.word >> offset) & mask]
                    out[out_offset + i] = ctypes.c_uint8(ord(last_chr))
                out_offset += self.packs[mark].bytes_unpacked
                original_offset += self.packs[mark].bytes_packed

        # append a 0-terminator if it fits
        if out_offset < out_length:
            out[out_offset] = ord('\0')

        return out_offset

    @staticmethod
    def decode_header(character):
        pointer = ctypes.POINTER(ctypes.c_ubyte)(ctypes.c_ubyte(character))
        pointer = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_byte))
        i = -1
        while pointer.contents.value < 0:
            pointer.contents.value <<= 1
            i += 1
        return i
