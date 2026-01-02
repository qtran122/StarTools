'''
Command-Line Tool to inspect & count a level's rectangles, polygons, and polylines

TODO: Expand this tool to do additional things like count the number of lights, AT's, relic blocks,
and so forth. Make the tool able to run on all files and let us sort which levels are most in need
of reddressment

USAGE EXAMPLE:
    python cli_inspect.py j01
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play

#--------------------------------------------------#
'''Pattern Lists'''



#--------------------------------------------------#
'''Main'''

arg_description = "Inspect a tiled level XML to inform aboutthe level's costs in terms of colliders, lights, and more"
arg_help1 = 'Name of the tiled level XML in which to count the rectangles, polygons, and polylines'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

def IsPolyline(tiled_object):
    polyline = tiled_object.find('polyline')
    if polyline is not None:
        return True
        
    return False

def IsPolygon(tiled_object):    
    polygon = tiled_object.find('polygon')
    if polygon is not None:
        return True
        
    return False

def InspectLevel(filename):
    ''' Inspects a Tiled level XML and returns a tuple that counts the totals the number of (num_rect, num_polys, num_lines, num_relic_block) '''
    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
    # Retrieve all the object groups, layers tucked inside folder are also solved by using GetAllObjectGroup (per comment from playdo file)
    obj_grps = playdo.GetAllObjectgroup(is_print=False)
    layers_w_collision = [] # ["collisions_CAVE", "collisions_BB", "collisions_TREE"] XML objectgroup with name attribute that starts with "collisions"
    num_relic = 0
    for obj_grp in obj_grps:                             
        group_name = obj_grp.get("name", "")
        if group_name.startswith("collisions"):
            layers_w_collision.append(obj_grp)
        if group_name.startswith("objects"): # Groups that starts with "objects" will only contain relic blocks
            for shape in obj_grp:
                if shape.get("name") == "relic_block":
                    num_relic += 1

    
    num_rects = 0
    num_polys = 0
    num_lines = 0
    # Count shapes in collision layers, hadle case where obj_group starts with "collisions" in which we have all shapes (polygon, lines, rects, and relic blocks)
    for obj_grp in layers_w_collision:
        for shape in obj_grp:
            if IsPolygon(shape):
                num_polys += 1
            elif IsPolyline(shape):
                num_lines += 1
            else:
                if shape.get("name") == "relic_block":
                    num_relic += 1
                else:
                    num_rects += 1

    shape_tuple = (num_rects, num_polys, num_lines, num_relic)
    return shape_tuple
        

def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    shape_results = InspectLevel(args.filename)
    print(f"Found {shape_results[0]} rectangles, {shape_results[1]} polygons, {shape_results[2]} lines, and {shape_results[3]} relic blocks!")
        
    
    #breakpoint()
    
    # Flush changes to File!
    #playdo.Write()


#--------------------------------------------------#

main()








# End of File