import sqlite3 as db
from sqlite3 import Connection, Cursor


# I don't know why it's actually exists but it's ok :|
class Session:
    conn: Connection
    curs: Cursor

    def __init__(self, conn: Connection, curs: Cursor):
        self.conn = conn
        self.curs = curs


def database_connect(db_name: str) -> Session:
    conn = db.connect(db_name)
    curs = conn.cursor()
    return Session(conn, curs)


def tables_database_init(session: Session):

    session.curs.execute("""
                CREATE TABLE IF NOT EXISTS 'tables'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'name' TEXT,
                    'date' TEXT,
                    'time' TEXT)
    """)
    session.conn.commit()


def database_init(session: Session, tb_name: str):
    session.curs.execute(f"""
                CREATE TABLE IF NOT EXISTS '{tb_name}'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'time' timestamp,
                    'change' INTEGER)
    """)
    session.conn.commit()


def db_init_users(session: Session):
    session.curs.execute(f"""
                CREATE TABLE IF NOT EXISTS 'users'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'points' INTEGER)
    """)
    session.conn.commit()


def db_init_admin(session: Session):
    session.curs.execute(f"""
                CREATE TABLE IF NOT EXISTS 'admins'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT)
    """)
    session.conn.commit()


def delete_table(session: Session, tb_name: str):
    session.curs.execute(f"""
        DROP TABLE '{tb_name}'
    """)


def insert_value(session: Session, value: dict, tb_name: str):
    try:
        session.curs.execute(f"""
            INSERT INTO '{tb_name}' ('tg_id', 'time', 'name', 'change') VALUES ('{value['tg_id']}', '{value['time']}', '{value['username']}', {value['change']})
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def insert_user(session: Session, value: dict):
    try:
        session.curs.execute(f"""
            INSERT INTO 'users' ('tg_id', 'name', 'points') VALUES ('{value['tg_id']}', '{value['username']}', '{value['points']}')
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def get_all(session: Session, tb_name: str) -> list:
    session.curs.execute(f"""
        SELECT * FROM '{tb_name}' ORDER BY 'db_id'
    """)
    return session.curs.fetchall()


def get_all_admins(session: Session) -> list:
    session.curs.execute(f"""
        SELECT * FROM 'admins' ORDER BY 'db_id'
    """)
    return session.curs.fetchall()


def get_all_users(session: Session) -> list:
    session.curs.execute(f"""
        SELECT * FROM 'users' ORDER BY 'db_id'
    """)
    return session.curs.fetchall()


def get_user(session: Session, tg_id: str) -> list:
    print(tg_id)
    session.curs.execute(f"""
        SELECT * FROM 'users' WHERE 'tg_id' = '{tg_id}'
    """)
    return session.curs.fetchall()


def insert_admin(session: Session, value: dict):
    try:
        session.curs.execute(f"""
            INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def remove_admin(session: Session, tg_id: str):
    try:
        session.curs.execute(f"""
            DELETE FROM 'admins' WHERE tg_id = '{tg_id}'
        """)
        lst = get_all_admins(session)
        delete_table(session, 'admins')
        db_init_admin(session)
        if lst:
            for human in lst:
                insert_admin(session, {'tg_id': human[1], 'username': human[2]})
        session.conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def remove_user(session: Session, tg_id: str):
    try:
        session.conn.execute(f"""
            DELETE FROM 'users' WHERE tg_id = '{tg_id}'
        """)
        lst = get_all_users(session)
        delete_table(session, 'users')
        db_init_users(session)
        if lst:
            for human in lst:
                insert_user(session, {'tg_id': human[1], 'username': human[2]})
        session.conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def get_all_in_order(session: Session, tb_name: str) -> list:
    session.curs.execute(f"""
        SELECT * FROM '{tb_name}' ORDER BY 'time'
    """)
    return session.curs.fetchall()


def close_connection(session: Session):
    session.curs.close()
    session.conn.close()


def get_status_by_id(session: Session, tg_id: str, tb_name: str) -> list:
    session.curs.execute(f"""
        SELECT * FROM '{tb_name}' WHERE tg_id = '{tg_id}' ORDER BY 'time'
    """)
    return session.curs.fetchall()


def get_status_by_no(session: Session, db_id: int, tb_name: str) -> list:
    session.curs.execute(f"""
        SELECT * FROM '{tb_name}' WHERE db_id = {db_id} ORDER BY 'time'
    """)
    return session.curs.fetchall()


def change_queue(session: Session, db_id1: list, db_id2: list, tb_name: str):
    try:
        session.curs.execute(f"""
            UPDATE '{tb_name}' SET tg_id = '{db_id2[1]}', name = '{db_id2[2]}', change = -1 WHERE db_id = {int(db_id1[0])}
        """)
        session.conn.commit()
        session.curs.execute(f"""
            UPDATE '{tb_name}' SET tg_id = '{db_id1[1]}', name = '{db_id1[2]}', change = -1 WHERE db_id = {int(db_id2[0])}
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: change_queue ERR:", e)


def update_change(session: Session, db_id: list, change: int, tb_name):
    try:
        session.curs.execute(f"""
            UPDATE '{tb_name}' SET tg_id = '{db_id[1]}', name = '{db_id[2]}', time = '{db_id[3]}', change = {change} WHERE db_id = {int(db_id[0])}
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: update_change ERR:", e)


def update_name(session: Session, tg_id: str, name: str, tb_name: str):
    try:
        session.curs.execute(f"""
            UPDATE '{tb_name}' SET name = '{name}' WHERE tg_id = '{tg_id}'
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: update_name ERR:", e)


def make_admin(session: Session, value: dict):
    try:
        session.curs.execute(f"""
            INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: make_admin ERR:", e)


def is_admin(session: Session, tg_id: str) -> bool:
    try:
        session.curs.execute(f"""
            SELECT * FROM 'admins' WHERE tg_id = '{tg_id}'
        """)
        if len(session.curs.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_admin ERR:", e)
        return False


def cancel_take(session: Session, tg_id: str, tb_name: str):
    try:
        session.curs.execute(
            f"""DELETE FROM '{tb_name}' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all(session, tb_name)
        delete_table(session, tb_name)
        database_init(session, tb_name)
        if lst:
            for human in lst:
                insert_value(session, {'tg_id': human[1], 'time': human[3], 'username': human[2], 'change': human[4]}, tb_name)
        session.conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def is_exist_table(session: Session, name: str) -> bool:
    try:
        session.curs.execute(f"""
            SELECT * FROM 'tables' WHERE name = '{name}'
        """)
        if len(session.curs.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_exist_table ERR:", e)
        return False


def get_all_tables(session: Session) -> list:
    session.curs.execute(f"""
        SELECT * from 'tables' ORDER BY 'name'
    """)
    return session.curs.fetchall()


def insert_table(session: Session, value: dict):
    try:
        session.curs.execute(f"""
            INSERT INTO 'tables' ('name', 'date', 'time') VALUES ('{value['name']}', '{value['date']}', '{value['time']}')
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: insert_table ERR:", e)


def delete_table_from_table(session: Session, name: str):
    try:
        session.curs.execute(f"""
            DELETE FROM 'tables' where name = '{name}'
        """)
        session.conn.commit()
    except Exception as e:
        print("FUNC: delete_table_from_table ERR:", e)


def get_table_name(session: Session, no: int) -> str:
    tables = get_all_tables(session)
    if len(tables) >= no:
        return tables[no - 1][1]
    return ''


def get_table_time(session: Session, no: int) -> str:
    tables = get_all_tables(session)
    if len(tables) >= no:
        return tables[no - 1][3]
    return ''


def set_table_time(session: Session, tb_name: str, time: str):
    try:
        session.curs.execute(f"""UPDATE 'tables' SET time = '{time}' WHERE name = '{tb_name}'""")
        session.conn.commit()
    except Exception as e:
        print("FUNC: set_table_time ERR:", e)


"""FOR TESTS"""
if __name__ == "__main__":
    con_test, cursor_test = database_connect('queue')
    database_init(con_test, cursor_test, 'queue')
    delete_table(con_test, cursor_test, 'queue')
