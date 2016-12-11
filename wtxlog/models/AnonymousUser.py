# -*- coding: utf-8 -*-
from flask_login import UserMixin, AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

