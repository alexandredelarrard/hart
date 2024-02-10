import re 
import string
import unidecode
 
def homogenize_columns(columns):

    columns = [str(x).upper().strip().translate(str.maketrans(' ', ' ', '!"#$%&()*+,-./:;<=>?@[\\]^`{|}~\'\"'))
                     for x in columns]

    # remove accents and space
    columns = [unidecode.unidecode(str(x).replace("'", "_").replace(" ", "_")) for x in columns]

    return columns
