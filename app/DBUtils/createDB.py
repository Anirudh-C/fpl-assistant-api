# DB imports
from sqlalchemy import create_engine
from sqlalchemy import text


def create_db(sql_file, engine):
    run_database_file(sql_file, engine)


def run_database_file(sql_file, engine):
    sql_file = open(sql_file, 'r')
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
                    engine.execute(text(sql_command))

                # Assert in case of error
                except:
                    print('Ops')

                # Finally, clear command string
                finally:
                    sql_command = ''


if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://root:pass@localhost:3600")
    engine = engine.connect()
    create_db("schema.sql", engine)
