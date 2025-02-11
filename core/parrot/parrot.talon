parrot(such):
	# app.notify(" such such ")
	print("Such detected")
	mouse_click(0)


parrot(hiss):
	print("Hiss detected")
	core.repeat_command(1)

parrot(thunk): print("unused thunk")

parrot(shush): 
	print("Shh detected")
 
parrot(bg): print("background detected")
parrot(speech): print("speech dtected")
