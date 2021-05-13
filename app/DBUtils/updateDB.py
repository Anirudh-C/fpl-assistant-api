# Basic imports
import os
import random

# DB imports
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.sql import exists

# FPL API wrapper
from fpl import FPL

# FPL API wrapper imports
import aiohttp
import asyncio

# Scoring Models
import app.Models as Models

team_fixture = {} # id : next_fix_team_id
team_att_form = {} # id : attack form
team_def_form = {} # id : defence form
team_att_strength = {}
team_def_stength = {}
team_score = {} # id : predicted_score

def update_player(Player, session, ict_form, minutes_form, value_form):

    score = None
    if Player.team in team_fixture.keys():
        opposition = team_fixture[Player.team][0]
        if Player.element_type == 1 or Player.element_type == 2:
            tscore = team_score[opposition] 
            feat_list = [minutes_form, float(Player.now_cost), ict_form, value_form, tscore]
            score = Models.setHistory(feat_name = "defPlayer_points", feat_list = feat_list)
        else:
            tscore = team_score[Player.team]
            feat_list = [minutes_form, float(Player.now_cost), ict_form, value_form, tscore]
            score = Models.setHistory(feat_name = "attPlayer_points", feat_list = feat_list)
    
    query = text("""UPDATE PLAYER SET element_status = :element_status,
                    chance_of_playing_next_round = :chance_of_playing_next_round,
                    chance_of_playing_this_round = :chance_of_playing_this_round, ep_next = :ep_next,
                    ep_this = :ep_this, event_points = :event_points, form = :form,
                    now_cost = :now_cost, points_per_game = :points_per_game, total_points = :total_points,
                    goals_scored = :goals_scored, assists = :assists, clean_sheets = :clean_sheets,
                    saves = :saves, bonus = :bonus, bps = :bps, influence = :influence, creativity = :creativity,
                    threat = :threat, ict_index = :ict_index, score = :score  WHERE id = :id""")

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
        players = await fpl.get_players(include_summary=True)

    for player in players:
        history = player.history
        history.reverse()

        history_len = min(len(history), 3)
        ict = [0] * 3
        minutes = [0] * 3
        value  = [0] * 3

        for i in range(history_len):
            ict[i] += float(history[i]["ict_index"])
            minutes[i] += float(history[i]["minutes"])
            value[i] += float(history[i]["value"])

        ict_form = Models.setHistory(feat_name = "player_ict", feat_list = ict)
        minutes_form = Models.setHistory(feat_name = "player_minutes", feat_list = minutes)
        value_form = Models.setHistory(feat_name = "player_value", feat_list = value)

        update_player(player, engine, ict_form, minutes_form, value_form)


def update_team(Team, engine):

    predicted_score = None

    if Team.id in team_fixture.keys():
        opposition = team_fixture[Team.id][0]
        off_strength = team_att_strength[Team.id] 
        def_strength = team_def_stength[opposition]
        off_form = team_att_form[Team.id]
        def_form = team_def_form[opposition]
        feat_list = [off_strength, def_strength, off_form, def_form]
        predicted_score = Models.setHistory(feat_name = "score", feat_list = feat_list)

    team_score[Team.id] = predicted_score   

    # team_score[Team.id] = predicted_score
    query = text("""UPDATE TEAM  SET strength = :strength, strength_overall_home = :strength_overall_home,
                    strength_overall_away = :strength_overall_away, strength_attack_home = :strength_attack_home,
                    strength_attack_away = :strength_attack_away, strength_defence_home = :strength_defence_home,
                    strength_defence_away = :strength_defence_away WHERE id = :id;"""
    )

    engine.execute(query,
                   strength=Team.strength,
                   strength_overall_home=Team.strength_overall_home,
                   strength_overall_away=Team.strength_overall_away,
                   strength_attack_home=Team.strength_attack_home,
                   strength_attack_away=Team.strength_attack_away,
                   strength_defence_home=Team.strength_defence_home,
                   strength_defence_away=Team.strength_defence_away,
                   id=Team.id)


async def update_teams(engine):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        teams = await fpl.get_teams()

        for team in teams:
            if team.id in team_fixture.keys():
                attack_points = [0] * 3
                defence_points = [0] * 3

                squad = await team.get_players()

                for player in squad:
                    player = await fpl.get_player(player.id, include_summary=True)
                    history = player.history
                    history.reverse()

                    history_len = min(len(history),3)

                    for i in range(history_len):
                        if player.element_type == 1 or player.element_type == 2:
                            defence_points[i] = defence_points[i] + history[-1*i]["total_points"]

                        elif player.element_type == 3 or player.element_type == 4:
                            attack_points[i] = attack_points[i] + history[i]["total_points"]

                team_att = Models.setHistory(feat_name = "team_att", feat_list = attack_points)
                team_def = Models.setHistory(feat_name = "team_def", feat_list = defence_points)

                team_att_form[team.id] = team_att
                team_def_form[team.id] = team_def

                if team_fixture[team.id][1] == "a":
                    team_att_strength[team.id] = team.strength_attack_away
                    team_def_stength[team.id] = team.strength_defence_away
                else:
                    team_att_strength[team.id] = team.strength_attack_home
                    team_def_stength[team.id] = team.strength_defence_home
                    
        
        for team in teams:
            update_team(team, engine)
    


def add_fixture(Fixture, engine):
    query = text("""INSERT INTO FIXTURE (code, id, team_a, team_h,
                    team_h_difficulty, team_a_difficulty)
                    VALUES (:code, :id, :team_a, :team_b,
                    :team_h_difficulty, :team_a_difficulty);""")

    engine.execute(query,
                   code=Fixture.code,
                   id=Fixture.id,
                   team_a=Fixture.team_a,
                   team_b=Fixture.team_h,
                   team_h_difficulty=Fixture.team_h_difficulty,
                   team_a_difficulty=Fixture.team_a_difficulty)


async def update_fixtures(engine):
    query = text("""truncate table FIXTURE;""")
    engine.execute(query)
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        gws = await fpl.get_gameweeks()

        gw_id = 38
        for gw in gws:
            if gw.is_next == True:
                gw_id = gw.id
                break
        
        fixtures = await fpl.get_fixtures_by_gameweek(gw_id)

        for fixture in fixtures:
            team_fixture[fixture.team_a] = (fixture.team_h,"a")
            team_fixture[fixture.team_h] = (fixture.team_a,"h")
            add_fixture(fixture, engine)


if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://root:pass@localhost:3600/FPL")
    engine = engine.connect()
    asyncio.run(update_fixtures(engine))
    asyncio.run(update_teams(engine))
    asyncio.run(update_players(engine))
