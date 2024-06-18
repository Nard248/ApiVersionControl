from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
import jwt
import datetime

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgresqlwireless2020:software2020!!@wirelesspostgresqlflexible.postgres.database.azure.com/wiroidb2'
app.config['SECRET_KEY'] = 'vX11BAn65dq$'  # Change this to a strong secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class UsersAPI(db.Model):
    __tablename__ = 'UsersAPI'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    HashedPassword = db.Column(db.String(255), nullable=False)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['UserName']
    password = data['Password']

    if UsersAPI.query.filter_by(UserName=username).first():
        return jsonify({'msg': 'Username already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = UsersAPI(UserName=username, Password=password, HashedPassword=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    logging.debug(f"User {username} created successfully")
    return jsonify({'msg': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = UsersAPI.query.filter_by(UserName=username).first()

    if not user or not bcrypt.check_password_hash(user.HashedPassword, password):
        return jsonify({'msg': 'Bad username or password'}), 401

    # Generate a token
    payload = {
        'user_id': user.UserID,
        'username': user.UserName,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    access_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'access_token': access_token}), 200


@app.route('/download', methods=['GET'])
def download():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Missing token'}), 401

    # Verify the token
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['user_id']
        # You can add more verification steps if needed
    except jwt.ExpiredSignatureError:
        return jsonify({'msg': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'msg': 'Invalid token'}), 401

    filename = request.args.get('filename')
    if not filename:
        return jsonify({'msg': 'Missing filename parameter'}), 400

    # Implement the logic to find and serve the requested file
    # This is just a placeholder for the actual file serving logic
    try:
        with open(filename, 'rb') as file:
            content = file.read()
        return content, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename={filename}'
        }
    except FileNotFoundError:
        return jsonify({'msg': 'File not found'}), 404


if __name__ == '__main__':
    app.run(host='81.16.12.92', port=80, debug=True)
