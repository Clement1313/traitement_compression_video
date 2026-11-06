with open("images_stack/0.pgm", "rb") as input: # read pgm
    magic_number = input.read(2)
    input.read(1) # separator
    width = input.read(3)
    input.read(1) # separator
    height = input.read(3)
    input.read(1) # separator
    max_value = input.read(3)
    input.read(1) # separator

    if int(max_value) != 255:
        raise NotImplementedError("To be done...")

    with open("file.ppm", "wb") as out: # write ppm
        out.write(b"P3\n")
        out.write(f"{int(width)} {int(height)}\n".encode())
        out.write(f'{int(max_value)}\n'.encode())
    
        while(True):
            byte = input.read(1)
            if not byte:
                break
            value = byte[0]
            out.write(f"{int(value)} {int(value)} {int(value)} \n".encode())



