import os
from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
from common.session import Session
from domain.Member import Member
from service.MemberService import MemberService

app = Flask(__name__)
app.secret_key = 'come_back_home'

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. 화면을 보여달라고 요청할 때 (GET)
    if request.method == 'GET':
        return render_template('login.html')

    # 2. 로그인 버튼을 눌러 데이터를 보냈을 때 (POST)
    uid = request.form.get('uid')
    pw = request.form.get('pw')

    # MemberService를 통해 DB 확인
    member = MemberService.login(uid, pw)

    if member:
        # 로그인 성공 시 세션(팔찌) 채워주기
        session['user_id'] = member.id
        session['user_uid'] = member.uid
        session['user_name'] = member.name
        session['user_role'] = member.role
        return redirect(url_for('index'))
    else:
        # 로그인 실패 시 메시지와 함께 뒤로가기
        return "<script>alert('아이디 또는 비번이 틀렸습니다.'); history.back();</script>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    name = request.form.get('name')
    uid = request.form.get('uid')
    pw = request.form.get('pw')

    result = MemberService.signup(uid, pw, name)

    if result == "EXIST":
        return "<script>alert('이미 존재하는 아이디입니다.'); history.back();</script>"
    elif result:
        return "<script>alert('가입 성공! 로그인해주세요.'); location.href='/login';</script>"
    else:
        return "<script>alert('가입 실패 (DB 오류)'); history.back();</script>"


@app.route('/member/edit', methods=['GET', 'POST'])
def edit():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('member_edit.html', user_name=session['user_name'])

    new_name = request.form.get('name')
    new_pw = request.form.get('pw')
    user_id_pk = session.get('user_id')

    if MemberService.modify(user_id_pk, new_name, new_pw):
        session['user_name'] = new_name
        return "<script>alert('수정 완료!'); location.href='/';</script>"
    return "<script>alert('수정 실패'); history.back();</script>"


@app.route('/delete', methods=['POST'])
def deactive():
    # 1. 로그인 여부 확인
    if not session.get('user_uid'):
        return redirect(url_for('login'))

    # 2. 세션에서 아이디 가져와서 서비스 호출
    uid = session.get('user_uid')

    if MemberService.deactive(uid):
        session.clear()  # 세션 파괴
        return "<script>alert('정상적으로 탈퇴되었습니다.'); location.href='/';</script>"
    else:
        return "<script>alert('처리 중 오류가 발생했습니다.'); history.back();</script>"

@app.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM members WHERE id = %s', (session['user_id'],))
            user_info = cursor.fetchone()
            return render_template('mypage.html', user=user_info, board_count=0)
    finally:
        conn.close()


@app.route('/shutdown')
def shutdown():
    if session.get('user_role') == 'admin':
        # 로깅 (터미널에서 확인용)
        print("!!! 관리자에 의해 컴퓨터 시스템 종료가 시작됩니다 !!!")

        # 윈도우 시스템 종료 명령어 실행
        # /s : shutdown (종료)
        # /f : force (실행 중인 프로그램 강제 종료)
        # /t 0 : 0초 뒤에 즉시 실행
        os.system("shutdown /s /f /t 0")

        return "<h1>시스템 종료 명령을 실행했습니다.</h1><p>곧 컴퓨터 전원이 꺼집니다. 안녕히 가세요!</p>"

    return "<h1>권한이 없습니다.</h1>", 403

#==============================================================================
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)



