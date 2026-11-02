import subprocess, sys, os, shlex
here = os.path.dirname(os.path.abspath(__file__))
log = open(os.path.join(here, "_run_all.txt"), "w", encoding="utf-8")
# each argument is "script.py [args...]" (quote it to pass arguments to a script)
for s in sys.argv[1:]:
    parts = shlex.split(s, posix=False)
    r = subprocess.run([sys.executable, os.path.join(here, parts[0])] + parts[1:], cwd=here, capture_output=True, text=True)
    log.write("== %s rc=%d\n%s\n%s\n" % (s, r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    log.flush()
log.write("ALLDONE\n")
