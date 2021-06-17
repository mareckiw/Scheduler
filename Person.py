#Created on 12/05/2020 by AS76173
from Config import WEEK_SLOTS
class Person():

    def __init__(self, name='', surname='', availability=([False] * WEEK_SLOTS), lessonSlots = ([False] * WEEK_SLOTS)):
        self.name = name
        self.surname = surname
        self.availability = availability
        self.lessonSlots = lessonSlots
        self.calculateSlotsNumber()

    def addAvailabilitySlots(self, startSlot, numberOfSlotsToAdd):
        counter = 0
        while counter != numberOfSlotsToAdd:
            self.availability[startSlot + counter] = True
            self.lessonSlots[startSlot + counter] = False
            counter += 1

    def removeAvailabilitySlots(self, startSlot, numberOfSlotsToRemove):
        counter = 0
        while counter != numberOfSlotsToRemove:
            self.availability[startSlot + counter] = False
            self.lessonSlots[startSlot + counter] = True
            counter += 1

    def calculateSlotsNumber(self):
        counter = 0
        for slot in self.availability:
            if slot:
                counter += 1
        self.numberOfAvailabilitySlots = counter





