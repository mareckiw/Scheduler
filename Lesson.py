#Created on 19/03/2020 by AS76173

import json
from LessonType import LessonType


class Lesson:

    def __init__(self, dbId=0, name='', duration=0, lessonType=None, groupSize=0, reqTeachers = [], optTeachers = [], differentSpec = 0):
        self.dbId = dbId
        self.name = name #String
        self.duration = duration #Int
        self.lessonType = lessonType
        self.groupSize = groupSize
        self.reqTeachers = filter(None.__ne__, reqTeachers)
        self.optTeachers = filter(None.__ne__, optTeachers)
        self.differentSpec = differentSpec
        self.numberOfTeachers = 1
        if self.isGroupLesson():
            self.numberOfTeachers = 2
        if not self.lessonType:
            self.lessonType = LessonType(0, '', 0)

    def __str__(self):
        result = 'LESSON dbId: ' + str(self.dbId) + ' lessonName: ' + str(self.name)
        return result

    def isGroupLesson(self):
        return self.groupSize > 1


    def to_json(self):
        return {"dbId": self.dbId,
                "name": self.name,
                "duration": self.duration,
                "type": self.lessonType.__dict__,
                "groupSize": self.groupSize,
                "reqTeachers": json.dumps([ob.index.strip() for ob in self.reqTeachers]),
                "optTeachers": json.dumps([ob.index.strip() for ob in self.optTeachers]),
                "differentSpec": self.differentSpec
                }

