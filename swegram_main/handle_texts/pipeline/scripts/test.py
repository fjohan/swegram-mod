import os
from compounds import find_compounds
from pycut import cut

from process import file_to_list

text = file_to_list('text.conll')

print(find_compounds('text.conll'))
