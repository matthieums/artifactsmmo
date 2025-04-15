# General
error_status = {
    422: code_invalid_payload, 
    429: code_too_many_requests, 
    404: code_not_found, 
    500: code_fatal_error, 
    
    # Account Error Codes
    452: code_token_invalid, 
    453: code_token_expired, 
    454: code_token_missing, 
    455: code_token_generation_fail, 
    456: code_username_already_used, 
    457: code_email_already_used, 
    458: code_same_password, 
    459: code_current_password_invalid, 
    
    # Character Error Codes
    483: code_character_not_enough_hp, 
    484: code_character_maximum_utilites_equiped, 
    485: code_character_item_already_equiped, 
    486: code_character_locked, 
    474: code_character_not_this_task, 
    475: code_character_too_many_items_task, 
    487: code_character_no_task, 
    488: code_character_task_not_completed, 
    489: code_character_already_task, 
    490: code_character_already_map, 
    491: code_character_slot_equipment_error, 
    492: code_character_gold_insufficient, 
    493: code_character_not_skill_level_required, 
    494: code_character_name_already_used, 
    495: code_max_characters_reached, 
    496: code_character_not_level_required, 
    497: code_character_inventory_full, 
    498: code_character_not_found, 
    499: code_character_in_cooldown, 
    
    # Item Error Codes
    471: code_item_insufficient_quantity, 
    472: code_item_invalid_equipment, 
    473: code_item_recycling_invalid_item, 
    476: code_item_invalid_consumable, 
    478: code_missing_item, 
    
    # Grand Exchange Error Codes
    479: code_ge_max_quantity, 
    480: code_ge_not_in_stock, 
    482: code_ge_not_the_price, 
    436: code_ge_transaction_in_progress, 
    431: code_ge_no_orders, 
    433: code_ge_max_orders, 
    434: code_ge_too_many_items, 
    435: code_ge_same_account, 
    437: code_ge_invalid_item, 
    438: code_ge_not_your_order, 
    
    # Bank Error Codes
    460: code_bank_insufficient_gold, 
    461: code_bank_transaction_in_progress, 
    462: code_bank_full, 
    
    # Maps Error Codes
    597: code_map_not_found, 
    598: code_map_content_not_found
}