#Created on 19/03/2020 by AS76173

import Lesson
import Teacher
import Child

class ScheduledClass:

    def __init__(self, children=None, lesson=None, teachers=None, startSlot=-1):
        self.children = children #Child[]
        if self.children is None:
            self.children = []
        self.lesson = lesson #Lesson
        self.teachers = teachers #Teacher[]
        if self.teachers is None:
            self.teachers = []
        self.startSlot = startSlot #Int