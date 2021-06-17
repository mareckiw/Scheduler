import unittest
from Person import Person
from Child import Child
from Requirement import Requirement
from Lesson import Lesson
from Teacher import Teacher

class TestRequirement(unittest.TestCase):

    def setUp(self):
        pass

    def test_getPossibleTeacherConfiguration_returnsCorrectList(self):
        t1 = Teacher(1,1)
        t2 = Teacher(2,2)
        t3 = Teacher(3,3)
        t4 = Teacher(4,4)
        reqTeachers = [t1, t2, t3]
        optTeachers = [t4]
        lesson = Lesson(dbId=0, name='TestLesson', reqTeachers=reqTeachers, optTeachers=optTeachers, groupSize=8)
        requirement = Requirement(lesson=lesson)
        result = requirement.getPossibleTeacherConfigurations()
        self.assertEqual(result, [(t1,t2), (t1,t3), (t2,t3), (t1,t4), (t2,t4), (t3,t4)])






if __name__ == '__main__':
    unittest.main()
