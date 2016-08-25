import os, psutil, gc, numpy, pandas, csv
import operator
from ref_genome_sizes import *

def generator(path):
    with open(path) as file:
        for line in file:
            value, index = line.split()
            values = [float(value), int(index)]
            yield values

def bash_sort(path, output_path, reverse=True, buffer_size=None, OS=None):
    dir = os.path.dirname(path)
    temp = dir + r"\temp"
    if not os.path.exists(temp):
        os.mkdir(temp)
    if buffer_size == None:
        cmd = "sort -r -n -s -k1 -o "+ output_path +" " + path
    else:
        buffer = str(buffer_size * 1000000)
        cmd = "sort -r -n -s -k1 -o "+ output_path +" --buffer-size="+ buffer + " --temporary-directory=temp " + path
    os.system(cmd)

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

def output_wig_fixed(replaced_sorted_file_paths, ref_genome, step):
    ref_genome_sizes = master_genome_sizes[ref_genome]
    sorted_sizes = sorted(ref_genome_sizes.items(), key=operator.itemgetter(1))

    for path in replaced_sorted_file_paths:
        output_path = ""
        output_file = open(output_path, "w")
        output_file.close()

        for chrom in sorted_sizes:
            result = []
            size = 0
            file = open(output_path, "a")
            file.write("   \n")
            chrom_size = chrom[1][1]- chrom[1][0]
            while chrom_size > 0:
                chrom_size -= step
                ### TODO:

                ###
        


    pass

def output_wig_vary(replaced_sorted_file_paths, ref_genome, step):
    pass

def output_wig(replaced_sorted_file_paths, format, ref_genome, step):
    if format == "fixed":
        output_wig_fixed(replaced_sorted_file_paths, ref_genome, step)
    elif format == "variable":
        output_wig_vary(replaced_sorted_file_paths, ref_genome, step)

