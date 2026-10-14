// <reference types="@mapeditor/tiled-api" />
/*
Tiled Plugin for cycling between different size of a grid cell in the XML.
Shortcut : [Ctrl] + [Shift] + [M]
 */
/**
 * @param thing {TileMap | GroupLayer}
 * @param name {string}
 */
//-----------------------------------------------------//
//-------------------- [Variables] --------------------//

// Meta Info
const action_shortcut  = "Ctrl+Shift+M";
const action_fn_name   = "PluginToggleMapSize";
const action_text      = "Plugin - Toggle Map Grid Size";
const print_prefix_msg = "[Plugin - Toggle Map Size]\n\n";

// Features
const allowed_grid_size = [
	[11,7],
	[12,8],
	[13,9],
]

// Debug Messages
const config_show_msg_end  =  false; // For showing the program concludes successfully
const config_print_grid    =  false; // Shows the altered grid size





//---------------------------------------------------------//
//-------------------- [Main Function] --------------------//

const PluginAction = tiled.registerAction(action_fn_name, function(/* action */) {
	/** @type TileMap */
	// Prints out an error message and exit
	const map = tiled.activeAsset;
	if (!map.isTileMap) { _print("ERROR\nNot a tile map!"); return; }
	const list_objects = map.selectedObjects;
	if (list_objects == null) { _print("ERROR\nNo object selected!"); return; }

	// Perform the Main Action
	map.macro(action_text, function() {
		_ToggleGridSize(map);
//		if(config_print_grid) _print(`Current Size : ${map.tileWidth} x ${map.tileHeight}`)
	});

	if(config_show_msg_end) _print("End of Procedure!");
});





//----------------------------------------------------------//
//-------------------- [Logic Function] --------------------//

function _ToggleGridSize(map){
	// TODO add comment
	const curr_width = map.tileWidth;

	// If is a 16x15 map, do nothing
	if( curr_width == 16 ) return;

	// Otherwise cycle through
	for( let i = 0; i < allowed_grid_size.length; ++i ){
		const grid = allowed_grid_size[i];
		if(curr_width == grid[0]){
			const next_index = (i + 1 + allowed_grid_size.length) % allowed_grid_size.length;
			const next_grid = allowed_grid_size[next_index];
			map.tileWidth  = next_grid[0];
			map.tileHeight = next_grid[1];

			if(!config_print_grid) return;
			let print_msg = "";
			print_msg += `From : ${grid[0]} x ${grid[1]}\n`;
			print_msg += `To : ${next_grid[0]} x ${next_grid[1]}\n`;
			print_msg += `Current Size : ${map.tileWidth} x ${map.tileHeight}\n`;
			_print(print_msg);

			return;
		}
	}

	// This should never happen
	_print("ERROR! Invalid Map Size!");
}





//----------------------------------------------------------//
//-------------------- [Testing Ground] --------------------//





//------------------------------------------------------------//
//-------------------- [Helper Functions] --------------------//



//----------------------------------------------------------//
//-------------------- [Math Functions] --------------------//




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

//--------------------------------------------------//










// End of File