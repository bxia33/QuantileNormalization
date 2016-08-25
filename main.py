import psutil, gc, numpy, pandas, ref_genome_sizes, csv
from util import *
from more_itertools import *

## step 1 : parse the wig file and add index, and remove no signal band.

## step 2 : sort based on signal value
bash_sort(indexed_file_path)

## step 3 : caulculate the average
def calculate_average_signal(sorted_file_paths):
    iters = []
    result = []
    size = 0
    path_avg = "avg.txt"
    output_file = open(path_avg, "w")
    output_file.close()
    for path in sorted_file_paths:
        iters.append(generator(path))
    while True:
        values = [next(x, [0, 0])[0] for x in iters]
        avg = sum(values)/len(values)
        if avg != 0:
            result.append(avg)
            size += 1
            if size > 1000000:
                open_file = open(path_avg, "a")
                writer = csv.writer(open_file)
                writer.writerow(result)
                del result[:]
                gc.collect()
        else:
            break
        if result:
            open_file = open(path_avg, "a")
            writer = csv.writer(open_file)
            writer.writerow(result)
            del result[:]
            gc.collect()

##  save the replaced value file
def replace_avg(sorted_file_paths, average_path):
    for path in sorted_file_paths:
        result = []
        sorted_file = generator(path)
        average_file = generator(average_path)
        while True:
            cur_avg = next(average_file, 0)
            if cur_avg != 0:
                result.append([next(sorted_file)[1], cur_avg])
            else:
                break
        if result:
            open_file = open(replaced_file_path, "a")
            writer = csv.writer(open_file)
            writer.writerow(result)
            del result[:]
            gc.collect()




## step 4 : sort the replaced file based on index

## step 5 : recreate wig file
