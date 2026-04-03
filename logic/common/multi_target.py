"""

Provides a reusable way to run any single-file function against all level files

USAGE EXAMPLE:
    import logic.common.multi_target as multi
    import logic.standalone.vary_block as VB

    def _VaryFile(file_path):
        playdo = play.LevelPlayDo(file_path)
        VB.VaryRelicBlocks(playdo)
        playdo.Write()

    multi.Init(_VaryFile)
    multi.ExecuteOnAll(prefix='Varying Progress:')
"""

import sys
import logic.common.file_utils as file_utils

_function = None

def _PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='='):
    """Call in a loop to create terminal progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()


def _FormatName(name):
    name = file_utils.StripFilename(name)
    if len(name) > 20:
        formatted_name = name[:17] + "..."
    else:
        formatted_name = name.ljust(20)
    return formatted_name


def Init(function):
    """
    Equip multi_target with the function it'll run on all files
    """
    global _function
    _function = function


def ExecuteOnAll(prefix='Progress:', level_files=None):
    """
    Runs the initialized function on every level file.

    Args:
        prefix: Label shown on the progress bar.
        level_files: Optional list of file paths. If None, uses file_utils.GetAllLevelFiles().

    Returns:
        errors: list of (filename, error_message) tuples.
    """
    if _function is None:
        print("multi_target: No function set. Call Init(func) first.")
        return []

    if level_files is None:
        level_files = file_utils.GetAllLevelFiles()

    total = len(level_files)
    errors = []

    print(f"Preparing to process {total} files...\n")

    for num, level_file in enumerate(level_files):
        short_name = _FormatName(level_file)
        try:
            _function(level_file)
        except Exception as e:
            errors.append((file_utils.StripFilename(level_file), str(e)))
        _PrintProgressBar(num + 1, total, prefix=prefix, suffix=f'processing {short_name}')

    print()
    return errors
