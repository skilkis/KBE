from math import *

from parapy.core import *
from parapy.geom import *

# C_L = [1.0, 1.5, 2.0]
# C_L_realistic = 1.1;
#
# C_L['']
#
# C_L[0]
#
# error = [abs(num-C_L_realistic) for num in C_L].index(min(error))
# C_L_selected = C_L[error.index(min(C_L_selected))]


# class Play(Base):
#     """
#     Play.py is a test file.
#         :param self.Test:
#     """
#
#     Test = Input(2.0, doc="This is a test document")
#
#     @Test.on_slot_change
#     def _on_eggs_change(self, slot, new, old):
#         msg = "slot '{:}' changed from {:} to {:}"
#         print msg.format(slot.__name__, old, new)
#
#
#     @Part
#     def parametricbox(self):
#         return Box(1.0, 1.0, 1.0)

from directories import *
from random import *
from os import listdir

from parapy.geom import Face, Rectangle, Circle




if __name__ == '__main__':
    from parapy.gui import display

    display(obj)
