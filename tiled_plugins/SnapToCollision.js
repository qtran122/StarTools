// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for <TBA>
Shortcut : [Ctrl] + [F]
 */
(function() {
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+F";
const action_fn_name   = "PluginSnapToCollision";
const action_text      = "Plugin - Snap Object To Nearest Collision";
const print_prefix_msg = "[Plugin - Snap To Collision]\n\n";

// Features
const name_layer_collision = ["collisions"];
const name_layer_pearl     = ["objects_pearl", "objects_pearls"];

// Feature Toggles

// Debug Messages
const config_print_msg_end =  false; // For showing the program concludes successfully
const config_print_index   =  false; // Shows 
const config_color_polygon =  false; // Change the target objects to red first, then green once procedure concludes





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
			if(layer_pearls == null) continue;
			for (const obj of layer_pearls.objects) list_objects.push(obj);
		}
	}

	// Perform the Main Action
	map.macro(action_text, function() {
		SnapObjectsToNearestCollision(list_objects);
	});

	if(config_print_msg_end) _print("End of Procedure!");
});





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function SnapObjectsToNearestCollision(list_objects){
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

	// Find nearest collision polygon to the selected objects
	for( const obj of list_objects ){
		if(config_color_polygon) obj.type = "1"; // Red

		const mid_pos      = GetMidPosition(obj);
		const closest_data = findClosestPolygon(mid_pos, list_collisions);
		const offset_pos   = {
			x : obj.x - mid_pos.x, 
			y : obj.y - mid_pos.y
		};

		obj.x = closest_data.pt_x + offset_pos.x;
		obj.y = closest_data.pt_y + offset_pos.y;
//		const new_angle   = 90;
		const new_angle   = closest_data.angle;
		const inclination = (90 + new_angle) * (Math.PI / 180);
		RotateAboutMidPoint(obj, new_angle);
		obj.x -= obj.width/2 * Math.cos(inclination);
		obj.y -= obj.width/2 * Math.sin(inclination);
		if(config_color_polygon) obj.type = "4"; // Green

		if(!config_print_index) continue;
		let print_msg = "";
		print_msg += `Mid : (${mid_pos[0]}, ${mid_pos[1]})\n`;
		print_msg += `Cloest ID : ${closest_data.ID}\n`;
		print_msg += `Snap Pos : (${_round(closest_data.pt_x,0)}, ${_round(closest_data.pt_y,0)})\n`;
		print_msg += `Angle : ${closest_data.angle}\n`;
		_print(print_msg);
		break;
	}

	// Print
	if(!config_print_index) return;
	let print_msg = "";
	print_msg += `Pearls : ${list_objects.length}\n`;
//	print_msg += `Collisions : ${list_collisions.length}\n`;
	print_msg += `Collisions : ${list_polygon_vertices.length}\n`;
//	print_msg += `${curr_angle}˚ -> ${next_angle}˚`;
	_print(print_msg)
}





//----------------------------------------------------------//
//-------------------- [Testing Ground] --------------------//





//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//





//----------------------------------------------------------//
//-------------------- [Math Functions] --------------------//

// 1. Helper to find the closest point on a single line segment to a point
function getClosestPointOnSegment(p, s1, s2, mid) {
    const ab = [s2.x - s1.x, s2.y - s1.y];
    const ap = [ p.x - s1.x,  p.y - s1.y];
    
    // Calculate projection factor t, clamped between 0 and 1
    const abLenSq = ab[0] * ab[0] + ab[1] * ab[1];
    if (abLenSq === 0) { _print("ERROR! Segment is a point"); return { x:s1.x, y:s1.y, angle:0}; }
    
    let t = (ap[0] * ab[0] + ap[1] * ab[1]) / abLenSq;
    t = Math.max(0, Math.min(1, t)); 
//	const contact_x = s1.x + t * ab[0];
//	const contact_y = s1.y + t * ab[1];
	const contact_pt = {x:s1.x + t * ab[0], y:s1.y + t * ab[1]};
	
	// Inclination angle
	let inclination_angle = 90;
	const dx = s2.x - s1.x;
	const dy = s2.y - s1.y;
	inclination_angle = Math.atan2(dy,dx) * (180 / Math.PI);
//	if(dx != 0) inclination_angle = Math.atan2(dy,dx) * (180 / Math.PI);
//	if(inclination_angle < 0) inclination_angle += 360;
//	_print(inclination_angle)

    // Return the closest coordinates on the segment
	return {
		x : contact_pt.x,
		y : contact_pt.y,
		angle : inclination_angle,
	};
}



// 2. Helper to get the minimum squared distance between a point and a polygon
function getSqDistanceToPolygon(point, obj) {
    let minSqDist = Infinity;
    let minPoint = [];
	let inclination_angle = 0;

	const vertices = GetVertices(obj);
	const mid_pos = GetMidPosition(obj);
	const is_clockwise = isClockwise(vertices);
    for (let i = 0; i < vertices.length; i++) {
		let next_id = i;
		if(!is_clockwise) next_id += 1;
		else              next_id -= 1;
		next_id = (next_id + vertices.length) % vertices.length; // Make sure can connect last vertex to first

        const s1 = vertices[i];
        const s2 = vertices[next_id];
        const closestPoint = getClosestPointOnSegment(point, s1, s2, mid_pos);
        
        const dx = point.x - closestPoint.x;
        const dy = point.y - closestPoint.y;
        const sqDist = dx * dx + dy * dy;

        if (minSqDist > sqDist) {
            minSqDist = sqDist;
			minPoint[0] = closestPoint.x;
			minPoint[1] = closestPoint.y;
			inclination_angle = closestPoint.angle;
        }
    }
	return {
		dist2: minSqDist,
		x_pos: minPoint[0],
		y_pos: minPoint[1],
		angle: inclination_angle,
	};
}
function isClockwise(vertices) {
    let sum = 0;
    for (let i = 0; i < vertices.length; i++) {
        const current = vertices[i];
        const next = vertices[(i + 1) % vertices.length]; // Loops back to the first vertex
        sum += (next.x - current.x) * (next.y + current.y);
    }
    return sum > 0;
}



// 3. Main function to find the closest polygon
function findClosestPolygon(point, list_polygon) {
    let closest_polygon_data = null;
    let minDistance = Infinity;
    list_polygon.forEach((polygon, index) => {
		const polygon_data = getSqDistanceToPolygon(point, polygon);
		const sqDist = polygon_data.dist2;
		if( minDistance > sqDist ){
			minDistance = sqDist;
			closest_polygon_data = {
				ID:index, poly:polygon, distance:Math.sqrt(sqDist), 
				pt_x  : polygon_data.x_pos,
				pt_y  : polygon_data.y_pos,
				angle : polygon_data.angle,
			};
		}
    });
    return closest_polygon_data;
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










})();
// End of File