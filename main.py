from design import *
from parapy.core import *
from parapy.geom import *
from directories import *


class UAV(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    @Part
    def params(self):
        return ParameterGenerator(initialize_estimations=True, label="Design Parameters")

    @Attribute
    def lalalala(self):
        return self.params.handlaunch

    @Attribute
    def weight(self):
        return ClassOne()

    @Part
    def fuselage(self):
        return Box(1, 1, 1)




if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
