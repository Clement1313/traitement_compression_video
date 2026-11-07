import cv2
import argparse
import numpy as np
import os


def convert(file_in, file_out, save, display):
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

    # create ppm
    out = b""
    if save:
        out = b"P3\n"
        out += f"{int(width)} {int(Y_height)}\n".encode()
        out += f"{int(max_value)}\n".encode()

    # create image for display
    img = np.empty((int(Y_height), int(width), 3), dtype=np.uint8)

    for i in range(Y_height):
        line = ""
        for j in range(width):
            y_current = Y[i * width + j] - 16
            u_current = U[(i // 2) * chroma_width + (j // 2)] - 128
            v_current = V[(i // 2) * chroma_width + (j // 2)] - 128

            r_current = max(
                0,
                min(
                    round(y_current * 1.164 + 1.596 * v_current),
                    int(max_value),
                ),
            )
            g_current = max(
                0,
                min(
                    round(y_current * 1.164 - u_current * 0.392 - v_current * 0.813),
                    int(max_value),
                ),
            )
            b_current = max(
                0,
                min(round(y_current * 1.164 + 2.017 * u_current), int(max_value)),
            )
            if save:
                line += (
                    str(r_current) + " " + str(g_current) + " " + str(b_current) + "\n"
                )

            if display:
                img[i, j] = np.array([b_current, g_current, r_current])
        if save:
            out += line.encode()

    if save and display:
        return out, img

    if save:
        return out, None

    if display:
        return None, img


def save_image(out, file_out):
    with open(file_out, "wb") as out_file:  # write ppm
        out_file.write(out)


def display_image(img):
    cv2.imshow("Image", img)  # display image
    cv2.waitKey(500)


def handle_directories(input, out, save, display):
    if not os.path.exists(input):
        raise Exception("Invalid path")
    if os.path.isfile(input):
        ppm, to_display = convert(input, out, save, display)
        if save:
            save_image(ppm, out)
        if display:
            display_image(to_display)
    else:
        if save and not os.path.exists(out):
            os.makedirs(out)
        if display:
            image_pile = []

        for i, e in enumerate(os.scandir(input)):
            if i % 10 == 0:
                print(f"image {i}...")
            if e.is_file():
                ppm, to_display = convert(e, f"{out}/{e.name}.ppm", save, display)
                if save:
                    name = f"{out}/{os.path.basename(e.name).split('.')[0]}.ppm"
                    save_image(ppm, name)
                if display:
                    image_pile.append(to_display)
                #     display_image(to_display)
        for image in image_pile:
            display_image(image)
            cv2.destroyAllWindows()
        print("Done :)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_in")
    parser.add_argument("--save", nargs="?", const=None, default=None)
    parser.add_argument("--display", action="store_true")
    args = parser.parse_args()
    if args.save is None and not args.display:
        if os.path.isdir(args.file_in):
            args.save = "out"
        else:
            args.save = "out.ppm"
    handle_directories(args.file_in, args.save, args.save is not None, args.display)

# convert("images_stack/0.pgm", "test.ppm")
