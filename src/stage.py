import time
from enum import Enum, unique
from typing import Literal

from pyseq.ystage import Ystage


@unique
class StageCommand(Enum):
    SET_DIST = "D"
    GO = "G"
    CHECK_POS = "R(IP)"
    READ_POS = "R(PA)"


class BetterYstage(Ystage):
    def move(self, position: int, precision: int = 1) -> Literal[True]:
        """Move ystage to absolute step position.

        **Parameters:**
         - position (int): Absolute step position must be between -7000000
           and 7500000.

        **Returns:**
         - bool: True when stage is in position.

        """

        if self.min_y <= position <= self.max_y:
            while abs(self.position - position) > precision:
                self.command("D" + str(position))  # Set distance
                self.command("G")  # Go
                while not self.check_position():  # Wait till y stage is in position
                    time.sleep(1)
                self.read_position()  # Update stage position
            return True  # Return True that stage is in position
        else:
            raise ValueError("YSTAGE can only between " + str(self.min_y) + " and " + str(self.max_y))
