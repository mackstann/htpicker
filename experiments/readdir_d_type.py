import os, timeit, ctypes
from ctypes import c_char_p, c_int, c_long, c_ushort, c_byte, c_char
from ctypes.util import find_library

class c_DIR(ctypes.Structure):
    pass
c_DIR_p = ctypes.POINTER(c_DIR)

class c_dirent(ctypes.Structure):
    """Directory entry"""
    # FIXME not sure these are the exactly correct types!
    _fields_ = (
        ('d_ino', c_long),        # inode number
        ('d_off', c_long),        # offset to the next dirent
        ('d_reclen', c_ushort),   # length of this record
        ('d_type', c_byte),       # type of file; not supported by all file system types
        ('d_name', c_char * 256), # filename
    )
c_dirent_p = ctypes.POINTER(c_dirent)

c_libc = ctypes.CDLL(find_library("c"))

opendir = c_libc.opendir
opendir.argtypes = [c_char_p]
opendir.restype = c_DIR_p

readdir = c_libc.readdir
readdir.argtypes = [c_DIR_p]
readdir.restype = c_dirent_p

closedir = c_libc.closedir
closedir.argtypes = [c_DIR_p]
closedir.restype = c_int

def listdir(path):
    dir_p = opendir(path)
    files = []
    while True:
        p = readdir(dir_p)
        if not p:
            break
        name = p.contents.d_name
        if name not in (".", ".."):
            files.append((name, p.contents.d_type))
    closedir(dir_p)
    return files

num_iterations = 1
num_files = 100000

directory = '/tmp/readdir_d_type_test'
try:
    os.mkdir(directory)
except OSError:
    if not os.path.exists(directory):
        raise

    os.system("rm -rf " + directory)
    os.mkdir(directory)

for i in range(num_files):
    f = open(directory + '/' + str(i), 'w')
    f.close()

def test_python_os_listdir_lstat():
    for name in os.listdir(directory):
        os.lstat(directory + '/' + name)
        pass

def test_ctypes_readdir_d_type():
    for name in listdir(directory):
        pass

t = timeit.Timer(stmt=test_python_os_listdir_lstat)
print "python listdir()/lstat(): %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_ctypes_readdir_d_type)
print "ctypes readdir()/d_type: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

os.system("rm -rf " + directory)
