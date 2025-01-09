export const errorMessages = {
    // General Errors
    422: "Invalid payload provided.",
    429: "Too many requests, please try again later.",
    404: "Not found. The requested resource doesn't exist.",
    500: "A fatal error occurred on the server.",
  
    // Account Errors
    452: "Invalid token.",
    453: "Token expired. Please reauthenticate.",
    454: "Missing token. Please log in.",
    455: "Token generation failed. Please try again.",
    456: "Username already in use.",
    457: "Email already in use.",
    458: "New password is the same as the old one.",
    459: "Current password is invalid.",
  
    // Character Errors
    483: "Not enough HP to perform the action.",
    484: "Maximum utilities equipped for character.",
    485: "Item already equipped.",
    486: "Character is locked.",
    474: "Character cannot perform this task.",
    475: "Too many items assigned to the character's task.",
    487: "Character has no task assigned.",
    488: "Character task not completed.",
    489: "Character is already assigned to this task.",
    490: "Character is already on this tile.",
    491: "Character slot equipment error.",
    492: "Insufficient gold to complete the action.",
    493: "Character's skill level is not high enough.",
    494: "Character name already in use.",
    495: "Maximum number of characters reached.",
    496: "Character not at the required level.",
    497: "Character's inventory is full.",
    498: "Character not found.",
    499: "Character is in cooldown.",
  
    // Item Errors
    471: "Insufficient quantity of the item.",
    472: "Invalid item for equipment.",
    473: "Item cannot be recycled.",
    476: "Item is not a valid consumable.",
    478: "Missing item.",
    
    // Grand Exchange Errors
    479: "Max quantity of this item reached in the Grand Exchange.",
    480: "Item is not in stock in the Grand Exchange.",
    482: "Item price doesn't match.",
    436: "A Grand Exchange transaction is already in progress.",
    431: "No Grand Exchange orders available.",
    433: "You have reached the max number of Grand Exchange orders.",
    434: "Too many items in the Grand Exchange order.",
    435: "Same account cannot be used for both sides of the transaction.",
    437: "Invalid item for Grand Exchange.",
    438: "You are not the owner of this Grand Exchange order.",
    
    // Bank Errors
    460: "Insufficient gold in the bank.",
    461: "A bank transaction is already in progress.",
    462: "Bank is full.",
    
    // Map Errors
    597: "Map not found.",
    598: "Content for the map not found.",
    
    // Default
    default: "An unknown error occurred."
  };