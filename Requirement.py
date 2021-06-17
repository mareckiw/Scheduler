#Created on 1/04/2020 by AS76173
import itertools
from Config import MINIMUM_GROUP_SIZE


class Requirement:

    def __init__(self, lesson=None, kids=None):
        self.lesson = lesson #Lesson
        self.kids = kids #List of pairs (Child, Int) - which kid wants this Lesson and how many times a week
        if self.kids is None:
            self.kids = []



    def __str__(self):
        result = 'REQ lessonName: ' + str(self.lesson.name) + ' dbId: ' + str(self.lesson.dbId)
        return result

    def getChildren(self):
        childList = []
        for pair in self.kids:
            childList.append(pair[0])
        return childList

    #TODO - zapisanie wyników w pamięci - Asia :( - ADAM POMOZE!

    def getChildrenWithPositiveRequirement(self):
        childList = []
        for pair in self.kids:
            if pair[1] > 0:
                childList.append(pair[0])
        return childList

    def getPossibleTeacherConfigurations(self):
        totalConfiguartions = []
        #TODO - sprawdzenie sortowania jakie robią itertoolsy
        #TODO - przywrocic, co zepsulam, Asia - speciality
        #TODO - przechowywanie w pamieci
        #TODO - gdzie sprawdzana dostepnosc
        allReqCombinations = list(itertools.combinations(self.lesson.reqTeachers, self.lesson.numberOfTeachers))
        reqPlusOptProduct = list(itertools.product(self.lesson.reqTeachers, self.lesson.optTeachers))
        if self.lesson.differentSpec != 0:
            for config in (allReqCombinations + reqPlusOptProduct):
                if self.lesson.differentSpec in [config[0].speciality.db_Id, config[1].speciality.db_Id]:
                    totalConfiguartions.append(config)
        else:
            totalConfiguartions = allReqCombinations + reqPlusOptProduct
        return totalConfiguartions

    def getPossibleChildrenConfigurations(self):
        childList = self.getChildrenWithPositiveRequirement()
        if self.lesson.groupSize == 1:
            return list(itertools.combinations(childList, 1))
        groupSize = self.lesson.groupSize
        if len(childList) < groupSize:
            return [childList]
        totalConfiguartions = []
        while groupSize >= MINIMUM_GROUP_SIZE:
            configurationsOfCurrentSize = list(itertools.combinations(childList, groupSize))
            for configuration in configurationsOfCurrentSize:
                totalConfiguartions.append(configuration)
            groupSize -= 1
        return totalConfiguartions

    def isFulfilled(self):
        for pair in self.kids:
            if pair[1] > 0:
                return False
        return True


