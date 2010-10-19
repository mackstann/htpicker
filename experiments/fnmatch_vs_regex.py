import sys, fnmatch, re, subprocess, pipes, timeit

if len(sys.argv) < 3:
    print "Usage: {0} <path> <num_iterations>".format(sys.argv[0])
    raise SystemExit(1)

path = sys.argv[1]
num_iterations = int(sys.argv[2])

fnmatch_patterns = ".* *~ *.bak *.nfo *.txt *.url *.sfv *.part*.rar".split()
regex = re.compile(r'^(?:\..*|.*~|.*\.bak|.*\.nfo|.*\.txt|.*\.url|.*\.sfv|.*\.part.*\.rar)$')
separate_regexes = (
    re.compile(r'^\..*$'),
    re.compile(r'^.*~$'),
    re.compile(r'^.*\.bak$'),
    re.compile(r'^.*\.nfo$'),
    re.compile(r'^.*\.txt$'),
    re.compile(r'^.*\.url$'),
    re.compile(r'^.*\.sfv$'),
    re.compile(r'^.*\.part.*\.rar$'),
)

proc = subprocess.Popen("find {0}".format(pipes.quote(path)),
        shell=True, stdout=subprocess.PIPE)
stdout, stderr = proc.communicate()

lines = map(str.lower, stdout.splitlines())
num_files = len(lines)

def test_fnmatch():
    fn = fnmatch.fnmatchcase
    for filename in lines:
        for pattern in fnmatch_patterns:
            fn(filename, pattern)

def test_fnmatch_filter():
    fn = fnmatch.filter
    for pattern in fnmatch_patterns:
        fn(lines, pattern)

def test_regex():
    fn = regex.match
    for filename in lines:
        fn(filename)

def test_separate_regexes():
    for regex in separate_regexes:
        fn = regex.match
        for filename in lines:
            fn(filename)

t = timeit.Timer(stmt=test_fnmatch)
print "fnmatch: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_fnmatch_filter)
print "fnmatch filter: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_regex)
print "regex: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_separate_regexes)
print "separate regexes: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

# and the results are...
# fnmatch: 9.09 usec per file
# fnmatch filter: 6.01 usec per file
# regex: 2.64 usec per file
# separate regexes: 4.83 usec per file
