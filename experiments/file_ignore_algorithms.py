import sys, timeit, subprocess, pipes, re

if len(sys.argv) < 3:
    print "Usage: {0} <path> <num_iterations>".format(sys.argv[0])
    raise SystemExit(1)

path = sys.argv[1]
num_iterations = int(sys.argv[2])

regex = re.compile(r'^(?:\..*|.*~|.*\.bak|.*\.nfo|.*\.txt|.*\.url|.*\.sfv|.*\.part.*\.rar)$')

proc = subprocess.Popen("find {0}".format(pipes.quote(path)),
        shell=True, stdout=subprocess.PIPE)
stdout, stderr = proc.communicate()

lines = stdout.splitlines()
num_files = len(lines)

def test_sets():
    ignore_files = set(regex.match(filename) for filename in lines)
    listing = set(lines)
    listing.difference_update(ignore_files)
    listing = sorted(listing, key=str.lower)

def test_brute():
    listing = sorted([
        filename for filename in lines
        if not regex.match(filename)
    ], key=str.lower)

t = timeit.Timer(stmt=test_sets)
print "sets: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_brute)
print "brute: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

# results:
# sets: 6.25 usec per file
# brute: 5.38 usec per file
