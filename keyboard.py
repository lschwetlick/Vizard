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


kn0 = pseudomidiknob(control=0)
kn1 = pseudomidiknob(control=1)
kn2 = pseudomidiknob(control=2)
kn3 = pseudomidiknob(control=3)
kn4 = pseudomidiknob(control=4)
kn5 = pseudomidiknob(control=5)
kn6 = pseudomidiknob(control=6)
kn7 = pseudomidiknob(control=7)
kn8 = pseudomidiknob(control=8)
kn9 = pseudomidiknob(control=9)
kn10 = pseudomidiknob(control=10)
kn11 = pseudomidiknob(control=11)
kn12 = pseudomidiknob(control=12)
kn13 = pseudomidiknob(control=13)
kn14 = pseudomidiknob(control=14)
kn15 = pseudomidiknob(control=15)


keysmap = {
    b"q": (kn0.turn, kn0.increment),
    b"Q": (kn0.turn, kn0.decrement),
    b"1": (kn0.click_out, kn0.nothing),
    b"w": (kn1.turn, kn1.increment),
    b"W": (kn1.turn, kn1.decrement),
    b"2": (kn1.click_out, kn1.nothing),
    b"e": (kn2.turn, kn2.increment),
    b"E": (kn2.turn, kn2.decrement),
    b"3": (kn2.click_out, kn2.nothing),
    b"r": (kn3.turn, kn3.increment),
    b"R": (kn3.turn, kn3.decrement),
    b"4": (kn3.click_out, kn3.nothing),

    b"a": (kn4.click_out, kn4.nothing),
    b"s": (kn5.turn, kn5.increment),
    b"S": (kn5.turn, kn5.decrement),
    b"d": (kn6.turn, kn6.increment),
    b"D": (kn6.turn, kn6.decrement),
    b"f": (kn7.turn, kn7.increment),
    b"F": (kn7.turn, kn7.decrement),

    b"<": (kn8.turn, kn8.increment),
    b">": (kn8.turn, kn8.decrement),
    b"y": (kn8.click_in, kn8.nothing),
    b"Y": (kn8.click_out, kn8.nothing),
    b"x": (kn10.turn, kn10.increment),
    b"X": (kn10.turn, kn10.decrement),

    b"m": (kn15.turn, kn15.increment),
    b"M": (kn15.turn, kn15.decrement),
    b";": (kn15.click_in, kn15.nothing),
    b"n": (kn14.click_in, kn14.nothing),

}
