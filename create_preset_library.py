import json
from viz_manager import Parameters

PRESETFILE = "preset_lib.json"

presets = {}
for i in range(127):
    presets[i] = Parameters().to_dict()
    presets[i]["need_update"] = ()

with open(PRESETFILE, 'w') as f:
    json.dump(presets, f)
