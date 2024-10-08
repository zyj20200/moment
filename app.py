from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Moment, Comment
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

API_URL = 'http://192.168.110.33:8888/gen'

@app.route('/')
def index():
    moments = Moment.query.order_by(Moment.timestamp.desc()).all()
    return render_template('index.html', moments=moments)

@app.route('/post', methods=['POST'])
def post_moment():
    content = request.form.get('content')
    if content:
        new_moment = Moment(username="张三", avatar="a.jpg", content=content)
        db.session.add(new_moment)
        db.session.commit()

        # 调用API获取评论内容
        response = requests.post(API_URL, json={"message": content})
        if response.status_code == 200:
            comments = response.json().get('comment', [])
            print("API返回的评论内容:", comments)  # Debug: 打印API返回的评论内容
            for comment_text in comments:
                new_comment = Comment(moment_id=new_moment.id, text=comment_text)
                db.session.add(new_comment)
            db.session.commit()

    return redirect(url_for('index'))

@app.route('/moment/<int:moment_id>', methods=['GET', 'POST'])
def view_moment(moment_id):
    moment = Moment.query.get_or_404(moment_id)
    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            new_comment = Comment(moment_id=moment.id, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('view_moment', moment_id=moment_id))
    return render_template('moment.html', moment=moment)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)