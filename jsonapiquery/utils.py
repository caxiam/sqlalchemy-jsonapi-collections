import sqlalchemy


class QueryCounter:
    
    def __init__(self, session):
        self.session = session
        self.engine = session.bind
        self.is_counting = False
        sqlalchemy.event.listen(
            self.engine, 'before_cursor_execute', self.callback)

    def __enter__(self):
        self.count = 0
        self.is_counting = True
        self.session.expire_all()
        return self

    def __exit__(self, *args, **kwargs):
        self.count = 0
        self.is_counting = False
        self.session.expire_all()

    def callback(self, *args, **kwargs):
        if self.is_counting:
            self.count += 1
