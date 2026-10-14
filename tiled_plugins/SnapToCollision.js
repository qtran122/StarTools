// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for <TBA>
Shortcut : [Ctrl] + [F] <TBA>
 */
/**
 * @param thing {TileMap | GroupLayer}
 * @param name {string}
 */
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+F";
const action_fn_name   = "PluginSnapToCollision";
const action_text      = "Plugin - Snap Object To Nearest Collision";
const print_prefix_msg = "[Plugin - Snap To Collision]\n\n";

// Features
const allowed_angles = [ 0, 14.036, 26.565, 45, 63.435, 75.964, 90, 104.036, 116.565, 135, 153.435, 165.964, 180, 194.036, 206.565, 225, 243.435, 255.964, 270, 284.036, 296.565, 315, 333.435, 345.964 ];
const name_layer_bu = "_collisions backup";
const name_layer_collision = ["collisions"];
const name_layer_pearl     = ["objects_pearl"];

// Feature Toggles
const config_keep_bu  = false; // Create backup layer; Move processed objects to the backup layer

// Debug Messages
const config_show_msg_end =  false; // For showing the program concludes successfully
const config_print_index  =  false; // Shows the coordinates of the convex hull created





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

const PluginAction = tiled.registerAction(action_fn_name, function(/* action */) {
	/** @type TileMap */
	// Prints out an error message and exit
	const map = tiled.activeAsset;
	if (!map.isTileMap) { _print("ERROR\nNot a tile map!"); return; }

	// If no objects selected, add all objects from the layers with matching names
	let list_objects = map.selectedObjects;
	if( !(list_objects && list_objects.length > 0) ) {		
		list_objects = [];
		for( const name of name_layer_pearl ){
			const layer_pearls = GetObjectLayerByName(name, false)
			for (const obj of layer_pearls.objects) list_objects.push(obj);
		}
	}

	// Perform the Main Action
	map.macro(action_text, function() {
		SnapObjectsToNearestCollision(map, list_objects);
	});

	if(config_show_msg_end) _print("End of Procedure!");
});





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function SnapObjectsToNearestCollision(map, list_objects){
	// Change the positions and rotations of all the selected obejcts
	// Snap them to the nearest collision objects

	// Recognise all the collision objects
	let list_collisions = [];
	for( const name of name_layer_collision ){
		const layer_collision = GetObjectLayerByName(name, false)
		for (const obj of layer_collision.objects) {
			list_collisions.push(obj);
		}
	}
	let list_polygon_vertices = [];
	for( const obj of list_collisions ){
		list_polygon_vertices.push( _GetVertices(obj, false) );
	}

	// TODO do more than 1 object
	// Find nearest collision polygon to the selected objects
	let pos_snap = [];
	for( const obj of list_objects ){
//		obj.type = "1";
//		break;

		const mid_pos    = _DictToArray(_GetMidPosition(obj));
		const offset_pos = [obj.x - mid_pos[0], obj.y - mid_pos[1]];
		const set_closest = findClosestPolygon(mid_pos, list_polygon_vertices);

		let print_msg = "";
		print_msg += `Mid : (${mid_pos[0]}, ${mid_pos[1]})\n`;
		print_msg += `Cloest : ${set_closest.ID}\n`;
		print_msg += `Snap Pos : (${set_closest.pt[0]}, ${set_closest.pt[1]})\n`;
//		_print(print_msg)
//		_print(mid_pos);


		obj.x = set_closest.pt[0] + offset_pos[0];
		obj.y = set_closest.pt[1] + offset_pos[1];
//		obj.type = "0";
//		break;
	}

	// Snap object to the nearest
	

	// --- Example Usage ---
	const targetPoint = [5, 5];
	const polygonA = [[0, 0], [0, 4], [4, 4], [4, 0]]; // Square
	const polygonB = [[10, 10], [10, 12], [12, 12]];    // Triangle

	const allPolygons = [polygonA, polygonB];
//	findClosestPolygon(targetPoint, allPolygons);

//	for( const pt of polygonB ) _print(pt);
//	for( const pt of list_polygon_vertices[0] ) _print(pt);

	// Print
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `Pearls : ${list_objects.length}\n`;
//	print_msg += `Collisions : ${list_collisions.length}\n`;
	print_msg += `Collisions : ${list_polygon_vertices.length}\n`;
//	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
}

function _DictToArray(pos){
	// For converting position data, from Dictionary format to Array format
	return [pos.x, pos.y];
}




//----------------------------------------------------------//
//-------------------- [Testing Ground] --------------------//

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







//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//




function _GetVertices(obj, dictionary_format = true){
	// Return a list of vertices
	//  Dictionary format: [ {x:x1, y:y1}, {x:x2, y:y2}, {x:x3, y:y3}, ...]
	//  Array      format: [ [x1,y1], [x2,y2], [x3,y3], ...]
	let list_vertices = [];
	let points = []; // TODO unneeded?
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
			list_vertices[i] = RotateAbout(list_vertices[i], pivot_pos, curr_angle);
		}
	}

	// Return in the correct format
	if(dictionary_format) return list_vertices;
	let new_list = []
	for( const vertex of list_vertices ){
		new_list.push( [vertex.x, vertex.y] );
	}
	return new_list;
}





//----------------------------------------------------------//
//-------------------- [Math Functions] --------------------//

// 1. Helper to find the closest point on a single line segment to a point
function getClosestPointOnSegment(p, s1, s2) {
    const ab = [s2[0] - s1[0], s2[1] - s1[1]];
    const ap = [p[0] - s1[0], p[1] - s1[1]];
    
    // Calculate projection factor t, clamped between 0 and 1
    const abLenSq = ab[0] * ab[0] + ab[1] * ab[1];
    if (abLenSq === 0) return s1; // Segment is a point
    
    let t = (ap[0] * ab[0] + ap[1] * ab[1]) / abLenSq;
    t = Math.max(0, Math.min(1, t)); 
    
    // Return the closest coordinates on the segment
    return [s1[0] + t * ab[0], s1[1] + t * ab[1]];
}

// 2. Helper to get the minimum squared distance between a point and a polygon
function getSqDistanceToPolygon(point, polygon) {
    let minSqDist = Infinity;
    let minPoint = [];
//	_print("Polygon Edges : " + polygon.length);
    for (let i = 0; i < polygon.length; i++) {
        const s1 = polygon[i];
        const s2 = polygon[(i + 1) % polygon.length]; // Connects last vertex to first
        
        const closestPoint = getClosestPointOnSegment(point, s1, s2);
        
        const dx = point[0] - closestPoint[0];
        const dy = point[1] - closestPoint[1];
        const sqDist = dx * dx + dy * dy;
//		_print(point + " vs " + closestPoint);

        if (minSqDist > sqDist) {
            minSqDist = sqDist;
			minPoint[0] = closestPoint[0];
			minPoint[1] = closestPoint[1];
        }
    }
//	return [minSqDist];
	return [minSqDist, minPoint];
}

// 3. Main function to find the closest polygon
function findClosestPolygon(point, polygons) {
    let closestPoly = null;
    let minDistance = Infinity;
	let count = 0;

    polygons.forEach((polygon, index) => {
		count += 1;
		const temp  = getSqDistanceToPolygon(point, polygon);
//		const sqDist = temp;
		const sqDist = temp[0];
		const closestPoint = temp[1];
		if (sqDist < minDistance) {
			minDistance = sqDist;
			closestPoly = { ID:index, poly:polygon, distance:Math.sqrt(sqDist), pt:closestPoint };
//			closestPoly = { ID:index, poly:polygon, distance:Math.sqrt(sqDist) };
//			closestPoly = { index, polygon, distance: Math.sqrt(sqDist) };
		}
    });
//	_print(count);

    return closestPoly;
}









//-----------------------------------------------------------//
//-------------------- [General Utility] --------------------//

function _print(print_msg){ PrintUniversal(print_msg, print_prefix_msg); }





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