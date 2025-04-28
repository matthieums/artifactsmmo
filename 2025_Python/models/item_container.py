from abc import ABC, abstractmethod


class ItemContainer(ABC):
    """
    Abstract class for objects that manage items.
    """

    @abstractmethod
    def available(self, resources: dict) -> dict:
        """
        Check the availability of ingredients.
        Should return a dictionary with the ingredients available.
        """
        pass

