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
const config_show_msg_end  = false; // Shows the program concludes successfully
const config_print_index   = false; // Shows the change in index & angle





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
	const curr_index = _GetCurrentIndex(obj);
	let index_change = 1;
	if(rotate_direction) index_change = -1;
	const next_index = (curr_index - index_change + allowed_angles.length) % allowed_angles.length;

	// Set angle to next index's value
	const curr_angle = obj.rotation;
	const next_angle = allowed_angles[next_index];
	obj.rotation = next_angle;

	// Print
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `${curr_index} -> ${next_index}\n`;
	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
}

function _GetCurrentIndex(object){
	const curr_angle = object.rotation;
	let next_index = -1;
	for( let i = 0; i < allowed_angles.length; ++i ){
		if(curr_angle > allowed_angles[i]) continue;
		next_index = i;
		break;
	}
	if(next_index < 0) return 0;
	return next_index;
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