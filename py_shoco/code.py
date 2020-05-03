import ctypes

class Code:
    def __init__(self):
        self.bytes = (ctypes.c_int8 * 4)()
        self.word = ctypes.c_int32()

    def reset_bytes(self):
        new_bytes = self.get_char_array_from_word()
        for i in range(4):
            self.bytes[i] = new_bytes[i]

    def reset_word(self):
        self.word = int.from_bytes(self.bytes, "big")

    def get_char_array_from_word(self):
        character_array = []
        # when unitialized we need to access word through .value,
        # when initialized .value raises an attribute error
        try:
            word = self.word.value
        except:
            word = self.word
        # first byte
        character_array.append((word >> 24))
        # second byte
        character_array.append(((word & 0x00FFFFFF) >> 16))
        # third byte
        character_array.append(((word & 0x0000FFFF) >> 8))
        # fourth byte
        character_array.append((word & 0x000000FF))
        return character_array

    def reset_all_from_char_array(self, char_array):
        first_byte = char_array[0] << 24
        second_byte = char_array[1] << 16
        third_byte = char_array[2] << 8
        fourth_byte = char_array[3]
        self.word  = first_byte | second_byte | third_byte | fourth_byte
        self.reset_bytes()