import Database
import aiohttp
import asyncio
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root:pass@localhost:3600/FPL")
engine.connect()

query = text("""SELECT * from PLAYER WHERE team_id = :x;""")

result = engine.execute(query, x = 1)

result = [dict(res) for res in result]

for res in result:
    print(res)

