import sqlite3
import sqlite3 as db


def database_connect(database_name: str) -> [sqlite3.Connection, sqlite3.Cursor]:
    conn = db.connect(database_name)
    curs = conn.cursor()
    return conn, curs


def tables_database_init(conn: sqlite3.Connection, curs: sqlite3.Cursor):
    curs.execute("""
                CREATE TABLE IF NOT EXISTS 'tables'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'name' TEXT,
                    'date' TEXT,
                    'time' TEXT)
    """)
    conn.commit()


def database_init(conn: sqlite3.Connection, curs: sqlite3.Cursor, table_name):
    curs.execute(f"""
                CREATE TABLE IF NOT EXISTS '{table_name}'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'time' timestamp,
                    'change' INTEGER)
    """)
    conn.commit()


def db_init_users(conn: sqlite3.Connection, curs: sqlite3.Cursor):
    curs.execute(f"""
                CREATE TABLE IF NOT EXISTS 'users'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'points' INTEGER)
    """)
    conn.commit()


def db_init_admin(conn: sqlite3.Connection, curs: sqlite3.Cursor):
    curs.execute("""
                CREATE TABLE IF NOT EXISTS 'admins'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT)
    """)
    conn.commit()


def delete_table(conn: sqlite3.Connection, curs: sqlite3.Cursor, table_name: str):
    curs.execute(f"""
        DROP TABLE '{table_name}'
    """)


def insert_value(conn: sqlite3.Connection, curs: sqlite3.Cursor, value: dict, table_name: str):
    try:
        curs.execute(
            f"INSERT INTO '{table_name}' ('tg_id', 'time', 'name', 'change') VALUES ('{value['tg_id']}', '{value['time']}', '{value['username']}', {value['change']})")
        conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def insert_user(conn: sqlite3.Connection, curs: sqlite3.Cursor, value: dict):
    try:
        curs.execute(
            f"INSERT INTO 'users' ('tg_id', 'name', 'points') VALUES ('{value['tg_id']}', '{value['username']}', '{value['points']}')")
        conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def get_all(conn: sqlite3.Connection, curs: sqlite3.Cursor, table_name: str) -> list:
    curs.execute(f"SELECT * from '{table_name}' ORDER BY 'db_id'")
    return curs.fetchall()


def get_all_admins(conn: sqlite3.Connection, curs: sqlite3.Cursor) -> list:
    curs.execute(f"SELECT * from 'admins' ORDER BY 'db_id'")
    return curs.fetchall()


def get_all_users(conn: sqlite3.Connection, curs: sqlite3.Cursor) -> list:
    curs.execute(f"SELECT * from 'users' ORDER BY 'db_id'")
    return curs.fetchall()


def get_user(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str) -> list:
    print(tg_id)
    curs.execute(f"SELECT * from 'users' WHERE 'tg_id' = '{tg_id}'")
    return curs.fetchall()


def insert_admin(conn: sqlite3.Connection, curs: sqlite3.Cursor, value: dict):
    try:
        curs.execute(
            f"INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')")
        conn.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def remove_admin(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str):
    try:
        curs.execute(
            f"""DELETE FROM 'admins' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all_admins(conn, curs)
        delete_table(conn, curs, 'admins')
        db_init_admin(conn, curs)
        if lst:
            for human in lst:
                insert_admin(conn, curs, {'tg_id': human[1], 'username': human[2]})
        conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def remove_user(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str):
    try:
        curs.execute(
            f"""DELETE FROM 'users' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all_users(conn, curs)
        delete_table(conn, curs, 'users')
        db_init_users(conn, curs)
        if lst:
            for human in lst:
                insert_user(conn, curs, {'tg_id': human[1], 'username': human[2]})
        conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def get_all_in_order(conn: sqlite3.Connection, curs: sqlite3.Cursor, table_name: str) -> list:
    curs.execute(f"SELECT * from '{table_name}' ORDER BY 'time'")
    return curs.fetchall()


def close_connection(conn: sqlite3.Connection, curs: sqlite3.Cursor):
    curs.close()
    conn.close()


def get_status_by_id(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str, table_name: str) -> list:
    curs.execute(f"select * from '{table_name}' where tg_id = '{tg_id}' order by 'time'")
    return curs.fetchall()


def get_status_by_no(conn: sqlite3.Connection, curs: sqlite3.Cursor, db_id: int, table_name: str) -> list:
    curs.execute(f"select * from '{table_name}' where db_id = {db_id} order by 'time'")
    return curs.fetchall()


def change_queue(conn: sqlite3.Connection, curs: sqlite3.Cursor, db_id1: list, db_id2: list, table_name: str):
    try:
        curs.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id2[1]}', name = '{db_id2[2]}', change = -1 WHERE db_id = {int(db_id1[0])}""")
        conn.commit()
        curs.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id1[1]}', name = '{db_id1[2]}', change = -1 WHERE db_id = {int(db_id2[0])}""")
        conn.commit()
    except Exception as e:
        print("FUNC: change_queue ERR:", e)


def update_change(conn: sqlite3.Connection, curs: sqlite3.Cursor, db_id: list, change: int, table_name):
    try:
        curs.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id[1]}', name = '{db_id[2]}', time = '{db_id[3]}', change = {change} WHERE db_id = {int(db_id[0])}""")
        conn.commit()
    except Exception as e:
        print("FUNC: update_change ERR:", e)


def update_name(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str, name: str, table_name: str):
    try:
        curs.execute(f"""UPDATE '{table_name}' SET name = '{name}' WHERE tg_id = '{tg_id}'""")
        conn.commit()
    except Exception as e:
        print("FUNC: update_name ERR:", e)


def make_admin(conn: sqlite3.Connection, curs: sqlite3.Cursor, value: dict):
    try:
        curs.execute(f"INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')")
        conn.commit()
    except Exception as e:
        print("FUNC: make_admin ERR:", e)


def is_admin(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str) -> bool:
    try:
        curs.execute(f"SELECT * FROM 'admins' WHERE tg_id = '{tg_id}'")
        if len(curs.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_admin ERR:", e)
        return False


def cancel_take(conn: sqlite3.Connection, curs: sqlite3.Cursor, tg_id: str, table_name: str):
    try:
        curs.execute(
            f"""DELETE FROM '{table_name}' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all(conn, curs, table_name)
        delete_table(conn, curs, table_name)
        database_init(conn, curs, table_name)
        if lst:
            for human in lst:
                insert_value(conn, curs, {'tg_id': human[1], 'time': human[3],
                                           'username': human[2],
                                           'change': human[4]}, table_name)
        conn.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def is_exist_table(conn: sqlite3.Connection, curs: sqlite3.Cursor, name: str) -> bool:
    try:
        curs.execute(f"SELECT * FROM 'tables' WHERE name = '{name}'")
        if len(curs.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_exist_table ERR:", e)
        return False


def get_all_tables(conn: sqlite3.Connection, curs: sqlite3.Cursor) -> list:
    curs.execute("SELECT * from 'tables' ORDER BY 'name'")
    return curs.fetchall()


def insert_table(conn: sqlite3.Connection, curs: sqlite3.Cursor, value: dict):
    try:
        curs.execute(
            f"INSERT INTO 'tables' ('name', 'date', 'time') VALUES ('{value['name']}', '{value['date']}', '{value['time']}')")
        conn.commit()
    except Exception as e:
        print("FUNC: insert_table ERR:", e)


def delete_table_from_table(conn: sqlite3.Connection, curs: sqlite3.Cursor, name: str):
    try:
        curs.execute(f"DELETE FROM 'tables' where name = '{name}'")
        conn.commit()
    except Exception as e:
        print("FUNC: delete_table_from_table ERR:", e)


def get_table_name(conn: sqlite3.Connection, curs: sqlite3.Cursor, no: int) -> str:
    tables = get_all_tables(conn, curs)
    if len(tables) >= no:
        return tables[no - 1][1]
    return ''


def get_table_time(conn: sqlite3.Connection, curs: sqlite3.Cursor, no: int) -> str:
    tables = get_all_tables(conn, curs)
    if len(tables) >= no:
        return tables[no - 1][3]
    return ''


def set_table_time(conn: sqlite3.Connection, curs: sqlite3.Cursor, table_name: str, time: str):
    try:
        curs.execute(f"""UPDATE 'tables' SET time = '{time}' WHERE name = '{table_name}'""")
        conn.commit()
    except Exception as e:
        print("FUNC: set_table_time ERR:", e)


"""FOR TESTS"""
if __name__ == "__main__":
    con_test, cursor_test = database_connect('queue')
    database_init(con_test, cursor_test, 'queue')
    delete_table(con_test, cursor_test, 'queue')
