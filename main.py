from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
from sqlalchemy import create_engine, Table, MetaData, select, desc, insert,update, delete
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:minus1chan@project301.c3lu1ffcsmca.us-east-2.rds.amazonaws.com'
db = SQLAlchemy(app)
engine = create_engine('postgresql+psycopg2://postgres:minus1chan@project301.c3lu1ffcsmca.us-east-2.rds.amazonaws.com:5432/postgres')
metadata = MetaData()

User = Table('users', metadata, autoload_with=engine)
Topic = Table('topic', metadata, autoload_with=engine)
Thread = Table('thread', metadata, autoload_with=engine)
Post = Table('post', metadata, autoload_with=engine)
Comment = Table('comment', metadata, autoload_with=engine)

@app.route('/register', methods=['POST'])
def register():
    user_name = request.form['user_name']
    password = request.form['password']
    profile_text = request.form['profile_text']

    with engine.connect() as connection:
        existing_user = connection.execute(select(User).where(User.c.user_name == user_name)).fetchone()
        
        if existing_user:
            flash('User already exists, please choose another username.', 'warning')
            return redirect(url_for('login'))
        
        new_user = User.insert().values(user_name=user_name, password=password, profile_text=profile_text)
        connection.execute(new_user)
        connection.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))


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


@app.route('/topics/<string:topic_name>', methods=['GET'])
def topic_threads(topic_name):
    username = session.get('user_name', 'Guest')
    with engine.connect() as connection:
        topic_id = connection.execute(select(Topic.c.topic_id).where(Topic.c.topic_title == topic_name)).scalar()
        result = connection.execute(select(Thread).where(Thread.c.topic_id == topic_id)).fetchall()
    threads = [row._asdict() for row in result]
    return render_template('topic.html', threads=threads, topic=topic_name,username=username,topic_id=topic_id)


@app.route('/threads/<int:thread_id>', methods=['GET'])
def thread_posts(thread_id):
    username = session.get('user_name', 'Guest')
    with engine.connect() as connection:
        thread = connection.execute(select(Thread).where(Thread.c.thread_id == thread_id)).fetchone()
        thread_title = thread.thread_title if thread else ""
        result = connection.execute(select(Post).where(Post.c.thread_id == thread_id).order_by(desc(Post.c.posts_likes))).fetchall()
        posts = [row._asdict() for row in result]
        for post in posts:
            comments_result = connection.execute(select(Comment).where(Comment.c.post_id == post['post_id']).order_by(Comment.c.comment_likes.desc())).fetchall()
            post['comments'] = [row._asdict() for row in comments_result]
    return render_template('post.html', posts=posts, thread_id=thread_id, username=username, thread_title=thread_title)



@app.route('/users/<string:user_name>', methods=['GET'])
def user_page(user_name):
    with engine.connect() as connection:
        user = connection.execute(select(User).where(User.c.user_name == user_name)).fetchone()._asdict()
        user_threads = connection.execute(select(Thread).where(Thread.c.user_name == user_name)).fetchall()
        user_threads = [row._asdict() for row in user_threads]
        user_posts = connection.execute(select(Post).where(Post.c.user_name == user_name)).fetchall()
        user_posts = [row._asdict() for row in user_posts]
        user_comments = connection.execute(select(Comment).where(Comment.c.user_name == user_name)).fetchall()
        user_comments = [row._asdict() for row in user_comments]

    return render_template('user.html', user=user, user_threads=user_threads, user_posts=user_posts, user_comments=user_comments)

@app.route('/add_thread', methods=['POST'])
def add_thread():
    title = request.form['title']
    user_name = session.get('user_name', 'Guest')
    topic_id = request.form.get('topic_id')
    creation_time = datetime.datetime.now()
    stmt = insert(Thread).values(thread_title=title, user_name=user_name, topic_id=topic_id, thread_creation_time=creation_time)
    result = db.session.execute(stmt)
    db.session.commit()
    new_thread_id = result.inserted_primary_key[0]

    return redirect(url_for('thread_posts', thread_id=new_thread_id))

@app.route('/add_post', methods=['POST'])
def add_post():
    text = request.form['text']
    title= request.form['title']
    user_name = session.get('user_name', 'Guest')
    thread_id = request.form.get('thread_id')
    post_creation_time = datetime.datetime.now()
    print(thread_id)
    stmt = insert(Post).values(post_title=title,post_text=text, user_name=user_name,thread_id=thread_id, post_creation_time=post_creation_time)
    db.session.execute(stmt)
    db.session.commit()

    return redirect(url_for('thread_posts', thread_id=thread_id))

@app.route('/add_comment', methods=['POST'])
def add_comment():
    text = request.form['text']
    user_name = session.get('user_name', 'Guest')
    post_id = request.form.get('post_id')
    thread_id = request.form.get('thread_id')
    print(thread_id)
    comment_creation_time = datetime.datetime.now()

    stmt = insert(Comment).values(comment_text=text, user_name=user_name, post_id=post_id, comment_creation_time=comment_creation_time)
    db.session.execute(stmt)
    db.session.commit()


    return redirect(url_for('thread_posts', thread_id=thread_id))

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    username = session.get('user_name', 'Guest')
    liked_posts = session.get(f'liked_posts_{username}', [])
    disliked_posts = session.get(f'disliked_posts_{username}', [])

    with engine.connect() as connection:
        post = connection.execute(select(Post).where(Post.c.post_id == post_id)).fetchone()
        if post:
            if post_id in disliked_posts:
                likes = post[5] + 1
                dislikes = post.posts_dislikes - 1
                disliked_posts.remove(post_id)
                liked_posts.append(post_id)
            elif post_id not in liked_posts:
                likes = post[5] + 1
                dislikes = post.posts_dislikes
                liked_posts.append(post_id)
            elif post_id in liked_posts:
                return redirect(request.referrer)

            stmt = Post.update().where(Post.c.post_id == post_id).values(posts_likes=likes, posts_dislikes=dislikes)
            connection.execute(stmt)
            connection.commit()

    session[f'liked_posts_{username}'] = liked_posts
    session[f'disliked_posts_{username}'] = disliked_posts
    return redirect(request.referrer)


@app.route('/dislike_post/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    username = session.get('user_name', 'Guest')
    disliked_posts = session.get(f'disliked_posts_{username}', [])
    liked_posts = session.get(f'liked_posts_{username}', [])

    with engine.connect() as connection:
        post = connection.execute(select(Post).where(Post.c.post_id == post_id)).fetchone()
        if post:
            if post_id in liked_posts:
                dislikes = post.posts_dislikes + 1
                likes = post[5] - 1
                liked_posts.remove(post_id)
                disliked_posts.append(post_id)
            elif post_id not in disliked_posts:
                dislikes = post.posts_dislikes + 1
                likes = post[5]
                disliked_posts.append(post_id)
            elif post_id in disliked_posts:
                return redirect(request.referrer)

            stmt = Post.update().where(Post.c.post_id == post_id).values(posts_likes=likes, posts_dislikes=dislikes)
            connection.execute(stmt)
            connection.commit()

    session[f'liked_posts_{username}'] = liked_posts
    session[f'disliked_posts_{username}'] = disliked_posts
    return redirect(request.referrer)



@app.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
    username = session.get('user_name', 'Guest')
    liked_comments = session.get(f'liked_comments_{username}', [])
    disliked_comments = session.get(f'disliked_comments_{username}', [])
    open_post_id = request.form.get('open_post_id', None)
    thread_id = request.form.get('thread_id')

    with engine.connect() as connection:
        comment = connection.execute(select(Comment).where(Comment.c.comment_id == comment_id)).fetchone()
        if comment:
            if comment_id in disliked_comments:
                likes = comment.comment_likes + 1
                dislikes = comment.comment_dislikes - 1
                disliked_comments.remove(comment_id)
                liked_comments.append(comment_id)
            elif comment_id not in liked_comments:
                likes = comment.comment_likes + 1
                dislikes = comment.comment_dislikes
                liked_comments.append(comment_id)
            elif comment_id in liked_comments:
                return redirect(url_for('thread_posts', thread_id=thread_id, open_post_id=open_post_id))

            stmt = Comment.update().where(Comment.c.comment_id == comment_id).values(comment_likes=likes, comment_dislikes=dislikes)
            connection.execute(stmt)
            connection.commit()

    session[f'liked_comments_{username}'] = liked_comments
    session[f'disliked_comments_{username}'] = disliked_comments
    return redirect(url_for('thread_posts', thread_id=thread_id, open_post_id=open_post_id))

@app.route('/dislike_comment/<int:comment_id>', methods=['POST'])
def dislike_comment(comment_id):
    username = session.get('user_name', 'Guest')
    disliked_comments = session.get(f'disliked_comments_{username}', [])
    liked_comments = session.get(f'liked_comments_{username}', [])
    open_post_id = request.form.get('open_post_id', None)
    thread_id = request.form.get('thread_id')

    with engine.connect() as connection:
        comment = connection.execute(select(Comment).where(Comment.c.comment_id == comment_id)).fetchone()
        
        if comment:
            if comment_id in liked_comments:
                dislikes = comment.comment_dislikes + 1
                likes = comment.comment_likes - 1
                liked_comments.remove(comment_id)
                disliked_comments.append(comment_id)
            elif comment_id not in disliked_comments:
                dislikes = comment.comment_dislikes + 1
                likes = comment.comment_likes
                disliked_comments.append(comment_id)
            elif comment_id in disliked_comments:
                return redirect(url_for('thread_posts', thread_id=thread_id, open_post_id=open_post_id))

            stmt = Comment.update().where(Comment.c.comment_id == comment_id).values(comment_likes=likes, comment_dislikes=dislikes)
            connection.execute(stmt)
            connection.commit()

    session[f'liked_comments_{username}'] = liked_comments
    session[f'disliked_comments_{username}'] = disliked_comments
    return redirect(url_for('thread_posts', thread_id=thread_id, open_post_id=open_post_id))


@app.route('/edit_post', methods=['GET','POST'])
def edit_post():
    #username = session.get('user_name', 'Guest')

    if request.method == 'POST':
        post_id = request.form.get('post_id')
        thread_id = request.form.get('thread_id')
        post_text = request.form.get('post_text')
        post_title = request.form.get('post_title')

        stmt = update(Post).where(Post.c.post_id == post_id).values(post_title=post_title, post_text=post_text)
        db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for('thread_posts', thread_id=thread_id))
    else:
        return redirect(url_for('topics'))

@app.route('/delete_post', methods=['GET','POST'])
def delete_post():
    #username = session.get('user_name', 'Guest')

    if request.method == 'POST':
        post_id = request.form.get('post_id')
        thread_id = request.form.get('thread_id')
        with engine.connect() as connection:
            connection.execute(select(Comment).where(Comment.c.post_id == post_id)).fetchall()
            stmt = delete(Comment).where(Comment.c.post_id == post_id)
            db.session.execute(stmt)
            stmt2 = delete(Post).where(Post.c.post_id == post_id)
            db.session.execute(stmt2)
            db.session.commit()
            return redirect(url_for('thread_posts', thread_id=thread_id))
    else:
        return redirect(url_for('topics'))
if __name__ == '__main__':
    app.run(debug=True,port=8000)
