'''
Logic module for cli_export_xl


USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_export_xl.py
	main_logic.logic(playdo)

'''
import logic.common.log_utils as log
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Font

#-----------------------------------------------------#
#-------------------- [Variables] --------------------#

# XML Configurations
layer_name = "BG"


# Spreadsheet Format
column_width = 30    # (in pixels) Width of each column in the spreadsheet

bg_hex     = "0076a3"    # dict_id_to_hex[411+1]
unused_hex = "000000"
dict_id_to_hex = {
	 16+1:"6858d0",
	 17+1:"b961e9",
	 18+1:"f8ca34",
	 19+1:"34d9c1",
	 20+1:"80c84f",
	 21+1:"5299f6",
	 22+1:"ef71cd",
	 23+1:"c78855",
	 24+1:"eb2a67",
	 25+1:"ff0000",

	154+1:"444444",
	155+1:"868686",
	156+1:"c4c4c4",
	157+1:"ffffff",
	158+1:"fefeff",
	159+1:"fdffff",

	283+1:"1b1464",
	284+1:"440e62",
	410+1:"00746b",
	411+1:"0076a3",
	412+1:"004a80",
	538+1:"8c6239",
	539+1:"362f2d",
	540+1:"7b0046",
}





#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def logic(playdo, filepath_output):
	'''
	 Reads the XML and output a XLSX spreadsheet in the designated filepath
	'''
	log.Must(f'  Reading the map data...')

	# Map data
	num_row = playdo.map_height
	num_col = playdo.map_width
	min_x = num_col+1
	min_y = num_row+1
	max_x = 0
	max_y = 0

	# Initialise the array
	empty_id = -1
	map_simple = [[empty_id for _ in range(num_col)] for _ in range(num_row)]

	# Check each cell in Tiled
	# The color data and max/min range is recorded, latter is shown as message
	tiles2d = playdo.GetTiles2d(layer_name)
	list_key = list(dict_id_to_hex.keys())
	for i in range(num_row):
		for j in range(num_col):
			if not tiles2d[i][j] in list_key: continue
			if min_x > j: min_x = j
			if min_y > i: min_y = i
			if max_x < j: max_x = j + 1
			if max_y < i: max_y = i + 1
			for key, value in dict_id_to_hex.items():
				if tiles2d[i][j] != key: continue
				map_simple[i][j]  = list_key.index(key)
	log.Must(f"   Map W: {num_col}, Map H: {num_row}")
	log.Must(f"    Min X: {min_x}, Min Y: {min_y}")
	log.Must(f"    Max X: {max_x}, Max Y: {max_y}")

	wb = openpyxl.Workbook()
	ws = wb.active

	# Create the new XLSX file with all the colors
#	ExportXlsx(ws, map_simple, filepath_output, min_x, min_y, max_x, max_y)
	ExportXlsx(ws, map_simple, min_x, min_y, max_x, max_y)
	AddFreezeLabel(ws, max_y - min_y) # Add a column & row to the left & top side respectively
	ResizeColumns(ws)                 # Resize all columns to smaller width

	# Save spreadsheet to filepath
	log.Must('')
	log.Must(f"  Exporting at : f{filepath_output}")
	log.Must(f"   Rows: {ws.max_row}, Columns: {ws.max_column}")
	wb.save(filepath_output)

	log.Must('')



#------------------------------------------------------------#
#-------------------- [Helper Functions] --------------------#

def AddFreezeLabel(ws, num_rows):

	ws.insert_cols(idx=1)
	ws.insert_rows(idx=1)

	# Top-row - Number & Syntax
	num = 0
	for col in ws.columns:
		column_letter = col[0].column_letter
		cell = ws[f"{column_letter}1"]
#		ws[f"{column_letter}1"] = num
		cell.value     = num
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")
		num += 1

	# Add number in left-column
	for i in range(num_rows+1):
		cell = ws[f"A{i+1}"]
		cell.value     = i
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")

	# Freeze first row and column
	ws.freeze_panes = "B2"


#def ExportXlsx(ws, map_simple, filepath_output, min_x, min_y, max_x, max_y):
def ExportXlsx(ws, map_simple, min_x, min_y, max_x, max_y):
	'''
	 This exports the XLSX based on the recorded coloring data
	'''
	# Creates an array for just the color hex values
	list_fill = []
	for key, value in dict_id_to_hex.items():
		list_fill.append( PatternFill(start_color = value, end_color = value, fill_type="solid") )
	list_fill.append( PatternFill(fill_type=None) )

	# Enter data to corresponding cells based on map data
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	for row in range(num_row):
		if row < min_y: continue
		for col in range(num_col):
			if col < min_x: continue
			if map_simple[row][col] < 0: continue
			new_x = col + 1 - min_x
			new_y = row + 1 - min_y
			fill_id = map_simple[row][col]
			ws.cell(row = new_y, column = new_x, value = " ").fill = list_fill[fill_id]

	# Set the default BG Color for the "unedited cells" and "out of bound cells"
	bg_fill    = PatternFill( start_color = bg_hex,     end_color = bg_hex,     fill_type="solid" )
	black_fill = PatternFill( start_color = unused_hex, end_color = unused_hex, fill_type="solid" )
	for row in ws.iter_rows(min_row = 1, max_row = max_y+1):
		for cell in row:
			if cell.fill.fill_type in (None, "none"): cell.fill = bg_fill
	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):	# NOTE Somehow this line crops sheet to 273 rows
#	for row in ws.iter_rows(min_row = max_y-min_y+1, max_row = max_y-min_y+1):
		for cell in row: cell.fill = black_fill
#	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):
#		for cell in row: cell.fill = black_fill



def PrintInConsole(map_simple, empty_id):
	'''
	 Prints the map data on console instead
	 For debugging, and in case want to switch over to the "copy-paste plain text" method
	'''
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	print_msg = ""
	for i in range(num_row):
		for j in range(num_col):
			if map_simple[i][j] == empty_id: print_msg += " "
#			else:                            print_msg += "x"
#			else:                            print_msg += map_simple[i][j][0]
#			else:                            print_msg += map_simple[i][j] // 10
			else:                            print_msg += f"{map_simple[i][j]}"
			print_msg += " "
		print_msg += "\n"
	log.Must(print_msg)

def ResizeColumns(ws):
	# Resize the column width so it's easier to fit into the screen
	for col in ws.columns:
		column_letter = col[0].column_letter
		ws.column_dimensions[column_letter].width = column_width / 7    # Function uses "character" as measurement, each ~7px




#------------------------------------------------------------#
#-------------------- [Unused Functions] --------------------#

def trim_empty_borders(ws):
    # 1. Find the minimum and maximum row/column indices containing actual data
    min_r, max_r = None, None
    min_c, max_c = None, None

    for r in range(1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            val = ws.cell(row=r, column=c).value
            # Check for None or whitespace-only strings
            if val is not None and str(val).strip() != "":
                if min_r is None or r < min_r:
                    min_r = r
                if max_r is None or r > max_r:
                    max_r = r
                if min_c is None or c < min_c:
                    min_c = c
                if max_c is None or c > max_c:
                    max_c = c

    # If the entire sheet is empty, clear all rows
    if min_r is None:
        ws.delete_rows(1, ws.max_row)
        return

    # 2. Delete bottom empty rows (delete from end first to avoid index shifts)
    if max_r < ws.max_row:
        ws.delete_rows(idx=max_r + 1, amount=ws.max_row - max_r)

    # 3. Delete top empty rows
    if min_r > 1:
        ws.delete_rows(idx=1, amount=min_r - 1)

    # 4. Delete right empty columns
    if max_c < ws.max_column:
        ws.delete_cols(idx=max_c + 1, amount=ws.max_column - max_c)

    # 5. Delete left empty columns
    if min_c > 1:
        ws.delete_cols(idx=1, amount=min_c - 1)





def delete_at_up_and_left(filepath):
	wb = openpyxl.load_workbook(filepath)
	ws = wb.active

	# 1. Find the first non-empty row (top)
	first_data_row = None
	for row in ws.iter_rows():
		if any(
			cell.value is not None and str(cell.value).strip() != "" for cell in row
		):
			first_data_row = row[0].row
			break

	# Delete all empty rows above the first data row
	if first_data_row and first_data_row > 1:
		ws.delete_rows(1, first_data_row - 1)

	# 2. Find the first non-empty column (left)
	first_data_col = None
	for col in ws.iter_cols():
		if any(
			cell.value is not None and str(cell.value).strip() != "" for cell in col
		):
			first_data_col = col[0].column
			break

	# Delete all empty columns to the left of the first data column
	if first_data_col and first_data_col > 1:
		ws.delete_cols(1, first_data_col - 1)

	wb.save(filepath)





#--------------------------------------------------#










# End of File