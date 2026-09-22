import subprocess

p = subprocess.Popen(
    ["../engine/abc.exe"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

p.stdin.write(b"uci\n")
p.stdin.flush()

while True:
    line = p.stdout.readline()

    print(repr(line))

    if line == b"uciok\r\n":
        break

p.stdin.write(b"ucinewgame\n")
p.stdin.flush()

p.stdin.write(b"go depth 6\n")
p.stdin.flush()

while True:
    line = p.stdout.readline()

    print(repr(line))

    #if line.startswith(b"bestmove"):
    #    break

p.kill()