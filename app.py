import json
import random
from logging.handlers import RotatingFileHandler
from flask import request, current_app
from flask.json import jsonify
from flask_restful import Resource, reqparse, request
from flask_jwt import JWT, jwt_required, current_identity
from config import app, api, mail
from models import *
import paho.mqtt.client as mqtt
import logging
from threading import Thread
from flask_mail import Message
from itsdangerous import URLSafeSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None

from flask import request, current_app


# @app.before_request
# def log_request():
#     logger.info(request.headers)
#     logger.info(request.data)
#

def authenticate(username, password):
    user = User.where('username', username).where('password', User.encode_password(password)).get().first()
    if user:
        return user


def identity(payload):
    user_id = payload['identity']
    return User.find(user_id)


jwt = JWT(app, authenticate, identity)


@api.resource('/')
class Root(Resource):
    def get(self):
        # Registered succesfully, and returned.
        response = jsonify({"message": "WTF m8?"})
        response.status_code = 401
        return response


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@api.resource('/register')
class Register(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('username', type=str, help='unique username', required=True)
        self.parser.add_argument('password', type=str, help='passwd', required=True)
        self.parser.add_argument('email', type=str, help='email', required=True)

    # TODO: Check email exists
    def post(self):
        # Parser handles bad requests.
        args = self.parser.parse_args()

        # If user already exists.
        if (User.where('username', args.username).get().first()):
            response = jsonify({"message": "Username  %s already in use" % args['username']})
            response.status_code = 409
            return response

        if (User.where('email', args.email).get().first()):
            response = jsonify({"username": "Email %s already in use" % args['email']})
            response.status_code = 409
            return response

        # Check ?
        # TODO : Hash password
        args['password'] = User.encode_password(args['password'])
        user = User.create(args)

        # Registered succesfully, and returned.
        response = jsonify({"message": "User created successfully.", "user": user.serialize()})
        response.status_code = 201
        return response


class Devices(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser(bundle_errors=True)
        self.post_parser.add_argument('name', type=str, help='unique username', required=True)
        self.post_parser.add_argument('topic', type=str, help='passwd', required=True)

        self.put_parser = reqparse.RequestParser(bundle_errors=True)
        self.put_parser.add_argument('status', type=int, help='Status of stuff', required=True)
        # TODO: Handle other stuff

    method_decorators = [jwt_required()]

    def get(self, dev_id=None):
        if dev_id is not None:
            logger.info(request)

            device = current_identity.devices().find(dev_id)

            if (device is None):
                response = jsonify({"message": "Device with id %s not found" % dev_id})
                response.status_code = 404
                return response

            device = device.with_('user').get().first()
            response = jsonify({"message": "Device %s" % dev_id, "data": device.serialize()})
            response.status_code = 200
            return response

        devices = current_identity.devices().with_('user').get()
        # TODO: Handle device errors

        response = jsonify({"message": "All devices of %s" % current_identity.username, "data": devices.serialize()})
        response.status_code = 200
        return response

    # TODO: Handle POST to /dev/<id>
    def post(self, dev_id=None):
        args = self.post_parser.parse_args()

        if (Device.where('user_id', current_identity.id).where('name', args['name']).get().first()):
            response = jsonify({"message": "Device name  %s already in use" % args['name']})
            response.status_code = 409
            return response

        device = current_identity.devices().create(args)
        # TODO: handle device errors
        device = device.load('user')

        response = jsonify({"message": "Device registered successfuly", "data": device.serialize()})
        response.status_code = 201
        return response

    def put(self, dev_id):
        args = self.put_parser.parse_args()

        device = Device.where('id', dev_id).get().first()

        if (device is None):
            response = jsonify({"message": "Device not found"})
            response.status_code = 404
            return response

        client.publish(device.topic, "%d" % args['status'], qos=2)
        response = jsonify({"message": "Request  -> %s <- send to device" % args['status']})
        response.status_code = 200
        return response

    def delete(self, dev_id):
        device = current_identity.devices().find(dev_id)
        if device is None:
            response = jsonify({"message": "Device not found"})
            response.status_code = 404
            return response

        client.publish(device.topic, "%d" % -1, qos=2)
        device.delete()

        response = jsonify({"message": "Device deleted successfully"})
        response.status_code = 200
        return response


api.add_resource(Devices, '/dev', '/dev/<int:dev_id>')


@api.resource('/passreset')
class PasswReset(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser(bundle_errors=True)
        self.post_parser.add_argument('email', type=str, help='email', required=True)

        self.serializer = URLSafeSerializer(app.config['SECRET_KEY'])

        self.put_parser = reqparse.RequestParser(bundle_errors=True)
        self.put_parser.add_argument('password', type=str, help='password', required=True)
        self.put_parser.add_argument('token', type=str, help='token', required=True)

    def encode_token(self, user):
        return self.serializer.dumps({"user_id": user.id, "passwd": user.password, "wtf": random.randint(0, 100)})

    def decode_token(self, token):
        return self.serializer.loads(token)

    def post(self):
        args = self.post_parser.parse_args()

        user = User.where('email', args['email']).get().first()

        if (user is None):
            response = jsonify({"message": "User not found"})
            response.status_code = 404
            return response

        # TODO: Use User's static methods
        token = self.encode_token(user)

        user_token = user.resettoken().order_by('created_at', 'desc').first()
        if (user_token is not None):
            user_token.active = False
            user_token.save()

        user_token = user.resettoken().create(token=token, active=True)

        msg = Message('Smart Switch password reset', recipients=[args['email']])
        msg.body = "%s?resettoken=%s" % (app.config['web-client'], user_token.token)
        mail.send(msg)

        response = jsonify({"message": "Password reset token", "token": token})
        response.status_code = 200
        return response

    def put(self):
        args = self.put_parser.parse_args()
        user_id = self.decode_token(args['token'])['user_id']
        new_password = User.encode_password(args['password'])
        user = User.find(user_id)

        if (user is None):
            response = jsonify({"message": "User not found"})
            response.status_code = 404
            return response

        tt = PasswordReset.where('token', args['token']).get().first()
        if tt is None or tt.active is 0:
            response = jsonify({"message": "Invalid token"})
            response.status_code = 401
            return response

        logger.info("id " + str(user_id))
        logger.info("passwd " + str(new_password))
        user.password = new_password
        user.save()
        tt.active = 0
        tt.save()

        response = jsonify({"message": "Password changed successfully"})
        response.status_code = 200
        return response


# def on_message(client, userdata, msg):
#     f = open('loggg', 'w')
#     f.write(str(msg) + '\n')
#     f.close()
#     logger.info(msg.topic+" "+str(msg.payload))
#     client.publish('flask', payload="aaaakikikiki", qos=0)

class MQTT_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop = False

    def run(self):
        while not self.stop and client.loop_forever() == 0:
            pass
        print "MQTT Thread terminado"


def on_connect(client, userdata, rc):
    if rc == 0:
        a = client.subscribe("#", qos=2)
        logger.info("Connected with result code " + str(rc))
        logger.info("subs result = " + str(a))


def on_message(client, userdata, msg):
    topic = msg.topic
    topic_elems = topic.split('/')

    if topic == "register":
        payload = json.loads(msg.payload)
        dev_name = payload['device']
        dev_topic = payload['username'] + "/" + payload['device']
        user = User.where('username', payload['username']).where('password', User.encode_password(
            payload['user_pass'])).get().first()

        if user is None:
            client.publish(dev_topic, "-1", qos=2)
            return

        d = user.devices().where('name', dev_name).get().first()
        if d is not None:
            logger.info('already registered device')
            # Send last known status
            client.publish(dev_topic, "%s" % d.status, qos=2)
            return

        b = user.devices().create(name=dev_name, topic=dev_topic)
        logger.info(b)

        return

    if len(topic_elems) == 3:
        ep = topic_elems[2]
        if ep == "status":
            user = User.where('username', topic_elems[0]).get().first()

            dev = user.devices().where('name', topic_elems[1]).get().first()

            dev.status = int(msg.payload)
            dev.save()

        if ep == "log":
            pass  # TODO : handle changes
            # logger.info("Topic : {0}, Message : {1}".format(*[msg.topic, msg.payload]))


if __name__ == '__main__':
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('access.log')
    logger.addHandler(handler)

    mqtt_thread = None

    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("188.166.40.162", 1883, 60)

    try:
        mqtt_thread = MQTT_Thread()
        mqtt_thread.daemon = True
        mqtt_thread.start()
    except Exception, e:
        client.disconnect()
        client.reconnect()
        logger.error(format(str(e)))

    app.run(host="0.0.0.0", port=5000, debug=True)
