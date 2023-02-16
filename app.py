from flask import Flask, request, jsonify
from models import Student, User
from blocklist import BLOCKLIST
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
    JWTManager
)


app = Flask(__name__)
app.config.from_object('config.BaseConfig')
mongo = Student(app)
Umongo = User(app)
jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    # TODO: Read from a config file instead of hard-coding
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# JWT configuration ends



@app.route("/students", methods=['GET'])
def get_all_students():
    return jsonify(mongo.find_students_all())


@app.route("/students", methods=['POST'])
def add_new_student():
    data = request.get_json() 
    return mongo.save_to_db(data)


@app.route("/students/<string:name>", methods=['GET'])
def find_student_by_name(name):
    return mongo.find_student_by_name(name)


@app.route("/students/<string:name>", methods=['DELETE'])
@jwt_required(fresh=True)
def delete_student(name):
    return mongo.delete_from_db(name)


@app.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json() 
    user = Umongo.find_user_by_username(data['username'])
    if user and user['password'] == data['password']:
        access_token = create_access_token(identity=data['username'], fresh=True)
        refresh_token = create_refresh_token(data['username'])
        return {"access_token": access_token, "refresh_token": refresh_token}

    return jsonify({"Message": "Bad username or password"}), 401


@app.route("/user/register", methods=["POST"])
def user_register():
    data = request.get_json()
    if Umongo.find_user_by_username(data['username']):
        return {"message": "A user with that username already exists"}

    return Umongo.save_user_to_db(data)    


@app.route("/user/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    return {"access_token": new_token}, 200


@app.route("/user/logout", methods=["POST"])
@jwt_required()
def user_logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    for x in BLOCKLIST:
        print(x)
    return {"message": "Successfully logged out"}, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) 