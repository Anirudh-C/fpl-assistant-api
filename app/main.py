# Basic imports
import os
from unidecode import unidecode

import flask
from flask import jsonify, request, make_response
import click

# FPL API wrapper imports
import aiohttp
import asyncio

from fpl import FPL

# DB imports
import sqlalchemy
import app.DBUtils as DBUtils

# Encryption imports
from cryptography.fernet import Fernet

# Application object
app = flask.Flask("FPL Assistant API")

# DB connection ENV variables
db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USERNAME")
db_pass = os.environ.get("DB_PASS")

# DB connection object
db = sqlalchemy.create_engine("mysql+pymysql://{}:{}@{}/FPL".format(
    db_user, db_pass, db_host))


# CLI commands
@app.cli.command("initdb")
@click.option("testing", "-t", is_flag=True, default=False, required=False)
def initdb(testing):
    """
    Initialise database with schema
    """
    with db.connect() as engine:
        DBUtils.create_db("app/DBUtils/schema.sql", engine)
        if not testing:
            asyncio.run(DBUtils.add_teams(engine))
            asyncio.run(DBUtils.add_players(engine))
            asyncio.run(DBUtils.update_fixtures(engine))
            asyncio.run(DBUtils.update_teams(engine))
            asyncio.run(DBUtils.update_players(engine))
        else:
            asyncio.run(DBUtils.add_teams(engine))
            asyncio.run(DBUtils.add_players(engine, testing=True))


@app.cli.command("updatedb")
def updatedb():
    """
    Initialise database with schema
    """
    with db.connect() as engine:
        asyncio.run(DBUtils.update_fixtures(engine))
        asyncio.run(DBUtils.update_teams(engine))
        asyncio.run(DBUtils.update_players(engine))


# API Routes
# Root
@app.route("/", methods=["GET"])
def root():
    """
    Return success response
    """
    return jsonify({"status": "Success"})


# Element type mapping
@app.route("/element_types", methods=["GET"])
def types():
    """
    Return element type to position mapping
    """
    return jsonify(
        {"element_types": ["Goalkeeper", "Defender", "Midfielder", "Forward"]})


# Search all players
@app.route("/search_players", methods=["GET"])
def search_players():
    """
    Get all players of the league
    """
    with db.connect() as engine:
        if "name" in request.args:
            query = sqlalchemy.text(
                """SELECT p.full_name, t.team_name, t.short_name, p.id, p.code, p.score, p.goals_scored,
                                       p.assists, p.clean_sheets, t.strength, p.element_type, p.bonus, p.now_cost,
                                       p.points_per_game, p.chance_of_playing_next_round from PLAYER p, TEAM t
                                       WHERE p.full_name LIKE \'%{}%\' and p.team_id = t.id ORDER BY score DESC;"""
                .format(request.args["name"]))
        else:
            query = sqlalchemy.text(
                """SELECT p.full_name, t.team_name, t.short_name, p.id, p.code, p.score, p.goals_scored,
                                       p.assists, p.clean_sheets, t.strength, p.element_type, p.bonus, p.now_cost,
                                       p.points_per_game, p.chance_of_playing_next_round from PLAYER p, TEAM t
                                       WHERE p.team_id = t.id ORDER BY score DESC;"""
            )
        players = [dict(player) for player in engine.execute(query)]
    if "name" in request.args:
        return jsonify({
            "players": [
                dict(player,
                     match=unidecode(player["full_name"]).lower().index(
                         request.args["name"])) for player in players
            ]
        })
    return jsonify({"players": players})


@app.route("/pick_players", methods=["GET"])
def pick_players():
    """
    Get all players of the league
    """
    if "userid" in request.args:
        squad,transfer_status = asyncio.run(getUserSquad(email="demo", password="demo"))
        avltransfers = transfer_status["limit"] - transfer_status["made"]
        balance = transfer_status["bank"]
        squadIdList = [player["element"] for player in squad]

        with db.connect() as engine:
            query_all = sqlalchemy.text(
                "SELECT id, score, now_cost from PLAYER ORDER BY score DESC;")
            all_players = [
                dict(player) for player in engine.execute(query_all)
            ]

            query_squad = sqlalchemy.text(
                "SELECT id, score, now_cost from PLAYER WHERE id = :id ORDER BY score DESC;"
            )
            user_squad = [
                dict(player) for id in squadIdList
                for player in engine.execute(query_squad, id=id)
            ]

        # transfers = transfer_algo(all_players,user_squad, avltransfers, )
        transfers = {}

        return jsonify(transfers)

    return jsonify({"message": "Specify the userid"})


async def getUserSquad(email: str, password: str):
    """
    Get the current user squad
    """
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        await fpl.login(email,password)
        user = await fpl.get_user()
        transfer_status = await user.get_transfers_status()
        squad = await user.get_team()
    return squad, transfer_status


@app.route("/get_fixtures", methods=["GET"])
def get_fixtures():
    '''
    Get all fixtures for the next gameweek
    '''
    with db.connect() as engine:
        query = sqlalchemy.text("""SELECT (select team_name from TEAM where id = f.team_h) as Home, 
                                (select code from TEAM where id = f.team_h) home_code,
                                (select team_name from TEAM where id = f.team_a) as Away,
                                (select code from TEAM where id = f.team_a) away_code
                                from FIXTURE f;""")

        fixtures = [dict(fixture) for fixture in engine.execute(query)]

        return jsonify({"fixtures" : fixtures})

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


def check_user_exists(email: str):
    """
    Check if user with email exists in database and delete if exists
    :param: email - str
    """
    with db.connect() as connection:
        result = connection.execute(
            sqlalchemy.text(
                "SELECT * from USER_TABLE WHERE user_email = '{}';".format(
                    email)))
        if result.all():
            connection.execute(
                sqlalchemy.text(
                    "DELETE from USER_TABLE where user_email = '{}';".format(
                        email)))


def write_user(user_id: int, email: str, enc_pass: str):
    """
    Write given user to database
    :param: user_id - int
    :param: email - str
    :param: enc_pass - encrypted password
    """
    with db.connect() as connection:
        try:
            connection.execute(sqlalchemy.sql.text("USE FPL;"))
            connection.execute(
                sqlalchemy.sql.text(
                    "INSERT INTO USER_TABLE (id, user_email, user_password) VALUES ({}, '{}', '{}')"
                    .format(user_id, email, enc_pass)))

        except:
            pass


# Login route
@app.route("/login", methods=["POST"])
def login():
    """
    Login to FPL on request
    """
    try:
        username = request.form["login"]
        # Check if user exists
        check_user_exists(username)

        # Get password
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
        response = make_response({"status": "Success"})
        response.set_cookie("key", key, max_age=90 * 60 * 60 * 24)
        response.set_cookie("user_id", str(user_id), max_age=90 * 60 * 60 * 24)
        del key

        # Write user
        write_user(user_id, username, enc_pass.decode("utf-8"))

        return response
    except ValueError:
        # Return unauthorize code
        return make_response({"status": "Incorrect Credentials!"}, 401)


# Username
@app.route("/username", methods=["GET"])
def username():
    if "id" in request.args:
        with db.connect() as connection:
            result = connection.execute(
                sqlalchemy.sql.text(
                    "SELECT * from USER_TABLE where id='{}'".format(
                        request.args["id"])))
            for row in result:
                username = row[1]
        return make_response({"name": username})
    return make_response({"name": ""})


def serve():
    """
    Method to return application object for waitress (production server)
    Note: Need not be called without waitress
    """
    return app


if __name__ == "__main__":
    app.run()
