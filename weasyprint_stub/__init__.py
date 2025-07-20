class HTML:
    def __init__(self, filename=None, string=None):
        self.filename = filename
        self.string = string
    def write_pdf(self, target, *args, **kwargs):
        with open(target, 'wb') as f:
            f.write(b"%PDF-1.4 stub")
