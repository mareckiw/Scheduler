#Created on 19/03/2020 by AS76173

from ScheduledClass import ScheduledClass
from DAO import DAO
from Decision import Decision
from CostCalculator import CostCalculator
from Config import WEEK_SLOTS
from Config import SEARCH_FOR_ALL_SCHEDULES
import numpy as np
import copy
import json

class Schedule:

    def __init__(self):
        self.classes = [] #ScheduledClass[]
        self.decisions = []
        self.requirements = []
        self.childrenIndexToStartWith = 0
        self.teachersIndexToStartWith = 0
        self.slotIndexToStartWith = 0
        self.currentRequirementIndex = 0
        self.cost = 1000000
        self.dao = None
        self.foundSchedulesCounter = 0
        self.foundSchedules = []  #to find all possible schedules, for testing
        #store currently proccessed group of children and teachers - when block hitted you know where to return
        self.currentlyProccessedChild= None
        #self.currentlyProccessedTeachers = []

    @staticmethod
    def findCommonSlotsInMultipleLists(listOfLists, length, slotToBegin):
        try:
            listLength = len(listOfLists[0])
            commonSlotsArray = np.array(listOfLists[0])
            for list in listOfLists[1:]:
                if len(list) != listLength:
                    raise ValueError('Lists are not of the same length')
                slotsArray = np.array(list)
                commonSlotsArray = commonSlotsArray & slotsArray
            commonSlotsList = commonSlotsArray.tolist()
            return Schedule.filterOutTooShortSlots(commonSlotsList, length, slotToBegin)
        except ValueError:
            raise

    @staticmethod
    def findStartSlot(slotList, lessonDuration):
        counter = 0
        daySlots = WEEK_SLOTS/5
        for slot in slotList:
            if slot == True:
                endSlotNumber = counter + lessonDuration - 1
                if counter//daySlots == endSlotNumber//daySlots:    #Make sure that the lesson won't be scheduled for 2 days - ex. Mon 19.40 - Tue 8.40
                    return counter
            counter += 1
        return -1 #No slot found

    @staticmethod
    def filterOutTooShortSlots(commonSlotList, length, slotToBegin):
        commonSlotList += (False,)
        counter = 0
        for i in range(0, slotToBegin):
            commonSlotList[i] = False
        for i in range(slotToBegin, len(commonSlotList)):
            if commonSlotList[i] is True:
                counter += 1
            else:
                if counter >= length:
                    counter = 0
                else:
                    while counter != 0:
                        commonSlotList[i - counter] = False
                        counter -= 1
        return commonSlotList[:-1]

    #GenerateSchedule - entry point for schedule calculation
    def generateSchedule(self, requirements, dao):
        self.dao = dao
        self.requirements = requirements
        requirementsNumber = len(requirements)
        while True: #generate all possible schedules (for testing!!!!)
            while self.currentRequirementIndex < requirementsNumber:
                currentRequirement = self.requirements[self.currentRequirementIndex]
                if currentRequirement.isFulfilled():
                    self.currentRequirementIndex += 1
                    self.decisions[-1].hasBeenLastDecisionInRequirement = True
                else:
                    try:
                        self.processRequirement(currentRequirement)
                    except ValueError:
                        print('error handled')
                        self.saveSchedulesToJSON()
                        return
            if SEARCH_FOR_ALL_SCHEDULES == False:
                print(self.getScheduleJSON(self.classes))
                self.dao.save
                break
            else:
                self.scheduleCreated()

    def processRequirement(self, req):
        decisionToBeMade = Decision()
        self.decisions.append(decisionToBeMade)
        if req.lesson.isGroupLesson():
            isClassScheduled = self.processGroupClass(req)
        else:
            isClassScheduled = self.processIndividualClass(req)
        if isClassScheduled is True:
            self.cleanStartIndexes()
        else:
            try:
                self.processReturn()
            except ValueError:
                raise

    def processGroupClass(self, req):
        isClassScheduled = False
        childrenGroupIndex = self.childrenIndexToStartWith
        self.childrenIndexToStartWith = 0
        possibleGroups = req.getPossibleChildrenConfigurations()
        for possibleGroup in possibleGroups[childrenGroupIndex:]:
            isClassScheduled = self.processPossibleGroup(possibleGroup, req)
            if isClassScheduled is True:
                self.decisions[-1].childrenGroupIndex = childrenGroupIndex
                self.decisions[-1].totalChildren = len(possibleGroups)
                #self.printLastDecision()
                break
            childrenGroupIndex += 1
        return isClassScheduled

    def processPossibleGroup(self, possibleGroup, requirement):
        isClassScheduled = False
        lessonDuration = requirement.lesson.duration
        listOfAvailabilities = []
        for child in possibleGroup:
            listOfAvailabilities.append(child.availability)
        childrenCommonSlots = Schedule.findCommonSlotsInMultipleLists(listOfAvailabilities, lessonDuration, 0)
        if True in childrenCommonSlots:
            results = self.findTeachersAndStartSlotForClass(requirement, childrenCommonSlots)
            if results != []:   #valid group found
                assignedTeachers = results[0]
                startSlot = results[1]
                self.scheduleClass(requirement, possibleGroup, assignedTeachers, startSlot)
                isClassScheduled = True
        return isClassScheduled

    def findTeachersAndStartSlotForClass(self, requirement, childrenCommonSlots):
        lessonDuration = requirement.lesson.duration
        teachersIndex = self.teachersIndexToStartWith
        self.teachersIndexToStartWith = 0
        results = []
        possibleTeacherConfigurations = requirement.getPossibleTeacherConfigurations()
        for teacherConfiguration in possibleTeacherConfigurations[teachersIndex:]:
            totalAvailabilities = [childrenCommonSlots]
            for teacher in teacherConfiguration:
                if(teacher.timeInPrograms[requirement.lesson.lessonType.programId] < lessonDuration):
                    continue    #if any of the teachers doesn't have time in program - continue
                totalAvailabilities.append(teacher.availability)
            totalCommonSlots = Schedule.findCommonSlotsInMultipleLists(totalAvailabilities, lessonDuration, self.slotIndexToStartWith)
            self.slotIndexToStartWith = 0
            if True in totalCommonSlots:
                startSlot = Schedule.findStartSlot(totalCommonSlots, lessonDuration)
                if startSlot != -1:
                    results.append(teacherConfiguration)
                    results.append(startSlot)
                    self.decisions[-1].teacherGroupIndex = teachersIndex
                    self.decisions[-1].totalTeachers = len(possibleTeacherConfigurations)
                    self.decisions[-1].startSlotNumber = startSlot
                    break
            teachersIndex += 1
        return results

    def processIndividualClass(self, req):
        isClassScheduled = False
        self.currentlyProccessedChild = req.getChildrenWithPositiveRequirement()[0]
        teacherIndex = self.teachersIndexToStartWith
        self.teachersIndexToStartWith = 0
        teachers = req.lesson.reqTeachers
        for teacher in teachers[teacherIndex:]:
            #self.currentlyProccessedTeachers = [teacher]
            if teacher.timeInPrograms[req.lesson.lessonType.programId] >= req.lesson.duration:
                #TODO - przechowywanie w pamieci
                commonSlots = self.findCommonSlotsInMultipleLists([self.currentlyProccessedChild.availability, teacher.availability], req.lesson.duration, self.slotIndexToStartWith)
                self.slotIndexToStartWith = 0
                if True in commonSlots:  # Found teacher who has slot corresponding with child's slot
                    assignedTeacher = [teacher]
                    assignedChild = [self.currentlyProccessedChild]
                    startSlot = Schedule.findStartSlot(commonSlots, req.lesson.duration)
                    self.scheduleClass(req, assignedChild, assignedTeacher, startSlot)
                    self.decisions[-1].teacherGroupIndex = teacherIndex
                    self.decisions[-1].totalTeachers = len(teachers)
                    self.decisions[-1].startSlotNumber = startSlot
                    self.decisions[-1].childrenGroupIndex = 0
                    isClassScheduled = True
                    #self.printLastDecision()
                    break
            teacherIndex += 1
        return isClassScheduled

    def processReturn(self):
        try:
            self.decisions.pop() #remove the decision placeholder - it hasn't been made
            requirementWhichBlocked = self.requirements[self.currentRequirementIndex]
            lastImportantDecisionFound = False
            while True:
                if lastImportantDecisionFound:
                    break
                if len(self.decisions) == 0:
                    raise ValueError('Unable to generate schedule. Provide correct input')
                lastMadeDecision = self.decisions.pop()
                if lastMadeDecision.hasBeenLastDecisionInRequirement:
                    self.goBackToPreviousRequirement()
                currentRequirement = self.requirements[self.currentRequirementIndex]
                lastImportantDecisionFound = self.isDecisionAffectingTheBlock(requirementWhichBlocked)
                if lastImportantDecisionFound:
                    print('Nawrót, istotna decyzja: ')
                    self.printLastDecision(lastMadeDecision)
                self.reverseClassScheduling(currentRequirement)
                self.restoreCircumstancesFromBeforeDecision(lastMadeDecision)
        except ValueError:
            print("Zakończono")
            raise

    def isDecisionAffectingTheBlock(self, requirementWhichBlocked):
        lastScheduledClass = self.classes[-1]
        if len(lastScheduledClass.teachers) > 2: #group lesson
            return True #for now - it seems more complicated to compare all the teachers and children in the requirement for group class with those in lastScheduled every time than to just consider everything (?)
        else:
            #LOGIC: The decision is important in relation to current blockage in algorithm, when:
            #1. It schedules a class for one of the teachers in req at the momenent when the blocked child is available, OR
            #2. It schedules a class for the blocked child at the moment when one of the teachers in req is available

            if self.currentlyProccessedChild.availability[lastScheduledClass.startSlot]: #1a - if the checked class is scheduled for the slot when blocked child is available...
                for teacher in requirementWhichBlocked.lesson.reqTeachers:               #1b - for all teachers which might have conducted the class at the block time...
                    if teacher.dbId == lastScheduledClass.teachers[0].dbId:              #1c - if it's this teacher whose time has been blocked...
                        return True                                                      #The decision is important - this teacher might have conducted the lesson for child at the moment of block!
            if self.currentlyProccessedChild.dbId == lastScheduledClass.children[0].dbId:#2a - if the checked class is for the blocked child...
                for teacher in requirementWhichBlocked.lesson.reqTeachers:               #2b - for all teachers which might have conducted the class at the block time...
                    if teacher.availability[lastScheduledClass.startSlot]:               #2c - if the teacher is available at that time...
                        return True                                                      #The decision is important - this child might have this class on this time
            return False





    def goBackToPreviousRequirement(self):
        try:
            self.currentRequirementIndex -= 1
            if self.currentRequirementIndex < 0:
                raise ValueError('Unable to generate schedule. Provide correct input')
        except ValueError:
            raise

    def reverseClassScheduling(self, requirement):
        lastScheduledClass = self.classes.pop()
        self.updateReversedScheduledLessonMembersAvailability(lastScheduledClass)
        self.updateReversedScheduledLessonTeachersTimeInProgram(lastScheduledClass)
        self.addChildrenRequirementForClass(requirement, lastScheduledClass.children)

    def restoreCircumstancesFromBeforeDecision(self, decision):
        self.childrenIndexToStartWith = decision.childrenGroupIndex
        self.teachersIndexToStartWith = decision.teacherGroupIndex
        if decision.startSlotNumber == WEEK_SLOTS:
            self.teachersIndexToStartWith += 1
            self.slotIndexToStartWith = 0
        else:
            self.slotIndexToStartWith = decision.startSlotNumber+1

    def scheduleClass(self, req, assignedChildren, assignedTeachers, startSlot):
        newScheduledClass = ScheduledClass(assignedChildren, req.lesson, assignedTeachers, startSlot)
        self.classes.append(newScheduledClass)
        self.updateScheduledLessonMembersAvailability(newScheduledClass)
        self.updateScheduledLessonTeachersTimeInProgram(newScheduledClass)
        self.removeChildrenRequirementForClass(req, assignedChildren)

    def scheduleCreated(self):
        #What happens after the program finishes scheduling?
        scheduleCost = self.calculateCost(self.classes)
        print('---Found schedule of cost: ' + str(scheduleCost) + '---')
        # for schClass in self.classes:
        #     print('Dziecko: ' + str(schClass.children[0].dbId) + ' startSlot: ' + str(schClass.startSlot) + ' teacher: ' + str(str(schClass.teachers[0].dbId)))

        #write found schedule to a file
        # scheduleJson = self.getScheduleJSON(self.classes)
        # filename = 'schedule' + str(self.foundSchedulesCounter)
        # with open(filename, 'w') as outfile:
        #     json.dump(scheduleJson, outfile, indent=4)
        # self.foundSchedulesCounter += 1

        if scheduleCost <= self.cost:
            if scheduleCost < self.cost:
                print('Better schedule found!!!!')
                self.cost = scheduleCost
                found_classes = copy.deepcopy(self.classes)
                self.foundSchedules.append(found_classes)  #Save found valid schedule
        placeholderDecision = Decision()
        self.decisions.append(placeholderDecision)
        self.processReturn()  #Force return

    def removeChildrenRequirementForClass(self, requirement, children):
        for child in children:
            for childRequirement in requirement.kids:
                if child == childRequirement[0]:
                    childRequirement[1] -= 1

    def addChildrenRequirementForClass(self, requirement, children):
        for child in children:
            for childRequirement in requirement.kids:
                if child == childRequirement[0]:
                    childRequirement[1] += 1

    def updateScheduledLessonMembersAvailability(self, scheduledClass):
        lessonDuration = scheduledClass.lesson.duration
        classStartSlot = scheduledClass.startSlot
        assignedChildren = scheduledClass.children
        assignedTeachers = scheduledClass.teachers
        self.removeAvailabilitySlots(assignedChildren, classStartSlot, lessonDuration)
        self.removeAvailabilitySlots(assignedTeachers, classStartSlot, lessonDuration)


    def updateScheduledLessonTeachersTimeInProgram(self, scheduledClass):
        assignedTeachers = scheduledClass.teachers
        programId = scheduledClass.lesson.lessonType.programId
        duration = scheduledClass.lesson.duration
        self.removeTimeInProgram(assignedTeachers, programId, duration)


    def updateReversedScheduledLessonMembersAvailability(self, rescheduledClass):
        lessonDuration = rescheduledClass.lesson.duration
        classStartSlot = rescheduledClass.startSlot
        assignedChildren = rescheduledClass.children
        assignedTeachers = rescheduledClass.teachers
        self.addAvailabilitySlots(assignedChildren, classStartSlot, lessonDuration)
        self.addAvailabilitySlots(assignedTeachers, classStartSlot, lessonDuration)

    def updateReversedScheduledLessonTeachersTimeInProgram(self, rescheduledClass):
        assignedTeachers = rescheduledClass.teachers
        programId = rescheduledClass.lesson.lessonType.programId
        duration = rescheduledClass.lesson.duration
        self.addTimeInProgram(assignedTeachers, programId, duration)

    def extractChildrenFromRequirement(self, req):
        return req.getChildren()

    def addAvailabilitySlots(self, peopleList, startSlot, numberOfSlotsToAdd):
        for person in peopleList:
            person.addAvailabilitySlots(startSlot, numberOfSlotsToAdd)

    def removeAvailabilitySlots(self, peopleList, startSlot, numberOfSlotsToRemove):
        for person in peopleList:
            person.removeAvailabilitySlots(startSlot, numberOfSlotsToRemove)

    def addTimeInProgram(self, assignedTeachers, programId, duration):
        for teacher in assignedTeachers:
            teacher.addTimeInProgram(programId, duration)

    def removeTimeInProgram(self, assignedTeachers, programId, duration):
        for teacher in assignedTeachers:
            teacher.removeTimeInProgram(programId, duration)

    def cleanStartIndexes(self):
        self.slotIndexToStartWith = 0
        self.childrenIndexToStartWith = 0
        self.teachersIndexToStartWith = 0

    def saveSchedulesToJSON(self):
        fileOutput = {"Schedules" : []}
        for classesList in self.foundSchedules:
            classesJson = self.getScheduleJSON(classesList)
            fileOutput["Schedules"].append(classesJson)
        jsonFile = json.dumps(fileOutput, indent=4)
        print("Znaleziono planow: " + str(len(self.foundSchedules)))
        print(jsonFile)
        with open('foundSchedules.txt', 'w') as outfile:
            json.dump(fileOutput, outfile, indent=4)

    def getScheduleJSON(self, classesList):
        classesOutput = {"Cost": 0, "Classes": []}
        classesOutput["Cost"] = self.calculateCost(classesList)
        for scheduledClass in classesList:
            scheduledClassOutput = {"Lesson": "", "Start Slot": 0, "Children": [], "Teachers": []}
            scheduledClassOutput["Lesson"] = scheduledClass.lesson.name
            scheduledClassOutput["Start Slot"] = scheduledClass.startSlot
            for child in scheduledClass.children:
                childOutput = {}
                childOutput["dbId"] = child.dbId
                scheduledClassOutput["Children"].append(childOutput)
            for teacher in scheduledClass.teachers:
                teacherOutput = {}
                teacherOutput["dbId"] = teacher.dbId
                scheduledClassOutput["Teachers"].append(teacherOutput)
            classesOutput["Classes"].append(scheduledClassOutput)
        return classesOutput


    def calculateCost(self, classesList):
        return CostCalculator.calculateCost(classesList, self.dao)

    def printLastDecision(self, decision):
        if self.requirements[self.currentRequirementIndex].lesson.groupSize == 1:
            print('-----------------')
            print('Requirement: ' + str(self.currentRequirementIndex) + '/' + str(len(self.requirements)))
            print('Child: ' + str(self.requirements[self.currentRequirementIndex].kids.index([self.classes[-1].children[0], 0])) + '/' + str(decision.totalChildren))
            print('TeacherGroup: ' + str(decision.teacherGroupIndex) + '/' + str(decision.totalTeachers))
            print('Slot: ' + str(decision.startSlotNumber) + '/165')
        else:
            print('-----------------')
            print('Requirement: ' + str(self.currentRequirementIndex) + '/' + str(len(self.requirements)))
            print('ChildGroup: ' + str(decision.childrenGroupIndex) + '/' + str(decision.totalChildren))
            print('TeacherGroup: ' + str(decision.teacherGroupIndex) + '/' + str(decision.totalTeachers))
            print('Slot: ' + str(decision.startSlotNumber) + '/165')
        

    def cross(self, secondSchedule):
        print('TO BE DONE')
        #crossing with second schedule, producing child
        return None #return child

    def mutate(self):
        print('TO BE DONE')
        #mutating

