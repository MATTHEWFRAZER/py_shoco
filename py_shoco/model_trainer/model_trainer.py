import collections
import ctypes

from py_shoco.constants import MAX_CONSECUTIVES, ENCODINGS, MAX_LEADING_CHARACTER_BITS, \
    ENCODING_TYPES, MAX_SUCCESSOR_BITS
from py_shoco.encoding import Encoding
from py_shoco.model_trainer.model_trainer_result import ModelTrainerResult
from py_shoco.pack import define_pack
from py_shoco.successor_tables.compression_successor_table import CompressionSuccessorTable
from py_shoco.successor_tables.decompression_successor_table import DecompressionSuccessorTable

__all__ = ["train"]

WHITESPACE = b" \t\n\r\x0b\x0c\xc2\xad"


def bigrams(sequence):
    sequence = iter(sequence)
    last = next(sequence)
    for item in sequence:
        yield last, item
        last = item


def get_packs(best_encodings, max_element_count):
    packs = (define_pack(max_element_count) * ENCODING_TYPES)()
    for i in range(ENCODING_TYPES):
        pack = packs[i]
        best_encoding = best_encodings[i]
        pack.word = ctypes.c_uint32(best_encoding.word)
        pack.bytes_packed = ctypes.c_uint(int(best_encoding.packed))
        pack.bytes_unpacked = ctypes.c_uint(best_encoding.unpacked)
        for i, x in enumerate(best_encoding.offsets.consecutive):
            pack.offsets[i] = ctypes.c_int(x)
        for i, x in enumerate(best_encoding.masks.consecutive):
            pack.masks[i] = ctypes.c_int16(x)
        pack.header_mask = ctypes.c_char(best_encoding.header_mask)
        pack.header = ctypes.c_char(best_encoding.header_code)
    return packs


def get_optimized_best_encodings(data, successors, chrs_indices):
    counters = {}
    encodings_by_encoding_type = ENCODINGS[:ENCODING_TYPES]

    for packed, _ in encodings_by_encoding_type:
        counters[packed] = collections.Counter()

    for chunk in data:
        for i in range(len(chunk)):
            for packed, encodings in encodings_by_encoding_type:
                for encoding in encodings:
                    if (encoding.bits.lead > MAX_LEADING_CHARACTER_BITS) or (
                            max(encoding.bits.consecutive) > MAX_SUCCESSOR_BITS):
                        continue
                    if encoding.can_encode(chunk[i:], successors, chrs_indices):
                        counters[packed][encoding] += packed / float(encoding.unpacked)

    best_encodings_raw = [(packed, counter.most_common(1)[0][0]) for packed, counter in counters.items()]
    max_encoding_len = max(encoding.size for _, encoding in best_encodings_raw)
    best_encodings = [Encoding(encoding.bits.datalist + [0] * (MAX_CONSECUTIVES - encoding.size)) for packed, encoding
                      in best_encodings_raw]
    return best_encodings, max_encoding_len


def train(data, optimize):
    chars_count = 1 << MAX_LEADING_CHARACTER_BITS
    successors_count = 1 << MAX_SUCCESSOR_BITS

    bigram_counters = collections.OrderedDict()
    first_char_counter = collections.Counter()
    for chunk in data:
        if not chunk:
            continue
        bgs = bigrams(chunk)
        for bg in bgs:
            a, b = bg
            # counting most common characters
            first_char_counter[a] += 1
            if a not in bigram_counters:
                bigram_counters[a] = collections.Counter()
            # count most common successors for a
            bigram_counters[a][b] += 1

    # generate list of most common chars
    successors = collections.OrderedDict()
    # associate each of the most common chars with their most common successors
    for char, _ in first_char_counter.most_common(chars_count):
        # most common successors to char
        successors[char] = [successor for successor, _ in bigram_counters[char].most_common(successors_count)]
        # fill in the rest with zeros to meet successors_count
        successors[char] += [0] * (successors_count - len(successors[char]))

    max_chr = max(successors.keys()) + 1
    min_chr = min(successors.keys())

    # associate most common chars with their order index
    chrs_indices = collections.OrderedDict(zip(successors.keys(), range(chars_count)))
    # for every byte character get its index if it is in the most common otherwise we take -1
    chrs_reversed = [chrs_indices.get(i, -1) for i in range(256)]

    # for each of the most common characters we associate a list of all most common characters as they appear in the
    # character's successor list. if that common character doesn't appear in the successor list we take -1
    successors_reversed = collections.OrderedDict()
    for char, successor_list in successors.items():
        successors_reversed[char] = [None] * chars_count
        s_indices = collections.OrderedDict(zip(successor_list, range(chars_count)))
        for i, s in enumerate(successors.keys()):
            successors_reversed[char][i] = s_indices.get(s, -1)

    zeros_line = [b'\0'] * successors_count

    # finding best backing structures
    if optimize:
        best_encodings, max_encoding_len = get_optimized_best_encodings(data, successors, chrs_indices)
    else:
        max_encoding_len = 8
        best_encodings = [Encoding([2, 4, 2, 0, 0, 0, 0, 0, 0]),
                          Encoding([3, 4, 3, 3, 3, 0, 0, 0, 0]),
                          Encoding([4, 5, 4, 4, 4, 3, 3, 3, 2])][:ENCODING_TYPES]

    max_successor_len = max_encoding_len - 1
    max_element_len = MAX_CONSECUTIVES
    packs = get_packs(best_encodings, max_element_len)

    # chr_by_chr_id: for every most common character associate the order of character with character in array
    chr_by_chr_id = (ctypes.c_char * chars_count)()
    for i, x in enumerate(successors.keys()):
        chr_by_chr_id[i] = ctypes.c_char(x)

    # chr_ids_by_chr: for every byte character get most common character index, -1 if character is not in most common
    chr_ids_by_chr = (ctypes.c_int8 * 256)()
    for i, x in enumerate(chrs_reversed):
        chr_ids_by_chr[i] = ctypes.c_int8(x)

    # successor_ids_by_chr_id_and_chr_id: most common character's index associated with a list of all most common
    # characters as they appear in that most common character's successor list
    successor_ids_by_chr_id_and_chr_id = ((ctypes.c_int8 * chars_count) * chars_count)()
    for i, x in enumerate(successors_reversed.values()):
        for j, y in enumerate(x):
            successor_ids_by_chr_id_and_chr_id[i][j] = ctypes.c_int8(y)

    # chrs_by_chr_and_successor_id: for all characters seen, construct a successor list from existing successor lists
    # if character is not in most common, we use a zero array
    chrs_by_chr_and_successor_id = ((ctypes.c_char * successors_count) * max_chr)()
    for i in range(max_chr):
        for j, y in enumerate(successors.get(i + min_chr, zeros_line)):
            chrs_by_chr_and_successor_id[i][j] = ctypes.c_char(y)

    compression_successor_table = CompressionSuccessorTable(chr_ids_by_chr, successor_ids_by_chr_id_and_chr_id, max_successor_len)
    decompression_successor_table = DecompressionSuccessorTable(chr_by_chr_id, chrs_by_chr_and_successor_id)
    return ModelTrainerResult(compression_successor_table, decompression_successor_table, packs, min_chr)
