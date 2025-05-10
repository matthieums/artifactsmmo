def format_action_message(character, action, location):
    if not character:
        return

    print(
        f"{character} performed {action}"
        + (f" at {location}" if location else "")
    )
    return 1


def format_error_message(response, character, action, location):
    print(f"{character} could not perform '{action}'. FAILED at {location}.")
    print(f"Status: {response.status_code}")
    print(response.text)
    raise Exception("Unidentified error during gather() request")


def format_loot_message(character, loot: dict):
    items = loot.get("items")
    gold = loot.get("gold")
    xp = loot.get("xp")

    items_str = (
        "\titems:\n" +
        "".join(f"\t  {name} x{quantity}\n" for name, quantity in items.items())
        if items else ""
    )

    gold_str = f"\tgold: {gold}\n" if gold else ""
    xp_str = f"\txp: {xp}\n" if xp else ""
    print(f"{character} received:\n{items_str}{gold_str}{xp_str}")
