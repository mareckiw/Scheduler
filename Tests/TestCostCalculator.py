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

class TestCostCalculator(unittest.TestCase):

    def setUp(self):
        self.schedule = Schedule()

        # Age: 7,9,5; Standard deviation: 1.6329931618555
        # SkillsLevel1 - standard deviation: 0.81649658092773
        # SkillsLevel2 - standard deviation: 1.2472191289246
        # Skills standard deviation: 1.49
        testChild1 = Child(1, 'J', dateOfBirth='2013-12-31', skillsLevel1=2, skillsLevel2=1)
        testChild2 = Child(2, 'K', dateOfBirth='2011-12-31', skillsLevel1=3, skillsLevel2=3)
        testChild3 = Child(3, 'L', dateOfBirth='2015-12-31', skillsLevel1=4, skillsLevel2=4)

        self.testChildren = [testChild1, testChild2, testChild3]
        self.scheduledClass = ScheduledClass(children=self.testChildren)

    def test_getCostAgeDiffs(self):
        result = CostCalculator.getCostOfAgeDiffs([self.scheduledClass])
        self.assertEqual(round(result, 2), 12.25)

    def test_getCostDisabilityLevelsDiffs(self):
        result = CostCalculator.getCostOfDisablityLevelsDiffs([self.scheduledClass])
        self.assertEqual(round(result, 1), 11.2)
