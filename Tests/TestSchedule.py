import unittest
from Schedule import Schedule
from Child import Child
from Teacher import Teacher
from Person import WEEK_SLOTS
from Lesson import Lesson
from LessonType import LessonType
from Requirement import Requirement
from ScheduledClass import ScheduledClass
from CostCalculator import CostCalculator
from Speciality import Speciality

class TestSchedule(unittest.TestCase):

    def setUp(self):
        self.schedule = Schedule()
        #Creating test children..
        testChild1 = Child(1, 'Janek')
        testChild2 = Child(2, 'AlwaysAvailable', availability=([True]*WEEK_SLOTS))
        testChild3 = Child(3, 'Nowak')
        testChild4 = Child(4, 'Kowalski')
        testChild5 = Child(5, 'Nowak')
        testChild6 = Child(6, 'Kowalski')
        testChild7 = Child(7, 'Nowak')
        testChild8 = Child(8, 'Kowalski')
        self.testChildren = [testChild1, testChild2, testChild3, testChild4, testChild5, testChild6, testChild7, testChild8]
        for child in self.testChildren:
            for i in range (0,4):
                child.availability[100+i] = True
            if child.index == 'Nowak':
                for j in range (0, 10):
                    child.availability[20+j] = True

        #Creating test teachers..
        testTeacher1 = Teacher(1, 'Smith', speciality=Speciality(1,""))
        testTeacher2 = Teacher(2, 'AlwaysAvailable', availability=([True]*WEEK_SLOTS))
        testTeacher3 = Teacher(3, 'Brown')
        for i in range (0,4):
            testTeacher1.availability[100+i] = True
            testTeacher3.availability[100+i] = True
        for i in range(0, 10):
            testTeacher3.availability[20+i] = True
        self.testTeachers = [testTeacher1, testTeacher2, testTeacher3]
        #Creating test lesson
        self.testLesson = Lesson(1, 'Muzykologia', 3, LessonType(2, "TEST", 12), 8, self.testTeachers, differentSpec=1)


        for child in self.testChildren:
            child.dueLessons.append(self.testLesson)
        # for teacher in self.testTeachers:
        #     teacher.lessons.append(self.testLesson)

        #Creating test requirement
        self.testRequirement = Requirement()
        self.testRequirement.lesson = self.testLesson
        for child in self.testChildren:
            self.testRequirement.kids.append([child, 1])

    def tearDown(self):
        self.testChildren = []
        self.testRequirement = None
        self.testTeachers = []
        self.testLesson = None

    def test_findCommonSlotInMultipleLists_RaisesValueErrorOnMismatchingLengths(self):
        list1 = [True, False, True, True, False, True, True, True, False, False]
        list2 = [False, False, True, True, False, True, False, True, True]
        with self.assertRaises(ValueError):
            Schedule.findCommonSlotsInMultipleLists([list1, list2], 2, 0)

    def test_findCommonSlotInMultipleLists_FindsSlot(self):
        list1 = [True, False, True, True, False, True, True, True, False, False]
        list2 = [False, False, True, True, False, True, True, True, True, False]
        list3 = [False, False, True, True, False, True, True, True, True, False]
        list4 = [False, False, False, False, False, True, True, True, False, False]
        listOfLists = [list1, list2, list3, list4]
        expectedResult = [False, False, False, False, False, True, True, True, False, False]
        result = Schedule.findCommonSlotsInMultipleLists(listOfLists, 3, 0)
        self.assertEqual(result, expectedResult)

    def test_findCommonSlotInMultipleLists_DoesNotFindSlot(self):
        list1 = [True, False, True, True, False, True, True, True, False, False]
        list2 = [False, False, True, True, False, True, True, True, True, False]
        list3 = [False, False, True, True, False, True, True, True, True, False]
        list4 = [False, False, False, False, False, True, True, False, False, False]
        listOfLists = [list1, list2, list3, list4]
        expectedResult = [False, False, False, False, False, False, False, False, False, False]
        result = Schedule.findCommonSlotsInMultipleLists(listOfLists, 3, 0)
        self.assertEqual(result, expectedResult)

    def test_findStartSlot_returnsCorrectStartSlot(self):
        list1 = [False, False, False, False, False, True, True, False, False, False]
        list2 = [True, False, False, False, False, True, True, False, False, False]
        list3 = [False, False, False, False, False, False, False, False, False, True]
        result1 = Schedule.findStartSlot(list1, 2)
        result2 = Schedule.findStartSlot(list2, 2)
        result3 = Schedule.findStartSlot(list3, 2)
        self.assertEqual(result1, 5)
        self.assertEqual(result2, 0)
        self.assertEqual(result3, 9)

    def test_findStartSlot_returnsSlotNotFoundCode(self):
        list = [False, False, False, False, False, False, False, False, False, False]
        result = Schedule.findStartSlot(list, 2)
        self.assertEqual(result, -1)

    def test_addAvailabilitySlots_addsSlotsForChildren(self):
        testList = self.testChildren
        self.schedule.addAvailabilitySlots(testList, 50, 2)
        self.assertEqual(testList[0].availability[50], True)
        self.assertEqual(testList[0].availability[51], True)
        self.assertEqual(testList[0].availability[52], False)
        self.assertEqual(testList[1].availability[50], True)
        self.assertEqual(testList[1].availability[51], True)
        self.assertEqual(testList[1].availability[52], True)

    def test_addAvailabilitySlots_addsSlotsForTeachers(self):
        testList = self.testTeachers
        self.schedule.addAvailabilitySlots(testList, 50, 2)
        self.assertEqual(testList[0].availability[50], True)
        self.assertEqual(testList[0].availability[51], True)
        self.assertEqual(testList[0].availability[52], False)
        self.assertEqual(testList[1].availability[50], True)
        self.assertEqual(testList[1].availability[51], True)
        self.assertEqual(testList[1].availability[52], True)

    def test_removeAvailabilitySlots_removesSlotsForChildren(self):
        testList = self.testChildren
        self.schedule.removeAvailabilitySlots(testList, 100, 2)
        self.assertEqual(testList[0].availability[100], False)
        self.assertEqual(testList[0].availability[101], False)
        self.assertEqual(testList[0].availability[102], True)
        self.assertEqual(testList[1].availability[100], False)
        self.assertEqual(testList[1].availability[101], False)
        self.assertEqual(testList[1].availability[102], True)

    def test_removeAvailabilitySlots_removesSlotsForTeachers(self):
        testList = self.testTeachers
        self.schedule.addAvailabilitySlots(testList, 50, 2)
        self.assertEqual(testList[0].availability[50], True)
        self.assertEqual(testList[0].availability[51], True)
        self.assertEqual(testList[0].availability[52], False)
        self.assertEqual(testList[1].availability[50], True)
        self.assertEqual(testList[1].availability[51], True)
        self.assertEqual(testList[1].availability[52], True)

    def test_extractChildrenFromRequirement_extractsChildren(self):
        result = self.schedule.extractChildrenFromRequirement(self.testRequirement)
        self.assertEqual(result, self.testChildren)

    def test_updateScheduledLessonMembersAvailability_updatesAvailability(self):
        scheduledClass = ScheduledClass(self.testChildren, self.testLesson, self.testTeachers, 100)
        self.schedule.updateScheduledLessonMembersAvailability(scheduledClass)
        for child in self.testChildren:
            self.assertEqual(child.availability[100], False)
            self.assertEqual(child.availability[101], False)
            self.assertEqual(child.availability[102], False)
        for teacher in self.testTeachers:
            self.assertEqual(teacher.availability[100], False)
            self.assertEqual(teacher.availability[101], False)
            self.assertEqual(teacher.availability[102], False)

    def test_removeChildrenRequirementForClass_decreasesChildrenRequirements(self):
        for pair in self.testRequirement.kids:
            if pair[0].index == 'Nowak':
                pair[1] = 2
        self.schedule.removeChildrenRequirementForClass(self.testRequirement, self.testChildren)
        for pair in self.testRequirement.kids:
            if pair[0].index == 'Nowak':
                self.assertEqual(pair[1], 1)
            else:
                self.assertEqual(pair[1], 0)

    def test_scheduleClass_schedulesCorrectClass(self):
        self.schedule.scheduleClass(self.testRequirement, self.testChildren, [self.testTeachers[0], self.testTeachers[1]], 100)
        self.assertEqual(len(self.schedule.classes), 1)
        self.assertEqual(self.schedule.classes[0].children, self.testChildren)
        self.assertEqual(self.schedule.classes[0].lesson, self.testLesson)
        self.assertEqual(self.testChildren[1].availability[100], False)

    # not passing

    def test_generateSchedule_generatesScheduleAsExpected(self):
        self.schedule.generateSchedule([self.testRequirement], None)
        self.assertEqual(len(self.schedule.classes), 1)
        self.assertEqual(self.schedule.classes[0].lesson, self.testLesson)
        self.assertEqual(self.schedule.classes[0].startSlot, 100)
        self.assertEqual(len(self.schedule.decisions), 1)


    def test_genereateSchedule_schedules2Classes(self):
        for pair in self.testRequirement.kids:
            if pair[0].index == 'Nowak':
                pair[1] = 2
        self.schedule.generateSchedule([self.testRequirement], None)
        self.assertEqual(len(self.schedule.classes), 2)
        self.assertEqual(len(self.schedule.decisions), 2)
        print(self.schedule.decisions[1].hasBeenLastDecisionInRequirement)

    def test_getFreePeriodSlots_returnsCorrectTable(self):
        testChild1 = Child(1, 'Kowalski')
        testChild1.lessonSlots[9] = True
        testChild1.lessonSlots[14] = True
        testChild1.lessonSlots[40] = True
        testChild1.lessonSlots[43] = True
        result = CostCalculator.getFreePeriodSlots(testChild1)
        self.assertEqual(result, [4, 2])

if __name__ == '__main__':
    unittest.main()
