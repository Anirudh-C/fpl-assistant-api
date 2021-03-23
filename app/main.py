import aiohttp
import asyncio

from fpl import FPL

import flask
from flask import jsonify, request

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

def serve():
    return app

if __name__ == "__main__":
    app.run()
