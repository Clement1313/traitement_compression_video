def convert(file_in, file_out):
    with open(file_in, "rb") as input:  # read pgm
        input.read(2)  # magic number
        input.read(1)  # separator
        width = input.read(3)
        input.read(1)  # separator
        height = input.read(3)
        input.read(1)  # separator
        max_value = input.read(3)
        input.read(1)  # separator

        pixels = input.read()

    if int(max_value) > 255:
        pixel_size = 2
    else:
        pixel_size = 1

    chroma_width = int(width) // 2
    Y_height = int(height) * 2 // 3
    chroma_heigth = int(Y_height) // 2
    width = int(width)

    Y = bytearray()
    for i in range(Y_height):
        for j in range(int(width)):
            Y.append(pixels[i * width + j])

    U = bytearray()
    for i in range(chroma_heigth):
        for j in range(chroma_width):
            U.append(pixels[(Y_height + i) * width + j])

    V = bytearray()
    for i in range(chroma_heigth):
        for j in range(chroma_width, chroma_width * 2):
            V.append(pixels[(Y_height + i) * width + j])

    with open(file_out, "wb") as out:  # write ppm
        out.write(b"P3\n")
        out.write(f"{int(width)} {int(Y_height)}\n".encode())
        out.write(f"{int(max_value)}\n".encode())

        for i in range(Y_height):
            line = ""
            for j in range(width):
                y_current = Y[i * width + j]
                u_current = U[(i // 2) * chroma_width + (j // 2)]
                v_current = V[(i // 2) * chroma_width + (j // 2)]

                r_current = max(
                    0, min(round(y_current + 1.140 * v_current), int(max_value))
                )
                g_current = max(
                    0,
                    min(
                        round(y_current - 0.395 * u_current - 0.581 * v_current),
                        int(max_value),
                    ),
                )
                b_current = max(
                    0, min(round(y_current + 2.032 * u_current), int(max_value))
                )

                line += (
                    str(r_current) + " " + str(g_current) + " " + str(b_current) + "\n"
                )
            out.write(line.encode())


convert("images_stack/0.pgm", "test.ppm")
