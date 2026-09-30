// <reference types="@mapeditor/tiled-api" />    // NOTE: dunno what it's for...
/*
Tiled Plugin for merging all the selected objects one polygon (convex hull)
Shortcut : [Ctrl] + [B]
 */
/**
 * @param thing {TileMap | GroupLayer}
 * @param name {string}
 */
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+B";
const action_fn_name   = "PluginMergePolygons";
const action_text      = "Plugin - Merge Polygons Into One";
const print_prefix_msg = "[Plugin - Merge Polygons]\n\n";

// Features
const name_layer_bu = "_collisions backup";

// Feature Toggles
const config_keep_bu   = false; // Create backup layer; Move processed objects to the backup layer

const config_highlight =  true;       // Highlight the types of output objects if criteria met
const max_vertices_allowed = 8;       // If the output polygon has more than (8) vertices, highlight it red
let   is_property_mismatched = false; // If the input objects have properties not shared by ALL other objects, highlight yellow
let   saved_properties = null;        // Dictionary of the properties saved, to be added to the output object
let    num_property = 0;              // Only remember ths initially assigned value, since there will always be mismatched if number changes



// Debug Messages
const config_show_msg_end  = false; // For showing the program concludes successfully
const config_print_convex  = false; // Shows the coordinates of the convex hull created





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

let PluginAction = tiled.registerAction(action_fn_name, function(/* action */) {
	/** @type TileMap */
	// Prints out an error message and exit
	const map = tiled.activeAsset;
	if (!map.isTileMap) { _print("ERROR\nNot a tile map!"); return; }
	const list_objects = map.selectedObjects;
	if (list_objects == null) { _print("ERROR\nNo object selected!"); return; }


	// Merge the selected polygons into 1 convex hull
	_MergePolygonsIntoOne(map, map.selectedObjects);


	if(config_show_msg_end) _print("End of Procedure!");
});





//-----------------------------------------------------------//
//-------------------- [Logic Functions] --------------------//

function _MergePolygonsIntoOne( map, list_object ){
	// Add vertices from objects to the array
	let list_vertices = [];
	let count = 0;
	for( const obj of list_object ){
		count += 1;
		let curr_vertices = _GetVertices(obj);
		for( const pt of curr_vertices ) list_vertices.push(pt);
		_CheckPropertyMismatched(obj);
	}
//	_PrintDictionary(saved_properties);
	let convex_hull = getConvexHull(list_vertices);

	// Create object in current layer
	let new_object = _VerticesToPolygon(convex_hull);
	new_object.setProperties(saved_properties);
	let curr_layer = list_object[0].layer;
	if (!(curr_layer && curr_layer.isObjectLayer)) {
		_print("ERROR\nObject layer not selected!");
		return;
	}

	// The only modifying-actions in the plugin
	map.macro(action_text, function() {
		curr_layer.addObject(new_object);
		target_layer = _GetObjectLayerByName(name_layer_bu, config_keep_bu);
		for(let i = list_object.length-1; i >= 0; --i) {
			obj = list_object[i];
			obj.layer.removeObject(obj);
			if(config_keep_bu) target_layer.addObject(obj);
		}
		if(config_highlight) {
			too_many_vertices = convex_hull.length > max_vertices_allowed;
			if(too_many_vertices)                           new_object.type = "1";
			if(is_property_mismatched)                      new_object.type = "2";
			if(too_many_vertices && is_property_mismatched) new_object.type = "3";
		}
	});

	// Print message if needed
	if(!config_print_convex) return;
	let print_msg  = `Merged ${list_object.length} polygons into ${count}`;
	print_msg += `\n${list_vertices.length} -> ${convex_hull.length}`;
	print_msg += "\n"; for( const pt of convex_hull ) print_msg += `\n(${pt["x"]}, ${pt["y"]})`;
	_print(print_msg);
}



//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//

function _CheckPropertyMismatched(object){
	// Save the first properties found
	let list_properties = object.properties();
	if(list_properties == null) list_properties = {};
	if(saved_properties == null){
		saved_properties = list_properties;
		num_property = _GetDictLength(saved_properties);
		return;
	}

	// If length is not equal, either current property is missing in the saved, or the other way around
	// If current property is not saved, add it to dictionary
	// If only value is mismatched, just change the boolean
	if( num_property != _GetDictLength(list_properties) ){ is_property_mismatched = true; }
	for(let key in list_properties){
		if(saved_properties[key] == list_properties[key]) continue;
		saved_properties[key] = list_properties[key];
		is_property_mismatched = true;
	}
}



function _VerticesToPolygon(list_vertices){
	// Returns either a polygon, or rectangle if possible
	// Input is the list of vertices, which should already be a convex hull

	// Return rectangle if criteria met
	let is_rectangle = isValidAxisAlignedRectangle(list_vertices);
	if(is_rectangle){
		const xCoords = list_vertices.map(v => v.x);
		const yCoords = list_vertices.map(v => v.y);
		const minX = Math.min(...xCoords);
		const maxX = Math.max(...xCoords);
		const minY = Math.min(...yCoords);
		const maxY = Math.max(...yCoords);
		const width = maxX - minX;
		const height = maxY - minY;

		let new_object = new MapObject(MapObject.Rectangle);
		new_object.x      = minX;
		new_object.y      = minY;
		new_object.width  = width;
		new_object.height = height;
		return new_object;
	}

	// If not a rectangle, return a polygon
	let new_object = new MapObject(MapObject.Polygon);
	new_object.polygon = list_vertices;
	return new_object;
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
	return list_vertices;
}





//----------------------------------------------------------//
//-------------------- [Math Functions] --------------------//

function crossProduct(o, a, b) {
	return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}
function getConvexHull(points) {
	if (points.length <= 3) return points;

	// Sort points lexicographically (by x, then by y)
	const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y);

	// Build lower hull
	const lower = [];
	for (const p of sorted) {
		while (lower.length >= 2 && crossProduct(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
			lower.pop();
		}
		lower.push(p);
	}

	// Build upper hull
	const upper = [];
	for (let i = sorted.length - 1; i >= 0; i--) {
		const p = sorted[i];
		while (upper.length >= 2 && crossProduct(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
			upper.pop();
		}
		upper.push(p);
	}

	// Last point of each half is repeated at the start of the other
	lower.pop();
	upper.pop();
	
	return lower.concat(upper);
}



function isValidAxisAlignedRectangle(points) {
	// 1. A rectangle must have exactly 4 vertices
	if (!points || points.length !== 4) return false;

	const xCoords = new Set();
	const yCoords = new Set();

	for (const point of points) {
		xCoords.add(point.x);
		yCoords.add(point.y);
	}

	// 2. An unrotated rectangle will have exactly 2 unique X values and 2 unique Y values
	if (xCoords.size !== 2 || yCoords.size !== 2) return false;

	// 3. Optional: Verify that the rectangle has a non-zero area (not flattened into a line)
	const [x1, x2] = Array.from(xCoords);
	const [y1, y2] = Array.from(yCoords);
	
	return Math.abs(x1 - x2) > 0 && Math.abs(y1 - y2) > 0;
}





//-----------------------------------------------------------//
//-------------------- [General Utility] --------------------//

function _print(print_msg){
	tiled.alert(`${print_prefix_msg}${print_msg}`);
}

function _GetDictLength(dictionary){ return Object.keys(dictionary).length; }
function _PrintDictionary(dictionary){
	if(dictionary == null) return;
	let print_msg = "";
	for( let key in dictionary ) print_msg += `${key} : ${dictionary[key]}\n`;
	_print(print_msg);
}

function _GetObjectLayerByName(name, create_new = true){
	const map = tiled.activeAsset;
	let target_layer = null;
	for (let i = 0; i < map.layerCount; ++i) {
		const layer = map.layerAt(i);
		if(layer.name != name) continue;
		target_layer = layer;
		break
	}
	if(target_layer == null && create_new){
		target_layer = new ObjectGroup(name);
		target_layer.visible = false;
		map.addLayer(target_layer);
	}
	return target_layer;
}
function _MoveObjectToLayer(obj, layer){
	obj.layer.removeObject(obj);
	target_layer.addObject(obj);
}





//-----------------------------------------------------//
//-------------------- [Meta Data] --------------------//

PluginAction.text     = action_text;
PluginAction.shortcut = action_shortcut;
tiled.extendMenu("Map", [
	{ separator: true },
	{ action: action_fn_name },
]);

//--------------------------------------------------//










// End of File