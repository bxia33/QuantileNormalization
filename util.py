import os, psutil, gc, numpy, pandas, csv, gzip
import operator
from ref_genome_sizes import *
from more_itertools import *

def generator(path):
    with open(path, "r") as file:
        for line in file:
            value, index = line.split()
            values = [float(value), int(index)]
            yield values

def load_wig_fixed(path, ref_genome):
    result = []
    size = 0
    ref_genome_sizes = master_genome_sizes[ref_genome]
    parameters = {
        "chrom" : None,
        "start" : None,
        "step" : None,
        "span" : None,
    }
    prefix = path.find("wig")
    output_path = path[:prefix]+"indexed.txt"
    output_file = open(output_path, "w")
    output_file.close()

    with open(path, "r") as open_file:
        for line in open_file:
            if not line.strip():
                if line[0:9]=='fixedStep':
                    parameter_values = line.split()
                    for term in parameter_values[1:]:
                        key, value = term.split("=")
                        if key.strip()=='chrom':
                            parameters[key] = value
                        elif key.strip() == 'start':
                            parameters[key] = int(value) + ref_genome_sizes['chrom'][0] - 1
                        elif key.strip() == 'step':
                            parameters[key] = int(value)
                        elif key.strip() == 'span':
                            parameters[key] = int(value)
                else:
                    if parameters["start"] > ref_genome_sizes["chrom"][1]:
                        print("index larger than current "+ parameters["chrom"])
                        continue
                    else:
                        signal = line.split()[0]
                        result.append([signal, parameters["start"]])
                        parameters["start"] += parameters["step"]
                        size += 1
                        if parameters["span"] != None and parameters["span"] != parameters["step"]:
                            print("currently, for fixed wig, span not equal to step is not supported")
                            return
                        if size > 1000000:
                            output_file = open(output_path, "a")
                            writer = csv.writer(output_file)
                            writer.writerow(result)
                            del result[:]
                            gc.collect()
                            size = 0
        if result:
            output_file = open(output_path, "a")
            writer = csv.writer(output_file)
            writer.writerow(result)
            del result[:]
            gc.collect()
    pass

def load_wig_vary(path, ref_genome):
    pass

def load_wig(*files, ref_genome):
    file_paths = list(files)
    for path in file_paths:
        if path[-3:] == 'wig':
            open_file = open(path, "r")
        elif path[-6:] == 'wig.gz':
            open_file = gzip.open(path, "r")

        for line in open_file:
            if line[0] == 't':
                continue
            elif line[0:9]=='fixedStep':
                load_wig_fixed(path, ref_genome)
                open_file.close()
                break
            elif line[0:3]=='var':
                load_wig_vary(path, ref_genome)
                open_file.close()
                break
    return

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
                size = 0
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

def output_wig_fixed(replaced_sorted_file_paths, ref_genome, step, span):
    ref_genome_sizes = master_genome_sizes[ref_genome]
    sorted_sizes = sorted(ref_genome_sizes.items(), key=operator.itemgetter(1))

    for path in replaced_sorted_file_paths:
        output_path = path[:-4] + "output.wig"
        output_file = open(output_path, "w")
        output_file.close()
        iter = peekable(generator(path))

        for chrom in sorted_sizes:
            result = []
            size = 0
            file = open(output_path, "a")
            file.write("fixedStep chrom="+chrom+" start=1  step="+str(step)+" span="+str(step)+"\n")
            chrom_size = chrom[1][1]- chrom[1][0] + 1
            position = chrom[1][0]
            while chrom_size >= 0:
                chrom_size -= step
                current = iter.peek()
                if current[1] == position:
                    current = iter.__next__()
                    result.append([current[0]])
                else:
                    result.append([0])
                position += step
                size += 1
                if size > 1000000:
                    open_file = open(output_path, "a")
                    writer = csv.writer(open_file)
                    writer.writerow(result)
                    del result[:]
                    gc.collect()
                    size = 0
            if result:
                open_file = open(output_path, "a")
                writer = csv.writer(open_file)
                writer.writerow(result)
                del result[:]
                gc.collect()

def output_wig_vary(replaced_sorted_file_paths, ref_genome, step, span):
    pass

def output_wig(replaced_sorted_file_paths, format, ref_genome, step, span):
    if format == "fixed":
        output_wig_fixed(replaced_sorted_file_paths, ref_genome, step, span)
    elif format == "variable":
        output_wig_vary(replaced_sorted_file_paths, ref_genome, step, span)

