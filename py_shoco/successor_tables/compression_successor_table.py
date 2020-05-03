class CompressionSuccessorTable(object):
    def __init__(self, chr_ids_by_chr, successor_ids_by_chr_id_and_chr_id, max_successor_len):
        self.chr_ids_by_chr = chr_ids_by_chr
        self.successor_ids_by_chr_id_and_chr_id = successor_ids_by_chr_id_and_chr_id
        self.max_successor_len = max_successor_len