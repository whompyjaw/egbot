#returns count of units/structures in dictionary
def get_count(dict: {}, name: str):
    if dict[name] != None:
        return len(dict[name].values())
    else:
        return 0

#returns the values
def get_values(dict: {}, name: str):
    if dict[name] != None:
        return dict[name].values()

