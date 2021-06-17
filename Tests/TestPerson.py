import unittest
from Person import Person
from Child import Child

class TestPerson(unittest.TestCase):

    def setUp(self):
        self.person = Person()
        self.person.availability[100] = True
        self.person.availability[101] = True
        self.person.availability[102] = True
        self.child = Child()

    def test_addAvailabilitySlots_addsSlots(self):
        self.person.addAvailabilitySlots(10, 3)
        self.assertEqual(self.person.availability[10], True)
        self.assertEqual(self.person.availability[11], True)
        self.assertEqual(self.person.availability[12], True)
        self.assertEqual(self.person.availability[13], False)

    def test_removeAvailabilitySlots_removesSlots(self):
        self.person.removeAvailabilitySlots(99, 3)
        self.assertEqual(self.person.availability[99], False)
        self.assertEqual(self.person.availability[100], False)
        self.assertEqual(self.person.availability[101], False)
        self.assertEqual(self.person.availability[102], True)

    def test_calculateAge(self):
        self.child.dateOfBirth = '2013-12-31'
        self.assertEqual(self.child.calculateAge(),7)

    def test_calculateAgeYE(self):
        self.child.dateOfBirth = '2013-12-31'
        self.assertEqual(self.child.calculateAgeYE(),7)





if __name__ == '__main__':
    unittest.main()
