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
        raise Exception("Could not find your 'Levels' directory. Please update input/root_dir.toml")
    
def GetPatternRoot():
    '''Retrieve the Pattern folder'''
    root_dirs = toml.load("input/root_dir.toml")
    if (os.path.exists(root_dirs["Q_INPUT"])):
        return root_dirs["Q_INPUT"] + "patterns/"
    elif (os.path.exists(root_dirs["T_INPUT"])):
        return root_dirs["T_INPUT"] + "patterns/"
    else:
        raise Exception("Could not find the Input directory. Please update input/root_dir.toml. " +
            "input directory needs to have a 'patterns' folder")

def GetTemplateRoot():
    '''Retrieve the Templates folder. Templates are similar to patterns, but are missing values'''
    root_dirs = toml.load("input/root_dir.toml")
    if (os.path.exists(root_dirs["Q_INPUT"])):
        return root_dirs["Q_INPUT"] + "templates/"
    elif (os.path.exists(root_dirs["T_INPUT"])):
        return root_dirs["T_INPUT"] + "templates/"
    else:
        raise Exception("Could not find the Templates directory. Please update input/root_dir.toml. " +
            "input directory needs to have a 'templates' folder")

def GetRemapRoot():
    root_dirs = toml.load("input/root_dir.toml")
    if (os.path.exists(root_dirs["Q_INPUT"])):
        return root_dirs["Q_INPUT"] + "remaps/"
    elif (os.path.exists(root_dirs["T_INPUT"])):
        return root_dirs["T_INPUT"] + "remaps/"
    else:
        raise Exception("Could not find the remaps directory. Please update input/root_dir.toml. " +
            "input directory needs to have a 'remaps' folder")

def GetFullLevelPath(filename):
    '''Given a name like x01, will construct the full path to the "level" & add ".xml" extension to the end'''
    if not filename.endswith(".xml"):
        return GetLevelRoot() + filename + ".xml"
    return GetLevelRoot() + filename

def GetFullPatternPath(filename):
    '''Given a name like breakables, will construct the full path to the "pattern" & add ".xml" extension to the end'''
    if not filename.endswith(".xml"):
        return GetPatternRoot() + filename + ".xml"
    return GetPatternRoot() + filename

def GetFullTemplatePath(filename):
    '''Given a name like breakables, will construct the full path to the "pattern" & add ".xml" extension to the end'''
    if not filename.endswith(".xml"):
        return GetTemplateRoot() + filename + ".xml"
    return GetTemplateRoot() + filename

def GetFullRemapPath(filename):
    '''Given a name like breakables, will construct the full path to the "pattern" & add ".xml" extension to the end'''
    if not filename.endswith(".xml"):
        return GetRemapRoot() + filename + ".xml"
    return GetRemapRoot() + filename


def StripFilename(file_path):
    '''Gets the Filename without the path leading to nor the ending extension'''
    # Extract the filename with extension
    filename_with_extension = os.path.basename(file_path)
    
    # Split the filename and the extension
    filename_without_extension, _ = os.path.splitext(filename_with_extension)

    return filename_without_extension