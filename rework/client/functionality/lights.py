
publisher = None 

# --------------------- Compulsory functions ----------------------- #
def get_functions():
	return {
			"setcolor":		    set_color,
			"setcolorlist":	    set_color_by_list,
            "setrelcolorlist":  set_color_by_list_relative,
			"setdimmer":	    set_dimmer,
            "incdimmer":        inc_dimmer,
            "decdimmer":        dec_dimmer,
			"setmode":		    set_mode,
			"setspeed":		    set_speed,
			"incspeed":	        inc_speed,
			"decspeed":     	dec_speed,
			"setetd":		    set_effect_time_difference,
			"select":		    select_bulb,
			"selectbyname":		select_bulb_by_name,
			"unselect":		    unselect_bulb,
			"unselectbyname":	unselect_bulb_by_name,
            "toggleselect":     toggle_bulb,
            "toggleselectbyname":toggle_bulb_by_name,
			"toggleselectall":	toggle_selected_bulbs,
			"activate":		    activate_bulbs,
			"deactivate":	    deactivate_bulbs
	}
    
def set_publisher(event_engine):
    global publisher
    publisher = event_engine
    
    
# -------------------------- Helper functions ---------------------------- #
def send_value_update(property, value):
    publisher.update_value(property, value)
    

# ------------------- Implementation specific functions ------------------ #
def set_color(color):
    pass
    
def set_color_by_list(list, index):
    print("Setting color list with list: ", list, " and index: ", index)
    pass
    
def set_color_by_list_relative(list, change):
    send_value_update("lights.selected.0", 1)
    pass
    
def set_dimmer(value):
    pass
    
def inc_dimmer(increase):
    pass
    
def dec_dimmer(decrease):
    pass
    
def set_mode(mode):
    pass
    
def set_speed(increase):
    pass
    
def inc_speed(increase):
    pass
    
def dec_speed(decrease):
    pass
    
def set_effect_time_difference(etd):
    pass
    
def select_bulb(index):
    pass
    
def select_bulb_by_name(name):
    pass
    
def unselect_bulb(index):
    pass
    
def unselect_bulb_by_name(name):
    pass
    
def toggle_bulb(index):
    pass
    
def toggle_bulb_by_name(name):
    pass
    
def toggle_selected_bulbs():
    pass
    
def activate_bulbs():
    pass
    
def deactivate_bulbs():
    pass