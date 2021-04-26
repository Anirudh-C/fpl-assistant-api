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

def update_player(Player, session):
    query = text("""UPDATE PLAYER SET element_status = :element_status, 
                    chance_of_playing_next_round = :chance_of_playing_next_round,
                    chance_of_playing_this_round = :chance_of_playing_this_round, ep_next = :ep_next, 
                    ep_this = :ep_this, event_points = :event_points, form = :form, 
                    now_cost = :now_cost, points_per_game = :points_per_game, total_points = :total_points, 
                    goals_scored = :goals_scored, assists = :assists, clean_sheets = :clean_sheets, 
                    saves = :saves, bonus = :bonus, bps = :bps, influence = :influence, creativity = :creativity,
                    threat = :threat, ict_index = :ict_index, score = :score  WHERE id = :id""")

    score = 0 #foo(Player)
    session.execute(query, element_status = Player.status,chance_of_playing_next_round = Player.chance_of_playing_next_round ,
                    chance_of_playing_this_round = Player.chance_of_playing_this_round, ep_next = Player.ep_next, 
                    ep_this = Player.ep_this, event_points = Player.event_points,
                    form = Player.form, now_cost = Player.now_cost, points_per_game = Player.points_per_game, 
                    total_points = Player.total_points, goals_scored = Player.goals_scored,
                    assists = Player.assists, clean_sheets = Player.clean_sheets, saves = Player.saves, bonus = Player.bonus,
                    bps = Player.bps, influence = Player.influence, creativity = Player.creativity, 
                    threat = Player.threat, ict_index = Player.ict_index, score = score, id = Player.id)


async def update_players(engine):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()
    
    for player in players:
        update_player(player, engine)

def update_team(Team, engine):
    query = text("""UPDATE TEAM  SET strength = :strength, strength_overall_home = :strength_overall_home,
                    strength_overall_away = :strength_overall_away, strength_attack_home = :strength_attack_home,
                    strength_attack_away = :strength_attack_away, strength_defence_home = :strength_defence_home,
                    strength_defence_away = :strength_defence_away WHERE id = :id;""")

    engine.execute(query, strength=Team.strength, strength_overall_home=Team.strength_overall_home,
                    strength_overall_away=Team.strength_overall_away,strength_attack_home=Team.strength_attack_home,
                    strength_attack_away=Team.strength_attack_away,strength_defence_home=Team.strength_defence_home,
                    strength_defence_away=Team.strength_defence_away, id = Team.id)

async def update_teams(engine):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        teams = await fpl.get_teams()
    
    for team in teams:
        update_team(team, engine)

def add_fixture(Fixture, engine):
    query = text("""INSERT INTO FIXTURE (code, id, team_a, team_h,
                    team_h_difficulty, team_a_difficulty)
                    VALUES (:code, :id, :team_a, :team_b,
                    :team_h_difficulty, :team_a_difficulty);""")

    engine.execute(query, code = Fixture.code, id = Fixture.id,
                    team_a = Fixture.team_a, team_b = Fixture.team_h,
                    team_h_difficulty = Fixture.team_h_difficulty, 
                    team_a_difficulty = Fixture.team_a_difficulty)

async def update_fixtures(engine):
    query = text("""truncate table FIXTURE;""")
    engine.execute(query)
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        fixtures = await fpl.get_fixtures()
    
    for fixture in fixtures:
        add_fixture(fixture, engine)

if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://root:pass@localhost:3600/FPL")
    engine = engine.connect()
    asyncio.run(update_teams(engine))
    asyncio.run(update_players(engine))
    asyncio.run(update_fixtures(engine))
