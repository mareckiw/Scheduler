class Decision:

    def __init__(self, childrenGroupIndex=-1, teacherGroupIndex=-1, startSlotNumber=-1):
        self.childrenGroupIndex = childrenGroupIndex
        self.teacherGroupIndex = teacherGroupIndex
        self.startSlotNumber = startSlotNumber
        self.totalChildren = 0
        self.totalTeachers = 0
        self.hasBeenLastDecisionInRequirement = False