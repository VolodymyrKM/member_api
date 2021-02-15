from flask import Flask, g, request, jsonify
from database_helper import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'password'


def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': 'Authentication failed!'}), 403
    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_curs = db.execute("""SELECT id, name, email, level from members""")
    all_members = members_curs.fetchall()
    return_values = []
    for member in all_members:
        member_dict = dict()
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']
        return_values.append(member_dict)


    return jsonify({'members': return_values,})


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute("""SELECT id, name, email, level from members where id = ?""", (member_id,))
    member = member_cur.fetchone()
    return_value = {'id': member['id'], 'name': member['name'], 'email': member['email'],
                    'level': member['level']}

    return jsonify({'member': return_value})


@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute("""INSERT INTO members (name, email, level)
                VALUES (?, ?, ?)""", (name, email, level))
    db.commit()

    member_curs = db.execute("""SELECT id, name, email, level from members WHERE name = ?""", (name,))
    new_member = member_curs.fetchone()

    return jsonify({'member': {'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'],
                               'level': new_member['level']}})


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    db = get_db()
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    db.execute("""UPDATE members SET name = ?, email = ?, level = ? where id = ?""", (name, email, level, member_id))
    db.commit()

    member_curs = db.execute("""SELECT id, name, email, level from members where id = ?""", (member_id,))
    update_member = member_curs.fetchone()

    return jsonify(
        {'member': {'id': update_member['id'], 'name': update_member['name'], 'email': update_member['email'],
                    'level': update_member['level']}})


@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute("""DELETE FROM members WHERE id = ?""", (member_id,))
    db.commit()

    return jsonify({'message': 'the member has been deleted'})


if __name__ == '__main__':
    app.run(debug=True)
