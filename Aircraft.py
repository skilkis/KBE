from Design.wingpowerloading import WingPowerLoading
from Design.weightestimator import *
from Design.paramgenerator import *


class Aircraft(Base):

    @Part
    def test(self):
        return ParameterGenerator(label="Design Parameters")


if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft()
    display(obj)
