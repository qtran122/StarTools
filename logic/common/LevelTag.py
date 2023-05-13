'''
	Object class for converting XML into intermediate structure
	This will then be converted into LevelDough afterwards
'''

from logic.common import utils_file
from logic.common import utils_level_reader

# pylint: disable
# pylint: disable = W0312
# pylint: disable = W0105
'''
W0312  Mixed indentation
W0105  Comment blocks

'''

 # Default settings for debugging
DEBUG_ = False


#--------------------------------------------------#

class LevelTag:
	'''Object Class for storing the data of each tag'''
	def __init__(self, tag_name, prop_list, hierarchy):
		self.tag_name = tag_name
		self.prop_list = prop_list
		self.ChildTag = []
		self.ParentTag = None
		self.hierarchy = hierarchy

	def add_child(self, child_tag):
		'''Link the child tag to self'''
		self.ChildTag.append(child_tag)
		child_tag.ParentTag = self



	'''Access functions'''
	def get_value_of(self, tag_name, property_name):
		'''Return non-empty value only if tag is matching AND contains property'''
		if self.tag_name != tag_name:
			return ""
		property_value = ""
		for prop in self.prop_list:
#			print(prop)
			if prop[0] == property_name:
				property_value = prop[1]
				break
		return property_value



	'''Printing'''
	def print(self):
		'''Print individual tag for debugging'''
		tag_str = f"  {self.tag_name} \t"
		for prop in self.prop_list:
			tag_str += f"    [{prop[0]}:{prop[1]}]"
		print(tag_str)

		# Recursive
		for child in self.ChildTag:
			child.print()

	def print_str(self):
		'''Print individual tag for XML'''
		tag_str = " " * self.hierarchy
		if self.tag_name == utils_level_reader.TILELAYER_TAG:
			tag_str += self.prop_list[0][1]
		else:
			tag_str += f"<{self.tag_name}"
			for prop in self.prop_list:
				tag_str += f" {prop[0]}=\"{prop[1]}\""
			tag_str += ">"
		print(tag_str)

		# Recursive
		for child in self.ChildTag:
			child.print_str()











#--------------------------------------------------#










# End of file
