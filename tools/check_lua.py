from pathlib import Path
import sys
from lupa.lua51 import LuaRuntime
root = Path(__file__).resolve().parents[1]
lua = LuaRuntime(unpack_returned_tuples=True)
compile_lua = lua.eval('function(source, name) local f, err = loadstring(source, name); return f ~= nil, err end')
files = sorted((root / '42/media/lua').rglob('*.lua'))
if not files:
    sys.exit('No Lua files found')
failed = 0
for path in files:
    ok, error = compile_lua(path.read_bytes(), '@' + str(path))
    if not ok:
        failed += 1
        print(error)
print(f'Lua 5.1 syntax: {len(files) - failed}/{len(files)} passed; {failed} failed')
sys.exit(bool(failed))
