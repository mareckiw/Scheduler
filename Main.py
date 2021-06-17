from Schedule import Schedule
from Child import Child
from Teacher import Teacher
from Lesson import Lesson
from LessonType import LessonType
from Requirement import Requirement
from DAO import DAO
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from Speciality import Speciality
import time
import tkinter

from Teacher import Teacher
from Config import WEEK_SLOTS
from Lesson import Lesson
from Requirement import Requirement
from ScheduledClass import ScheduledClass


    #TESTING

dao = DAO()
dao.loadData()
testChildren = dao.childList
testTeachers = dao.teacherList
testLessons = dao.lessonList
specs = dao.specialitiesList
testRequirements = [dao.reqsList[0]]

for restReq in testRequirements:
    restReq.kids = restReq.kids[:18]
    restReq.lesson.reqTeachers = restReq.lesson.reqTeachers

#schedule = Schedule()
#time1 = time.time()
#schedule.generateSchedule(testRequirements, dao)
#time2 = time.time()

#print('Laczny czas:')
#print((time2 - time1))

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/kids/<child_id>', methods=['DELETE'])
def delete_kid(child_id):
    child = next(filter(lambda x: x.index == str(child_id), testChildren), None)
    if child:
        testChildren.remove(next(filter(lambda x: x.index == str(child_id), testChildren), None))
        # TODO - removing child from database
    children = list(child.to_json() for child in testChildren)
    return json.dumps(children)


@app.route('/api/kids/<child_id>', methods=['PUT'])
def update_kid(child_id):
    data = request.get_json()
    child = next(filter(lambda x: x.index == str(child_id), testChildren), None)
    if child is None:
        return jsonify({'message': "Child does not exist, so it cannot be updated"}), 400
    index = testChildren.index(child)
    for key, value in data.items():
        child.__setattr__(key, value)
    testChildren[index] = child
    return jsonify(child.to_json())


@app.route('/api/kids/<child_id>')
def get_kid_by_id(child_id):
    child = next(filter(lambda x: x.index == str(child_id), testChildren), None)
    if child:
        return jsonify(child.to_json()), 200
    else:
        return 404


@app.route('/api/kids', methods=['POST'])
def add_new_kid():
    data = request.get_json()
    if 'index' not in data:
        return jsonify({'message': "Child index is required"}), 400
    if next(filter(lambda x: x.index == str(data['index']), testChildren), None):
        return jsonify({'message': "Child with index '{}' already exists".format(data['index'])}), 400
    child = Child(index=data['index'])
    for key, value in data.items():
        child.__setattr__(key, value)
    testChildren.append(child)
    # TODO - adding child to database
    return jsonify(child.to_json()), 201


@app.route('/api/kids')
def get_kids():
    children = list(child.to_json() for child in testChildren)
    return json.dumps(children)


@app.route('/api/kidsAndTeachers')
def get_kids_and_teachers():
    children = list(child.to_json(endpointSpec='kidsAndTeacher') for child in testChildren)
    teachers = list(teacher.to_json(endpointSpec='kidsAndTeacher') for teacher in testTeachers)
    return json.dumps(children + teachers)


@app.route('/api/teachers', methods=['POST'])
def add_new_teacher():
    data = request.get_json()
    if 'index' not in data:
        return jsonify({'message': "Teacher index is required"}), 400
    if next(filter(lambda x: x.index.strip() == str(data['index']), testTeachers), None):
        return jsonify({'message': "Teacher with index '{}' already exists".format(data['index'])}), 400
    teacher = Teacher(index=data['index'])
    for key, value in data.items():
        if key == "speciality":
            teacher.speciality = Speciality(name = value)
        teacher.__setattr__(key, value)
    testTeachers.append(teacher)
    # TODO - adding teacher to database
    return jsonify(teacher.to_json()), 201


@app.route('/api/teachers/<teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.get_json()
    teacher = next(filter(lambda x: x.index.strip() == str(teacher_id), testTeachers), None)
    if teacher is None:
        return jsonify({'message': "Teacher does not exist, so it cannot be updated"}), 400
    index = testTeachers.index(teacher)
    for key, value in data.items():
        if key == "speciality":
            teacher.speciality.name = Speciality(name = value)
        teacher.__setattr__(key, value)
    testTeachers[index] = teacher
    return jsonify(teacher.to_json())


@app.route('/api/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    teacher = next(filter(lambda x: x.index.strip() == str(teacher_id), testTeachers), None)
    if teacher:
        testTeachers.remove(next(filter(lambda x: x.index.strip() == str(teacher_id), testTeachers), None))
        # TODO - removing teacher from database
    teachers = list(teacher.to_json() for teacher in testTeachers)
    return json.dumps(teachers)


@app.route('/api/teachers/<teacher_id>')
def get_teacher_by_id(teacher_id):
    teacher = next(filter(lambda x: x.index.strip() == str(teacher_id), testTeachers), None)
    if teacher:
        return jsonify(teacher.to_json()), 200
    else:
        return '', 404


@app.route('/api/teachers')
def get_teachers():
    teachers = list(teacher.to_json() for teacher in testTeachers)
    return json.dumps(teachers)


@app.route('/api/lessons/<lesson_id>', methods=['DELETE'])
def delete_class(lesson_id):
    lesson = next(filter(lambda x: x.dbId == int(lesson_id), testLessons), None)
    if lesson:
        testLessons.remove(next(filter(lambda x: x.dbId == int(lesson_id), testLessons), None))
        # TODO - removing class from database
    lessons = list(lesson.to_json() for lesson in testLessons)
    return json.dumps(lessons)


@app.route('/api/lessons/<lesson_id>', methods=['PUT'])
def update_class(lesson_id):
    data = request.get_json()
    lesson = next(filter(lambda x: x.dbId == int(lesson_id), testLessons), None)
    if lesson is None:
        return jsonify({'message': "Class does not exist, so it cannot be updated"}), 400
    index = testLessons.index(lesson)
    for key, value in data.items():
        if key == "dbId":
            continue
        elif key == "type":
            for k, v in value.items():
                lesson.lessonType.__setattr__(k, v)
        elif key == "reqTeachers" :
            lesson.reqTeachers = []
            for item in json.loads(value):
                teacher = next((t for t in testTeachers if t.index.strip() == item), None)
                lesson.reqTeachers.append(teacher)
        elif key == "optTeachers":
            lesson.optTeachers = []
            for item in json.loads(value):
                teacher = next((t for t in testTeachers if t.index.strip() == item), None)
                lesson.optTeachers.append(teacher)
        else:
            lesson.__setattr__(key, value)
    testLessons[index] = lesson
    return jsonify(lesson.to_json())

@app.route('/api/lessons/<lesson_id>')
def get_class_by_id(lesson_id):
    lesson = next(filter(lambda x: x.dbId == int(lesson_id), testLessons), None)
    if lesson:
        return jsonify(lesson.to_json()), 200
    else:
        return '', 404

@app.route('/api/lessons', methods=['POST'])
def add_class():
    data = request.get_json()
    dbId = testLessons[len(testLessons)-1].dbId
    while next(filter(lambda x: x.dbId == dbId, testLessons), None):
        dbId += 1
    lesson = Lesson(dbId=dbId)
    for key, value in data.items():
        if key == "dbId":
            continue
        elif key == "type":
            for k, v in value.items():
                lesson.lessonType.__setattr__(k, v)
        elif key == "reqTeachers" :
            lesson.reqTeachers = []
            for item in json.loads(value):
                teacher = next((t for t in testTeachers if t.index.strip() == item), None)
                lesson.reqTeachers.append(teacher)
        elif key == "optTeachers":
            lesson.optTeachers = []
            for item in json.loads(value):
                teacher = next((t for t in testTeachers if t.index.strip() == item), None)
                lesson.optTeachers.append(teacher)
        else:
            lesson.__setattr__(key, value)

    testLessons.append(lesson)
    # TODO - adding class to database
    return jsonify(lesson.to_json()), 201

@app.route('/api/lessons')
def get_all_classes():
    lessons = list(lesson.to_json() for lesson in testLessons)
    return json.dumps(lessons)

@app.route('/api/specs')
def get_all_specs():
    specialities = list(spec.__dict__ for spec in specs)
    return json.dumps(specialities)


@app.route('/api/schedule/<symbol>/<index>')
def get_schedule_by_id(symbol, index):
    return json.dumps({"Classes": [
                {
                    "Lesson": "PSYCHOLOGIA/PEDAGOG                               ",
                    "Start Slot": 18,
                    "Children": [
                        {
                            "dbId": 7
                        }
                    ],
                    "Teachers": [
                        {
                            "dbId": 1
                        }
                    ]
                },
                {
                    "Lesson": "PSYCHOLOGIA/PEDAGOG                               ",
                    "Start Slot": 23,
                    "Children": [
                        {
                            "dbId": 33
                        }
                    ],
                    "Teachers": [
                        {
                            "dbId": 1
                        }
                    ]
                },
                {
                    "Lesson": "PSYCHOLOGIA/PEDAGOG                               ",
                    "Start Slot": 20,
                    "Children": [
                        {
                            "dbId": 35
                        }
                    ],
                    "Teachers": [
                        {
                            "dbId": 1
                        }
                    ]
                }
            ]})


app.run(port=8000)
#Creating test children..
"""
testChild1 = Child('Janek', 'Kowalski', 'TESTPESEL', False)
testChild2 = Child('AlwaysAvailable', 'Child', 'TESTPESEL', availability=([True]*WEEK_SLOTS))
testChild3 = Child('Kasia', 'Nowak', 'TESTPESEL', False)
testChild4 = Child('Michał', 'Kowalski', 'TESTPESEL', False)
testChild5 = Child('Wiktor', 'Nowak', 'TESTPESEL', False)
testChild6 = Child('Ania', 'Kowalski', 'TESTPESEL', False)
testChild7 = Child('Ola', 'Nowak', 'TESTPESEL', False)
testChild8 = Child('Marta', 'Kowalski', 'TESTPESEL', False)
testChildren = [testChild1, testChild2, testChild3, testChild4, testChild5, testChild6, testChild7, testChild8]
for child in testChildren:
    for i in range (0,4):
        child.availability[100+i] = True
    if child.surname == 'Nowak':
        for j in range (0, 3):
           child.availability[20+j] = True

#Creating test teachers..
testTeacher1 = Teacher('Profesor', 'Smith')
testTeacher2 = Teacher('AlwaysAvailable', 'Teacher', availability=([True]*WEEK_SLOTS))
testTeacher3 = Teacher('Doktor', 'Brown')
for i in range (0,4):
    testTeacher1.availability[100+i] = True
    testTeacher3.availability[100+i] = True
for i in range(0, 10):
    testTeacher3.availability[20+i] = True
    testTeachers = [testTeacher1, testTeacher2, testTeacher3]

#Creating test lesson
testLesson = Lesson('Muzykologia', 3, None, 8, 2)

for child in testChildren:
    child.dueLessons.append(testLesson)
for teacher in testTeachers:
    teacher.lessons.append(testLesson)

#Creating test requirement
testRequirement = Requirement()
testRequirement.lesson = testLesson
testRequirement.teachers = testTeachers
for child in testChildren:
    testRequirement.kids.append([child, 1])

for pair in testRequirement.kids:
    if pair[0].surname == 'Nowak':
        pair[1] = 2
"""
#Real testing
# testAvailability1 = ([True] * WEEK_SLOTS)
# testAvailability1[2] = False
#
# testAvailability2 = ([False] * WEEK_SLOTS)
# testAvailability2[2] = True
# testAvailability2[3] = True
# testAvailability2[10] = True
# testAvailability2[11] = True
# testAvailability2[15] = True
# testAvailability2[16] = True
# testAvailability2[20] = True
# testAvailability2[21] = True
#
# testAvailability3 = ([False] * WEEK_SLOTS)
# testAvailability3[0] = True
# testAvailability3[1] = True
#
# testAvailability4 = ([True] * WEEK_SLOTS)
#
#
# testChild1 = Child(1, '1', availability=testAvailability1)
# testChild2 = Child(2, '2', availability=testAvailability2)
# testChild3 = Child(3, '3', availability=testAvailability3)
# testTeacher = Teacher(0, '0', timeInPrograms=[0, 10, 0, 0, 0, 0], availability=testAvailability4)
# testLesson = Lesson(0, 'TestoweZajecia', 2, LessonType(1, 'Test', 2), groupSize=1, reqTeachers=[testTeacher], optTeachers=[])
# testRequirmenet = Requirement(lesson=testLesson, kids=[[testChild1,1], [testChild2, 1], [testChild3, 1]])
# dao = DAO()
# dao.childList = [testChild1, testChild2, testChild3]
# dao.teacherList = [testTeacher]
# dao.lessonList = [testLesson]
# dao.reqsList = [testRequirmenet]
#
# schedule = Schedule()
# time1 = time.time()
# schedule.generateSchedule(dao.reqsList, dao)
# time2 = time.time()
#
# print('Laczny czas:')
# print((time2 - time1))



