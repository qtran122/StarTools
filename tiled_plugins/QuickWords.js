// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for adding the text into tilelayer, from the selected objects (whose names contain the text)
Shortcut : [Ctrl] + [Shift] + [W]

 - If a tilelayer is currently selected, draw on said tilelayer
 -- Otherwise, create a new tilelayer (see name_layer_output below)
 */
(function() {
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+Shift+W";
const action_fn_name   = "PluginQuickWords";
const action_text      = "Plugin - Draw Tiles from Named Objects";
const print_prefix_msg = "[Plugin - Quick Words]\n\n";

// Features
const name_layer_output = "_QuickWords"; // Name of the new layer created, only if no tilelayer is selected

// Variables
let dict_char_index = {};

// Debug Messages
const config_print_msg_end =  false; // For showing the program concludes successfully
const config_print_index   =  false; // Shows all characters in our tilesheet-index
const config_print_text    =  false; // Shows the starting position and text for each object

const error_msg = "Quick Words requires the follow:\n - an object (to transcribe)\n - a tile layer (to receive transcription)";





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

let PluginAction = tiled.registerAction(action_fn_name, function(/* action */) {
	/** @type TileMap */
	// Prints out an error message and exit
	const map = tiled.activeAsset;
	if (!map.isTileMap) { _print("ERROR\nNot a tile map!"); return; }
	const curr_layer = map.currentLayer;

	// If no object is selected, check if any object layers are selected as well
	let list_objects = map.selectedObjects;
	if (list_objects == null || list_objects.length == 0) {
		list_objects = [];
		map.selectedLayers.forEach(layer => {
			if( !layer.isObjectLayer ) return;
			for (const obj of layer.objects) if(obj.name != null && obj.name != "") list_objects.push(obj);
		});
	}
	if( list_objects.length == 0 ){
		let print_msg = "! ERROR !\n";
		print_msg += `No object with name has been selected.\n`;
		print_msg += "\n";
		print_msg += "Make sure you have either:\n";
		print_msg += " - Selected specific objects\n";
		print_msg += " - Selected the object layers that contain the text objects\n";
		_print(print_msg);
		return;
	}

	// Exit if either no layer or more than 1 layer are selected
	let output_layer = null;
	const selected_layers = map.selectedLayers.filter(layer => layer.isTileLayer);
	if( selected_layers.length < 1 ){
 		let print_msg = "! ERROR !\n";
		print_msg += `No tile layer has been selected.\n`;
		print_msg += "\n";
		print_msg += "You can select both the object layers and tile layer simultaneously by left-clicking them while holding [Shift]\n";
		_print(print_msg);
		return;
	}
	if( selected_layers.length > 1 ){
 		let print_msg = "! ERROR !\n";
		print_msg += `More than 1 tile layers have been selected.\n`;
		print_msg += "\n";
		print_msg += "This is not allowed because exactly 1 tile layer is needed to transcript texts, from objects onto tile layer.\n";
		_print(print_msg);
		return;
	}
	output_layer = selected_layers[0]; // Disable this line to auto-create a new output layer instead

	// Perform the Main Action
	map.macro(action_text, function() {
		_Logic_PluginQuickWords(list_objects, output_layer);
	});

	if(config_print_msg_end) _print("End of Procedure!");
});





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function _Logic_PluginQuickWords(list_objects, output_layer){
	// Get index of all character to tile ID
	_SetCharacterIndex();

	// Check attribute, write into tilelayer, delete object
//	const output_layer = GetTileLayerByName(name_layer_output);
	if( output_layer == null ) output_layer = GetTileLayerByName(name_layer_output);
	for( const obj of list_objects ) {
		// Object attributes
		const text = obj.name;
		const start_x = Math.round(obj.x      / 16);
		const start_y = Math.round(obj.y      / 16);
		const obj_w   = Math.round(obj.width  / 16);
		const obj_h   = Math.round(obj.height / 16); // Unused
		const end_x   = start_x + obj_w;
		const end_y   = start_y + obj_h;             // Unused
		
		// Write into tilelayer
		_SetText(output_layer, text, start_x, start_y, end_x);
		obj.layer.removeObject(obj);

		// Print info
		if(!config_print_text) continue;
		let print_msg = "";
		print_msg += `(${start_x},${start_y}) to `;
		print_msg += `(${end_x},${end_y})\n`;
		print_msg += `Text : ${text}`;
		_print(print_msg);
	}
}

function _SetText(layer, text, start_x, start_y, end_x){
	let layerEdit = layer.edit();
	let x = start_x;
	let y = start_y;
	for( const char of text ){
		// Skip char if not valid in our tilesheet
		if(!dict_char_index.hasOwnProperty(char)) continue;
		const current_id   = dict_char_index[char];
		if(char != ' ') layerEdit.setTile(x, y, tiled.activeAsset.tilesets[0].tile(current_id));

		// If exceeding width and is space char, move to next row
		x += 1;
		if( x >= end_x && char == ' ' ){
			x = start_x;
			y += 1;
		}
	}
	layerEdit.apply();
}





//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//

function _SetCharacterIndex(){
	// Sets the char-to-ID dictionary each tiem this plugin is executed
	let my_dict = {};

	// For porting code from Python
	const ord = (char) => char.charCodeAt(0);
	const chr = (code) => String.fromCharCode(code);

	// A~Z, big and small letters
	curr_id = 784
	for( let i = ord('a'); i <= ord('z'); ++i ){
		c = chr(i)           // Small letters
		my_dict[c] = curr_id
		c = chr(i-32)        // Capital letters
		my_dict[c] = curr_id
		curr_id += 1
		if (i%5 == 1) curr_id += 128-5
	}
	
	// Letters
	curr_id = 0
	for( let i = ord('1'); i <= ord('9'); ++i ){
		c = chr(i)
		my_dict[c] = curr_id
		curr_id += 1
	}
	my_dict['0'] = 9

	// Additional Punctuations
	my_dict[' '] = -1
	my_dict['?'] = 1425
	my_dict['/'] = 1426

	// Link it to the local variable
	dict_char_index = my_dict;
	if(config_print_index) PrintDictionary(dict_char_index);
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