from flask import Blueprint, render_template, request
from app import db
from app.models import User

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
    db.session.delete(user)
    db.session.commit()
    return render_template('windowclose.html')