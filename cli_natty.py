""" Command-Line Interface Tool to create natty mark ATs that match with natty mark tiles.
    This helps expedite the process of making natty marks glow - the flippness and rotation are handled,
    and their glow values are randomly generated within their acceptable range. After which, it's easy
    to trim down and reduce their effect as needed.
    
    USAGE EXAMPLE: "python cli_natty.py d51"
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
templates = ["good1", "good2", "good3", "good4", "bad1", "bad2",
    "bad3", "bad4", "clam1", "clam2", "clam3", "clam4"]
pattern_matcher = PM.PatternMatcher()
for template_file in templates:
    file_path = file_utils.GetTemplateRoot() + f"{template_file}.xml"
    pattern_matcher.LoadPattern(file_path)

# Look for matches. We search all visible tile layers
pattern_matcher.FindAndCreateAll(playdo, "objects_natty_mark_ATs")

# After FindAndCreateAll(), we have created a new object layer called "objects_natty_mark_ATs" that
# contains Natty Mark AT objects. However, the objects are still "templates" - meaning they contain
# placeholder text like "[GEN_NUM_GOOD]" and need to be replaced with appropriate values.

# Define 3 random number generators. They will be used by playdo to fill in the template information
generate_natty_blue_num = lambda: format(random.uniform(0, 2), '.1f')
generate_natty_red_num = lambda: format(random.uniform(0, 3), '.1f')
generate_natty_green_num = lambda: format(random.uniform(0, 4.5), '.1f')

# Tell playdo to fill in the template using the random number generators
playdo.RegexReplacePropertyValues("[GEN_NUM_GOOD]", generate_natty_blue_num)
playdo.RegexReplacePropertyValues("[GEN_NUM_BAD]", generate_natty_red_num)
playdo.RegexReplacePropertyValues("[GEN_NUM_CLAM]", generate_natty_green_num)

# Flush changes to File!
playdo.Write()
