// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for rotating objects to fixed intervals
Shortcut : [Ctrl] + [Shift] + [R] - Clockwise
Shortcut : [Ctrl] + [Shift] + [E] - Counter Clockwise
 */
/**
 * @param thing {TileMap | GroupLayer}
 * @param name {string}
 */
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+Shift+R";
const action_fn_name   = "PluginRotateClockwise";
const action_text      = "Plugin - Rotate (Clockwise)";
const action_shortcut2 = "Ctrl+Shift+E";
const action_fn_name2  = "PluginRotateCounterclockwise";
const action_text2     = "Plugin - Rotate (Counterclockwise)";
const print_prefix_msg = "[Plugin - Align Rotation]\n\n";

// https://docs.google.com/spreadsheets/d/1JYWzR7IYWb8jDBJ_br0MZChSR9SVV_-DM_VFDRFhpbc/edit?gid=876407627#gid=876407627
const allowed_angles = [ 0, 14.036, 26.565, 45, 63.435, 75.964, 90, 104.036, 116.565, 135, 153.435, 165.964, 180, 194.036, 206.565, 225, 243.435, 255.964, 270, 284.036, 296.565, 315, 333.435, 345.964 ];

// Debug Messages
const config_show_msg_end  =  false; // Shows the program concludes successfully
const config_print_index   =  false; // Shows the change in index & angle





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

const PluginAction = tiled.registerAction(action_fn_name, function(/* action */) {
	_Logic(true);
});
const PluginAction2 = tiled.registerAction(action_fn_name2, function(/* action */) {
	_Logic(false);
});
function _Logic(direction){
	/** @type TileMap */
	// Prints out an error message and exit
	const map = tiled.activeAsset;
	if (!map.isTileMap) { _print("ERROR\nNot a tile map!"); return; }
	const list_objects = map.selectedObjects;
	if (list_objects == null) { _print("ERROR\nNo object selected!"); return; } // TODO this isn't responding

	// Same function, but rotated in a different direction
	_RotateSelectedPolygons(map, map.selectedObjects, direction);

	if(config_show_msg_end) _print("End of Procedure!");
}





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function _RotateSelectedPolygons(map, list_objects, rotate_direction){
	let new_action_text = action_text;
	if(!rotate_direction) new_action_text = action_text2;
	map.macro(new_action_text, function() {
		for( const obj of list_objects ) {
			_RotatePolygon(obj, rotate_direction);
		}
	});
}



//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//

function _RotatePolygon(obj, rotate_direction){
	// Get current index
	const next_index = _GetNextIndex(obj, rotate_direction);

	// Set angle to next index's value
	const curr_angle = obj.rotation;
	const next_angle = allowed_angles[next_index];
	obj.rotation = next_angle;

	// Offset position based on mid-point coordinations
//	const angle_diff = next_angle - curr_angle;
//	_RotateWithOffset(obj, next_angle, angle_diff);
//	rotateObjectAboutCenter(obj, next_angle);

	// Print
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `${0} -> ${next_index}\n`;
	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
}

function _OffsetPolygon(obj, angle_diff){
	const start_x = obj.x;
	const start_y = obj.y;
	const mid_x = start_x + 10;
	const mid_y = start_y + 10;
}

function _GetNextIndex(object, rotate_direction){
	// Find the index of the "closest slightly smaller" or "exact" angle value
	const curr_angle = object.rotation;
	let smaller_index = -1;
	let is_exact = false;
	for( let i = 0; i < allowed_angles.length; ++i ){
		if(curr_angle >  allowed_angles[i]) continue;
		if(curr_angle == allowed_angles[i]) is_exact = true;
		smaller_index = i;
		break;
	}
	if(smaller_index < 0) smaller_index = 0;

	// Set the index of the next number, based on rotating direction
	let index_change = -1;
	if(!rotate_direction) index_change = 1;
	else if(!is_exact)    index_change = 0;
	const next_index = (smaller_index - index_change + allowed_angles.length) % allowed_angles.length;

	return next_index;
}





//----------------------------------------------------------//
//-------------------- [Math Functions] --------------------//

function rotateObjectAboutCenter(obj, newAngle) {
    // 1. Calculate the current center point of the object before rotation
    // Convert current angle to radians for trigonometry
    let currentRad = obj.rotation * Math.PI / 180;
    
    // Half dimensions
    let hW = obj.width / 2;
    let hH = obj.height / 2;
    
    // Default relative offset from the origin (top-left for shapes, bottom-left for tiles)
//    let localCenterX = hW;
//    let localCenterY = (obj.tile) ? -hH : hH; // Tile objects have a bottom-left origin
    let localCenterX = getAverageVertexX(obj);
    let localCenterY = getAverageVertexY(obj);
    
    // Rotate local center vector by the object's current rotation to find the world center
    let worldCenterX = obj.x + (localCenterX * Math.cos(currentRad) - localCenterY * Math.sin(currentRad));
    let worldCenterY = obj.y + (localCenterX * Math.sin(currentRad) + localCenterY * Math.cos(currentRad));
    
    // 2. Apply the new rotation angle
    obj.rotation = newAngle;
    let newRad = newAngle * Math.PI / 180;
    
    // 3. Translate the object's (X, Y) origin so the world center remains identical
    obj.x = worldCenterX - (localCenterX * Math.cos(newRad) - localCenterY * Math.sin(newRad));
    obj.y = worldCenterY - (localCenterX * Math.sin(newRad) + localCenterY * Math.cos(newRad));
}

function getAverageVertexX(mapObject) {
    // 1. Check if the object is a Polygon or Polyline
    if (mapObject.polygon && mapObject.polygon.length > 0) {
        let sumX = 0;
        
        for (let i = 0; i < mapObject.polygon.length; i++) {
            // mapObject.polygon[i].x is local/relative to the object's origin
            // Add mapObject.x to convert it to absolute map coordinates
            sumX += mapObject.x + mapObject.polygon[i].x;
        }
        
        return sumX / mapObject.polygon.length;
    } 
    
    // 2. Fallback for Rectangles (average of left and right x bounds)
    else if (mapObject.shape === MapObject.Rectangle) {
        let leftX = mapObject.x;
        let rightX = mapObject.x + mapObject.width;
        return (leftX + rightX) / 2;
    }
    
    // 3. Fallback for points or single coordinate locations
    return mapObject.x;
}

function getAverageVertexY(mapObject) {
    // 1. Check if the object is a Polygon or Polyline
    if (mapObject.polygon && mapObject.polygon.length > 0) {
        let sumX = 0;
        
        for (let i = 0; i < mapObject.polygon.length; i++) {
            // mapObject.polygon[i].x is local/relative to the object's origin
            // Add mapObject.x to convert it to absolute map coordinates
            sumX += mapObject.y + mapObject.polygon[i].y;
        }
        
        return sumX / mapObject.polygon.length;
    } 
    
    // 2. Fallback for Rectangles (average of left and right x bounds)
    else if (mapObject.shape === MapObject.Rectangle) {
        let leftY = mapObject.y;
        let rightY = mapObject.y + mapObject.height;
        return (leftY + rightY) / 2;
    }
    
    // 3. Fallback for points or single coordinate locations
    return mapObject.y;
}





//-----------------------------------------------------------//
//-------------------- [General Utility] --------------------//

function _print(print_msg){
	tiled.alert(`${print_prefix_msg}${print_msg}`);
}





//-----------------------------------------------------//
//-------------------- [Meta Data] --------------------//

PluginAction.text     = action_text;
PluginAction.shortcut = action_shortcut;
tiled.extendMenu("Map", [
	{ separator: true },
	{ action: action_fn_name },
]);

PluginAction2.text     = action_text2;
PluginAction2.shortcut = action_shortcut2;
tiled.extendMenu("Map", [
	{ separator: true },
	{ action: action_fn_name2 },
]);

//--------------------------------------------------//










// End of File