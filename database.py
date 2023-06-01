import sqlite3 as db


def database_connect(database_name: str):
    con = db.connect(database_name)
    cursor = con.cursor()
    return con, cursor


def database_init(con, cursor):
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS 'queue'
                    ('db_id' INTEGER PRIMARY KEY AUTOINCREMENT,  
                    'tg_id' TEXT,
                    'name' TEXT,
                    'time' TEXT,
                    'change' INTEGER)
    """)
    con.commit()


def delete_table(con, cursor):
    cursor.execute("""
        DROP TABLE 'queue'
    """)


def insert_value(con, cursor, value):
    cursor.execute(f"INSERT INTO 'queue' ('tg_id', 'time', 'name', 'change') VALUES ('{value['tg_id']}', '{value['time']}', '{value['username']}', {value['change']})")
    con.commit()


def get_all(con, cursor):
    cursor.execute("SELECT * from 'queue' ORDER BY 'time'")
    return cursor.fetchall()


def close_connection(con, cursor):
    cursor.close()
    con.close()


def get_status_by_id(con, cursor, id):
    cursor.execute(f"select * from 'queue' where tg_id = {id} order by 'time'")
    return cursor.fetchall()


def get_status_by_no(con, cursor, id):
    cursor.execute(f"select * from 'queue' where db_id = {id} order by 'time'")
    return cursor.fetchall()


def change_queue(con, cursor, db_id1, db_id2):
    try:
        cursor.execute(f"""UPDATE 'queue' SET tg_id = '{db_id2[1]}', name = '{db_id2[2]}', change = -1 WHERE db_id = {int(db_id1[0])}""")
        con.commit()
        cursor.execute(f"""UPDATE 'queue' SET tg_id = '{db_id1[1]}', name = '{db_id1[2]}', change = -1 WHERE db_id = {int(db_id2[0])}""")
        con.commit()
    except Exception as e:
        print(e)


def update_change(con, cursor, db_id, change):
    try:
        cursor.execute(f"""UPDATE 'queue' SET tg_id = '{db_id[1]}', name = '{db_id[2]}', time = '{db_id[3]}', change = {int(change)} WHERE db_id = {int(db_id[0])}""")
        con.commit()
    except Exception as e:
        print(e)


def update_name(con, cursor, tg_id, name):
    try:
        cursor.execute(f"""UPDATE 'queue' SET name = '{name}' WHERE tg_id = '{tg_id}'""")
        con.commit()
    except Exception as e:
        print(e)


def cancel_take(con, cursor, id):
    try:
        cursor.execute(
            f"""DELETE FROM 'queue' WHERE tg_id = '{id}'"""
        )
        lst = get_all(con, cursor)
        delete_table(con, cursor)
        database_init(con, cursor)
        if lst:
            for human in lst:
                insert_value(con, cursor, {'tg_id': human[1], 'time': human[3],
                                   'username': human[2],
                                   'change': human[4]})
        con.commit()

    except Exception as e:
        print(e)


"""FOR TESTS"""
if __name__ == "__main__":
    con, cursor = database_connect('queue')
    database_init(con, cursor)
    delete_table(con, cursor)
