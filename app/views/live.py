from flask import blueprints, render_template
from app.models import User

bp = blueprints.Blueprint('live', __name__, url_prefix='/live')

@bp.route('/')
def index():
    Users = User.query.all()
    data = []
    for user in Users:
        data.append({
            'id': user.id,
            'nickname': user.nickname
        })
    return render_template('live/index.html', users=data)