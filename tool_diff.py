'''
Whenever builds are swapped and you need  to get a quick stock of which files have changed, run 
this script! It will diff the XML level and CS script files and inform which ones have changed.

You need only specify the name of the 2 directories by updating the 2 variables below:
DIR_NAME_1 & DIR_NAME_2
'''

DIR_NAME_1 = 'WhaleNebula'
DIR_NAME_2 = 'WhaleNebula(TriedAddingShockwaveFail)'


import os
import filecmp

def compare_files(dir1, dir2, file_ending):
    changed_files = []
    
    for root, _, files in os.walk(dir1):
        for file in files:
            if file.endswith('.xml') or file.endswith(file_ending):
                path1 = os.path.join(root, file)
                path2 = os.path.join(dir2, os.path.relpath(path1, dir1))
                
                if os.path.exists(path2):
                    if not filecmp.cmp(path1, path2, shallow=False):
                        changed_files.append(os.path.relpath(path1, dir1))
                else:
                    changed_files.append(os.path.relpath(path1, dir1))
    
    return changed_files

def main():
    levels_directory1 = rf'C:\Users\qtran\Desktop\PROJECT Whale Nebula\{DIR_NAME_1}\Assets\StreamingAssets\levels'
    levels_directory2 = rf'C:\Users\qtran\Desktop\PROJECT Whale Nebula\{DIR_NAME_2}\Assets\StreamingAssets\levels'
    scripts_directory1 = rf'C:\Users\qtran\Desktop\PROJECT Whale Nebula\{DIR_NAME_1}\Assets\Scripts'
    scripts_directory2 = rf'C:\Users\qtran\Desktop\PROJECT Whale Nebula\{DIR_NAME_2}\Assets\Scripts'
    
    changed_levels = compare_files(levels_directory1, levels_directory2, '.txt')
    changed_scripts = compare_files(scripts_directory1, scripts_directory2, '.cs')
    change_occurred = False
    
    if changed_scripts:
        change_occurred = True
        print("\nThe following SCRIPT files have been edited:")
        for file in changed_scripts:
            print('\t' + file)
            
    if changed_levels:
        change_occurred = True
        print("\nThe following LEVEL files have been edited:")
        for file in changed_levels:
            print('\t' + file)

    if not change_occurred:
        print("No LEVEL or CS files have been edited.")

if __name__ == "__main__":
    main()