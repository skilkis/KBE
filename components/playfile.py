from parapy.core import *
from components import *


class Test(Base):

    @Part
    def test(self):
        return Motor()


if __name__ == '__main__':
    from parapy.gui import display

    obj = Test()
    display(obj)
