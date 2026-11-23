""" Command-Line Interface Tool to create gut star ATs that match with the star tiles.
    This helps expedite the process of aligning glimmering star ATs with the tiles. Their 
    flippness and rotation will be handled, their glow values  randomly generated within 
    acceptable ranges, etc. After which, it's easy to trim down and reduce their effect as needed.
    
    USAGE EXAMPLE: "python cli_stars.py i04"
"""
import argparse
import random
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Search a level for natty mark tiles & add corresponding natty mark ATs.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to natty mark objects to')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

# Create a PatternMatcher and load in the patterns it'll scan for
templates = [
"stars1", 
"stars2",
#"stars3",
"stars4",
"stars5",
"stars6",
"stars7",
#"stars8",
"stars9",
"stars10",
"stars11",
"stars12",
"stars13",
"stars14",
"stars15",
"stars16",
"stars17",
"stars18",
"stars19",
#"stars20",
"stars21",
"stars22",
"stars23",
"stars24",
"stars25",
"stars26",
"stars27",
"stars28",
"stars29"]

pattern_matcher = PM.PatternMatcher()
for template_file in templates:
    file_path = file_utils.GetTemplateRoot() + f"{template_file}.xml"
    pattern_matcher.LoadPattern(file_path)

# Look for matches. We search all visible tile layers
pattern_matcher.FindAndCreateAll(playdo, "objects_glimmering_star_ATs")

# After FindAndCreateAll(), we have created a new object layer called "objects_natty_mark_ATs" that
# contains Natty Mark AT objects. However, the objects are still "templates" - meaning they contain
# placeholder text like "[GEN_NUM_GOOD]" and need to be replaced with appropriate values.

# Define guided random number generators for the glimmering star's cycle time, start time, & power
# UNDULATE_COLOR,ffffff/[GUT_STARS_LO_VAL],ffffff/[GUT_STARS_HI_VAL],cycle_time,[GUT_STARS_CYCLE_TIME],start_time,[GUT_STARS_START_TIME]
generate_lo_val_fn = lambda: format(random.uniform(0.0, 0.35), '.1f')
generate_hi_val_fn = lambda: format(random.uniform(0.45, 0.8), '.1f')
generate_start_time_fn = lambda: format(random.uniform(0, 7), '.1f')
generate_cycle_duration_fn = lambda: format(random.uniform(2.5, 6.5), '.1f')

# Tell playdo to fill in the template using the random number generators
playdo.RegexReplacePropertyValues("[GUT_STARS_LO_VAL]", generate_lo_val_fn)
playdo.RegexReplacePropertyValues("[GUT_STARS_HI_VAL]", generate_hi_val_fn)
playdo.RegexReplacePropertyValues("[GUT_STARS_START_TIME]", generate_start_time_fn)
playdo.RegexReplacePropertyValues("[GUT_STARS_CYCLE_TIME]", generate_cycle_duration_fn)

# Flush changes to File!
playdo.Write()
