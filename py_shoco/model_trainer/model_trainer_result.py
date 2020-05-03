class ModelTrainerResult(object):
    def __init__(self, compression_successor_table, decompression_successor_table, packs, min_char):
        self.compression_successor_table = compression_successor_table
        self.decompression_successor_table = decompression_successor_table
        self.packs = packs
        self.min_char = min_char