import aiohttp
import asyncio

from fpl import FPL

import flask
from flask import jsonify, request, make_response

from cryptography.fernet import Fernet

app = flask.Flask("FPL Assistant API")

@app.route("/", methods=["GET"])
def root():
    return jsonify({ "status": "Success" })

async def get_squad(team: int):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        team = await fpl.get_team(team)
        players = await team.get_players(return_json=True)
    return players

@app.route("/api/players", methods=["GET"])
def teams():
    if "team" in request.args:
        team_id = int(request.args["team"])
        return jsonify(asyncio.run(get_squad(team_id)))
    return jsonify({ "status": "Error: Specify team index" })

async def fpl_login(email: str, password: str):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        await fpl.login(email, password)

@app.route("/api/login", methods=["POST"])
def login():
    try:
        username = request.form["login"]
        password = request.form["password"]
        asyncio.run(fpl_login(username, password))
        key = Fernet.generate_key()
        fernet = Fernet(key)
        enc_pass = fernet.encrypt(password.encode())
        del password
        del fernet
        response = make_response({ "status": "Success" })
        response.set_cookie("key", key, secure=True)
        del key
        return response
    except ValueError:
        response = make_response({ "status": "Incorrect Credentials!" }, 401)
        return response
    except:
        return make_response({ "status": "Failure!" })

def serve():
    return app

if __name__ == "__main__":
    app.run()
