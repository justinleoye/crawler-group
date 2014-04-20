import struct

def unpack (format, buffer) :
    while True :
        pos = format.find ('z')
        if pos>=0:
            asciiz_start = struct.calcsize (format[:pos])
            asciiz_len = buffer[asciiz_start:].find('\0')
            format = '%s%dsx%s' % (format[:pos], asciiz_len, format[pos+1:])
        else:
            pos = format.find ('Z')
            if pos>=0:
                start = struct.calcsize (format[:pos])
                end = struct.calcsize (format[pos+1:])
                asciiz_len = len(buffer)-start-end
                if asciiz_len<0:
                    raise Exception("invalid format: %s for buffer: [%s]" % (format, buffer))
                format = '%s%ds%s' % (format[:pos], asciiz_len, format[pos+1:])
            #can only support one Z
            break
    return struct.unpack (format, buffer)

def pack (format, *args) :
    new_format = ''
    arg_number = 0
    for c in format :
        if c == 'z' :
            new_format += '%ds' % (len(args[arg_number])+1)
            arg_number += 1
        elif c == 'Z' :
            new_format += '%ds' % len(args[arg_number])
            arg_number += 1
        else :
            new_format += c
            if c in 'cbB?hHiIlLqQfdspP' :
                arg_number += 1
    return struct.pack (new_format, *args)


if __name__ == '__main__':
    """
    print repr(pack('>Zi', 'abc', 2))
    print repr(pack('>zi', 'abc', 2))

    print repr(pack('>izizi', 1, 'abc', 2, 'D', 3))
    print repr(pack('>iziZi', 1, 'abc', 2, 'D', 3))

    print repr(pack('3si', 'abc', 2))
    print repr(pack('>Zi',  'A', 2))
    """

    assert pack('>iziZi', 1, 'abc', 2, 'd', 3)==pack('>i4si1si', 1, 'abc', 2, 'd', 3)
    assert pack('>izizi', 1, 'abc', 2, 'd', 3)==pack('>i4si2si', 1, 'abc', 2, 'd', 3)
    assert pack('>iziZi', 1, 'abc', 2, 'd', 3)==pack('>i4si1si', 1, 'abc', 2, 'd', 3)


