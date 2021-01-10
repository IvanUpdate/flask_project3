import json
from random import sample

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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


#наполнение БД из json файла
with open("data.json", "r", encoding='utf-8') as f:
    teachers_list = json.load(f)
for teacher in teachers_list:
    teacher = Teacher(id=int(teacher["id"]), name=teacher["name"], about=teacher["about"], rating=float(teacher["rating"]),
                      picture=teacher["picture"], price=int(teacher["price"]), goals=str(teacher["goals"]), free=json.dumps(teacher["free"]))
    db.session.add(teacher)
db.session.commit()



@app.route('/')
def render_main():
    with open("data.json", "r", encoding='utf-8') as f:
        teachers_list = json.load(f)
    return render_template('index.html', teachers=sample(teachers_list, 6), goals=goals)


@app.route('/all/')
def render_all():
    with open("data.json", "r", encoding='utf-8') as f:
        teachers_list = json.load(f)
    return render_template('all.html', teachers=teachers_list, number_of_teachers=len(teachers_list))


@app.route('/goals/<goal>/')
def render_goal(goal):
    with open("data.json", "r", encoding='utf-8') as f:
        teachers_list = json.load(f)
    teachers_by_goal = []
    for teacher in teachers_list:
        if goal in teacher["goals"]:
            teachers_by_goal.append(teacher)
    return render_template('goal.html', goal=goals[goal], teachers_by_goal=teachers_by_goal)


@app.route('/profiles/<id>/')
def render_teacher(id):
    with open("data.json", "r", encoding='utf-8') as f:
        teachers_list = json.load(f)
    teacher = None
    for temp in teachers_list:
        if temp["id"] == int(id):
            teacher = temp
    if teacher is None:
        return "Что-то не так, но мы все починим:\n{}".format(404)
    return render_template('profile.html', teacher=teacher, goals=goals, days=days)


@app.route('/request/')
def render_request():
    return render_template('request.html')


@app.route('/request_done/', methods=['POST'])
def render_request_done():
    goal = request.form.get("goal")
    time = request.form.get("time")
    client_name = request.form.get("clientName")
    client_phone = request.form.get("clientPhone")
    temp_dict = {"goal": goal, "client_time": time, "client_name": client_name, "client_phone": client_phone}
    with open("request.json", "r") as r:
        contents = r.read()
    contents += json.dumps(temp_dict)
    with open("request.json", "w", encoding='utf-8') as f:
        f.write(contents)
    return render_template('request_done.html', goal=goal, client_name=client_name, time=time, client_phone=client_phone, goals=goals)


@app.route('/booking/<id>/<day>/<time>/')
def render_booking(id, day, time):
    with open("data.json", "r", encoding='utf-8') as f:
        teachers_list = json.load(f)
    return render_template('booking.html', teacher=teachers_list[int(id)], day=day, time=time)


@app.route('/booking_done/', methods=['POST'])
def render_booking_done():
    client_weekday = request.form.get("clientWeekday")
    client_time = request.form.get("clientTime")
    client_teacher = request.form.get("clientTeacher")
    client_name = request.form.get("clientName")
    client_phone = request.form.get("clientPhone")
    temp_dict = {"client_weekday": client_weekday, "client_time": client_time, "client_teacher": client_teacher, "client_name": client_name, "client_phone": client_phone}
    with open("booking.json", "a") as b:
        json.dump(temp_dict, b)
    return render_template('booking_done.html', time=client_time, day=client_weekday, teacher=client_teacher, client_name=client_name, client_phone=client_phone)


if __name__ == '__main__':
    app.run(debug=True)
