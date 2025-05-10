import state
from models.task_manager import TaskManager

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
ch = "chicken"
a_p = "ash_plank"
w_s = "wooden_shield"
e_i = "empty_inventory"
c_o = "copper_ore"
g_s = "green_slime"
co = "copper"
i_r = "iron_rocks"


def load_character_tasks(manager: TaskManager) -> None:
    for character in state.characters.values():
        if character.is_on_cooldown():
            manager.add_task(1, character, "handle_cooldown", character.cooldown_duration)

        manager.add_task(1, character, f, location=ch)
    return
