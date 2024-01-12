from datetime import datetime
from flask import Flask, render_template, request, redirect, abort, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid

# 앱 및 데이터베이스 설정
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Data 모델 정의
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))  # URL 설명
    author = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)  # 작성일시
    password = db.Column(db.String(100))  # 패스워드 (선택적)
    category = db.Column(db.String(100))  # 분류
    allowed_count = db.Column(db.Integer)  # 허용횟수
    actual_count = db.Column(db.Integer, default=0)  # 실제 접속 횟수

    def __repr__(self):
        return '<Data %r>' % self.id

# Device 모델 정의
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'), nullable=False)
    device_id = db.Column(db.String(200), nullable=False)

# 데이터베이스 테이블 생성
@app.before_first_request
def create_tables():
    db.create_all()

# 메인 페이지 라우트
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data_content = request.form['content']
        data_description = request.form['description']
        data_author = request.form['author']
        data_password = request.form.get('password')
        data_category = request.form['category']
        data_allowed_count = int(request.form['allowed_count'])
        new_data = Data(content=data_content, description=data_description,
                        author=data_author, password=data_password, 
                        category=data_category, allowed_count=data_allowed_count)
        db.session.add(new_data)
        db.session.commit()
        return redirect('/')
    else:
        datas = Data.query.all()
        return render_template('index.html', datas=datas)

# 링크 처리 라우트
@app.route('/<int:id>', methods=['GET'])
def handle_link(id):
    data = Data.query.get_or_404(id)
    device_id = request.cookies.get('device_id')
    if not device_id:  # 쿠키가 없는 경우, 새로운 기기로 간주
        device_id = str(uuid.uuid4())  # 새로운 기기 ID를 생성
    device = Device.query.filter_by(data_id=id, device_id=device_id).first()
    if device:
        abort(403)  # Forbidden
    if data.allowed_count <= 0:
        abort(403)  # Forbidden
    data.allowed_count -= 1
    new_device = Device(data_id=id, device_id=device_id)
    db.session.add(new_device)
    data.actual_count += 1
    db.session.commit()
    response = make_response(redirect(data.content))
    response.set_cookie('device_id', device_id, max_age=60*60*24*365)  # 1년 동안 유효한 쿠키 설정
    return response

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
