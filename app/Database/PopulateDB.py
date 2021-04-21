# Basic imports
import os

# DB imports
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.sql import exists    

# FPL API wrapper
from fpl import FPL

# FPL API wrapper imports
import aiohttp
import asyncio

def add_player(Player, session):
    query = text("""INSERT INTO PLAYER (code, element_type, web_name,
                    id, team_id, element_status, chance_of_playing_next_round,
                    chance_of_playing_this_round, ep_next, ep_this, event_points,
                    form, now_cost, points_per_game, total_points, goals_scored,
                    assists, clean_sheets, saves, bonus, bps, influence, creativity,
                    threat, ict_index) 
                    VALUES (:code, :element_type, :web_name,
                    :id, :team_id, :element_status, :chance_of_playing_next_round,
                    :chance_of_playing_this_round, :ep_next, :ep_this, :event_points,
                    :form, :now_cost, :points_per_game, :total_points, :goals_scored,
                    :assists, :clean_sheets, :saves, :bonus, :bps, :influence, :creativity,
                    :threat, :ict_index);""")

    session.execute(query, code = Player.code, element_type = Player.element_type, web_name = Player.web_name,
                    id = Player.id, team_id = Player.team, element_status = Player.status, 
                    chance_of_playing_next_round = Player.chance_of_playing_next_round ,
                    chance_of_playing_this_round = Player.chance_of_playing_this_round, ep_next = Player.ep_next, 
                    ep_this = Player.ep_this, event_points = Player.event_points,
                    form = Player.form, now_cost = Player.now_cost, points_per_game = Player.points_per_game, 
                    total_points = Player.total_points, goals_scored = Player.goals_scored,
                    assists = Player.assists, clean_sheets = Player.clean_sheets, saves = Player.saves, bonus = Player.bonus,
                    bps = Player.bps, influence = Player.influence, creativity = Player.creativity, 
                    threat = Player.threat, ict_index = Player.ict_index)


async def add_players(engine):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()
    
    for player in players:
        add_player(player, engine)

def add_team(Team, engine):
    query = text("""REPLACE INTO TEAM (id, team_name, short_name, strength, strength_overall_home,
                    strength_overall_away,strength_attack_home,strength_attack_away,
                    strength_defence_home,strength_defence_away) 
                    VALUES (:id, :team_name, :short_name, :strength, :strength_overall_home,
                    :strength_overall_away,:strength_attack_home,:strength_attack_away,
                    :strength_defence_home, :strength_defence_away);""")

    engine.execute(query, id=Team.id, team_name=Team.name, short_name=Team.short_name, strength=Team.strength, strength_overall_home=Team.strength_overall_home,
                    strength_overall_away=Team.strength_overall_away,strength_attack_home=Team.strength_attack_home,strength_attack_away=Team.strength_attack_away,
                    strength_defence_home=Team.strength_defence_home,strength_defence_away=Team.strength_defence_away)

async def add_teams(engine):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        teams = await fpl.get_teams()
    
    for team in teams:
        add_team(team, engine)

if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://root:pass@localhost:3600/FPL")
    engine = engine.connect()
    asyncio.run(add_teams(engine))
    asyncio.run(add_players(engine))


