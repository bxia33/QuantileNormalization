import psutil, os, numpy, pandas

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

