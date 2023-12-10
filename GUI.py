import prettytable
import os

vizardlogo = '''
                                                                        ,      
                                                                     \  :  /   
.-----..-. .-..----.    .-.   .-..-..---.   .--.  .---. .----.    `. __/ \__ .'
`-' '-'{ {_} |} |__}     \ \_/ / { |`-`} } / {} \ } }}_}} {-. \   _ _\     /_ _
  } {  | { } }} '__}      \   /  | }{ /.-./  /\  \| } \ } '-} /      /_   _\   
  `-'  `-' `-'`----'       `-'   `-' `---'`-'  `-'`-'-' `----'     .'  \ /  `. 
                                                                     /  :  \   
                                                                        '      
'''

kal_names = ["None", "Multiscope", "Recurseoscope", "Flexoscope"]
waveforms_names = ["sin", "square", "noise", "constant", "triangle"]


table_dict = {
    1: {
        1: "RB + 'Red' + Y   + ' [r=' + str(MIDIKNOBS[0].register) + ']' + N",
        2: "RB + 'Green' + Y + ' [r=' + str(MIDIKNOBS[1].register) + ']' + N",
        3: "RB + 'Blue' + Y  + ' [r=' + str(MIDIKNOBS[2].register) + ']' + N",
        4: "RB + 'Speed' + Y + ' [r=' + str(MIDIKNOBS[2].register) + ']' + N"
    },
    2: {
        1: "W + str(parameters['r_freq'])        + N",
        2: "W + str(parameters['g_freq'])        + N",
        3: "W + str(parameters['b_freq'])        + N",
        4: "W + str(parameters['px_scan_speed']) + N",
    },
    3: {
        1: "B + waveforms_names[parameters['r_waveform_ix']] + N",
        2: "B + waveforms_names[parameters['g_waveform_ix']] + N",
        3: "B + waveforms_names[parameters['b_waveform_ix']] + N",
        4: "Y + 'RESET'                          + N",
    },
    4: {
        1: "RB + 'Kaleidoscope' + N",
        2: "RB + 'N Segments'   + N",
        3: "RB + 'Flip'         + N",
        4: "''"
    },
    5: {
        1: "W + kal_names[parameters['kaleidoscope_ix']] + N",
        2: "W + str(parameters['k_n_segments'])    + N",
        3: "W + str(parameters['k_flip'])          + N",
        4: "''"
    },
    6: {
        1: "RB + 'Manual Kaleidoscope' + N",
        2: "''",
        3: "RB + 'Flip 2' + N",
        4: "''"
    },
    7: {
        1: "W + str(parameters['k_manual_rot_curr']) + N",
        2: "''",
        3: "W + str(parameters['k_alternate_flip'])  + N",
        4: "''"
    },
    8: {
        1: "Y + 'Apply' + N + '/' + B + 'Clear' + N",
        2: "''",
        3: "''",
        4: "''"
    },
    9: {
        1: "''",
        2: "RB + 'Kal Presets' + N",
        3: "''",
        4: "RB + 'Presets' + N"
    },
    10: {
        1: "''",
        2: "W + str(MIDIKNOBS[13].value) + N",
        3: "''",
        4: "W + str(MIDIKNOBS[15].value) + N",
    },
    11: {
        1: "''",
        2: "Y + 'Load' + N",
        3: "''",
        4: "Y + 'Load' + N + '/' + B + 'Save' + N",
    }
}



def print_table(MIDIKNOBS, parameters, extra_message=""):
    # Color
    # \033    [   0     ;1      ; 4          m
    # Color       color  bold     underline  end?
    W = "\033[0;97m"  # RED
    R = "\033[0;31m"  # RED
    RB = "\033[31;1m"  # RED
    # G = "\033[0;32;40m"  # GREEN
    Y = "\033[0;33m"  # Yellow
    B = "\033[0;96m"  # Blue

    N = "\033[0m"  # Reset
    tab = prettytable.PrettyTable(default_color="blue")
    tab.hrules = 1
    tab.header = False


    for i in table_dict:
        row_dict = table_dict[i]
        r = []
        for j in row_dict:
            what = eval(row_dict[j])
            r.append(what)
        tab.add_row(r)
    # PRINTING
    os.system('clear')
    print(vizardlogo)
    print(tab)
    print(W + 'White' + N + ' = turn')
    print(B + 'Blue' + N + ' = longclick')
    print(Y + 'Yellow' + N + ' = short click')
    print('')
    if extra_message != "":
        print(RB + 'FYI:' + N + extra_message)
