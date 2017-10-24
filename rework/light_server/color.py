
    
def get_black_color():
    return {"red": 0, "green": 0, "blue": 0, "white": 0}
    
def colors_equal(color1, color2):
    color2_full = get_complete_rgbw_color(color2)
    for key, value in get_complete_rgbw_color(color1).items():
        if not color2_full[key] == value:
            return False
    return True
    
def get_complete_rgbw_color(color):
    return {"red": color.get("red", 0), "green": color.get("green", 0), "blue": color.get("blue", 0), "white": color.get("white", 0)}