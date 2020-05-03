import ctypes

def define_pack(max_element_count):
    class Pack(ctypes.Structure):
        _fields_ = [("word", ctypes.c_uint32),
                    ("bytes_packed", ctypes.c_uint),
                    ("bytes_unpacked", ctypes.c_uint),
                    ("offsets", ctypes.c_int * max_element_count),
                    ("masks", ctypes.c_int16 * max_element_count),
                    ("header_mask", ctypes.c_char),
                    ("header", ctypes.c_char)]

    return Pack