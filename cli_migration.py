import os
import sys
import time
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.remapper.tile_remapper as TM


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
        print("\ntiles migration canceled...\n")
        sys.exit()
        
        
        
def _CompactPrintFiles(files):
    for i in range(0, len(files), 5):
        formatted_line = ''
        for filename in files[i:i+5]:
            filename = file_utils.StripFilename(filename)
            if len(filename) > 20: formatted_filename = filename[:17] + "..."
            else : formatted_filename = filename
            formatted_line += f'{formatted_filename:<20}'
        print(formatted_line)



def _FetchTilesPngFullPath(filename):
    if not filename.endswith(".png"):
        return file_utils.GetInputFolder() + '/migrate/' + filename + ".png"
    return file_utils.GetInputFolder() + '/migrate/' + filename



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



tool_description = 'Retiles all levels after the master tiles.png has been edited'
arg_real_run_desc = 'By default, all runs are simulation runs. Set this flag to really perform the migration'
arg_old_tiles_desc = 'Name of the old tiles png we are migrating from. This png should sit in the "input/migrate" folder'
arg_new_tiles_desc = 'Name of the new tiles png we are migrating to. This png should sit in the "input/migrate" folder'
arg_desc_verbosity = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'
arg_prefix_desc = 'Narrows the migration selection requiring files match a prefix. For Ex: "--prefix=f" targets the stomach area'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('--real_run', action='store_true', help=arg_real_run_desc)
    parser.add_argument('--old_tiles', type=str, default='migrate_tiles_old.png', help=arg_old_tiles_desc)
    parser.add_argument('--new_tiles', type=str, default='migrate_tiles_new.png', help=arg_new_tiles_desc)
    parser.add_argument('--prefix', type=str, default=None, help=arg_prefix_desc)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help=arg_desc_verbosity )
    args = parser.parse_args()
    
    if args.real_run: print("\nRunning REAL Tiles Migration...")
    else: print("\nRunning Tiles Migration SIMULATION...\nNo changes will be recorded.\n")
    
    tile_remapper = TM.TileRemapper()
    
    old_tiles_png_path = _FetchTilesPngFullPath(args.old_tiles)
    new_tiles_png_path = _FetchTilesPngFullPath(args.new_tiles)
    num_unmatched_tiles = tile_remapper.LoadMigrationMap(old_tiles_png_path, new_tiles_png_path)
    
    # Question 1 : Ask user to check migration images & reconcile any mismatches
    if num_unmatched_tiles > 0:
        print(f"\nDiscovered {num_unmatched_tiles} unmatched tiles! See generated mismatch image.")
        print("Unmatched tiles should be reconciled via an override_bindings file.\n\nStill Proceed? (Y/N)")
        CheckForUserExit()
            
    else:
        print("Matches for all tiles were found!")
    
    # Question 2 : Scan levels folder and confirm number of files to be operated upon
    files_to_process = file_utils.GetAllLevelFiles()
    if not files_to_process:
        print("prefix Levels folder not found! Please update 'root_dir.toml'")
        
    # Prune the list of files to migrate if "prefix" is specified
    if args.prefix is not None:
        print(f"Narrowing search to select prefix '{args.prefix}'...\n")
        files_to_process = [fn for fn in files_to_process if file_utils.StripFilename(fn).startswith(args.prefix)]
        if not files_to_process:
            print("No files are targeted with specified prefix!")
        _CompactPrintFiles(files_to_process)
    
    time.sleep(0.5)
    print(f"\nFound {len(files_to_process)} files for Tiles Migration! Proceed with migration? (Y/N)")
    CheckForUserExit()
        
    # Begin the Tiles Migration
    print()
    errors = PerformTilesMigration(tile_remapper, files_to_process, args.real_run)
    print()
    
    if not errors: sys.exit()
    
    time.sleep(1)
    print(f"\nHowever, {len(errors)} files errored out!")
    for filename, error_message in errors:
        time.sleep(0.1)
        print(f"\t{filename} - {error_message}")

