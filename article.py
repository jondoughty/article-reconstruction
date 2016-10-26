class Article():
    def __init__(self):
        self.headline = None
        self.byline = None
        self.article_text = []

    def set_headline(self, hl):
        self.headline = hl

    def set_byline(self, bl):
        self.byline = bl

    def add_text(self, paragraph_num, text):
        self.article_text.append((paragraph_num, text))

    def reconstruct_artcile(self):
        '''Reconstruct all text contained in article_text as the text may
           be out of order.'''
