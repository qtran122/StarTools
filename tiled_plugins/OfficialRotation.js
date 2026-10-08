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
const config_show_msg_end   =  false; // Shows the program concludes successfully
const config_print_index    =  false; // Shows the change in index & angle
const config_print_vertices =  false; // Shows all vertices of a rotated object





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
//	obj.rotation = next_angle;

	// Offset position based on mid-point coordinations
	const angle_diff = next_angle - curr_angle;
	_RotateWithOffset(obj, next_angle, angle_diff);

	// Print
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `${0} -> ${next_index}\n`;
	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
}

function _RotateWithOffset(obj, next_angle, angle_diff){
	const curr_vertices = _GetVertices(obj); // For printing only
	const start_pos = {x:obj.x, y:obj.y};
	const mid_pos = _GetMidPosition(obj);
	const new_pos = _RotateAbout(mid_pos, start_pos, angle_diff);
	const offset_x = mid_pos.x - new_pos.x;
	const offset_y = mid_pos.y - new_pos.y;

	// Apply changes
	obj.rotation = next_angle;
	obj.x += offset_x;
	obj.y += offset_y;

	if(!config_print_vertices) return;
	let print_msg = "";
	for( const vertex of curr_vertices ) print_msg += `(${_round(vertex.x)}, ${_round(vertex.y)})\n`;
	print_msg += `\n(${_round(mid_pos.x)}, ${_round(mid_pos.y)})`;
	print_msg += `\n\n${angle_diff} -> (${_round(new_pos.x)}, ${_round(new_pos.y)})`;
	const temp_mid = _GetMidPosition(obj);
	print_msg += `\nTemp Mid : (${_round(temp_mid.x)}, ${_round(temp_mid.y)})`;
	print_msg += `\nOffsets : ${_round(offset_x)}, ${_round(offset_y)}`;
	_print(print_msg)
}



function _GetMidPosition(obj){
	const curr_vertices = _GetVertices(obj);
	let mid_x = 0;
	let mid_y = 0;
	let count = 0;
	for( const pt of curr_vertices ) {
		mid_x += pt.x;
		mid_y += pt.y;
		count += 1;
	}
	if(count == 0) return {x:0, y:0};

	mid_x /= count;
	mid_y /= count;
	mid_x = _round(mid_x);
	mid_y = _round(mid_y);

	if(config_print_vertices) {
		let print_msg = "";
		for( const vertex of curr_vertices ) print_msg += `(${vertex.x}, ${vertex.y})\n`;
		print_msg += `\n${count} : (${mid_x}, ${mid_y})`;
		_print(print_msg)
	}
	return {x:mid_x, y:mid_y};
}

function _GetVertices(obj){
	// Return a list of vertices
	// TODO it crashes the Tiled app now, am contemplating whether I should spend time fixing it
	let list_vertices = [];
	let points = [];
	if(obj.shape === MapObject.Polygon) {
		const points = obj.polygon;
		for( const pt of points ){
			const x_pos = obj.x + pt.x;
			const y_pos = obj.y + pt.y;
			list_vertices.push( {x: x_pos, y: y_pos} );
		}
	}
	if(obj.shape === MapObject.Rectangle) {
		const x = obj.x;
		const y = obj.y;
		const w = obj.width;
		const h = obj.height;
		list_vertices.push( {x: x  , y: y  } );
		list_vertices.push( {x: x+w, y: y  } );
		list_vertices.push( {x: x  , y: y+h} );
		list_vertices.push( {x: x+w, y: y+h} );
	}

	// Account for rotation in the object itself
	const curr_angle = obj.rotation;
	if(curr_angle != 0){
		const pivot_pos = { x:list_vertices[0].x, y:list_vertices[0].y };
		for( let i = 1; i < list_vertices.length; ++i ){
			list_vertices[i] = _RotateAbout(list_vertices[i], pivot_pos, curr_angle);
		}
	}

	return list_vertices;
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

function _RotateAbout(point_pos, pivot_pos, angle_diff, do_rounding = false){
	const new_mid_pos = rotatePoint(pivot_pos.x, pivot_pos.y, point_pos.x, point_pos.y, angle_diff, do_rounding);
	return new_mid_pos;
}
function rotatePoint(cx, cy, x, y, angle, do_rounding = false) {
    // 1. Convert angle from degrees to radians
    const radians = (Math.PI / 180) * angle;
    const cos = Math.cos(radians);
    const sin = Math.sin(radians);

    // 2. Translate point back to origin (relative to pivot)
    const nx = x - cx;
    const ny = y - cy;
	let new_x = (nx * cos - ny * sin) + cx;
	let new_y = (nx * sin + ny * cos) + cy;
	if(do_rounding){ new_x = _round(new_x); new_y = _round(new_y); }

	// 3. Apply rotation and translate back to the pivot
    return { x: new_x, y: new_y };
}





//-----------------------------------------------------------//
//-------------------- [General Utility] --------------------//

function _print(print_msg){
	tiled.alert(`${print_prefix_msg}${print_msg}`);
}

function _round(num, digit = 3){ return Number(num.toFixed(digit)); }





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