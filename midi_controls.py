from dataclasses import dataclass
import time
import types

class midiknob:
    def __init__(self, control=0, value=1, color=120,
                 longclick_min=1, longclick_max=10,
                 turn_var="", click_out_var="", longclick_out_var="",
                 turn=None, click_out=None, longclick_out=None):
        self.control = control # dial ID
        self.color = color
        #self.channel = channel
        self.value = value
        self.click_counter = 0

        self.click_in_timer = time.time()
        self.isclicked = False
        self.longclick_min = longclick_min
        self.longclick_max = longclick_max
        # influenced vars in VIZ
        self.turn_var = turn_var
        self.click_out_var = click_out_var
        self.longclick_out_var = longclick_out_var
        # functions!
        # they need to be bound to the class because they care about accessing self!
        self.turn = types.MethodType(turn, self) if turn is not None else self.do_nothing
        self.click_out = types.MethodType(click_out, self) if click_out is not None else self.do_nothing
        self.longclick_out = types.MethodType(longclick_out, self) if longclick_out is not None else self.do_nothing
        self._register = 0
        self.reg_values = [0, 0]


    @property
    def register(self):
        return(self._register)

    @register.setter
    def register(self, register):
        self._register = register % 2
        self.value = self.reg_values[self._register]


    def is_longclick(self):
        now = time.time()
        if ((now - self.click_in_timer) <= self.longclick_min):
            # print("ad")
            return False
        if ((now - self.click_in_timer) > self.longclick_min) & \
                ((now - self.click_in_timer) < self.longclick_max):
            # print("werwer")
            return True
        else:
            return False

    def click_in(self):
        self.click_in_timer = time.time()

    def do_nothing(self, VIZ):
        return VIZ




##################### FUNCTIONS
# TURN FUNCTIONS
def default_turn(self, VIZ):
    VIZ.params.__setattr__(self.turn_var, self.value)
    return VIZ

def register_turn(self, VIZ):
    self.reg_values[self.register] = self.value
    computed_value = self.reg_values[0] + (self.reg_values[1]*127)
    VIZ.params.__setattr__(self.turn_var, computed_value)
    return VIZ

def inc_register(self, VIZ):
    self.register += 1
    return VIZ

def make_n_step_turn_func(steps):
    def n_step_turn(self, VIZ):
        VIZ.params.__setattr__(self.turn_var, int(self.value/steps))
        return VIZ
    return n_step_turn

def k_rot_map(self, VIZ):
    if self.value < 74:
        val = (self.value * 5, True)
    else:
        val = ((self.value - 74) * 5, False)
    VIZ.params.__setattr__(self.turn_var, val)
    return VIZ


# CLICK FUNCTIONS
def default_click(self, VIZ):
    val = VIZ.params.__getattribute__(self.click_out_var) + 1
    VIZ.params.__setattr__(self.click_out_var, val)
    return VIZ

def make_n_ix_click_func(steps, varname):
    def n_ix_click(self, VIZ):
        self.click_counter += 1
        self.click_counter = self.click_counter % steps
        VIZ.params.__setattr__(varname, int(self.click_counter))
        return VIZ
    return n_ix_click


def reset_states(self, VIZ):
    VIZ.params.r_state = 0
    VIZ.params.g_state = 0
    VIZ.params.b_state = 0
    VIZ.params.update_state = True
    return VIZ

def refl_load_fun(self, VIZ):
    thispreset = VIZ.params.current_refl_num
    VIZ.load_reflection_from_preset(thispreset)
    return VIZ

def preset_load_fun(self, VIZ):
    thispreset = VIZ.params.current_preset_num
    print(f" loading {thispreset}")
    try:
        extra_message = \
            VIZ.load_params_from_preset(thispreset)
    except Exception as e:
        print(f"Could not load Preset {thispreset}")
        print(e)
        raise
    send_dataclass_to_midi(OUTPORT, VIZ.params, keyboard.PSEUDOKNOBS)
    return VIZ

def preset_save_fun(self, VIZ):
    thispreset = VIZ.params.current_preset_num
    try:
        extra_message = \
            VIZ.add_params_as_preset(thispreset)
    except:
        print(f"Could not save Preset {thispreset}")
        raise
    return VIZ

def rot_apply_fun(self, VIZ):
    VIZ.params.k_manual_rot = \
                    VIZ.params.k_manual_rot + (VIZ.params.k_manual_rot_curr,)
    return VIZ

def rot_clear_fun(self, VIZ):
    VIZ.params.k_manual_rot = ()
    return VIZ

##############################


MIDIKNOBS = {
    # RED
    0: midiknob(control=0, color=80,
                turn=register_turn, turn_var="r_freq",
                click_out=inc_register, click_out_var="inc_register",
                longclick_out=make_n_ix_click_func(5, "r_waveform_ix"), longclick_out_var="r_waveform_ix"),
    # GREEN
    1: midiknob(control=1, color=50,
                turn=register_turn, turn_var="g_freq",
                click_out=inc_register, click_out_var="inc_register",
                longclick_out=make_n_ix_click_func(5, "g_waveform_ix"), longclick_out_var="g_waveform_ix"),
    # BLUE
    2: midiknob(control=2, color=1,
                turn=register_turn, turn_var="b_freq",
                click_out=inc_register, click_out_var="inc_register",
                longclick_out=make_n_ix_click_func(5, "b_waveform_ix"), longclick_out_var="b_waveform_ix"),
    # PXSPEED
    3: midiknob(control=3, color=70,
                turn=register_turn, turn_var="px_scan_speed",
                click_out=inc_register, click_out_var="inc_register",
                longclick_out=reset_states, longclick_out_var="reset_states"),
    # SELECT KALEIDOSCOPE
    4: midiknob(control=4, color=100,
                click_out=make_n_ix_click_func(4, "kaleidoscope_ix"), click_out_var="kaleidoscope_ix"),
    # KALEIDOSCOPE SEGMENTS
    5: midiknob(control=5, color=100,
                turn=make_n_step_turn_func(steps=12), turn_var="k_n_segments"),
    # KALEIDOSCOPE FLIP
    6: midiknob(control=6, color=100,
                turn=make_n_step_turn_func(steps=17), turn_var="k_flip"),
    # FREE
    7: midiknob(control=7),
    # MANUAL KALEIDOSCOPE
    8: midiknob(control=8, color=100,
                turn=k_rot_map, turn_var="k_manual_rot_curr",
                click_out=rot_apply_fun, click_out_var="k_manual_rot",
                longclick_out=rot_clear_fun, longclick_out_var="clear_rot"),
    # FREE
    9: midiknob( control=9, color=120),
    # KALEIDOSCOPE FLIP 2
    10: midiknob(control=10, color=100,
                 turn=make_n_step_turn_func(steps=17), turn_var="k_alternate_flip"),
    # FREE
    11: midiknob(control=11, color=120),
    # FREE
    12: midiknob(control=12, color=1),
    # LOAD FREE KALEIDOSCOPES
    13: midiknob(control=13, color=50,
                 turn=default_turn, turn_var="current_refl_num",
                 click_out=refl_load_fun, click_out_var="Refl_load"),
    # FREE
    14: midiknob(control=14, color=60),
    # LOAD PRESETS
    15: midiknob(control=15, color=60,
                 turn=default_turn, turn_var="current_preset_num",
                 click_out=preset_load_fun, click_out_var="Preset_load",
                 longclick_out=preset_save_fun, longclick_out_var="Preset_save")
}

