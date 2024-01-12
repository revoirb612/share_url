from datetime import datetime
from flask import Flask, render_template, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    author = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    password = db.Column(db.String(100))
    category = db.Column(db.String(100))
    allowed_count = db.Column(db.Integer)
    actual_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Data %r>' % self.id

@app.before_first_request
def create_tables():
    db.create_all()

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
                author=data_author, password=data_password, category=data_category, allowed_count=data_allowed_count)
        db.session.add(new_data)
        db.session.commit()
        return redirect('/')
    else:
        datas = Data.query.all()
        return render_template('index.html', datas=datas)

@app.route('/<int:id>', methods=['GET'])
def handle_link(id):
    data = Data.query.get_or_404(id)

    if data.allowed_count <= data.actual_count:
        abort(403) 

    data.allowed_count -= 1
    data.actual_count += 1
    db.session.commit()

    return redirect(data.content)

if __name__ == '__main__':
    app.run(debug=True)
