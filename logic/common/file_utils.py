'''Common math functions that are generally useful for all Tiling-related scripts.'''
import os
import toml


def _SearchMatchingPathWithSuffix(root_dir, suffix):
    """Helper function that loops over a dictionary and returns the first existing path with the given suffix
    The dictionary should come from root_dir.toml file
    """
    for key, path in root_dir.items():
        if key.endswith(suffix) and os.path.exists(path):
            return path
    return None;

def GetLevelRoot():
    root_dirs = toml.load("input/root_dir.toml")
    path = _SearchMatchingPathWithSuffix(root_dirs, "_ROOT")
    if path:
        return path
    raise Exception("Could not find your 'Levels' directory. Please update input/root_dir.toml")
    
        
def GetInputFolder():
    root_dirs = toml.load("input/root_dir.toml")
    path = _SearchMatchingPathWithSuffix(root_dirs, "_INPUT")
    if path:
        return path
    raise Exception("Could not find your 'Input' directory. Please update input/root_dir.toml")
        

def GetGfxFolder():
    root_dirs = toml.load("input/root_dir.toml")
    path = _SearchMatchingPathWithSuffix(root_dirs, "_INPUT")
    if path:
        return path
    raise Exception("Could not find your 'GFX' directory. Please update input/root_dir.toml")


def GetAllLevelFiles():
    folder_location = GetLevelRoot()
    files_to_process = []
    for root, dirs, files in os.walk(folder_location):
        for file in files:
            if file.lower().endswith(('.xml', '.tmx')):
                file_path = os.path.join(root, file)
                files_to_process.append(file_path)
    return files_to_process

    
def GetOutputFolder():
    root_dirs = toml.load("input/root_dir.toml")
    output_dir = None
    
    # Output Folder might not exist, so check for the input folder to verify which machine we're on
    if (os.path.exists(root_dirs["Q_INPUT"])):
        output_dir = root_dirs["Q_OUTPUT"]
    elif (os.path.exists(root_dirs["T_INPUT"])):
        output_dir = root_dirs["T_OUTPUT"]
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir
    
    
def GetPatternRoot():
    '''Retrieve the Pattern folder'''
    root_dirs = toml.load("input/root_dir.toml")
    for key, path in root_dirs.items():
        if key.endswith("_ROOT") and os.path.exists(path):
            return os.path.join(path, "star_tools/patterns/")
    raise Exception("Could not find the Root Level directory. Please update input/root_dir.toml. " + "Level directory needs to have a '/star_tools/patterns' folder")
    


def GetTemplateRoot():
    '''Retrieve the Templates folder. Templates are similar to patterns, but are missing values'''
    root_dirs = toml.load("input/root_dir.toml")
    for key, path in root_dirs.items():
        if key.endswith("_ROOT") and os.path.exists(path):
            return os.path.join(path, "/star_tools/templates/")
    raise Exception("Could not find the Root Level directory. Please update input/root_dir.toml. " +
            "Level directory needs to have a '/star_tools/templates' folder")

    
def GetRemapRoot():
    root_dirs = toml.load("input/root_dir.toml")
    for key, path in root_dirs.items():
        if key.endswith("_ROOT") and os.path.exists(path):
            return os.path.join(path, "/star_tools/remaps/")
    raise Exception("Could not find the Root Level directory. Please update input/root_dir.toml. " +
        "Level directory needs to have a '/star_tools/remaps' folder")
            
def GetGfxRoot():
    root_dirs = toml.load("input/root_dir.toml")
    for key, path in root_dirs.items():
        if key.endswith("_ROOT") and os.path.exists(path):
            return os.path.join(path, "gfx/")
    raise Exception("Could not find the gfx directory. Please update input/root_dir.toml. " +
        "input directory needs to have a 'gfx' folder")

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

def GetFullGfxPath(filename):
    '''Given a name like tiles, will construct the full path to the image & add ".png" extension to the end'''
    if not filename.endswith(".png"):
        return GetGfxRoot() + filename + ".png"
    return GetGfxRoot() + filename

def StripFilename(file_path):
    '''Gets the Filename without the path leading to nor the ending extension'''
    # Extract the filename with extension
    filename_with_extension = os.path.basename(file_path)
    
    # Split the filename and the extension
    filename_without_extension, _ = os.path.splitext(filename_with_extension)

    return filename_without_extension





def EnsureFolderExists(filename):
    '''Create new folders if provided one does not exist, also accepts full filename'''

    # If provided string is not a folder's path, remove characters past the last /
    folder_path = filename
    if not filename.endswith("/"):
        folder_path = "/".join( filename.split("/")[0:-1] )

    # Create new folder if not already exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f'Created new directory: {folder_path}')







