import pymysql

class Session:
    @staticmethod
    def get_connection():
        return pymysql.connect(
            host="localhost",
            user='ymy',
            password='0807',
            db='Mbc_Test',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )