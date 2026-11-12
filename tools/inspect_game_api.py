"""List declared Java fields/methods from a local game JAR without loading it."""
import argparse
import re
import struct
from io import BytesIO
from zipfile import ZipFile


def members(data, metadata=None):
    stream = BytesIO(data)

    def number(size):
        return int.from_bytes(stream.read(size), "big")

    if number(4) != 0xCAFEBABE:
        raise ValueError("Not a Java class")
    stream.read(4)
    pool = [None] * number(2)
    index = 1
    while index < len(pool):
        tag = number(1)
        if tag == 1:
            pool[index] = stream.read(number(2)).decode("utf-8", errors="replace")
        elif tag in (3, 4):
            stream.read(4)
        elif tag in (5, 6):
            stream.read(8)
            index += 1
        elif tag == 7:
            pool[index] = number(2)
        elif tag in (8, 16, 19, 20):
            stream.read(2)
        elif tag in (9, 10, 11, 12):
            pool[index] = (tag, number(2), number(2))
        elif tag in (17, 18):
            stream.read(4)
        elif tag == 15:
            stream.read(3)
        else:
            raise ValueError(f"Unknown constant pool tag {tag}")
        index += 1
    _, _, superclass = struct.unpack(">HHH", stream.read(6))
    if metadata is not None:
        metadata['superclass'] = pool[pool[superclass]] if superclass else None
    interfaces = [number(2) for _ in range(number(2))]
    if metadata is not None:
        metadata['interfaces'] = [pool[pool[i]] for i in interfaces]
        metadata['pool'] = pool
        metadata['bytecode'] = {}
    for kind in ("field", "method"):
        for _ in range(number(2)):
            flags, name, descriptor = struct.unpack(">HHH", stream.read(6))
            yield kind, flags, pool[name], pool[descriptor]
            for _ in range(number(2)):
                attribute = pool[number(2)]
                payload = stream.read(number(4))
                if metadata is not None and attribute == 'Code':
                    size = int.from_bytes(payload[4:8], 'big')
                    metadata['bytecode'][pool[name] + pool[descriptor]] = payload[8:8+size]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jar")
    parser.add_argument("classes", nargs="+")
    parser.add_argument("--filter", default=".")
    parser.add_argument("--code", action="store_true", help="Show raw method bytecode and constant references")
    args = parser.parse_args()
    with ZipFile(args.jar) as jar:
        for name in args.classes:
            print(name)
            metadata = {}
            declared = list(members(jar.read(name.replace(".", "/") + ".class"), metadata))
            def describe(index):
                value = metadata['pool'][index]
                if isinstance(value, int):
                    return describe(value)
                if isinstance(value, tuple):
                    return describe(value[1]) + '.' + describe(value[2])
                return str(value)
            for kind, flags, member, descriptor in declared:
                if re.search(args.filter, member):
                    print(f"  {kind} 0x{flags:04x} {member} {descriptor}")
                    if args.code and member + descriptor in metadata['bytecode']:
                        code = metadata['bytecode'][member + descriptor]
                        print('    code:', code.hex(' '))
                        for index, value in enumerate(metadata['pool']):
                            if isinstance(value, tuple) and value[0] in (9, 10, 11):
                                operand = index.to_bytes(2, 'big')
                                if any(bytes([opcode]) + operand in code for opcode in range(0xb2, 0xba)):
                                    print('    reference:', describe(index))
