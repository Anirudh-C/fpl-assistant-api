# Basic imports
import os

import flask
from flask import jsonify, request, make_response

# FPL API wrapper imports
import aiohttp
import asyncio

from fpl import FPL

# DB imports
import sqlalchemy

# Encryption imports
from cryptography.fernet import Fernet

# Application object
app = flask.Flask("FPL Assistant API")

# DB connection ENV variables
db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USERNAME")
db_pass = os.environ.get("DB_PASS")

# DB connection object
db = sqlalchemy.create_engine(
    "mysql+pymysql://{}:{}@{}/FPL".format(db_user, db_pass, db_host))

# CLI commands
@app.cli.command("initdb")
def initdb():
    """
    Initialise database with schema
    """
    with db.connect() as connection:
        # Create schema
        # TODO: add full schema here
        connection.execute(
            sqlalchemy.sql.text(
                "CREATE TABLE IF NOT EXISTS USER( id INT PRIMARY KEY, email TEXT, enc_pass TEXT );"))

# API Routes
# Root
@app.route("/", methods=["GET"])
def root():
    """
    Return success response
    """
    return jsonify({ "status": "Success" })

async def get_squad(team: int):
    """
    Get players from :team:
    :param: team - int (1-20) team index
    """
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        team = await fpl.get_team(team)
        players = await team.get_players(return_json=True)
    return players

# Players route
@app.route("/players", methods=["GET"])
def players():
    """
    Get players in a particular team via request argument
    """
    if "team" in request.args:
        team_id = int(request.args["team"])
        return jsonify(asyncio.run(get_squad(team_id)))
    return jsonify({ "status": "Error: Specify team index" })

async def fpl_login(email: str, password: str) -> int:
    """
    Login to FPL with given credentials
    :param: email - str
    :param: password - str
    """
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        await fpl.login(email, password)
        user = await fpl.get_user()
        return user.id

def check_user_exists(email: str) -> bool:
    """
    Check if user with email exists in database
    :param: email - str
    """
    with db.connect() as connection:
        result = connection.execute(
            sqlalchemy.text(
                "SELECT * from USER WHERE email = '{}';".format(email)))
    return bool(result.all())

def write_user(user_id: int, email: str, enc_pass: str):
    """
    Write given user to database
    :param: user_id - int
    :param: email - str
    :param: enc_pass - encrypted password
    """
    with db.connect() as connection:
        connection.execute(
            sqlalchemy.sql.text(
                "USE FPL;"))
        connection.execute(
            sqlalchemy.sql.text(
                "INSERT INTO USER (id, email, enc_pass) VALUES ({}, '{}', '{}')"
                .format(user_id, email, enc_pass)))

# Login route
@app.route("/login", methods=["POST"])
def login():
    """
    Login to FPL on request
    """
    try:
        username = request.form["login"]
        # Check if user exists
        # TODO: improve the checking mechanism with key cookie
        if check_user_exists(username):
            return make_response({ "status": "Success" })
        else:
            password = request.form["password"]
            # Get user ID
            user_id = asyncio.run(fpl_login(username, password))

            # Encrypt password and forget secret information
            key = Fernet.generate_key()
            fernet = Fernet(key)
            enc_pass = fernet.encrypt(password.encode())
            del password
            del fernet

            # Set cookie in response and forget key
            response = make_response({ "status": "Success" })
            response.set_cookie("key", key)
            del key

            # Write user
            write_user(user_id, username, enc_pass.decode("utf-8"))

            return response
    except ValueError:
        # Return unauthorize code
        return make_response({ "status": "Incorrect Credentials!" }, 401)
    except:
        # Return generic error code
        return make_response({ "status":  "Failure"}, 500)

def serve():
    """
    Method to return application object for waitress (production server)
    Note: Need not be called without waitress
    """
    return app

if __name__ == "__main__":
    app.run()
