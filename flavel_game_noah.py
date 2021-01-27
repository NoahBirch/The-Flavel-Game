from sys import exit
import re

inventory = []
current_location = []
mona_with_ball = False

class Location:
	"""Locations are places you can gold"""
	def __init__(self, modifier, call_name, stored_items, interactors, nearby_loc_text):
		self.modifier = modifier
		self.call_name = call_name
		self.stored_items = stored_items
		self.visits = 0
		self.interactors = interactors
		self.nearby_loc_text = nearby_loc_text

	def display_stored_items(self):
		for item in self.stored_items:
			item.see_me()

	def display_loc_interactors(self):
		for interactor in self.interactors:
			interactor.see_me()

	def go_to(self):
		print "\n",
		if self.visits == 0:
			print "You arrive %s %s for the first time." % (self.modifier, self.call_name.capitalize())
		elif self == current_location[-1]:
			print "You are still %s %s." % (self.modifier, self.call_name.capitalize())
		else:
			print "You arrive back %s %s." % (self.modifier, self.call_name.capitalize())
		
		self.visits += 1
		self.display_loc_interactors()
		self.display_stored_items()
		current_location.append(self)

class Item:
	"""Items are things you can TAKE into your inventory"""
	def __init__(self, call_name, intro_text, hidden, takeable, cant_take_text,):
		self.call_name = call_name
		self.intro_text = intro_text
		self.hidden = hidden
		self.takeable = takeable
		self.cant_take_text = cant_take_text

	def see_me(self):
		if self.hidden == False:
			print "%s" % (self.intro_text)
		else:
			pass

	def take_item(self):
		# first checks if valid item take is in current location or if hidden. (since both should return a "you dont see anywhere" error)
		if self not in current_location[-1].stored_items or self.hidden == True:
			print "You don't see a %s anywhere." % self.call_name
			get_input_until_valid()
		# Then checks if it is takeable, if it is it is added to inventory and removed from location
		elif self.takeable == True:
			print "You take the %s and toss it in your backpack to take with you." % self.call_name
			inventory.append(self)
			current_location[-1].stored_items.remove(self)
			self.uncover_if_valid()
			main_gameplay(current_location[-1])
		# if not it must be in location but not takeable
		else:
			print self.cant_take_text
			get_input_until_valid()

	def use_cases(self, interactor_obj):
		global mona_with_ball
		### This will only get called if there is a valid item use on interactor combo. These are the speicifc cases of those interactions.
		
		if self == key:
			print "You use the key to unlock the door to Sawyer's!"
			inventory.remove(self)
			outside_sawyers.call_name = "XSAWYERSX"
			inside_sawyers.call_name = "sawyer's"
			update_locations_hashmap()
			main_gameplay(inside_sawyers)

		# This next bit is a bit messy. First we check if you're giving the stick to mona.
		elif self == stick and interactor_obj == mona:
			print "Mona eyes the stick skeptically and clearly doesn't want such a grubby toy in her mouth."
			main_gameplay(current_location[-1])

		# Then we check if the stick is being given (we can assume from above its not to mona) and mona doesn't yet have ball
		elif self == stick and mona_with_ball == False:
			print "Mona growls and you get the sense she doesn't want goldie to have the stick.\nMaybe if Mona was distracted she wouldn't care as much..."
			main_gameplay(current_location[-1])

		# Then we know from above that mona must have the ball, so when stick is given to goldie she accepts it. 
		elif self == stick and interactor_obj == goldie_far:
			print "You take the stick out and goldie comes running to the gate and accepts it."
			inventory.remove(self)
			goldie_far.hidden = True
			goldie_close.hidden = False
			goldie_far.call_name = "XGOLDIEX"
			goldie_close.call_name = "goldie"
			update_interactor_hashmap()
			key.hidden = False
			key.takeable = True
			main_gameplay(current_location[-1])

		# anytime you use the ball on goldie mona gets mad.
		elif self == ball and interactor_obj == goldie_far:
			print "Mona growls at you and you get the sense she doesn't want you to give the ball to Goldie."
			get_input_until_valid()

		# anytime u use ball on mona she accepts.
		elif self == ball and interactor_obj == mona:
			print "Mona gladly accepts the ball!"
			inventory.remove(self)
			mona_with_ball = True
			mona.intro_text = "Mona is leashed by your side, furiously chewing on her ball."
			main_gameplay(current_location[-1])

		else: 
			get_input_until_valid()

	def uncover_if_valid(self):
		if self.call_name == "trash can":
			ball.hidden = False
		elif self.call_name == "sign":
			stick.hidden = False
		else:
			pass

class Interactor:
	"""Interactors are things you can USE objects on."""
	def __init__(self, call_name, intro_text, valid_items, invalid_take_txt, hidden,):
		self.call_name = call_name
		self.intro_text = intro_text
		self.valid_items = valid_items
		self.invalid_take_txt = invalid_take_txt
		self.hidden = hidden

	def see_me(self):
		if self.hidden == False:
			print "%s" % (self.intro_text)
		else:
			pass

#---------------- GAMEPLAY FUNCTIONS ----------------------#

def get_input_until_valid():
	"""Gets input and checks input against valid commands and routes to gameplay functions"""
	#print get_all_obj_keys()
	print "\n",
	i = raw_input("> ").lower()
	print "\n",

	# first we want to check some anywhere & always valid commands: help, inventory, & look around
	if i.strip() == "help":
		print "Here are the valid commands:"
		print "go to - travels to a specified location"
		print "take - takes an item if it is nearby and able to be taken"
		print "use - uses an item if it's in your inventory and can be used"
		print "look around - displays nearby locations and things of interest around you"
		get_input_until_valid()

	elif i.strip() == "inventory":
		if inventory == []:
			print "Your inventory is currently empty."
			get_input_until_valid()
		else:
			pass
		print "Here is your inventory:"
		for item in inventory:
			print item.call_name
		get_input_until_valid()

	elif i.strip() == "look around":
		print current_location[-1].nearby_loc_text
		main_gameplay(current_location[-1])

	# if its not an anywhere command we should check it for a valid cmd and obj call
	# This uses regex to find a valid command and object
	find_cmd = re.findall(r"^\bgo to|^\btake|^\buse", i.lstrip())
	find_obj = re.findall(r"" + get_all_obj_keys(), i.replace("\'", ""))

	# if it's not an anywhere command now we need to check if both a command and a obj have been entered
	# first we error out and suggest help text if no valid command or object.
	if find_cmd == [] and find_obj == []:
		print "I'm afraid I don't understand %s." % i
		print "Type help for a list of valid commands."
		get_input_until_valid()

	# now we know theres at least one valid cmd or obj. so now we check if the other field is blank. 
	#elif find_cmd[0] == "go to" and find_obj == []:
	#	print "%s is a valid command, but it must be followed by a valid location." % (find_cmd[0])
	#	get_input_until_valid()	

	elif find_cmd != [] and find_obj == []:
		if find_cmd[0] == "go to":
			print "%s is a valid command, but it must be followed by a valid location." % (find_cmd[0])
			get_input_until_valid()	
		else:
			pass

		print "%s is a valid command, but it must be followed by a valid object." % (find_cmd[0])
		get_input_until_valid()

	elif find_cmd == [] and find_obj != []:
		print "I don't quite understand what you want to do to the %s." % find_obj[0]
		print "Type help for a list of valid commands."
		get_input_until_valid()

	# now we have confirmed we have both a valid command and a valid object, we route the cmd + obj pair to the correct route. 
	else:

		if find_cmd[0] == "go to":
			go_to_route(find_cmd[0], find_obj[0])
		elif find_cmd[0] == "take":
			take_route(find_cmd[0], find_obj[0])
		elif find_cmd[0] == "use":
			use_route(find_cmd[0], find_obj[0])
		else:
			print "Don't have a way to route this."
			get_input_until_valid()

def go_to_route(passed_cmd, passed_obj):
	if passed_obj in all_locations_hashmap:
		next_loc = all_locations_hashmap[passed_obj]
		main_gameplay(next_loc)
	else:
		print "You can't go to %s because %s is not a location." % (passed_obj, passed_obj)
		get_input_until_valid()

def take_route(passed_cmd, passed_obj):
	#first we check if the obj is an item and assign it to a new object if it is
	if passed_obj in all_items_hashmap:
		item_obj = all_items_hashmap[passed_obj]
	#then we check if its an interactor because they have specific text output for the take command. 
	elif passed_obj in all_interactor_hashmap:
		if all_interactor_hashmap[passed_obj] in current_location[-1].interactors:
			pass
		else:
			print "You don't see any %s around here that you could take." % passed_obj
			get_input_until_valid()
		print all_interactor_hashmap[passed_obj].invalid_take_txt
		get_input_until_valid()
	else: 
		print "How would you possibly think you could take %s? Yeah right!" % passed_obj
		get_input_until_valid()
	
	#now that we know were dealing with an item, we need to check if its actually around to be taken:
	if item_obj in current_location[-1].stored_items:
		item_obj.take_item()
	#if we know its a valid item but its not around, then you're in the wrong place or you already have it. 
	elif item_obj in inventory:
		print "You already have the %s in your inventory!" % passed_obj
		get_input_until_valid()
	else:
		print "You don't see a %s anywhere around here." % passed_obj
		get_input_until_valid()

def use_route(passed_cmd, passed_obj):
	# for use we realy want it to send you back to input unless the item is in your inventory. so we do this first:
	# the first loop checks if there is an error which would happen if the passed object is not an item
	try: 
		all_items_hashmap[passed_obj]
	except:
		print "You can only use things that are in your inventory. I don't see a %s in your inventory!" % passed_obj
		get_input_until_valid()

	#now we know its a valid item name. now we check if its in your inv, if yes then its set to a new item_to_use object
	if all_items_hashmap[passed_obj] in inventory:
		item_to_use = all_items_hashmap[passed_obj]
	else:
		print "You can only use things that are in your inventory. I don't see a %s in your inventory!" % passed_obj
		get_input_until_valid()

	#Now we know it is an item and is in your inventory, we need to get an input for what interactor to use it on
	input_possible_interactor = raw_input("What would use like to use the %s on?\n\n> " % passed_obj).lower().strip()
	print"\n",

	#now we use regex to find any interactor call names in the interactor call name dict.
	#This requires calling the setup function get all interactor keys because this makes it into a readable string for regex
	regex_find_interactor = re.findall(get_all_interactor_keys(), input_possible_interactor)

	#then we check if any valid interactor call names have been returned, and pass on the first one as the object if it is.
	if regex_find_interactor != []:
		interactor_obj = all_interactor_hashmap[regex_find_interactor[0]]
		pass
	else:
		print "The %s doesn't seem to do anything to the %s." % (passed_obj, input_possible_interactor)
		main_gameplay(current_location[-1])

	#then we see if the interactor object is in our current location
	if interactor_obj in current_location[-1].interactors:
		pass
	else:
		print "You don't see a %s anywhere to use the %s on." % (input_possible_interactor, passed_obj)
		main_gameplay(current_location[-1])

	#then we check if the item can be used on that specific interactor
	#and its a match we send it to the function that uses it (special case for each use.)	
	if item_to_use in interactor_obj.valid_items:
		item_to_use.use_cases(interactor_obj)
	else:
		print "The %s doesn't seem to do anything to the %s." % (passed_obj, input_possible_interactor)
		main_gameplay(current_location[-1])
	

def main_gameplay(location):
	win_check()
	location.go_to()
	get_input_until_valid()

def win_check():
	if beer_inside in inventory:
		print "You got beer from Sawyer's! You WIN!!"
 		exit(0)
 	else:
 		pass

#------------------------ ITEMS -----------------------------#

# outside sawyers items
beer_outside = Item("beer", "You see beer inside. It looks cold and refreshing!", False, False, "You cant take something when you're outside silly!")
ball = Item("ball", "You now see there is a red ball wedged by the door where the trash can used to be.", True, True, "you cant!")
trash_can = Item("trash can", "You see a trash can by the door. It's empty with a couple random stickers on it.", False, True, "You cant!")

# inside sawyers items
tv = Item("tv", "There is a TV sitting on the counter. It's tuned to a music video channel.", False, False, "How dare you! You shouldn't take their TV!")
beer_inside = Item("pbr", "You see a bunch of PBR gleaming in the corner fridge. It's Noah's favorite!", False, True, "You can't take beer from behind a locked door silly!")
snacks = Item("snacks", "There are so many kinds of snacks lining the shelves!", False, True, "You cant!")

# flavilla items
sign = Item("sign", "You notice a sign tucked away in the bushes. It says \"Be kind PDX!\"", False, True, "you try to take the sign but it's too heavy to carry with you.")
stick = Item("stick", "Where the sign used to be you now see a grubby stick in bushes.", True, True, "You cant!")

# goldie house items

key = Item("key", "You now notice the shiny thing on goldies collar is a key!", True, False, "you cant!")

all_items_hashmap = {
beer_outside.call_name : beer_outside,
trash_can.call_name : trash_can,
stick.call_name : stick,
tv.call_name : tv,
beer_inside.call_name : beer_inside,
snacks.call_name : snacks,
sign.call_name : sign,
ball.call_name : ball,
key.call_name : key,
}

#------------------------ INTERACTORS -----------------------------#

# sawyers interactors
door = Interactor("door", "There is a locked glass door right in front of you. For some reason Sawyer's is closed.", [key], "Even if it wasn't attached to the building, theres no way you could take that door!", False)

# flavilla interactors
truck = Interactor("truck", "You see a truck in front of you. It looks old and junky.", [], "Theres no way that truck has run in years, and theres no way you could take it!", False)

# neighbors house interactors
goldie_far = Interactor("goldie", "Goldie the golden retriever sits on the steps of the house.\nShe has something shiny attached to her collar.", [stick, ball], "She is all the way on the porch, and you really shouldn't take someone elses dog!", False)
goldie_close = Interactor("XGOLDIEX", "Now Goldie is right behind the gate, close to you. She is happily chewing the stick you gave her.", [stick], "Seriously, you really shouldn't take someone elses dog!", True)

# universal interactors
mona = Interactor("mona", "Mona is leashed by your side, sniffing about.", [ball, stick], "Mona is already leashed to you!", False)

all_interactor_hashmap = {}

def update_interactor_hashmap():
	global all_interactor_hashmap
	all_interactor_hashmap = {
	door.call_name : door,
	truck.call_name : truck,
	goldie_far.call_name : goldie_far,
	goldie_close.call_name : goldie_close,
	mona.call_name : mona,
	}

#------------------------ LOCATIONS -----------------------------#

outside_sawyers = Location("outside", "sawyer's", [beer_outside, trash_can, ball], [door, mona], "You don't feel like venturing further, but you could go back to the Flavilla.")
inside_sawyers = Location("inside", "XSAWYERSX", [tv, beer_inside, snacks], [mona], "You don't feel like venturing further, but you could go back to the Flavilla.")
flavilla = Location("at the", "flavilla", [sign, stick], [truck, mona], "Sawyer's is to your left, and the Neighbor's House is to your right.")
neighbors_house = Location("at the", "neighbor's house", [key], [goldie_far, goldie_close, mona], "You don't feel like venturing further, but you could go back to the Flavilla.")

all_locations_hashmap = {}

def update_locations_hashmap():
	global all_locations_hashmap
	all_locations_hashmap = {
	outside_sawyers.call_name.replace("\'", "") : outside_sawyers, 
	inside_sawyers.call_name.replace("\'", "") : inside_sawyers, 
	flavilla.call_name : flavilla, 
	neighbors_house.call_name.replace("\'", "") : neighbors_house,
	}

#------------------------ SETUP FUNCTIONS -----------------------------#

def get_all_obj_keys():
	"""This creates a string of all obj keys seperated by | for regex parsing"""
	obj_name_str = ""
	for key in all_items_hashmap.viewkeys():
		obj_name_str += key + "|"
	for key in all_locations_hashmap.viewkeys():
		obj_name_str += key + "|"
	for key in all_interactor_hashmap.viewkeys():
		obj_name_str += key + "|"
	return obj_name_str.strip("|")

def get_all_interactor_keys():
	"""This creates a string of all interactor keys seperated by | for regex parsing"""
	obj_name_str = ""
	for key in all_interactor_hashmap.viewkeys():
		obj_name_str += key + "|"
	return obj_name_str.strip("|")

#------------------------ GAMEPLAY -----------------------------#

###include this if you want to jump to locations for debugging. 
#from sys import argv
#first_loc = str(argv)
#if "inside" in argv:
#main_gameplay(inside_sawyers)
#else:
#pass
	
print "\n\n"
print "Welcome to the Flavel Street Game!"
print "The goal of the game is to get beer from Sawyer's (the local mini-mart.)"
print "Your story begins outside the Flavilla, the fond nickname for your house."
update_locations_hashmap()
update_interactor_hashmap()
main_gameplay(flavilla)





