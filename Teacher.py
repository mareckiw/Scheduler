#Created on 19/03/2020 by AS76173
from Person import Person
from Config import WEEK_SLOTS
from Speciality import Speciality


class Teacher(Person):

    def __init__(self, dbId = 0, index='', timeInPrograms = [0,0,0,0], speciality=Speciality(), availability=None):
        self.dbId = dbId #Integer
        self.index = index #String
        self.timeInPrograms = timeInPrograms #[Int]
        self.speciality = speciality
        self.availability = availability #Boolean[WEEK_SLOTS]
        if self.availability is None:
            self.availability = ([False] * WEEK_SLOTS)
        self.lessonSlots = ([False] * WEEK_SLOTS)
        self.calculateSlotsNumber()

    def __str__(self):
        result = 'TEACHER dbId: ' + str(self.dbId) + ' index' + str(self.index)
        return result


    def addTimeInProgram(self, programId, duration):
        self.timeInPrograms[programId] += duration

    def removeTimeInProgram(self, programId, duration):
        self.timeInPrograms[programId] -= duration

    def to_json(self, endpointSpec = None):
        if endpointSpec:
            return {"index": self.index,
                    "symbol": "T"
                    }
        return {"index": self.index,
                "timeInPrograms": self.timeInPrograms,
                "speciality": self.speciality.name,
                "lessonSlots": self.lessonSlots,
                "slots": self.availability
                }


