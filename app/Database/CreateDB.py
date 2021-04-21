# Basic imports
import os

# DB imports
from sqlalchemy import create_engine
from sqlalchemy import text

# FPL API wrapper imports
import aiohttp
import asyncio

def run_file(sql_file, engine):
    sql_file = open(sql_file,'r')
    session = engine.connect()
    # Create an empty command string
    sql_command = ''

    # Iterate over all lines in the sql file
    for line in sql_file:
        # Ignore commented lines
        if not line.startswith('--') and line.strip('\n'):
            # Append line to the command string
            sql_command += line.strip('\n')

            # If the command string ends with ';', it is a full statement
            if sql_command.endswith(';'):
                # Try to execute statement and commit it
                try:
                    session.execute(text(sql_command))
                    # session.commit()

                # Assert in case of error
                except:
                    print('Ops')

                # Finally, clear command string
                finally:
                    sql_command = ''

if __name__ == "__main__":
    # # DB connection ENV variables
    # db_host = os.environ.get("DB_HOST")
    # db_user = os.environ.get("DB_USERNAME")
    # db_pass = os.environ.get("DB_PASS")
    # db_name = "FPL"
    # engine = create_engine(
        # "mysql+pymysql://{}:{}@{}/{}".format(db_user, db_pass, db_host, db_name))
    engine = create_engine("mysql+pymysql://root:pass@localhost:3600")
    run_file("schema.sql", engine)


