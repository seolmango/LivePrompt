from flask import Blueprint, render_template, request
from run import db
from models.models import User, Setlist
import json

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/')
def index():
    users = User.query.all()
    return render_template('user/user-index.html', users=users)

@bp.route('/add', methods=['GET'])
def add():
    return render_template('user/useradd.html')

@bp.route('/delete', methods=['GET'])
def delete():
    return render_template('user/userdelete.html')

@bp.route('/adduser', methods=['POST'])
def add_user():
    user = User(nickname=request.form['nickname'])
    db.session.add(user)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/deleteuser', methods=['POST'])
def delete_user():
    user = User.query.filter_by(id=request.form['userid']).first()
    setlists = Setlist.query.all()
    for setlist in setlists:
        data = json.loads(setlist.setlist_users)
        if user.nickname in data:
            data.remove(user.nickname)
            setlist.setlist_users = json.dumps(data)
            db.session.commit()
        data = json.loads(setlist.setlist_data)
        for song in data:
            if request.form['userid'] in song.keys():
                del song[request.form['userid']]
        setlist.setlist_data = json.dumps(data)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    return render_template('windowclose.html')