// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin utility functions, automatically included into all other JS files.
 */
/**
 * @param thing {TileMap | GroupLayer}
 * @param name {string}
 */
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//





//----------------------------------------------------------------//
//-------------------- [JavaScript Functions] --------------------//

function _round(num, digit = 3){ return Number(num.toFixed(digit)); }

function GetDictLength(dictionary){ return Object.keys(dictionary).length; }



//-----------------------------------------------------------//
//-------------------- [Tiled Functions] --------------------//

function PrintUniversal(print_msg, prefix = "[Plugin - Utility]\n\n"){ tiled.alert(`${prefix}${print_msg}`); }
function _print(print_msg){ PrintUniversal(print_msg); }

function PrintDictionary(dictionary){
	if(dictionary == null) return;
	let print_msg = "";
	for( let key in dictionary ) print_msg += `${key} : ${dictionary[key]}\n`;
//	_print(print_msg);
	PrintUniversal(print_msg);
}



//------------------------------------------------------------//
//-------------------- [Object Functions] --------------------//

function MoveObjectToLayer(obj, target_layer){
	obj.layer.removeObject(obj);
	target_layer.addObject(obj);
}



//-----------------------------------------------------------//
//-------------------- [Layer Functions] --------------------//

function GetObjectLayerByName(name, create_new = true){
	const map = tiled.activeAsset;
	let target_layer = null;
	for (let i = 0; i < map.layerCount; ++i) {
		const layer = map.layerAt(i);
		if(!layer.isObjectLayer) continue;
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

function GetTileLayerByName(name, create_new = true, set_visible = true){
	const map = tiled.activeAsset;
	let target_layer = null;
	for (let i = 0; i < map.layerCount; ++i) {
		const layer = map.layerAt(i);
		if(!layer.isTileLayer) continue;
		if(layer.name != name) continue;
		target_layer = layer;
		break
	}
	if(target_layer == null && create_new){
		target_layer = new TileLayer(name);
		if(!set_visible) target_layer.visible = false;
		map.addLayer(target_layer);
	}
	return target_layer;
}




//-------------------------------------------------------------//
//-------------------- [Polygon Functions] --------------------//

function GetVertices(obj){
	// Return a list of vertices
	//  Dictionary format: [ {x:x1, y:y1}, {x:x2, y:y2}, {x:x3, y:y3}, ...]
	//  Array      format: [ [x1,y1], [x2,y2], [x3,y3], ...]
	let list_vertices = [];
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

	return list_vertices;
}

function GetMidPosition(obj, do_print = false){
	const curr_vertices = GetVertices(obj);
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

	if(do_print) {
		let print_msg = "";
		for( const vertex of curr_vertices ) print_msg += `(${vertex.x}, ${vertex.y})\n`;
		print_msg += `\n${count} : (${mid_x}, ${mid_y})`;
//		_print(print_msg);
		PrintUniversal(print_msg);
	}
	return {x:mid_x, y:mid_y};
}

function RotateAboutMidPoint(obj, next_angle, do_print = false){
	const angle_diff = next_angle - obj.rotation; 
	const curr_vertices = GetVertices(obj); // For printing only
	const start_pos = {x:obj.x, y:obj.y};
	const mid_pos = GetMidPosition(obj, do_print);
	const new_pos = RotateAbout(mid_pos, start_pos, angle_diff);
	const offset_x = mid_pos.x - new_pos.x;
	const offset_y = mid_pos.y - new_pos.y;

	// Apply changes
	obj.rotation = next_angle;
	obj.x += offset_x;
	obj.y += offset_y;

	if(!do_print) return;
	let print_msg = "";
	for( const vertex of curr_vertices ) print_msg += `(${_round(vertex.x)}, ${_round(vertex.y)})\n`;
	print_msg += `\n(${_round(mid_pos.x)}, ${_round(mid_pos.y)})`;
	print_msg += `\n\n${angle_diff} -> (${_round(new_pos.x)}, ${_round(new_pos.y)})`;
	const temp_mid = GetMidPosition(obj, do_print);
	print_msg += `\nTemp Mid : (${_round(temp_mid.x)}, ${_round(temp_mid.y)})`;
	print_msg += `\nOffsets : ${_round(offset_x)}, ${_round(offset_y)}`;
//	_print(print_msg);
	PrintUniversal(print_msg);
}

function RotateAbout(point_pos, pivot_pos, angle_diff, do_rounding = false){
	// Wraping function from the AI code
//	return rotatePoint(pivot_pos.x, pivot_pos.y, point_pos.x, point_pos.y, angle_diff, do_rounding);
	const new_mid_pos = _rotatePoint(pivot_pos.x, pivot_pos.y, point_pos.x, point_pos.y, angle_diff, do_rounding);
	return new_mid_pos;
}
function _rotatePoint(cx, cy, x, y, angle, do_rounding = false) {
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






function VerticesToPolygon(list_vertices){
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







//--------------------------------------------------//










// End of File