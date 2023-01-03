import psycopg2
from flask import Flask
from quotes import db_quotes

app = None

# name of the table to create
TABLE_NAME = "quotes"


def import_app(_app: Flask) -> None:
    """import app object from main file"""
    global app
    app = _app


def check_if_table_exists(db_conn: dict) -> bool:
    """check if the table already exists"""
    app.logger.info("Checking if the table exists in the database ...")
    check_table_exists_sql = f"""
    SELECT EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public' AND tablename  = '{TABLE_NAME}'
    )
    """
    # we assume that the table exists
    exists = True
    res = None

    try:
        with psycopg2.connect(
            host=db_conn["host"],
            port=db_conn["port"],
            user=db_conn["user"],
            password=db_conn["password"],
            database=db_conn["name"],
        ) as connection:
            with connection.cursor() as cursor:
                app.logger.info("Checking if table exists ...")
                cursor.execute(check_table_exists_sql)
                res = cursor.fetchone()
            connection.commit()
        exists = res[0]
    except psycopg2.DatabaseError as err:
        app.logger.error(f"check if table exists: {err}")
        return False

    app.logger.info(f"Table exists: {exists}")

    # if it exists return ture, otherwise create the table
    # and return true if table creation succeeds
    if exists:
        return True
    created = create_table(db_conn)
    return created


def create_table(db_conn: dict) -> bool:
    """create the table for storing quotes"""

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        quote VARCHAR(1000) NOT NULL
    );
    """
    try:
        app.logger.info("Creating table ...")
        with psycopg2.connect(
            host=db_conn["host"],
            port=db_conn["port"],
            user=db_conn["user"],
            password=db_conn["password"],
            database=db_conn["name"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)
            connection.commit()
            insert_default_quotes(db_conn)
            return True
    except psycopg2.DatabaseError as err:
        app.logger.error(f"when creating table: {err}")
        return False


def get_version(db_conn: dict) -> str:
    """check the version of the database"""
    app.logger.info("Checking the version of the database ...")
    try:
        with psycopg2.connect(
            host=db_conn["host"],
            port=db_conn["port"],
            user=db_conn["user"],
            password=db_conn["password"],
            database=db_conn["name"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW server_version;")
                res = cursor.fetchone()
                app.logger.info(f"Database version: {res[0]}")
                return res[0]
    except psycopg2.DatabaseError as err:
        app.logger.error(f"when checking database version: {err}")
        return None


def check_connection(db_conn: dict) -> bool:
    """check if the db is connected"""
    app.logger.info("Attempting to connect to the database ...")
    try:
        # try to creat a connection to the database
        with psycopg2.connect(
            host=db_conn["host"],
            port=db_conn["port"],
            user=db_conn["user"],
            password=db_conn["password"],
            database=db_conn["name"],
        ):
            # do nothing, we only want to check if we can connect
            app.logger.info("Successfully connected to the database.")
        return True
    except psycopg2.OperationalError as err:
        app.logger.error(f"Could not connect to to database, reason: {err}")
        return False


def insert_quote(quote: str, db_conn: dict) -> bool:
    """insert a new quote into the database"""
    insert_sql = f"INSERT INTO {TABLE_NAME} (quote) VALUES (%s);"
    try:
        if check_if_table_exists(db_conn):
            with psycopg2.connect(
                host=db_conn["host"],
                port=db_conn["port"],
                user=db_conn["user"],
                password=db_conn["password"],
                database=db_conn["name"],
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(insert_sql, (quote,))
                connection.commit()
                return True
        app.logger.error("table does not exist.")
        return False
    except psycopg2.OperationalError as err:
        app.logger.error(f"Could not connect to to database, reason: {err}")
        return False


def get_quotes(db_conn: dict) -> list:
    """get list of all quotes from the database"""
    select_sql = f"SELECT quote FROM {TABLE_NAME}"
    try:
        if check_if_table_exists(db_conn):
            with psycopg2.connect(
                host=db_conn["host"],
                port=db_conn["port"],
                user=db_conn["user"],
                password=db_conn["password"],
                database=db_conn["name"],
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(select_sql)
                    res = list(cursor.fetchall())
                    if res:
                        quotes = []
                        for row in res:
                            quotes.append(row[0])
                        return quotes
                    return []
        app.logger.error("table does not exist.")
        return []
    except psycopg2.DatabaseError as err:
        app.logger.error(f"when getting quotes from the db: {err}")
        return None


def insert_default_quotes(db_conn: dict):
    """insert the default quotes into the database"""
    app.logger.info("Inserting default quotes into database ...")
    for quote in db_quotes:
        insert_quote(quote, db_conn)


def get_db_hostname(db_conn: dict) -> str:
    """get the hostname of the postgres database"""
    # read the file /etc/hostname file to get hostname of postgres server
    select_sql = "select pg_read_file('/etc/hostname') as hostname;"
    try:
        with psycopg2.connect(
            host=db_conn["host"],
            port=db_conn["port"],
            user=db_conn["user"],
            password=db_conn["password"],
            database=db_conn["name"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(select_sql)
                res = cursor.fetchone()[0]
                if res:
                    # strip whitespace from string and return
                    return res.strip()
                return None
    except psycopg2.DatabaseError as err:
        app.logger.error(f"when getting hostname of db server")
        app.logger.error(err)
        return None
