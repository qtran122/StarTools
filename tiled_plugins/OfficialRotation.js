// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for rotating objects to fixed intervals, rotated about vertices mid-point
Shortcut : [Ctrl] + [Shift] + [R] - Clockwise
Shortcut : [Ctrl] + [Shift] + [E] - Counter Clockwise
*/
(function() {
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
const config_print_msg_end  =  false; // Shows the program concludes successfully
const config_print_index    =  false; // Shows the change in index & angle
const config_print_vertices =  false; // Shows all vertices of a rotated object

// Variables
const config_rectangle_only = true;
let count_non_rectangle = 0; // Print message at the end if a polygon is detected trying to be rotated





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

const PluginAction1 = tiled.registerAction(action_fn_name, function(/* action */) {
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

	// Perform the Main Action;
	//  Wraping is done in the function this time
	//  Same function, but rotated in a different direction
	count_non_rectangle = 0;
	_RotateSelectedPolygons(map, list_objects, direction);

	if(config_rectangle_only && count_non_rectangle > 0) {
		let print_msg = "";
		print_msg += `${count_non_rectangle} polygons selected.\n`;
		print_msg += "Official Rotations are only supported for rectangular objects.\n";
		print_msg += "\n";
		print_msg += "No rotation was applied to them.\n";		
		_print(print_msg);
	}
	if(config_print_msg_end) _print("End of Procedure!");
}





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function _RotateSelectedPolygons(map, list_objects, rotate_direction){
	let new_action_text = action_text;
	if(!rotate_direction) new_action_text = action_text2;
	map.macro(new_action_text, function() {
		for( const obj of list_objects ) {
			if(config_rectangle_only && obj.shape != MapObject.Rectangle){
				count_non_rectangle += 1;
				continue;
			}
			_RotatePolygon(obj, rotate_direction);
		}
	});
}



//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//

function _RotatePolygon(obj, rotate_direction){
	// Get index of next angle in the array
	const next_index = _GetNextIndex(obj, rotate_direction);

	// Get angle value from array, then apply rotation with offsets
	const curr_angle = obj.rotation;
	const next_angle = allowed_angles[next_index];
	RotateAboutMidPoint(obj, next_angle, config_print_vertices);

	// Print message
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `Next Index : ${next_index}\n`;
	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
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





//-----------------------------------------------------------//
//-------------------- [General Utility] --------------------//

function _print(print_msg){ PrintUniversal(print_msg, print_prefix_msg); }





//-----------------------------------------------------//
//-------------------- [Meta Data] --------------------//

PluginAction1.text     = action_text;
PluginAction1.shortcut = action_shortcut;
tiled.extendMenu("Map", [
	{ separator: true },
	{ action: action_fn_name },
]);

PluginAction2.text     = action_text2;
PluginAction2.shortcut = action_shortcut2;
tiled.extendMenu("Map", [
//	{ separator: true },
	{ action: action_fn_name2 },
]);

//--------------------------------------------------//










})();
// End of File