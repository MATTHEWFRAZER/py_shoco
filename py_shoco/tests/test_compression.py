import ctypes

from hypothesis import given, assume, reject
from hypothesis.strategies import text

from py_shoco.compressor import Compressor
from py_shoco.decompressor import Decompressor
from py_shoco.tests.successor_tables.successor_tables import compressor_successor_table, decompressor_successor_table, packs, min_char

class TestCompression:
    @given(text())
    def test_compression_is_invertible(self, string):
        # not ready for unicode
        if any(ord(x) > 255 or ord(x) & 0x80 for x in string):
            reject()

        # can't have null terminated string
        if any(ord(x) == 0x00 for x in string):
            reject()

        assume(len(string) > 0 and len(string) < 100)
        length = len(string)
        original = (ctypes.c_uint8 * length)()
        out = (ctypes.c_uint8 * length)()
        for i, x in enumerate(string):
            original[i] = ord(x)
        compressor = Compressor(compressor_successor_table, packs)
        decompressor = Decompressor(decompressor_successor_table, packs, min_char)
        out_length = compressor.compress(original, length, out, length)

        assert out_length <= length

        out2 = (ctypes.c_uint8 * length)()
        out2_length = decompressor.decompress(out, out_length, out2, length)

        final = ""
        for i in range(out2_length):
            final += chr(out2[i])

        assert out2_length == length
        assert final == string
