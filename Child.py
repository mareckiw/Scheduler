#Created on 19/03/2020 by AS76173
from Config import WEEK_SLOTS, END_OF_YEAR
from Person import Person
from datetime import date
import json


class Child(Person):

    def __init__(self, dbId = 0,  index='', dateOfBirth='', availability=None, skillsLevel1=0, skillsLevel2=0, skillsLevel3=0, skillsLevel4=0, hasSiblings=False, dueLessons=None, siblings=None):
        self.dbId = dbId
        self.index = index #String
        self.dateOfBirth = dateOfBirth #String
        self.availability = availability #Boolean[WEEK_SLOTS]
        if self.availability is None:
            self.availability = ([False] * WEEK_SLOTS)
        self.skillsLevel1 = skillsLevel1 #Integer
        self.skillsLevel2 = skillsLevel2 #Integer
        self.skillsLevel3 = skillsLevel3 #Integer
        self.skillsLevel4 = skillsLevel4 #Integer
        self.hasSiblings = hasSiblings #Boolean
        self.dueLessons = dueLessons #Lesson[]
        if self.dueLessons is None:
            self.dueLessons = []
        self.siblings = siblings #Child[]
        if self.siblings is None:
            self.siblings = []
        self.slotAmount = 0
        self.lessonSlots = ([False] * WEEK_SLOTS)
        self.calculateSlotsNumber()


    def __str__(self):
        result = 'CHILD dbId: ' + str(self.dbId) + ' index: ' + str(self.index)
        return result

##MM
    def calculateAge(self):
        bdate = date(int(self.dateOfBirth[0:4]),int(self.dateOfBirth[5:7]),int(self.dateOfBirth[8:10]))
        if date.today().month < bdate.month or (date.today().month == bdate.month and date.today().day < bdate.day):
            age = (date.today().year - bdate.year) - 1
        else:
            age = (date.today().year - bdate.year)
        return age

    def calculateAgeYE(self):
        bdate = date(int(self.dateOfBirth[0:4]), int(self.dateOfBirth[5:7]), int(self.dateOfBirth[8:10]))
        ye = date(int(END_OF_YEAR[0:4]), int(END_OF_YEAR[5:7]), int(END_OF_YEAR[8:10]))
        if ye.month < bdate.month or (ye.month == bdate.month and ye.day < bdate.day):
            age = (ye.year - bdate.year) - 1
        else:
            age = (ye.year - bdate.year)
        return age

    def to_json(self, endpointSpec = None):
        if endpointSpec:
            return {"index": self.index,
                    "symbol": "K"}
        return {"index": self.index,
                "dateOfBirth": self.dateOfBirth,
                "skillsLevel1": self.skillsLevel1,
                "skillsLevel2": self.skillsLevel2,
                "skillsLevel3": self.skillsLevel3,
                "skillsLevel4": self.skillsLevel4,
                "hasSiblings": int(self.hasSiblings),
                "slots": self.availability
                }


