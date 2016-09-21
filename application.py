#all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, render_template_string
from contextlib import closing
from datetime import datetime
from flask.ext.paginate import Pagination
from flask.ext.misaka import Misaka
from flask.ext.triangle import Triangle

#configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = "PUjF\x8eMX\xf1`\x14q\xc9\xc7\xfe\xb7\xa0\xc7`\xcb]\xcc\xd9\xee\x96"

#app section
application = Flask(__name__)
application.config.from_object(__name__)
Misaka(application)
Triangle(application)

def connect_db():
	return sqlite3.connect(application.config['DATABASE'])

@application.before_request
def before_request():
    g.db = connect_db()

@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def get_password(username):
    cur = g.db.execute('select password from users where username=?',[username])
    row = cur.fetchall()
    if row:
        return row[0][0]
    else:
        return

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/random')
def random():
    return render_template('random.html')

@application.route('/')
def show_entries():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    cur = g.db.execute('select title, text, time, id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], time = row[2][:-10], entryId = row[3]) for row in cur.fetchall()]
    pagination = Pagination(page=page, total=len(entries), search=search, record_name='entries')
    return render_template('show_entries.html', entries=entries, pagination=pagination,)

@application.route('/entry/<entryId>')
def show_entry(entryId):
    cur = g.db.execute('select title, text, time from entries where id = ?', [entryId])
    row = cur.fetchall()
    if row:
        entry = dict(title = row[0][0], text = row[0][1], time= row[0][2][:-10] ,id = entryId)
        return render_template('show_entry.html', entry = entry)
    else:
        return show_entries()

@application.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text, time) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], datetime.now()])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@application.route('/edit/<entryId>', methods=['POST'])
def edit_entry(entryId):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('update entries set title=?, text=?, time=? where id = ?',
                 [request.form['title'], request.form['text'], datetime.now(), entryId])
    g.db.commit()
    flash('Entry was successfully updated')
    return redirect(url_for('show_entries'))

@application.route('/delete/<entryId>')
def delete_entry(entryId):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from entries where id = ?', [entryId])
    g.db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))

@application.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        PASSWORD = get_password(request.form['username'])
        if PASSWORD != request.form['password']:
            error = 'Invalid password/username'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@application.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
	application.run()
