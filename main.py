from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, Table, MetaData, select, desc

from flask import session



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
engine = create_engine('postgresql+psycopg2://postgres:minus1chan@project301.c3lu1ffcsmca.us-east-2.rds.amazonaws.com:5432/postgres')
metadata = MetaData()

User = Table('users', metadata, autoload_with=engine)
Topic = Table('topic', metadata, autoload_with=engine)
Thread = Table('thread', metadata, autoload_with=engine)
Post = Table('post', metadata, autoload_with=engine)
Comment = Table('comment', metadata, autoload_with=engine)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']

        with engine.connect() as connection:
            result = connection.execute(select(User.c.user_name, User.c.password).where(User.c.user_name == user_name)).fetchone()

            if result and result[1] == password:
                session['user_name'] = result[0]
                return redirect(url_for('topics'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')



@app.route('/topics', methods=['GET'])
def topics():
    username = session.get('user_name', 'Guest')
    with engine.connect() as connection:
        result = connection.execute(select(Topic)).fetchall()
    categories = {}
    for row in result:
        category = row[3]
        topic = row[1]
        if category in categories:
            categories[category].append(topic)
        else:
            categories[category] = [topic]
    print(categories)
    return render_template('topics.html', categories=categories,username=username)


# @app.route('/threads/<int:topic_id>')
# def threads(topic_id):
#     with engine.connect() as connection:
#         results = connection.execute(select(Thread).where(Thread.c.topic_id == topic_id).order_by(desc(Thread.c.vote_ratio))).fetchall()
#     return render_template('threads.html', threads=results)

# @app.route('/posts/<int:post_id>')
# def posts(post_id):
#     with engine.connect() as connection:
#         post = connection.execute(select(Post).where(Post.c.post_id == post_id)).fetchone()
#         comments = connection.execute(select(Comment).where(Comment.c.post_id == post_id)).fetchall()
#     return render_template('post.html', post=post, comments=comments)


if __name__ == '__main__':
    app.run(debug=True,port=8000)
