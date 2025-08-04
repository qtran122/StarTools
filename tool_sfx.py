import sys
import os
import shutil

import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.text2tile as t2t

'''
ALT Tool to facilitate swapping in/out a lot of sound effects for quick demo-ing.

See this video demo link:
https://trello.com/1/cards/688d9ec02aed4df2824f538b/attachments/68903f861ad0810fa358de0f/download/Guide_to_using_tool_sfx.mp4
'''

# Configuration variables
INPUT_FOLDER = r"C:\Users\qtran\Desktop\Star Iliad Audio Dev\SIREN"  # Replace with your input folder path
OUTPUT_FOLDER = r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\WhaleNebula\Assets\Audio2\CHARACTER_FX"  # Replace with your output folder path
INPUT_NAME = "sfx_warning_siren_{0}.ogg"  # Replace with your input file name
OUTPUT_NAME = "SFX_DANGER_SIREN.ogg"  # Replace with your desired output file name
TILED_LEVEL = "test_grapple.xml"

def WriteSfxNameIntoTiledLevel():
    # Writes the name of the sound just copied into the game's project folders into the XML Level File as well.
    # When recording w OBS, this allows us to display the sound name being tested easily, facilitating polling

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(TILED_LEVEL))
    
    # Grab the TEXT_TO_TILE objects & replace their property value / content with the sfx name
    txt2tile_objects = playdo.GetAllObjectsWithName("TEXT_TO_TILES")
    sfx_name = INPUT_NAME.format(sys.argv[1])[4:-4] # Calculate the sfx name, prettified & trimmed
    properties_dict = {'txt2tile_content': sfx_name}
    for txt2tile_obj in txt2tile_objects:
        play.AddPropertiesToObject(txt2tile_obj, properties_dict)
    
    # Next, use text2tile library to process those object updates into graphical tile layer updates
    t2t_args = ("_text_notes", "fg_text2tile", "TEXT_TO_TILES","txt2tile_content")
    t2t.logic(playdo, t2t_args)
    
    # Flush changes
    playdo.Write()
    print("Rewrite Complete!")
    

def copy_ogg_file_and_write_name():
    # Check for command-line argument
    if len(sys.argv) != 2:
        print("Error: Please provide exactly one argument (e.g., python cli_sfx.py 5)")
        return
    
    try:
        # Get the number from command-line argument
        number = sys.argv[1]
        # Format INPUT_NAME with the provided number
        formatted_input_name = INPUT_NAME.format(number)
        
        # Construct full paths
        input_path = os.path.join(INPUT_FOLDER, formatted_input_name)
        output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_NAME)
        
        # Check if input file exists
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' not found")
            return
            
        # Create output folder if it doesn't exist
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Copy file (overwrites if exists)
        shutil.copy2(input_path, output_path)
        print(f"Successfully copied '{formatted_input_name}' to '{OUTPUT_NAME}' in {OUTPUT_FOLDER}")
        
        # Write formatted_input_name to SFX_NAME.txt on desktop
        desktop_path = os.path.expanduser("~/Desktop")
        sfx_file_path = os.path.join(desktop_path, "SFX_NAME.txt")
        
        with open(sfx_file_path, 'w') as f:
            f.write(formatted_input_name)
        print(f"Successfully wrote '{formatted_input_name}' to '{sfx_file_path}'")
        
    except ValueError:
        print("Error: The argument must be a valid number")
    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    copy_ogg_file_and_write_name()
    WriteSfxNameIntoTiledLevel()