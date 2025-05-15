import logging


logger = logging.getLogger("__name__")


def update_inventory(self, item: str, quantity: int):
    if quantity > 0:
        self.inventory.add(item, quantity)
    elif quantity < 0:
        self.inventory.remove(item, abs(quantity))
    else:
        logger.error("Invalid quantity provided to update_inventory")
