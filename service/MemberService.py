from common.session import Session
from domain.Member import Member

class MemberService:
    @classmethod
    def load_count(cls):
        conn = Session.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) as cnt FROM members')
                return cursor.fetchone()['cnt']

        except Exception as e:
            print(f'오류 발생: {e}')

        finally:
            conn.close()

    @classmethod
    def signup(cls,uid,pw,name):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("select id from members where uid = %s",(uid,))
                if cursor.fetchone():
                    return 'EXIST'

                sql = 'insert into members (uid,pw,name) values (%s,%s,%s)'
                cursor.execute(sql,(uid,pw,name))
                conn.commit()
                return True

        except Exception as e:
            print(f'오류 발생 : {e}')
            conn.rollback()
            return False

        finally:
            conn.close()


    @classmethod
    def login(cls,uid,pw):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = 'select * from members where uid = %s and pw = %s and active = 1'
                cursor.execute(sql, (uid,pw))
                row = cursor.fetchone()
                if row:
                    member = Member.from_db(row)
                    return member
                return None

        finally:
            conn.close()

    @classmethod
    def modify(cls, user_no, new_name, new_pw):  # user_no가 숫자여야 함
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # SQL의 %s 순서: 1.이름, 2.비번, 3.ID(숫자)
                sql = "UPDATE members SET name = %s, pw = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_pw, user_no))
                conn.commit()
                return True

        except Exception as e:
            print(f"수정 중 오류 발생: {e}")
            conn.rollback()
            return False

        finally:
            conn.close()

    @classmethod
    def deactive(cls, user_uid):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE members SET active = 0 WHERE uid = %s"
                cursor.execute(sql, (user_uid,))

                conn.commit()
                return True
        except Exception as e:
            print(f"비활성화 중 오류 발생: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


