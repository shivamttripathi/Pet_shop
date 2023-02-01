import psycopg2

class DBConnection:
    # class members
    conn = None
    cur = None
    
    def __init__(self):
        pass
    
    @classmethod
    def dbConnect(cls):
        if not cls.conn:
            cls.conn = psycopg2.connect(
                database="postgres",
                user='postgres',
                password='Finserv@2023',
                host='127.0.0.1',
                port='5432'
            )
            cls.cur = cls.conn.cursor()
    
    @classmethod
    def createTables(cls):
        cls.cur.execute('CREATE TABLE IF NOT EXISTS owners (owner_id int generated always as identity primary key, owner_name varchar(40) not null);')
        cls.cur.execute('CREATE TABLE IF NOT EXISTS pets (pet_id int generated always as identity primary key, pet_name varchar(40) not null, pet_price int not null, pet_category varchar(40) not null);')
        cls.cur.execute('CREATE TABLE IF NOT EXISTS ownership (owner_id int not null, pet_id int not null, constraint fk_owner foreign key (owner_id) references owners (owner_id) on delete cascade, constraint fk_pet foreign key (pet_id) references pets (pet_id) on delete cascade);')
        cls.conn.commit()
    
    @classmethod
    def selectTable(cls, tname, condition = None, additions = ''):
        if condition:
            cls.cur.execute(f"SELECT * FROM {tname} WHERE {condition}{additions};")
        else:
            cls.cur.execute(f"SELECT * FROM {tname}{additions};")
        rows = cls.cur.fetchall()
        return rows
    
    @classmethod
    def insertTable(cls, tname, params):
        if len(params) == 1:
            cls.cur.execute(f"INSERT INTO {tname}(owner_name) VALUES ('{params[0]}');")
        elif len(params) == 3:
            cls.cur.execute(f"INSERT INTO {tname} (pet_name, pet_price, pet_category) VALUES ('{params[0]}', {params[1]}, '{params[2]}');")
        else:
            cls.cur.execute(f"INSERT INTO {tname} VALUES ({params[0]}, {params[1]});")
        cls.conn.commit()
    
    @classmethod
    def deleteTable(cls, tname, condition=None):
        if condition:
            cls.cur.execute(f"DELETE FROM {tname} WHERE {condition};")
        cls.conn.commit()
    
    @classmethod
    def updateTable(cls, tname, setCols=None, condition=None):
        if setCols and condition:
            cls.cur.execute(f"UPDATE {tname} SET {setCols} WHERE {condition}")
        cls.conn.commit()
    
    @classmethod
    def closeDbConnection(cls):
        cls.cur.close()
        cls.conn.close()
        cls.cur = None
        cls.conn = None