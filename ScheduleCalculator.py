#Created on 19/03/2020 by AS76173

import Schedule
from Requirement import Requirement
from Lesson import Lesson
from DAO import dao
import random

class ScheduleCalculator:

    def __init__(self, maxLoops, populationSize):
        self.population = [] #Schedule[populationSize]
        self.maxLoops = maxLoops #Int
        self.populationSize = populationSize #Int
        self.bestSolution = None #Schedule, the best solution so far
        self.groupLessonRequirements = []  # List of requirements for group lessons
        self.individualLessonRequirements = []  # List of requirements for individual lessons

    #Gather requiremets - collect all requiremets (In format of Lesson + list of Childs who wants to have it...
    #...and how many times a week
    def gatherRequiremets(self):
        self.groupLessonRequirements = []       # List of requirements for group lessons
        self.individualLessonRequirements = []  # List of requirements for individual lessons
        allRequirements = []

        #Collect all lessons with children insterested in it
        for kid in dao.childList:
            for lesson in kid.dueLessons:
                isFound = False
                amountInWeek = kid.dueLessons.count(lesson)
                pair = (kid, amountInWeek)
                for req in allRequirements:
                    if req.lesson == lesson:
                        req.kids.append(pair)
                        isFound = True
                        break
                if isFound == False:
                    newReq = Requirement()
                    newReq.kids.append(pair)
                    newReq.lesson = lesson
                    allRequirements.append(newReq)

        #Add teachers to this requirements
        for req in allRequirements:
            #Collect teachers
            for teacher in dao.teacherList:
                if req.lesson in teacher.lessons:
                    req.techers.append(teacher)

            if req.lesson.isGroupLesson():
                self.groupLessonRequirements.append(req)
            else:
                self.individualLessonRequirements.append(req)

    #Generate some Schedule compliant with hard restrictions
    def generateStartPopulation(self):
        for i in range(0, self.populationSize):
            newSchedule = Schedule()
            random.shuffle(self.groupLessonRequirements)
            random.shuffle(self.individualLessonRequirements)
            newSchedule.generateSchedule(self.groupLessonRequirements + self.individualLessonRequirements)
            self.population.append(newSchedule)

    def crossPopulation(self):
        print('TO BE DONE')
        #produce children set

    #main program loop
    def mainLoop(self):
        self.generateStartPopulation()

        loopCounter = 0

        #Main Loop
        while True:

            loopCounter += 1

            children = self.crossPopulation() #crossing

            for solution in children:
                solution.mutate() #mutation
                solution.calculateCost() #count cost function of solution
                self.population.append(solution) #add child to population

            #here sort population by cost ascending - to be done

            self.population = self.population[0, self.populationSize/2] #'kill' the worse half of population

            if self.bestSolution is None or self.population[0].cost < self.bestSolution.cost:
                self.bestSolution = self.population[0] #pick the new best solution

            #Exit conditions
            if loopCounter == self.maxLoops or self.bestSolution.cost == 0:
                return self.bestSolution #end of program














