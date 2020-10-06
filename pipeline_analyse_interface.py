import psycopg2


class database_connection:
    def __init__(self, host, port, database_name, user, password):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg2.connect(host=self.host, port=self.port, 
                          database=self.database_name, user=self.user, password=self.password)
        self.cursor = self.connection.cursor()
    
    def get_by_id(self, institute_id: str):
        self.cursor.execute("SELECT * FROM output WHERE instituutid={}".format(institute_id))
        return self.cursor.fetchall()
    
    def get_all_entries(self):
        self.cursor.execute("SELECT * FROM output")
        return self.cursor.fetchall()
    
    def add_new_entry(self, word: str, institute_id: int, count: int):
        self.cursor.execute("INSERT INTO output VALUES (\'{0}\', {1}, {2})".format(word, institute_id, count))
        self.connection.commit()
    
    def clear_table(self, table_name):
        self.cursor.execute("DELETE FROM {}".format(table_name))
        self.connection.commit()

    def create_dict(self, institute_id):
        if institute_id == "*":
            return self.get_dict(self.get_all_entries())
        else:
            return self.get_dict(self.get_by_id(int(institute_id)))

    def get_dict(self, data_entries):
        entry_dict = {}
        for data_entry in data_entries:
            entry_dict[data_entry[0]] = data_entry[2]
        return entry_dict


def main():
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_name = "innodb"
    user = "innouser"
    password = "innouser"
    db = database_connection(host, port, database_name, user, password)
    db.connect()

    for i in range(0, 100):
        db.add_new_entry("test" + str(i), i, i * 10)
    print(db.get_all_entries())

    # db.add_new_entry("test4", 66, 666)
    # print(db.get_all_entries())
    # test_dict = db.create_dict(69)
    # print(test_dict)

    # db.clear_table("output")
    # print(db.get_all_entries())


# main()