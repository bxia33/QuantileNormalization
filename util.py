import psutil, os, numpy, pandas

def generator(path):
    with open(path) as file:
        for line in file:
            value, index = line.split()
            values = [float(value), int(index)]
            yield values

def bash_sort(path, output_path, reverse=False, buffer_size=None, OS=None):
    dir = os.path.dirname(path)
    temp = dir + r"\temp"
    if not os.path.exists(temp):
        os.mkdir(temp)
    cmd = ""
    os.system(cmd)


bash_sort(r"C:\Users\uc214464\Desktop\PycharmProjects\QM\mock.txt", "lala.txt")