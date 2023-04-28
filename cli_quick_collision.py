import toml
import logic.quick_collision.quick_collision_logic as qct
import logic.common.level_playdo as playdo

root_dirs = toml.load("input/root_dir.toml")
default_args = toml.load("input/quick_collision_input.toml")

# LATER TODO : Use "argparse" standard library to check if command-line args were provided. 
# If provided, the command-line args will override the args in input

# TODO: Loop through root_dirs and find the most suitable root

level_playdo = playdo.LevelPlayDo(default_args["default_level"])
qct.create_quick_collisions(level_playdo)
level_playdo.write()

# TODO: The above are just stubs. They won't blow up when run, but will need implementing