from design import *
from parapy.core import *


class Aircraft(Base):

    @Part
    def test(self):
        return ParameterGenerator(label="Design Parameters")

    @Attribute
    def lalalala(self):
        return self.test.handlaunch



if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft()
    display(obj)
