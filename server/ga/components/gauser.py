from flask_login import UserMixin


class GAUser(UserMixin):

    def __init__(self, _id):
        self.id = _id