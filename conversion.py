
def convert(file_in, file_out):
    with open(file_in, "rb") as input: # read pgm
        input.read(2) # magic number
        input.read(1) # separator
        width = input.read(3)
        input.read(1) # separator
        height = input.read(3)
        input.read(1) # separator
        max_value = input.read(3)
        input.read(1) # separator

        if int(max_value) > 255:
            pixel_size = 2
        else:
            pixel_size = 1

        with open(file_out, "wb") as out: # write ppm
            out.write(b"P3\n")
            out.write(f"{int(width)} {int(height)}\n".encode())
            out.write(f'{int(max_value)}\n'.encode())
        
            while(True):
                byte = input.read(pixel_size)
                if not byte:
                    break
                value = byte[0]
                out.write(f"{int(value)} {int(value)} {int(value)} \n".encode()) # RGB values


convert("images_stack/0.pgm", "test.ppm")


