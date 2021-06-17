#Created on 9/06/2020 by AS76173
from Config import WEEK_SLOTS
import math

#Static class
class CostCalculator:

    numberOfClassesWeight = 10
    childrenFreePeriodWeight = 9
    teachersFreePeriodWeight = 8
    siblingsDifferentSlotsWeight = 7
    childrenAgeWeight = 5
    childrenDisabilityGroupWeight = 5
    groupFillingWeight = 4
    fullHourStartWeight = 2


    @staticmethod
    def isClassDividedBetween2Days(scheduledLesson):
        startSlot = scheduledLesson.startSlot
        lessonDuration = scheduledLesson.lesson.duration
        endSlot = startSlot+lessonDuration-1
        daySlots = WEEK_SLOTS/5
        return startSlot//daySlots != endSlot//daySlots

    @staticmethod
    def getDayStartSlotsForPerson(person):
        startSlots = []
        for dayNum in range (1, 6):
            slotsOfTheDay = CostCalculator.getDaySlots(dayNum)
            firstDaySlot = slotsOfTheDay[0]
            lastDaySlot = slotsOfTheDay[1]
            startSlot = -1
            for slotNum in range(firstDaySlot, lastDaySlot+1):
                if person.lessonSlots[slotNum]:
                    startSlot = slotNum
                    break
            startSlots.append(startSlot)
        return(startSlots)

    # day = int value in range 0-4 where 0 represents Monday, 2 Tuesday etc.
    @staticmethod
    def getDaySlots(day):
    # new hard requirement: slot 33 and 34 are two different days
    # start 8am finish 7pm = 11hrs/20min = 33
        multiplier = WEEK_SLOTS/5
        firstSlotOfDay = (multiplier+1)*day
        lastSlotOfDay = firstSlotOfDay + multiplier # number of slots per day 33*20min = 11hours
        return [firstSlotOfDay, lastSlotOfDay]

    @staticmethod
    def getFreePeriodSlots(person):
        currentFreePeriod = 0
        hasFoundFirstLessonInDay = False
        FreePeriods = []
        currentSlot = 0
        daySlots = WEEK_SLOTS/5
        for slot in person.lessonSlots:
            if currentSlot % daySlots == 0:
                hasFoundFirstLessonInDay = False
                currentFreePeriod = 0
            if slot is True:
                hasFoundFirstLessonInDay = True
                if currentFreePeriod > 0:
                    FreePeriods.append(currentFreePeriod)
                currentFreePeriod = 0
            else:   #False
                if hasFoundFirstLessonInDay is True:
                    currentFreePeriod += 1
            currentSlot += 1
        return FreePeriods

    @staticmethod
    def getCostofFreePeriodSlotsForPerson(person):
        freePeriods = CostCalculator.getFreePeriodSlots(person)
        totalCost = 0
        for freePeriod in freePeriods:
            if freePeriod <= 3:
                totalCost += freePeriod
            elif freePeriod <= 5:
                totalCost += freePeriod*1.5
            else:
                totalCost += freePeriod*2
        return totalCost

    @staticmethod
    def getCostOfFreePeriodSlotsForAll(dao):
        totalCost = 0
        for child in dao.childList:
            totalCost += CostCalculator.getCostofFreePeriodSlotsForPerson(child) * CostCalculator.childrenFreePeriodWeight
        for teacher in dao.teacherList:
            totalCost += CostCalculator.getCostofFreePeriodSlotsForPerson(teacher) * CostCalculator.teachersFreePeriodWeight
        return totalCost

    @staticmethod
    def getCostOfSiblingsDifferentTimings(dao): #duplicates
        totalCost = 0
        for child in dao.childList:
            childStartSlots = CostCalculator.getDayStartSlotsForPerson(child)
            for sibling in child.siblings:
                siblingStartSlots = CostCalculator.getDayStartSlotsForPerson(sibling)
                for i in range(1,6):
                    if childStartSlots[i] != siblingStartSlots[i]:
                        totalCost += 1
        return totalCost

    @staticmethod
    def getCostOfAgeDiffs(scheduledClasses):
        totalCost = 0
        for sClass in scheduledClasses:
            mean = sum(c.calculateAge() for c in sClass.children)/len(sClass.children)
            stdev = math.sqrt(sum((c.calculateAge()-mean)**2 for c in sClass.children)/(len(sClass.children)))
            if stdev <= 1:
                totalCost += stdev * CostCalculator.childrenAgeWeight
            elif stdev <= 3:
                totalCost += stdev * CostCalculator.childrenAgeWeight * 1.5
            else:
                totalCost += stdev * CostCalculator.childrenAgeWeight * 2
        return totalCost

    @staticmethod
    def getCostOfDisablityLevelsDiffs(scheduledClasses):
        totalCost = 0
        disabilityLevelsStdevs = []
        for sClass in scheduledClasses:
            mean = sum(c.skillsLevel1 for c in sClass.children) / len(sClass.children)
            disabilityLevelsStdevs.append(math.sqrt(sum((c.skillsLevel1 - mean) ** 2 for c in sClass.children) / (len(sClass.children))))
            mean = sum(c.skillsLevel2 for c in sClass.children) / len(sClass.children)
            disabilityLevelsStdevs.append(math.sqrt(sum((c.skillsLevel2 - mean) ** 2 for c in sClass.children) / (len(sClass.children))))
            mean = sum(c.skillsLevel3 for c in sClass.children) / len(sClass.children)
            disabilityLevelsStdevs.append(math.sqrt(sum((c.skillsLevel3 - mean) ** 2 for c in sClass.children) / (len(sClass.children))))
            mean = sum(c.skillsLevel4 for c in sClass.children) / len(sClass.children)
            disabilityLevelsStdevs.append(math.sqrt(sum((c.skillsLevel4 - mean) ** 2 for c in sClass.children) / (len(sClass.children))))
            stdev = math.sqrt(sum(s**2 for s in disabilityLevelsStdevs))
            if stdev <= 1:
                totalCost += stdev * CostCalculator.childrenDisabilityGroupWeight
            elif stdev <= 3:
                totalCost += stdev * CostCalculator.childrenDisabilityGroupWeight * 1.5
            else:
                totalCost += stdev * CostCalculator.childrenDisabilityGroupWeight * 2
        return totalCost

    @staticmethod
    def getCostOfNotFullHour(schedule):
        cost = 0
        for lesson in schedule.classes:
            if lesson.startSlot % 3 != 0:
                cost +=1
        return cost

    @staticmethod
    def calculateCost(schedule, dao):
        totalCost = 0

        #Adjust the cost by adding the class number multiplied by corresponding weight
        numberOfClasses = len(schedule)
        totalCost += numberOfClasses * CostCalculator.numberOfClassesWeight

        #Adjust the cost by adding the free slots periods for all
        if dao is not None:
            totalCost += CostCalculator.getCostOfFreePeriodSlotsForAll(dao)



        return totalCost


