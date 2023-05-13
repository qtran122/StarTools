'''
This file contains time-related utility functions:
 - Header & Ending functions, for indicating the time elapsed in a successful run
'''

'''Import'''
import time
from logic.common import utils_file

#--------------------------------------------------#

class Clock:
	def __init__(self):
		'''Template starting function'''
		self.start_time = time.time()
		print("")
		print("\tCommencing procedures...")
		utils_file.print_linebreak(0,1)

	def end_procedures(self):
		'''Template ending function'''
		time_passed = round((time.time() - self.start_time), 3)
		utils_file.print_linebreak(1,0)
		print(f"\t~End of All Procedures~ ({time_passed}s)")
		print("")
		print("")
		print("")



#--------------------------------------------------#










# End of File
