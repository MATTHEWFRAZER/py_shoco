class DecompressionSuccessorTable(object):
    def __init__(self, chr_by_chr_id, chrs_by_chr_and_successor_id):
        self.chr_by_chr_id = chr_by_chr_id
        self.chrs_by_chr_and_successor_id = chrs_by_chr_and_successor_id