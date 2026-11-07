# Sends a script file to the running Mechanical session and prints the result.
import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from ansys.mechanical.core import connect_to_mechanical
app = connect_to_mechanical(ip="127.0.0.1", port=10000, cleanup_on_exit=False)
code = open(sys.argv[1], encoding="utf-8").read()
out = app.run_python_script(code, enable_logging=True)
print(out)
