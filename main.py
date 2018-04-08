from design import *
from parapy.core import *
from parapy.geom import *
from directories import *


class Aircraft(Base):

    @Part
    def params(self):
        return ParameterGenerator(label="Design Parameters")

    @Attribute
    def lalalala(self):
        return self.params.handlaunch

    @Attribute
    def weight(self):
        return ClassOne()

    @Part
    def fuselage(self):
        return Box(length=1)

    @Attribute
    def path(self):
        return ICON_DIR




if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft()
    display(obj)
