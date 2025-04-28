def subtract_dicts(dict1, dict2):
    for key, value in dict(dict1).items():
        available_qty = dict2.get(key, 0)
        value -= available_qty
        if value <= 0:
            del dict1[key]
        else:
            dict1[key] = value
    return dict1
