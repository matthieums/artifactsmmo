from models import Character

g = "gather"
d= "deposit"
w = "withdraw"
f = "fight"
cr = "craft"
r = "rest"
t_e = "toggle_equipped"

c_r = "copper_rocks"
a_w = "ash_wood"
a_t = "ash_tree"
ch = "chickens"
a_p = "ash_plank"
w_s = "wooden_shield"
e_i = "empty_inventory"
c_o = "copper_ore"
g_s = "green_slime"
co = "copper"
i_r = "iron_rocks"


def load_character_tasks(characters: list[Character]) -> None:
    for character in characters:
        if character.is_on_cooldown():
            character.add_task(1, "handle_cooldown", character.cooldown_duration)

        character.add_task(1, f, location=ch)
        character.add_task(1, f, location=ch)
    return

    
# if craft, add the skill
    # item_data = await get_item_info(*args)
    # required_position = item_data["data"]["craft"]["skill"]


        #     # character.add_task(1, g, location=i_r)

        #     # character.add_task(1, w, item=c_o, quantity=100)
            # character.add_task(1, e_i)
            # character.add_task(1, w, item=c_o, quantity=100)
            # character.add_task(1, cr, co, quantity=10)
            # character.add_task(1, e_i)
            # character.add_task(1, w, item=c_o, quantity=100)
            # character.add_task(1, cr, co, quantity=10)
            # character.add_task(None, cr, co)

            # character.add_task(None, g, location=i_r)
            # character.add_task(None, cr, co)
            # character.add_task(None, cr, co)
            # character.add_task(None, g, location=i_r)
            # character.add_task(None, e_i)

            # tg.create_task(character.run_tasks())