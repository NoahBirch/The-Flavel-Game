from sys import exit

inventory = []

current_location = []

all_item_operators = ["take", "use"]
all_location_operators = ["go to",]
all_interactor_operators = ["take"]
all_valid_commands = []
mona_with_ball = False

class Location:
	"""Locations are places you can gold"""
	def __init__(self, modifier, call_name, stored_items, interactors, nearby_loc_text):
		self.modifier = modifier
		self.call_name = call_name
		self.stored_items = stored_items
		self.visits = 0
		self.interactors = interactors
		self.adjacent_locations = {}
		self.nearby_loc_text = nearby_loc_text
		# This creates a list that we will use for valid commands
		for operator in all_location_operators:
			all_valid_commands.append(operator + " " + self.call_name)

	def get_name(self):
		return self.call_name

	def display_stored_items(self):
		for item in self.stored_items:
			item.see_me()

	def display_loc_interactors(self):
		for interactor in self.interactors:
			interactor.see_me()

	def go_to(self):
		if self.visits == 0:
			print "You arrive %s %s for the first time." % (self.modifier, self.get_name())
		elif self == current_location[-1]:
			print "You are still %s %s." % (self.modifier, self.get_name())
		else:
			print "You arrive back %s %s." % (self.modifier, self.get_name())
		
		self.visits += 1
		self.display_stored_items()
		self.display_loc_interactors()	
		current_location.append(self)

class Item:
	"""Items are things you can TAKE into your inventory"""
	def __init__(self, call_name, intro_text, hidden, takeable, cant_take_text,):
		self.call_name = call_name
		self.intro_text = intro_text
		self.hidden = hidden
		self.takeable = takeable
		self.cant_take_text = cant_take_text
		# This creates a list that we will use for valid commands
		for operator in all_item_operators:
			all_valid_commands.append(operator + " " + self.call_name.lower())

	def see_me(self):
		if self.hidden == False:
			print "%s" % (self.intro_text)
		else:
			pass

	def take_item(self):
		# first checks if valid item take is in current location or if hidden. (since both should return a "you dont see anywhere" error)
		if self not in current_location[-1].stored_items or self.hidden == True:
			print "You don't see a %s anywhere." % self.call_name
			main_gameplay(current_location[-1])
		# Then checks if it is takeable, if it is it is added to inventory and removed from location
		elif self.takeable == True:
			print "You take the %s and stuff it in your pocket." % self.call_name
			inventory.append(self)
			current_location[-1].stored_items.remove(self)
			self.uncover_if_valid()
			main_gameplay(current_location[-1])
		# if not it must be in location but not takeable
		else:
			print self.cant_take_text
			main_gameplay(current_location[-1])

	def use_item(self, interactor_obj):
		global mona_with_ball
		### This will only get called if there is a valid item use on interactor combo. These are the speicifc cases of those interactions.
		
		if self == key:
			print "You use the key to unlock the door to sawyers!"
			inventory.remove(self)
			outside_sawyers.call_name = "Past_sawyers"
			inside_sawyers.call_name = "sawyers"
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
			key.hidden = False
			key.takeable = True
			main_gameplay(current_location[-1])

		# anytime you use the ball on goldie mona gets mad.
		elif self == ball and interactor_obj == goldie_far:
			print "Mona growls at you and you get the sense she doesn't want you to give the ball to Goldie."
			main_gameplay(current_location[-1])

		# anytime u use ball on mona she accepts.
		elif self == ball and interactor_obj == mona:
			print "Mona gladly accepts the ball!"
			inventory.remove(self)
			mona_with_ball = True
			mona.intro_text = "Mona is leashed by your side, furiously chewing on her ball."
			main_gameplay(current_location[-1])

		else: 
			main_gameplay(current_location[-1])


	def uncover_if_valid(self):
		if self.call_name == "trash can":
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
		for operator in all_interactor_operators:
			all_valid_commands.append(operator + " " + self.call_name)

	def see_me(self):
		if self.hidden == False:
			print "%s" % (self.intro_text)
		else:
			pass

#---------------- GAMEPLAY FUNCTIONS ----------------------#

def input_check_and_route(i):
	"""Checks input against valid commands and routes to gameplay functions"""
	if "help" in i:
		print "Here are the valid commands:"
		print "go to - travels to a specified location"
		print "take - takes an item if it is nearby and able to be taken"
		print "use - uses an item if it's in your inventory and can be used"
		print "look around - displays nearby locations you can travel to"
		return False

	elif "inventory" in i:
		print "Here is your inventory:"
		for item in inventory:
			print item.call_name
		return False

	elif "look around" in i:
		print current_location[-1].nearby_loc_text
		main_gameplay(current_location[-1])

	elif i.strip() in all_valid_commands:
		go_to_route(i)
		take_route(i)
		use_route(i)
		return True
	else:
		print "You try to %s but you can't.\nType \"help\" to see a list of valid commands." % i
		return False

def go_to_route(i):
	if "go to" in i:
		next_loc_name = (i.replace("go to", " ", 1)).strip()
		next_loc = all_locations_hashmap[next_loc_name]
		main_gameplay(next_loc)
	else:
		pass

def take_route(i):
	if "take" in i:
		item_to_take_name = (i.replace("take", " ", 1)).strip()
		# we quickly intercept to see if user is trying to "take" and interactor
		if item_to_take_name in all_interactor_call_names:
			print all_interactor_hashmap[item_to_take_name].invalid_take_txt
			main_gameplay(current_location[-1])
		else:
			pass
		item_obj = all_items_hashmap[item_to_take_name]
		item_obj.take_item()
	else:
		pass

def use_route(i):
	if "use" in i:
		item_to_use_name = (i.replace("use", " ", 1)).strip()
		item_obj = all_items_hashmap[item_to_use_name]

		#first we check if item to be used is in inventory
		if item_obj in inventory:
			pass
		else:
			print "You don't seem to have a %s with you to use." % item_to_use_name
			main_gameplay(current_location[-1])

		#then we get an input for what interactor to use it on
		input_possible_interactor = raw_input("What would use like to use the %s on?\n>" % item_to_use_name).strip().lower()

		#then we check if interactor input is a valid interactor name, and pass it on as the object if it is.
		if input_possible_interactor in all_interactor_call_names:
			interactor_obj = all_interactor_hashmap[input_possible_interactor]
		else:
			print "%s is not a valid interactor that the %s would work on." % (input_possible_interactor, item_to_use_name)
			main_gameplay(current_location[-1])

		#then we see if the interactor object is in our current location
		if interactor_obj in current_location[-1].interactors:
			pass
		else:
			print "You don't see a %s anywhere to use the %s on." % (interactor_obj.call_name, item_obj.call_name)
			main_gameplay(current_location[-1])

		#then we check if the item can be used on that specific interactor
		if item_obj in interactor_obj.valid_items:
			item_obj.use_item(interactor_obj)
		else:
			print "Unfortunately the %s doesn't seem to do anything to the %s." % (item_obj.call_name, interactor_obj.call_name)
			main_gameplay(current_location[-1])
		# and after all that if we send it to the function that uses it (special case for each use.)	
		
	else:
		pass

def main_gameplay(location):
	win_check()
	location.go_to()

	i = raw_input("> ").lower()

	while input_check_and_route(i) == False:
		i = raw_input("> ").lower()

def win_check():
	if beer_inside in inventory:
		print "You got beer from sawyers! You WIN!!"
 		exit(0)
 	else:
 		pass


#------------------------ ITEMS -----------------------------#

# outside sawyers items
beer_outside = Item("beer", "You see beer inside. It looks cold and refreshing!", False, False, "You cant take something when you're outside silly!")
stick = Item("stick", "Where the trash can was you now see a stick in the corner. It's covered in dirt and grime.", True, True, "You cant!")
trash_can = Item("trash can", "You see a trash can by the door. It's empty with a couple random stickers on it.", False, True, "You cant!")

# inside sawyers items
tv = Item("tv", "There is a TV sitting on the counter. It's tuned to a music video channel.", False, False, "How dare you! You shouldn't take their TV!")
beer_inside = Item("pbr", "You see a 40 of PBR gleaming in the corner fridge. It's Noah's favorite!", False, True, "You can't take beer from behind a locked door silly!")
snacks = Item("snacks", "There are so many kinds of snacks lining the shelves!", False, True, "You cant!")

# flavilla items
sign = Item("sign", "You notice a sign tucked away in the bushes. It says \"Be kind PDX!\"", False, False, "you try to take the sign but it's too heavy to carry with you.")

# goldie house items
ball = Item("ball", "Out of the corner of your eye you see a red ball in the gutter.", False, True, "you cant!")
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
door = Interactor("door", "There is a locked glass door right in front of you. For some reason Sawyers is closed.", [key], "Even if it wasn't attached to the building, theres no way you could take that door!.", False)

# flavilla interactors
truck = Interactor("truck", "You see a truck in front of you. It looks old and junky.", [], "Theres no way that truck has run in years, and theres no way you could take it!", False)

# goldies house interactors
goldie_far = Interactor("goldie", "Goldie the golden retriever sits on the steps of the house.\nShe has something shiny attached to her collar.", [stick, ball], "She is all the way on the porch, and you really shouldn't take someone elses dog!", False)
goldie_close = Interactor("XGOLDIEX", "Now Goldie is right behind the gate, close to you. She is happily chewing the stick you gave her.", [stick], "Seriously, you really shouldn't take someone elses dog!", True)

# universal interactors
mona = Interactor("mona", "Mona is leashed by your side, sniffing about.", [ball, stick], "Mona is already leashed to you!", False)

all_interactor_call_names = [
door.call_name,
truck.call_name,
goldie_far.call_name,
goldie_close.call_name,
mona.call_name
]

all_interactor_hashmap = {
door.call_name : door,
truck.call_name : truck,
goldie_far.call_name : goldie_far,
goldie_close.call_name : goldie_close,
mona.call_name : mona,
}

#------------------------ LOCATIONS -----------------------------#

outside_sawyers = Location("outside", "sawyers", [beer_outside, trash_can, stick], [door, mona], "You don't feel like venturing further, but you could go back to the Flavilla.")
inside_sawyers = Location("inside", "XSAWYERSX", [tv, beer_inside, snacks], [mona], "You don't feel like venturing further, but you could go back to the Flavilla.")
flavilla = Location("at the", "flavilla", [sign], [truck, mona], "Sawyers is to your left, and Goldies House is to your right.")
goldies_house = Location("at", "goldies house", [ball, key], [goldie_far, goldie_close, mona], "You don't feel like venturing further, but you could go back to the Flavilla.")

all_locations_hashmap = {}

def update_locations_hashmap():
	global all_locations_hashmap
	all_locations_hashmap = {
	outside_sawyers.call_name : outside_sawyers, 
	inside_sawyers.call_name : inside_sawyers, 
	flavilla.call_name : flavilla, 
	goldies_house.call_name: goldies_house,
	}

#------------------------ GAMEPLAY -----------------------------#

###include this if you want to jump to locations for debugging. 
#from sys import argv
#first_loc = str(argv)
#if "inside" in argv:
#main_gameplay(inside_sawyers)
#else:
#pass
	
#def goto_location(location):
#print all_valid_commands
print "\n\n"

update_locations_hashmap()
main_gameplay(flavilla)





