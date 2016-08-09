from itsdangerous import URLSafeSerializer

from config import db
from orator.orm import has_many, belongs_to
from orator import Model
from config import app

Model.set_connection_resolver(db)


class User(Model):
    __fillable__ = ['username', 'email', 'password']
    __hidden__ = ['password', 'created_at', 'updated_at']
    s = URLSafeSerializer(app.config['SECRET_KEY'])
    @has_many
    def devices(self):
        return Device

    @has_many
    def resettoken(self):
        return PasswordReset

    @staticmethod
    def encode_password(password):
       # s = URLSafeSerializer(app.config['SECRET_KEY'])
        return User.s.dumps(password)
    @staticmethod
    def decode_password(password):
        #s = URLSafeSerializer(app.config['SECRET_KEY'])
        return User.s.loads(password)

    def __repr__(self):
        return '<User %r>' % self.username


class Device(Model):
    __fillable__ = ['name', 'topic']
    __hidden__ = ['user_id'] # this doesnt need to return, eager loading already return user
    s = URLSafeSerializer(app.config['SECRET_KEY'])
    @belongs_to
    def user(self):
        return User

    @staticmethod
    def encode_id(device):
        # s = URLSafeSerializer(app.config['SECRET_KEY'])
        return Device.s.dumps(device.id)

    @staticmethod
    def decode_id(token):
        # s = URLSafeSerializer(app.config['SECRET_KEY'])
        return User.s.loads(token)

    def __repr__(self):
        return '<Device %r>' % self.name


class PasswordReset(Model):
    __table__ = 'password_reset'
    __fillable__ = ['token', 'active']
    __hidden__ = ['user']

    @belongs_to
    def user(self):
        return User