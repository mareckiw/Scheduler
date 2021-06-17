#Created on 19/03/2020 by AS76173
from Child import Child
from Teacher import Teacher
from LessonType import LessonType
from Lesson import Lesson
from Requirement import Requirement
from Speciality import Speciality
import pyodbc


class DAO:

    def __init__(self):
        self.connectionString = ('Driver={SQL Server};'
                      'Server=***;'
                      'Database=***;'
                      'UID=***;'
                      'PWD=***')
        self.cursor = None
        self.conn = None
        self.childList = []
        self.teacherList = []
        self.lessonList = []
        self.reqsList = []
        self.siblings = []
        self.specialitiesList = []

    #database communication methods to be done below

    def sortLists(self):
        for child in self.childList:
            child.slotAmount = child.availability.count(True)
        self.childList.sort(key=lambda x: x.slotAmount, reverse=False)
        self.teacherList.sort(key=lambda x: x.contractHours, reverse=False)

    def connectToDb(self):
        try:
            self.conn = pyodbc.connect(self.connectionString)
            self.cursor = self.conn.cursor()
        except:
            print("Couldn't connect to database") 
        

    def loadData(self):
        self.connectToDb()
        self.loadTeachers()
        self.loadLessons()
        self.loadChildren()
        self.loadReqs()
        self.loadSiblings()
        self.loadSpecialities()
        self.cursor.close()
        self.conn.close()

    def loadChildren(self):
        self.cursor.execute('SELECT * FROM dbo.ns_TEM_VS_Kids')
        for row in self.cursor:
            params = [elem for elem in row]
            slots = self.parseSlots(params[8])
            #Child(dbId, index, dateOfBirth, availability, skillsLevel1, skillsLevel2, skillsLevel3, skillsLevel4, hasSiblings)
            child = Child(params[0], params[1].strip(), params[2], slots, int(params[3]), int(params[4]), int(params[5]), int(params[6]), self.intToBool(params[7]))
            self.childList.append(child)

    def loadSiblings(self):
        self.cursor.execute('SELECT * FROM dbo.ns_TEM_VS_Siblings')
        for row in self.cursor:
            params = [elem for elem in row]
            childrenID = list(params[1].split('; '))
            children = []
            for id in childrenID:
                child = next((c for c in self.childList if c.index == id.strip()), None)
                children.append(child)
            for i, child in enumerate(children):
                j = 0
                while j < len(children):
                    if i != j:
                        child.siblings.append(children[j])
                    j += 1


    def loadReqs(self):
        self.cursor.execute('SELECT * FROM dbo.ns_TEM_VS_Requirements ORDER BY classID')
        lesson = None
        requirement = None
        for row in self.cursor:
            params = [elem for elem in row]
            child = next((c for c in self.childList if c.dbId == params[1]), None)
            if (lesson is None) or (lesson.dbId != params[2]):
                lesson = next((l for l in self.lessonList if l.dbId == params[2]), None)
                requirement = Requirement(lesson, [[child, params[3]]])
                self.reqsList.append(requirement)
            else:
                requirement.kids.append([child, params[3]])
            child.dueLessons.append(lesson)
        ##MM Add ADAPTACJA FUNKCJONALNA - ClassID -1 or -2 as requirement for 7 years old kids
        kidsThatMustHaveAdaptacja = []
        lesson = next((af for af in self.lessonList if af.dbId < 0), None)
        for ch in self.childList:
            if ch.calculateAge() == 7:
                kidsThatMustHaveAdaptacja.append([ch, 1])
                ch.dueLessons.append(lesson)
        requirement = Requirement(lesson, kidsThatMustHaveAdaptacja)
        self.reqsList.append(requirement)
        #sort children in reqList
        for req in self.reqsList:
            req.kids.sort(key=lambda x: x[0].numberOfAvailabilitySlots, reverse=False)
        #sort requirements - start from group lessons
        #self.reqsList.sort(key=lambda x: x.lesson.groupSize, reverse=True)

    def loadSpecialities(self):
        self.cursor.execute(""" SELECT s.specialityID, s.specialityName from dbo.ns_TEM_VS_Speciality as s """)
        for row in self.cursor:
            params = [elem for elem in row]
            spec = Speciality(params[0], params[1])
            self.specialitiesList.append(spec)

    def loadTeachers(self):
        self.cursor.execute(""" SELECT  t.teacherID, t.teacher_index, t.TimeInProgram1, t.TimeInProgram2,
        t.TimeInProgram3, t.TimeInProgram4,
        t.Slots,s.specialityID, s.specialityName from dbo.ns_TEM_VS_Teachers as t
        LEFT JOIN dbo.ns_TEM_VS_Speciality as s ON t.specialityID = s.specialityID""")
        for row in self.cursor:
            params = [elem for elem in row]
            slots = self.parseSlots(params[6])
            spec = Speciality(params[7], params[8])
            teacher = Teacher(params[0], params[1],
                              timeInPrograms=[params[2], params[3], params[4], params[5]],
                              speciality=spec, availability=slots)

            self.teacherList.append(teacher)

    def loadLessons(self):
        self.cursor.execute(""" SELECT c.*, p.programName
        FROM dbo.ns_TEM_VS_Classes as c 
        LEFT JOIN dbo.ns_TEM_VS_Programs as p
        ON c.programID = p.programID""")
        for row in self.cursor:
            params = [elem for elem in row]
            lessonType = LessonType(programId=params[2], name=params[8], dueDuration=params[3])
            params[5] = params[5].strip()
            params[6] = params[6].strip()
##MM Create list of required teachers based on string "KAŻDY" and program
            if params[5] is not None and len(params[5]) > 0:
                if params[5].find("KAZDY") == -1 and params[5].find("KAŻDY") == -1:
                    reqTeachers = self.parseTeachers(list(params[5].split(';')))
                else:
                    if params[5].find("OSWIA") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[0] > 0:
                                reqTeachers.append(t)
                    elif params[5].find("PEFRON") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[1] > 0:
                                reqTeachers.append(t)
                    elif params[5].find("NFZ") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[2] > 0:
                                reqTeachers.append(t)
                    else:
                        reqTeachers = self.teacherList
            else:
                reqTeachers = []

##MM Create list of optional teachers based on string "KAŻDY" + program
            if params[6] and len(params[6]) > 0:
                if params[6].find("KAZDY") == -1 and params[6].find("KAŻDY") == -1:
                    optTeachers = self.parseTeachers(list(params[6].split(';')))

                    print(optTeachers)
                else:
                    if params[6].find("OSWIA") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[0] > 0:
                                optTeachers.append(t)
                    elif params[6].find("PEFRON") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[1] > 0:
                                optTeachers.append(t)
                    elif params[6].find("NFZ") != -1:
                        for t in self.teacherList:
                            if t.timeInPrograms[2] > 0:
                                optTeachers.append(t)
                    else:
                        optTeachers = self.teacherList
            else:
                optTeachers = []

            if reqTeachers != [] and reqTeachers[0] is not None:
                reqTeachers.sort(key=lambda x: x.numberOfAvailabilitySlots, reverse=False)
            if optTeachers != [] and optTeachers[0] is not None:
                optTeachers.sort(key=lambda x: x.numberOfAvailabilitySlots, reverse=False)

            lesson = Lesson(dbId=params[0], name=params[1], duration=params[3], lessonType=lessonType, groupSize=params[4], reqTeachers=reqTeachers, optTeachers=optTeachers, differentSpec=params[7])
            self.lessonList.append(lesson)

    def parseTeachers(self, teacherList):
        teachers = []
        for index in teacherList:
            if index is not None and index != '':
                teacher = next((t for t in self.teacherList if t.dbId == int(index)), None)
                teachers.append(teacher)
        return teachers


    def parseSlots(self, availability):
        slots = []
        slots[:0] = availability
        slots = [self.intToBool(int(x)) for x in slots]
        return slots

    def intToBool(self, s):
        if s == 1:
            return True
        elif s == 0:
            return False
        else:
            raise ValueError
