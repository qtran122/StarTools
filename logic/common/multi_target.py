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


