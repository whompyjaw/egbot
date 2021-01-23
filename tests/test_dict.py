from collections import defaultdict
import pprint


class NewUnit:
    def __init__(self):
        self.name = 'Drone'

class OldUnit:
    def __init__(self):
        self.name = 'Larva'

class NestedDefaultDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    def __repr__(self):
        return repr(dict(self))


def remove_unit(tag: int, units, pp):
    # del_unit = None
    for unit_type in units.keys():   
           unit_type.pop(tag)
           
           pp.pprint(units)
           break

def print_dict(units, pp):
    # pp.pprint(units.keys())
    # pp.pprint(units.values())
    # pp.pprint(units.items())
    pass
    # print("Printing next level")
    # pp.pprint(units['New Units'].keys(123))
    # pp.pprint(units[unit_type].get(123))
    # pp.pprint(units['New Units'][199])
    # pp.pprint(units.keys().values())
    # pp.pprint(units.keys().items())

if __name__ == "__main__":
   
    units = NestedDefaultDict()
    # units = {}
    # units['New Units'] = {}
    # units['Old Units'] = {}
    pp = pprint.PrettyPrinter()
    units['New Units'][123] = NewUnit()
    units['New Units'][153] = NewUnit()
    units['New Units'][173] = NewUnit()
    units['New Units'][183] = NewUnit()
    units['New Units'][193] = NewUnit()
    units['Old Units'][283] = OldUnit()
    units['Old Units'][293] = OldUnit()
    #print(type(units['New Units']))
    remove_unit(123, units, pp)
    #print_dict(units, pp)