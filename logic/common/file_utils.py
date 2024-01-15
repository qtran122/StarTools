'''Common math functions that are generally useful for all Tiling-related scripts.'''
import os
import toml

def GetLevelRoot():
    root_dirs = toml.load("input/root_dir.toml")
    if (os.path.exists(root_dirs["Q_ROOT"])):
        return root_dirs["Q_ROOT"]
    elif (os.path.exists(root_dirs["T_ROOT"])):
        return root_dirs["T_ROOT"]
    else:
        raise Exception("Could not find the Root directory. Please update input/root_dir.toml")
    
def GetPatternRoot():
    root_dirs = toml.load("input/root_dir.toml")
    if (os.path.exists(root_dirs["Q_PATTERN"])):
        return root_dirs["Q_PATTERN"]
    elif (os.path.exists(root_dirs["T_PATTERN"])):
        return root_dirs["T_PATTERN"]
    else:
        raise Exception("Could not find the Patterns directory. Please update input/root_dir.toml")

def StripFilename(file_path):
    '''Gets the Filename without the path leading to nor the ending extension'''
    # Extract the filename with extension
    filename_with_extension = os.path.basename(file_path)
    
    # Split the filename and the extension
    filename_without_extension, _ = os.path.splitext(filename_with_extension)

    return filename_without_extension