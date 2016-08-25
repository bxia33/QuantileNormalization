from util import *
from more_itertools import *




## step 1 : parse the wig file

## step 2: check steps and make sure the step could be applied to all the samples

##  step 3: add index, and remove no signal band based on step

## step 4: sort based on signal value
bash_sort(indexed_file_path)

## step 5 : caulculate the average


## step 6 save the replaced value file


## step 7 : sort the replaced file based on index

bash_sort(replaced_file_paths)

## step 5 : recreate wig file
