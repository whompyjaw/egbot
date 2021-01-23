;; This buffer is for text that is not saved, and for Lisp evaluation.
;; To create a file, visit it with C-x C-f and enter text in its buffer.

>>> questions = ['name', 'quest', 'favorite color']
>>> answers = ['lancelot', 'the holy grail', 'blue']
>>> for q, a in zip(questions, answers):
...     print('What is your {0}?  It is {1}.'.format(q, a))

def remove_unit(self, tag: int):
    for unit_name, struct_name in zip(self.units.keys(), self.structures.keys()):
        for struct_tag, unit_tag in (self.structures[name].keys(), self.units[name].keys()):
            if unit_tag == tag:
                del self.units[name][tag]
            else:
                del self.structures[name][tag]
