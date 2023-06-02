import sqlite3 as db


def database_connect(database_name: str):
    con = db.connect(database_name)
    cursor = con.cursor()
    return con, cursor


def tables_database_init(con, cursor):
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'tables'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'name' TEXT,
                    'date' TEXT)
    """)
    con.commit()


def database_init(con, cursor, name):
    cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS '{name}'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'time' TEXT,
                    'change' INTEGER)
    """)
    con.commit()


def admin_db_init(con, cursor):
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'admins'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT)
    """)
    con.commit()


def delete_table(con, cursor, name):
    cursor.execute(f"""
        DROP TABLE '{name}'
    """)


def insert_value(con, cursor, value, db_name):
    cursor.execute(
        f"INSERT INTO '{db_name}' ('tg_id', 'time', 'name', 'change') VALUES ('{value['tg_id']}', '{value['time']}', '{value['username']}', {value['change']})")
    con.commit()


def get_all(con, cursor, name):
    cursor.execute(f"SELECT * from '{name}' ORDER BY 'db_id'")
    return cursor.fetchall()


def close_connection(con, cursor):
    cursor.close()
    con.close()


def get_status_by_id(con, cursor, id, db_name):
    cursor.execute(f"select * from '{db_name}' where tg_id = {id} order by 'time'")
    return cursor.fetchall()


def get_status_by_no(con, cursor, id, name):
    cursor.execute(f"select * from '{name}' where db_id = {id} order by 'time'")
    return cursor.fetchall()


def change_queue(con, cursor, db_id1, db_id2):
    try:
        cursor.execute(
            f"""UPDATE 'queue' SET tg_id = '{db_id2[1]}', name = '{db_id2[2]}', change = -1 WHERE db_id = {int(db_id1[0])}""")
        con.commit()
        cursor.execute(
            f"""UPDATE 'queue' SET tg_id = '{db_id1[1]}', name = '{db_id1[2]}', change = -1 WHERE db_id = {int(db_id2[0])}""")
        con.commit()
    except Exception as e:
        print(e)


def update_change(con, cursor, db_id, change, db_name):
    try:
        cursor.execute(
            f"""UPDATE '{db_name}' SET tg_id = '{db_id[1]}', name = '{db_id[2]}', time = '{db_id[3]}', change = {int(change)} WHERE db_id = {int(db_id[0])}""")
        con.commit()
    except Exception as e:
        print(e)


def update_name(con, cursor, tg_id, name, db_name):
    try:
        cursor.execute(f"""UPDATE '{db_name}' SET name = '{name}' WHERE tg_id = '{tg_id}'""")
        con.commit()
    except Exception as e:
        print(e)


def make_admin(con, cursor, value):
    try:
        cursor.execute(f"INSERT INTO 'admins' ('tg_id', 'name') VALUES ('{value['tg_id']}', '{value['username']}')")
        con.commit()
    except Exception as e:
        print(e)


def is_admin(con, cursor, tg_id):
    try:
        cursor.execute(f"SELECT * FROM 'admins' WHERE tg_id = '{tg_id}'")
        if len(cursor.fetchall()) >= 1:
            print('true')
            return True
        else:
            print('false')
            return False
    except Exception as e:
        print(e)
        return False


def cancel_take(con, cursor, id, name):
    try:
        cursor.execute(
            f"""DELETE FROM '{name}' WHERE tg_id = '{id}'"""
        )
        lst = get_all(con, cursor)
        delete_table(con, cursor, name)
        database_init(con, cursor, name)
        if lst:
            for human in lst:
                insert_value(con, cursor, {'tg_id': human[1], 'time': human[3],
                                           'username': human[2],
                                           'change': human[4]})
        con.commit()

    except Exception as e:
        print(e)


def is_exist_table(con, cursor, name):
    try:
        cursor.execute(f"SELECT * FROM 'tables' WHERE name = '{name}'")
        if len(cursor.fetchall()) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def get_all_tables(con, cursor):
    cursor.execute("SELECT * from 'tables' ORDER BY 'name'")
    return cursor.fetchall()


def insert_table(con, cursor, value):
    try:
        cursor.execute(f"INSERT INTO 'tables' ('name', 'date') VALUES ('{value['name']}', '{value['date']}')")
        con.commit()
    except Exception as e:
        print(e)


def delete_table_from_table(con, cursor, name):
    try:
        cursor.execute(f"DELETE FROM 'tables' where name = '{name}'")
        con.commit()
    except Exception as e:
        print(e)


"""FOR TESTS"""
if __name__ == "__main__":
    con, cursor = database_connect('queue')
    database_init(con, cursor, 'queue')
    delete_table(con, cursor, 'queue')
