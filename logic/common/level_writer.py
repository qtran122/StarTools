'''Utility class for processing and outputting an XML file'''

#import _common.__base as b
from logic.common import file_utils as b

# pylint: disable
# pylint: disable = W0312
# pylint: disable = W0105
'''
W0312  Mixed indentation
W0105  Comment blocks

'''

#==================================================#

'''User's Interface'''

def print_level(level_name, tag_list):
	'''Overwrite the directory with an XML level generated using the provided tag_list'''
	b._print(f"Overwriting file {level_name}...")
	result = extract_tag_str(tag_list)

	file_object = open(level_name, "w")
	file_object.write(result)
	file_object.close()



def extract_tag_str(tag_list):
	'''Process and concatenate the list of level data tags as a single string'''
#	b._print("")
	result = ""
	for num, tag in enumerate(tag_list):
		curr_tag_str = tag.get_string()
		if not (num == 0 or num == len(tag_list)-1):
			if tag.hierarchy >= tag_list[num+1].hierarchy:
				if not tag.is_end_tag():
					curr_tag_str = curr_tag_str[0:len(curr_tag_str)-1] + "/>"
			h_diff = tag.hierarchy - tag_list[num+1].hierarchy
#		b._print(curr_tag_str)
		result += f"{curr_tag_str}\n"
#	b._print(f"\n{result}")
#	b._print("")
	return result



def _get_space(space_char):
	'''Return the requested number of space char as string'''
	result = ""
	for num in range(space_char):
		result += " "
	return result



#==================================================#










# End of file
