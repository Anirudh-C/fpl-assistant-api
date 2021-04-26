-- Server version	8.0.18

CREATE DATABASE IF NOT EXISTS FPL;
USE FPL;

CREATE TABLE IF NOT EXISTS TEAM(
    id INTEGER,
    team_name text,
    short_name text,
    strength INTEGER,
    strength_overall_home INTEGER,
    strength_overall_away INTEGER,
    strength_attack_home INTEGER,
    strength_attack_away INTEGER,
    strength_defence_home INTEGER,
    strength_defence_away INTEGER,
    CONSTRAINT pk_team PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS PLAYER(
    code integer,
    element_type integer,
    web_name varchar(255),
    id integer,
    team_id integer,
    element_status varchar(1),
    chance_of_playing_next_round float,
    chance_of_playing_this_round float,
    ep_next float,
    ep_this float,
    event_points integer,
    form float,
    now_cost float,
    points_per_game float,
    total_points integer,
    goals_scored integer,
    assists integer,
    clean_sheets integer,
    saves integer,
    bonus integer,
    bps integer,
    influence integer,
    creativity integer,
    threat integer,
    ict_index integer,
    full_name text,
    score float,
    CONSTRAINT pk_player PRIMARY KEY (id),
    CONSTRAINT fk_team_id FOREIGN KEY (team_id) REFERENCES TEAM(id)
);

CREATE TABLE IF NOT EXISTS FIXTURE(
    code INTEGER,
    id INTEGER,
    team_a INTEGER,
    team_h INTEGER,
    team_h_difficulty INTEGER,
    team_a_difficulty INTEGER,
    CONSTRAINT pk_fixture PRIMARY KEY (id),
    CONSTRAINT fk_team_a FOREIGN KEY (team_a) REFERENCES TEAM(id),
    CONSTRAINT fk_team_h FOREIGN KEY (team_h) REFERENCES TEAM(id)
);

CREATE TABLE IF NOT EXISTS USER(
    id INTEGER,
    user_email varchar(255),
    user_password varchar(255),
    CONSTRAINT pk_user PRIMARY KEY (id)
); 