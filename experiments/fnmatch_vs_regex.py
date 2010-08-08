import sys, fnmatch, re, subprocess, pipes, timeit

if len(sys.argv) < 3:
    print "Usage: {0} <path> <num_iterations>".format(sys.argv[0])
    raise SystemExit(1)

path = sys.argv[1]
num_iterations = int(sys.argv[2])

fnmatch_patterns = "*~ *.bak *.nfo *.txt *.url *.sfv *.part*.rar".split()
regex = re.compile(r'.*(?:~|\.bak|\.nfo|\.txt|\.url|\.sfv|\.part.*\.rar)$', re.I)
separate_regexes = (
    re.compile(r'.*~$', re.I),
    re.compile(r'.*\.bak$', re.I),
    re.compile(r'.*\.nfo$', re.I),
    re.compile(r'.*\.txt$', re.I),
    re.compile(r'.*\.url$', re.I),
    re.compile(r'.*\.sfv$', re.I),
    re.compile(r'.*\.part.*\.rar$', re.I),
)

proc = subprocess.Popen("find {0}".format(pipes.quote(path)),
        shell=True, stdout=subprocess.PIPE)
stdout, stderr = proc.communicate()

lines = stdout.splitlines()
num_files = len(lines)

def test_fnmatch():
    for filename in lines:
        for pattern in fnmatch_patterns:
            fnmatch.fnmatch(filename, pattern)

def test_fnmatch_filter():
    for pattern in fnmatch_patterns:
        fnmatch.filter(lines, pattern)

def test_regex():
    for filename in lines:
        regex.match(filename)

def test_separate_regexes():
    for filename in lines:
        for regex in separate_regexes:
            regex.match(filename)

t = timeit.Timer(stmt=test_fnmatch)
print "fnmatch: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_fnmatch_filter)
print "fnmatch filter: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_regex)
print "regex: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

t = timeit.Timer(stmt=test_separate_regexes)
print "separate regexes: %.2f usec per file" % (1000000 * t.timeit(number=num_iterations)/num_iterations/num_files)

# and the results are...
# fnmatch: 19.68 usec per file
# fnmatch filter: 4.75 usec per file
# regex: 13.68 usec per file
# separate regexes: 16.95 usec per file
