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

def generator_one(path):
    with open(path, "r") as file:
        for line in file:
            value  = float(line.strip())
            yield value


def create_file(path):
    file = open(path, "w")
    file.close()

def save_result(result, output_path):
    output_file = open(output_path, "a")
    writer = csv.writer(output_file)
    writer.writerow(result)
    output_file.close()

def load_wig_fixed(path, ref_genome, zip):
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
    create_file(output_path)

    if zip:
        open_file = gzip.open(path, "r")
    else:
        open_file = open(path, "r")
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
                        save_result(result, output_path)
                        del result[:]
                        gc.collect()
                        size = 0
    if result:
        save_result(result, output_path)
        del result[:]
        gc.collect()
    open_file.close()
    return

def load_wig_vary(path, ref_genome, zip):
    pass

def load_wig(*files, ref_genome):
    file_paths = list(files)
    for path in file_paths:
        if path[-3:] == 'wig':
            open_file = open(path, "r")
            zip = False
        elif path[-6:] == 'wig.gz':
            open_file = gzip.open(path, "r")
            zip = True
        for line in open_file:
            if not line.strip():
                if line[0:9]=='fixedStep':
                    load_wig_fixed(path, ref_genome, zip)
                    open_file.close()
                    break
                elif line[0:3]=='var':
                    load_wig_vary(path, ref_genome, zip)
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
    create_file(path_avg)
    length = len(sorted_file_paths)

    for path in sorted_file_paths:
        iters.append(generator(path))
    while True:
        values = [next(x, [0, 0])[0] for x in iters]
        avg = sum(values)/float(length)
        if avg != 0:
            result.append([avg])
            size += 1
            if size > 1000000:
                save_result(result, path_avg)
                del result[:]
                gc.collect()
                size = 0
        else:
            break
    if result:
        save_result(result, path_avg)
        del result[:]
        gc.collect()
    return

def replace_avg(sorted_file_paths, average_path):
    for path in sorted_file_paths:
        replaced_file_path = path[:-4] + "relaced.txt"
        result = []
        size = 0
        sorted_file = generator(path)
        average_file = generator_one(average_path)
        while True:
            cur_avg = next(average_file, 0)
            if cur_avg != 0:
                result.append([next(sorted_file)[1], cur_avg])
                size += 1
                if size > 1000000:
                    save_result(result, replaced_file_path)
                    del result[:]
                    gc.collect()
                    size = 0
            else:
                break
        if result:
            save_result(result, replaced_file_path)
            del result[:]
            gc.collect()
    return

def output_wig_fixed(replaced_sorted_file_paths, ref_genome, step, span):
    ref_genome_sizes = master_genome_sizes[ref_genome]
    sorted_sizes = sorted(ref_genome_sizes.items(), key=operator.itemgetter(1))

    for path in replaced_sorted_file_paths:
        output_path = path[:-4] + "output.wig"
        create_file(output_path)
        iter = peekable(generator(path))

        for chrom in sorted_sizes:
            result = []
            size = 0
            with open(output_path, "a") as file:
                file.write("fixedStep chrom="+chrom+" start=1  step="+str(step)+" span="+str(step)+"\n")
                chrom_size = chrom[1][1]- chrom[1][0] + 1
                position = chrom[1][0]
                while chrom_size >= 0:
                    chrom_size -= step
                    current = iter.peek()
                    if current[0] == position:
                        current = iter.__next__()
                        result.append([current[1]])
                        size +=1
                        if size > 1000000:
                            writer = csv.writer(file)
                            writer.writerow(result)
                            del result[:]
                            gc.collect()
                            size = 0
                    else:
                        result.append([0])
                    position += step
                    size += 1
                    if size > 1000000:
                        writer = csv.writer(file)
                        writer.writerow(result)
                        del result[:]
                        gc.collect()
                        size = 0
                if result:
                    writer = csv.writer(file)
                    writer.writerow(result)
                    del result[:]
                    gc.collect()
    return

def output_wig_vary(replaced_sorted_file_paths, ref_genome, step, span):
    pass

def output_wig(replaced_sorted_file_paths, format, ref_genome, step, span):
    if format == "fixed":
        output_wig_fixed(replaced_sorted_file_paths, ref_genome, step, span)
    elif format == "variable":
        output_wig_vary(replaced_sorted_file_paths, ref_genome, step, span)

