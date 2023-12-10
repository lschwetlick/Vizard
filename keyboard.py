from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class pseudomidiknob:
    ix: int = 0
    channel: int = 0
    value: int = 1
    control: int = 0

    def increment(self):
        if self.value < 127:
            self.value += 1

    def decrement(self):
        if self.value >= 1:
            self.value -= 1

    def turn(self):
        return self

    def click_in(self):
        return pseudomidiknob(control=self.control, value=127, channel=1)

    def click_out(self):
        return pseudomidiknob(control=self.control, value=0, channel=1)

    def nothing(self):
        pass


PSEUDOKNOBS = {
    0: pseudomidiknob(control=0),
    1: pseudomidiknob(control=1),
    2: pseudomidiknob(control=2),
    3: pseudomidiknob(control=3),
    4: pseudomidiknob(control=4),
    5: pseudomidiknob(control=5),
    6: pseudomidiknob(control=6),
    7: pseudomidiknob(control=7),
    8: pseudomidiknob(control=8),
    9: pseudomidiknob(control=9),
    10: pseudomidiknob(control=10),
    11: pseudomidiknob(control=11),
    12: pseudomidiknob(control=12),
    13: pseudomidiknob(control=13),
    14: pseudomidiknob(control=14),
    15: pseudomidiknob(control=15),
}


KEYSMAP = {
    b"q": (PSEUDOKNOBS[0].turn, PSEUDOKNOBS[0].increment),
    b"Q": (PSEUDOKNOBS[0].turn, PSEUDOKNOBS[0].decrement),
    b"1": (PSEUDOKNOBS[0].click_out, PSEUDOKNOBS[0].nothing),
    b"w": (PSEUDOKNOBS[1].turn, PSEUDOKNOBS[1].increment),
    b"W": (PSEUDOKNOBS[1].turn, PSEUDOKNOBS[1].decrement),
    b"2": (PSEUDOKNOBS[1].click_out, PSEUDOKNOBS[1].nothing),
    b"e": (PSEUDOKNOBS[2].turn, PSEUDOKNOBS[2].increment),
    b"E": (PSEUDOKNOBS[2].turn, PSEUDOKNOBS[2].decrement),
    b"3": (PSEUDOKNOBS[2].click_out, PSEUDOKNOBS[2].nothing),
    b"r": (PSEUDOKNOBS[3].turn, PSEUDOKNOBS[3].increment),
    b"R": (PSEUDOKNOBS[3].turn, PSEUDOKNOBS[3].decrement),
    b"4": (PSEUDOKNOBS[3].click_out, PSEUDOKNOBS[3].nothing),

    b"a": (PSEUDOKNOBS[4].click_out, PSEUDOKNOBS[4].nothing),
    b"s": (PSEUDOKNOBS[5].turn, PSEUDOKNOBS[5].increment),
    b"S": (PSEUDOKNOBS[5].turn, PSEUDOKNOBS[5].decrement),
    b"d": (PSEUDOKNOBS[6].turn, PSEUDOKNOBS[6].increment),
    b"D": (PSEUDOKNOBS[6].turn, PSEUDOKNOBS[6].decrement),
    b"f": (PSEUDOKNOBS[7].turn, PSEUDOKNOBS[7].increment),
    b"F": (PSEUDOKNOBS[7].turn, PSEUDOKNOBS[7].decrement),

    b"<": (PSEUDOKNOBS[8].turn, PSEUDOKNOBS[8].increment),
    b">": (PSEUDOKNOBS[8].turn, PSEUDOKNOBS[8].decrement),
    b"y": (PSEUDOKNOBS[8].click_in, PSEUDOKNOBS[8].nothing),
    b"Y": (PSEUDOKNOBS[8].click_out, PSEUDOKNOBS[8].nothing),
    b"x": (PSEUDOKNOBS[10].turn, PSEUDOKNOBS[10].increment),
    b"X": (PSEUDOKNOBS[10].turn, PSEUDOKNOBS[10].decrement),

    b"m": (PSEUDOKNOBS[15].turn, PSEUDOKNOBS[15].increment),
    b"M": (PSEUDOKNOBS[15].turn, PSEUDOKNOBS[15].decrement),
    b";": (PSEUDOKNOBS[15].click_in, PSEUDOKNOBS[15].nothing),
    b"n": (PSEUDOKNOBS[14].click_in, PSEUDOKNOBS[14].nothing),

}
