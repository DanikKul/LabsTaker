import sqlite3
import sqlite3 as db


def database_connect(database_name: str) -> [sqlite3.Connection, sqlite3.Cursor]:
    con = db.connect(database_name)
    cursor = con.cursor()
    return con, cursor


def tables_database_init(con: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'tables'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'name' TEXT,
                    'date' TEXT,
                    'time' TEXT)
    """)
    con.commit()


def database_init(con: sqlite3.Connection, cursor: sqlite3.Cursor, table_name):
    cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS '{table_name}'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'time' timestamp,
                    'change' INTEGER)
    """)
    con.commit()


def db_init_users(con: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS 'users'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'points' INTEGER)
    """)
    con.commit()


def db_init_admin(con: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'admins'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT)
    """)
    con.commit()


def delete_table(con: sqlite3.Connection, cursor: sqlite3.Cursor, table_name: str):
    cursor.execute(f"""
        DROP TABLE '{table_name}'
    """)


def insert_value(con: sqlite3.Connection, cursor: sqlite3.Cursor, value: dict, table_name: str):
    try:
        cursor.execute(
            f"INSERT INTO '{table_name}' ('tg_id', 'time', 'name', 'change') VALUES ('{value['tg_id']}', '{value['time']}', '{value['username']}', {value['change']})")
        con.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def insert_user(con: sqlite3.Connection, cursor: sqlite3.Cursor, value: dict):
    try:
        cursor.execute(
            f"INSERT INTO 'users' ('tg_id', 'name', 'points') VALUES ('{value['tg_id']}', '{value['username']}', '{value['points']}')")
        con.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def get_all(con: sqlite3.Connection, cursor: sqlite3.Cursor, table_name: str) -> list:
    cursor.execute(f"SELECT * from '{table_name}' ORDER BY 'db_id'")
    return cursor.fetchall()


def get_all_admins(con: sqlite3.Connection, cursor: sqlite3.Cursor) -> list:
    cursor.execute(f"SELECT * from 'admins' ORDER BY 'db_id'")
    return cursor.fetchall()


def get_all_users(con: sqlite3.Connection, cursor: sqlite3.Cursor) -> list:
    cursor.execute(f"SELECT * from 'users' ORDER BY 'db_id'")
    return cursor.fetchall()


def get_user(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str) -> list:
    print(tg_id)
    cursor.execute(f"SELECT * from 'users' WHERE 'tg_id' = '{tg_id}'")
    return cursor.fetchall()


def insert_admin(con: sqlite3.Connection, cursor: sqlite3.Cursor, value: dict):
    try:
        cursor.execute(
            f"INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')")
        con.commit()
    except Exception as e:
        print("FUNC: insert_value ERR:", e)


def remove_admin(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str):
    try:
        cursor.execute(
            f"""DELETE FROM 'admins' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all_admins(con, cursor)
        delete_table(con, cursor, 'admins')
        db_init_admin(con, cursor)
        if lst:
            for human in lst:
                insert_admin(con, cursor, {'tg_id': human[1], 'username': human[2]})
        con.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def remove_user(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str):
    try:
        cursor.execute(
            f"""DELETE FROM 'users' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all_users(con, cursor)
        delete_table(con, cursor, 'users')
        db_init_users(con, cursor)
        if lst:
            for human in lst:
                insert_user(con, cursor, {'tg_id': human[1], 'username': human[2]})
        con.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def get_all_in_order(con: sqlite3.Connection, cursor: sqlite3.Cursor, table_name: str) -> list:
    cursor.execute(f"SELECT * from '{table_name}' ORDER BY 'time'")
    return cursor.fetchall()


def close_connection(con: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.close()
    con.close()


def get_status_by_id(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str, table_name: str) -> list:
    cursor.execute(f"select * from '{table_name}' where tg_id = '{tg_id}' order by 'time'")
    return cursor.fetchall()


def get_status_by_no(con: sqlite3.Connection, cursor: sqlite3.Cursor, db_id: int, table_name: str) -> list:
    cursor.execute(f"select * from '{table_name}' where db_id = {db_id} order by 'time'")
    return cursor.fetchall()


def change_queue(con: sqlite3.Connection, cursor: sqlite3.Cursor, db_id1: list, db_id2: list, table_name: str):
    try:
        cursor.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id2[1]}', name = '{db_id2[2]}', change = -1 WHERE db_id = {int(db_id1[0])}""")
        con.commit()
        cursor.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id1[1]}', name = '{db_id1[2]}', change = -1 WHERE db_id = {int(db_id2[0])}""")
        con.commit()
    except Exception as e:
        print("FUNC: change_queue ERR:", e)


def update_change(con: sqlite3.Connection, cursor: sqlite3.Cursor, db_id: list, change: int, table_name):
    try:
        cursor.execute(
            f"""UPDATE '{table_name}' SET tg_id = '{db_id[1]}', name = '{db_id[2]}', time = '{db_id[3]}', change = {change} WHERE db_id = {int(db_id[0])}""")
        con.commit()
    except Exception as e:
        print("FUNC: update_change ERR:", e)


def update_name(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str, name: str, table_name: str):
    try:
        cursor.execute(f"""UPDATE '{table_name}' SET name = '{name}' WHERE tg_id = '{tg_id}'""")
        con.commit()
    except Exception as e:
        print("FUNC: update_name ERR:", e)


def make_admin(con: sqlite3.Connection, cursor: sqlite3.Cursor, value: dict):
    try:
        cursor.execute(f"INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')")
        con.commit()
    except Exception as e:
        print("FUNC: make_admin ERR:", e)


def is_admin(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str) -> bool:
    try:
        cursor.execute(f"SELECT * FROM 'admins' WHERE tg_id = '{tg_id}'")
        if len(cursor.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_admin ERR:", e)
        return False


def cancel_take(con: sqlite3.Connection, cursor: sqlite3.Cursor, tg_id: str, table_name: str):
    try:
        cursor.execute(
            f"""DELETE FROM '{table_name}' WHERE tg_id = '{tg_id}'"""
        )
        lst = get_all(con, cursor, table_name)
        delete_table(con, cursor, table_name)
        database_init(con, cursor, table_name)
        if lst:
            for human in lst:
                insert_value(con, cursor, {'tg_id': human[1], 'time': human[3],
                                           'username': human[2],
                                           'change': human[4]}, table_name)
        con.commit()

    except Exception as e:
        print("FUNC: cancel_take ERR:", e)


def is_exist_table(con: sqlite3.Connection, cursor: sqlite3.Cursor, name: str) -> bool:
    try:
        cursor.execute(f"SELECT * FROM 'tables' WHERE name = '{name}'")
        if len(cursor.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print("FUNC: is_exist_table ERR:", e)
        return False


def get_all_tables(con: sqlite3.Connection, cursor: sqlite3.Cursor) -> list:
    cursor.execute("SELECT * from 'tables' ORDER BY 'name'")
    return cursor.fetchall()


def insert_table(con: sqlite3.Connection, cursor: sqlite3.Cursor, value: dict):
    try:
        cursor.execute(
            f"INSERT INTO 'tables' ('name', 'date', 'time') VALUES ('{value['name']}', '{value['date']}', '{value['time']}')")
        con.commit()
    except Exception as e:
        print("FUNC: insert_table ERR:", e)


def delete_table_from_table(con: sqlite3.Connection, cursor: sqlite3.Cursor, name: str):
    try:
        cursor.execute(f"DELETE FROM 'tables' where name = '{name}'")
        con.commit()
    except Exception as e:
        print("FUNC: delete_table_from_table ERR:", e)


def get_table_name(con: sqlite3.Connection, cursor: sqlite3.Cursor, no: int) -> str:
    tables = get_all_tables(con, cursor)
    if len(tables) >= no:
        return tables[no - 1][1]
    return ''


def get_table_time(con: sqlite3.Connection, cursor: sqlite3.Cursor, no: int) -> str:
    tables = get_all_tables(con, cursor)
    if len(tables) >= no:
        return tables[no - 1][3]
    return ''


def set_table_time(con: sqlite3.Connection, cursor: sqlite3.Cursor, table_name: str, time: str):
    try:
        cursor.execute(f"""UPDATE 'tables' SET time = '{time}' WHERE name = '{table_name}'""")
        con.commit()
    except Exception as e:
        print("FUNC: set_table_time ERR:", e)


"""FOR TESTS"""
if __name__ == "__main__":
    con_test, cursor_test = database_connect('queue')
    database_init(con_test, cursor_test, 'queue')
    delete_table(con_test, cursor_test, 'queue')
