import json
from random import sample

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func

from data import goals
from days import days

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String, nullable=False)
    free = db.Column(db.JSON)
    bookings = db.relationship("Booking")


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    client = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher")


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String)
    time = db.Column(db.String, nullable=False)
    client = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)


db.create_all()


"""
#наполнение БД из json файла
with open("data.json", "r", encoding='utf-8') as f:
    teachers_list = json.load(f)
for teacher in teachers_list:
    teacher = Teacher(id=int(teacher["id"]), name=teacher["name"], about=teacher["about"], rating=float(teacher["rating"]),
                      picture=teacher["picture"], price=int(teacher["price"]), goals=str(teacher["goals"]), free=json.dumps(teacher["free"]))
    db.session.add(teacher)
db.session.commit()
"""


@app.route('/')
def render_main():
    teachers_list = db.session.query(Teacher).all()
    return render_template('index.html', teachers=sample(teachers_list, 6), goals=goals)


@app.route('/all/')
def render_all():
    teachers_list = db.session.query(Teacher).order_by(func.random())
    return render_template('all.html', teachers=teachers_list, number_of_teachers=teachers_list.count())


@app.route('/all_done/', methods=['POST'])
def render_all_done():
    goal = int(request.form.get("sorted"))
    if goal == 0:
        teachers_list = db.session.query(Teacher).order_by(func.random())
    elif goal == 3:
        teachers_list = db.session.query(Teacher).order_by(Teacher.rating.desc())
    elif goal == 1:
        teachers_list = db.session.query(Teacher).order_by(Teacher.price.desc())
    elif goal == 2:
        teachers_list = db.session.query(Teacher).order_by(Teacher.price)
    return render_template('all.html', teachers=teachers_list, number_of_teachers=teachers_list.count())


@app.route('/goals/<goal>/')
def render_goal(goal):
    teachers_by_goal = db.session.query(Teacher).filter(Teacher.goals.contains(goal)).order_by(Teacher.rating.desc())
    return render_template('goal.html', goal=goals[goal], teachers_by_goal=teachers_by_goal)


@app.route('/profiles/<id>/')
def render_teacher(id):
    teacher_profile = db.session.query(Teacher).get(int(id))
    if teacher_profile is None:
        return "Что-то не так, но мы все починим:\n{}".format(404)
    return render_template('profile.html', teacher=teacher_profile, goals=goals, days=days,
                           free=json.loads(teacher_profile.free))


@app.route('/request/', methods=['GET', 'POST'])
def render_request():
    if request.method == 'POST':
        goal = request.form.get("goal")
        time = request.form.get("time")
        client_name = request.form.get("clientName")
        client_phone = request.form.get("clientPhone")
        requested = Request(goal=goal, time=time, phone=client_phone, client=client_name)
        db.session.add(requested)
        db.session.commit()
        return render_template('request_done.html', goal=goal, client_name=client_name, time=time,
                               client_phone=client_phone, goals=goals)
    else:
        return render_template('request.html')


@app.route('/booking/<id>/<day>/<time>/', methods=['GET', 'POST'])
def render_booking(id, day, time):
    if request.method == 'POST':
        client_weekday = request.form.get("clientWeekday")
        client_time = request.form.get("clientTime")
        client_teacher = request.form.get("clientTeacher")
        client_name = request.form.get("clientName")
        client_phone = request.form.get("clientPhone")
        booking = Booking(weekday=client_weekday, time=client_time, client=client_name, phone=client_phone, teacher_id = int(client_teacher))
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', time=client_time, day=client_weekday, teacher=client_teacher,
                               client_name=client_name, client_phone=client_phone)
    else:
        teacher_profile = db.session.query(Teacher).get(int(id))
        return render_template('booking.html', teacher=teacher_profile, day=day, time=time)


if __name__ == '__main__':
    app.run(debug=True)
