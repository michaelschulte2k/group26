

# imports
import os  # os is used to get environment variables IP & PORT
import bcrypt
from io import BytesIO
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template  # Import render_template class
from flask import request  # Import request class
from flask import redirect, url_for  # Import redirect and url_for class
from flask import session
from flask import Response
from flask import send_file
from database import db
from models import Note as Note
from models import User as User
from models import Rating as Rating
from models import Comment as Comment
from models import Upload as Upload
from models import View as View
from forms import RegisterForm
from forms import LoginForm
from forms import RegisterForm, LoginForm, CommentForm, RatingForm, UploadForm, CountForm
from werkzeug.utils import secure_filename

app = Flask(__name__)  # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_note_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'

# Bind SQLAlchemy db object to this Flask App
db.init_app(app)

# Setup Models
with app.app_context():
    db.create_all()  # run under the app context


# notes = {1: {'title': 'First note', 'text': 'This is my first note', 'date': '10-1-2020'},
#        2: {'title': 'Second note', 'text': 'This is my second note', 'date': '10-2-2020'},
#       3: {'title': 'Third note', 'text': 'This is my third note', 'date': '10-3-2020'}
#      }


# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/')
@app.route('/index')
def index():
    # check if a user is saved in session
    if session.get('user'):
        return render_template('index.html', user=session['user'])
    return render_template("index.html")


@app.route('/notes')
def get_notes():
    if session.get('user'):
        my_notes = db.session.query(Note).filter_by(user_id=session['user_id']).all()
        return render_template('notes.html', notes=my_notes, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/notes/<note_id>')
def get_note(note_id):
    if session.get('user'):
        my_note = db.session.query(Note).filter_by(id=note_id, user_id=session['user_id']).one()
        form = CommentForm()
        return render_template('note.html', note=my_note, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))


@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    a_user = {'name': 'Mogli', 'email': 'mogli@uncc.edu'}

    print('request method is', request.method)
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['noteText']
            from datetime import date
            today = date.today()
            today = today.strftime("%m-%d-%Y")
            new_record = Note(title, text, today, session['user_id'])
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('get_notes'))
        else:
            return render_template('new.html', user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/notes/edit/<note_id>', methods=['GET', 'POST'])
def update_note(note_id):
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['noteText']
            note = db.session.query(Note).filter_by(id=note_id).one()
            note.title = title
            note.text = text
            db.session.add(note)
            db.session.commit()

            return redirect(url_for('get_notes'))
        else:
            # GET request - show new note form to edit note

            # Retrieve note from database
            my_note = db.session.query(Note).filter_by(id=note_id).one()
            return render_template('new.html', note=my_note, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/notes/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    if session.get('user'):
        my_note = db.session.query(Note).filter_by(id=note_id).one()
        db.session.delete(my_note)
        db.session.commit()

        return redirect(url_for('get_notes'))
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_notes'))

    # something went wrong - display register view
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_notes'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))


@app.route('/notes/<note_id>/comment', methods=['POST'])
def new_comment(note_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            
            new_record = Comment(comment_text, int(note_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_note', note_id=note_id))

    else:
        return redirect(url_for('login'))

@app.route('/notes/<note_id>/rating', methods=['POST'])
def new_rating(note_id):
    if session.get('user'):
        rating_form = RatingForm()
        if rating_form.validate_on_submit():
            rating_num = request.form['rating']
            new_rating = Rating(rating_num, int(note_id),session['user_id'])
            db.session.add(new_rating)
            db.session.commit()
        return redirect(url_for('get_note', note_id=note_id))
    else:
        return redirect(url_for('login'))


@app.route('/notes/<note_id>/upload', methods=['POST'])
def upload(note_id):
    if session.get('user'):
        upload_file = request.files['file']

        filename = secure_filename(upload_file.filename)
        mimetype = upload_file.mimetype

        img = Upload(img=upload_file.read(), name=filename, mimetype=mimetype, note_id=int(note_id), user_id=session['user_id'])
        db.session.add(img)
        db.session.commit()
        return redirect(url_for('get_note', note_id=note_id))
    else:
        return redirect(url_for('login'))


@app.route('/download/<upload_id>', methods=['GET'])
def download(upload_id):
    if session.get('user'):
        downloadFile = Upload(None, None, None, None, None).query.filter_by(id=upload_id).first()
        return send_file(BytesIO(downloadFile.img), as_attachment=True, download_name=downloadFile.name)
    else:
        return redirect(url_for('login'))

    
    #class for incrementing the number of times someone goes onto a specific project page
@app.route('/notes/<note_id>/view', methods = ['POST'])
def viewcount(note_id):
    
    counting_form = CountForm()
    counter_num = request.form['counter']
    new_count = View(counter_num, int(note_id), session['user_id'])
    db.session.add(new_count)
    db.session.commit()
    return render_template('note.html', note_id = note_id)


app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
