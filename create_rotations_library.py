import json
from viz_manager import Parameters

REFL_PRESETFILE = "kal_rotations_lib.json"

presets = {}
for i in range(127):
    presets[i] = []

with open(REFL_PRESETFILE, 'w') as f:
    json.dump(presets, f)
