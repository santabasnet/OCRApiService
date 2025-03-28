# Field Info

class FieldInfo:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __isAreaZero(self):
        return self.height * self.width

    def topLeft(self):
        return [self.x, self.y]

    def bottomRight(self):
        return [self.x + self.width, self.y + self.height]

    def isEmpty(self):
        return self.__isAreaZero() == 0
