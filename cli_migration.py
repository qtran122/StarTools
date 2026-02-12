"""
The Command-Line Tool to "rebind" all of the levels inside the root Levels folder. This is done
when the master tilesheet.png has become too disordered and re-organizing it becomes desired.

INSTRUCTIONS:
    1.  Create a new XML level that is as big as the master tiles.png (128 x 128 tiles)
        Call this file "new_tiles.xml"
    2.  We'll be using TILED to construct the new tiles.png since it already has 
        all the functionality we need to quickly organize the tiles
    3.  Re-organize the tiles within new_tiles.xml. Flipping & Rotating tiles is OK
    4.  Once finished, export this level as a new tiles.PNG. Leave this png on desktop.
    5.  Back up the levels folder and the graphics
    6.  Run the cli_migration tool (see below)
    7.  Confirm that all the levels now show a jumbled mess
    8.  Take the new tiles.png (from step 4) and place it in the project graphics folder
    9.  Confirm everything has been successfully migrated over
    
USAGE EXAMPLE:
    The below command performs a "test" run. No changes will be flushed. This is useful since
    a test run will compile an image and inform us if any tiles are missing. If we proceed,
    missing tiles will be "zeroed" out
    
    > python cli_migration.py

    The below command has "real_run" specified, so changes will be recorded. However, a prefix
    is also specified, so it'll target just one level (a02). Useful as a small test run
    > python cli_migration.py --real_run --prefix=a02
    
    The below command performs the run for real on the entire levels folder
    > python cli_migration.py --real_run 
    
TRELLO SOURCES:
    https://trello.com/c/rzlr5Ncw <-- This contains the latest video how-to demo

"""


import os
import sys
import time
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.remapper.tile_remapper as TM
import logic.common.log_utils as log



def PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='='):
    """Call in a loop to create terminal progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()



def _FormatName(name):
    name = file_utils.StripFilename(name)
    if len(name) > 20:
        # Truncate and add "..." to the end
        formatted_name = name[:17] + "..."
    else:
        # Pad with spaces to make it 20 characters
        formatted_name = name.ljust(20)
    return formatted_name
    
    
    
def CheckForUserExit():
    user_input = input().strip().upper()
    if user_input != 'Y':
        time.sleep(0.5)
        log.Must("\ntiles migration canceled...\n")
        sys.exit()
        
        
        
def _CompactPrintFiles(files):
    for i in range(0, len(files), 5):
        formatted_line = ''
        for filename in files[i:i+5]:
            filename = file_utils.StripFilename(filename)
            if len(filename) > 20: formatted_filename = filename[:17] + "..."
            else : formatted_filename = filename
            formatted_line += f'{formatted_filename:<20}'
        log.Info(formatted_line)



def PerformTilesMigration(tile_remapper, files_to_process, is_real_run):
    total_files = len(files_to_process)
    errored_files_n_messages = [] # List of tuple of file_name to error_messages
    for i, file_path in enumerate(files_to_process, 1):
        short_name = _FormatName(file_path)
        try:
            PrintProgressBar(i, total_files, prefix='Migration Progress:', suffix=f'processing {short_name}', length=50)
            playdo = play.LevelPlayDo(file_path)
            tile_remapper.Remap(playdo)
            if is_real_run: playdo.Write()
        except Exception as e:
            errored_files_n_messages.append((short_name, str(e)))
            
    PrintProgressBar(100, 100, prefix='Migration Progress:', suffix='COMPLETE!!!'.ljust(40), length=50)
    return errored_files_n_messages



tool_description = 'Rebinds all levels after the master tiles.png has been re-organized'
arg_real_run_desc = 'By default, all runs are simulation runs. Set this flag to really perform the migration'
arg_new_tiles_desc = 'Name of the new tiles XML we are migrating to. This XML should sit in the regular Levels folder'
arg_prefix_desc = 'Narrows the migration selection requiring files match a prefix. For Ex: "--prefix=f" targets the stomach area'
arg_desc_verbosity = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('--real_run', action='store_true', help=arg_real_run_desc)
    parser.add_argument('--new_tiles', type=str, default='new_tiles', help=arg_new_tiles_desc)
    parser.add_argument('--prefix', type=str, default=None, help=arg_prefix_desc)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help=arg_desc_verbosity )
    args = parser.parse_args()
    
    log.SetVerbosityLevel(args.v)
    
    if args.real_run: log.Must("\nRunning REAL Tiles Migration...")
    else: log.Must("\nRunning Tiles Migration SIMULATION...\nNo changes will be recorded.\n")
    
    tile_remapper = TM.TileRemapper()
    mapping_file_path = file_utils.GetFullLevelPath(args.new_tiles)
    tiles_png_path = file_utils.GetGfxFolder() + "tiles.png"
    
    unseen_tile_ids = tile_remapper.LoadMigrationMap(mapping_file_path, tiles_png_path)
    
    if unseen_tile_ids:
        log.Must(f"\nDiscovered {len(unseen_tile_ids)} forgotten tiles! Check generated image.")
    else:
        log.Must(f"All tiles FOUND!")
    
    # Question : Scan levels folder and confirm number of files to be operated upon
    files_to_process = file_utils.GetAllLevelFiles()
    if not files_to_process:
        log.Must("Levels folder not found! Please update 'root_dir.toml'")
        sys.exit()
        
    # Prune the list of files to migrate if "prefix" is specified
    if args.prefix is not None:
        log.Must(f"Narrowing search to select prefix '{args.prefix}'...\n")
        files_to_process = [fn for fn in files_to_process if file_utils.StripFilename(fn).startswith(args.prefix)]
        if not files_to_process:
            log.Must("No files are targeted with specified prefix!")
            sys.exit()
        _CompactPrintFiles(files_to_process)
    
    time.sleep(0.5)
    log.Must(f"\nFound {len(files_to_process)} files! Proceed with Tiles Migration? (Y/N)")
    CheckForUserExit()
        
    # Begin the Tiles Migration
    log.Must('\n')
    errors = PerformTilesMigration(tile_remapper, files_to_process, args.real_run)
    log.Must('\n')
    
    if not errors: sys.exit()
    
    time.sleep(1)
    log.Must(f"\nHowever, {len(errors)} files errored out!")
    for filename, error_message in errors:
        time.sleep(0.1)
        log.Must(f"\t{filename} - {error_message}")

