from typing import Dict, List



class ItemHelper:
    """
        Helper class for parsing items in queries using 
        SQLAlchemy, among other functionalities.
    """

    async def remove_items(self, dictionary: Dict, items_to_remove: List) -> Dict:
        """
            Removes multiple elements from a dictionary asynchronously.

            Args:
                dictionary (dict): The dictionary from which the elements will be removed.
                items_to_remove (list): A list of keys to be removed from the dictionary.

            Returns:
                dict: The dictionary with the removed elements.
        """
        for item in items_to_remove:
            parts = item.split(".")
            current_dict = dictionary

            for part in parts[:-1]:
                if part in current_dict and isinstance(current_dict[part], dict):
                    current_dict = current_dict[part]
                else:
                    break
            else:
                if parts[-1] in current_dict:
                    if isinstance(current_dict[parts[-1]], dict):
                        current_dict[parts[-1]].clear()
                    else:
                        current_dict.pop(parts[-1], None)

        return dictionary
    


ITEM_HELPER = ItemHelper()
