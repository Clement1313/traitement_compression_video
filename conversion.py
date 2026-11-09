import cv2
import argparse
import numpy as np
import os


def read_pgm(file_in):
    with open(file_in, "rb") as input:  # read pgm
        input.read(2)  # magic number
        input.read(1)  # separator
        width = int(input.read(3))
        input.read(1)  # separator
        height = int(input.read(3))
        input.read(1)  # separator
        max_value = input.read(3)
        input.read(1)  # separator

        pixels = np.frombuffer(input.read(), dtype=np.uint8).reshape(height, width)

    chroma_width = int(width) // 2
    Y_height = int(height) * 2 // 3
    width = int(width)

    Y = pixels[:Y_height]  # Y_height firsts row, all thje columns
    # Y = bytearray()
    # for i in range(Y_height):
    #     for j in range(int(width)):
    #         Y.append(pixels[i, j])

    U = pixels[Y_height:, :chroma_width]
    # U = bytearray()
    # for i in range(chroma_heigth):
    #     for j in range(chroma_width):
    #         U.append(pixels[Y_height + i, j])

    V = pixels[Y_height:, chroma_width:]
    # V = bytearray()
    # for i in range(chroma_heigth):
    #     for j in range(chroma_width, chroma_width * 2):
    #         V.append(pixels[Y_height + i, j])

    return Y, U, V, Y_height, width, chroma_width, max_value


def YUV_to_RGB(Y, U, V, Y_height, width, chroma_width, max_value):
    img = np.empty((int(Y_height), int(width), 3), dtype=np.uint8)

    for i in range(Y_height):
        for j in range(width):
            y_current = int(Y[i, j]) - 16
            u_current = int(U[(i // 2), (j // 2)]) - 128
            v_current = int(V[(i // 2), (j // 2)]) - 128

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

            img[i, j] = np.array([b_current, g_current, r_current])

    return img


def convert(file_in):
    Y, U, V, Y_height, width, chroma_width, max_value = read_pgm(file_in)
    img = YUV_to_RGB(Y, U, V, Y_height, width, chroma_width, max_value)
    return img


def write_file(file_out, max_value, img):
    height, width, _ = img.shape
    rgb = img[:, :, ::-1].reshape(-1, 3)
    with open(file_out, "w") as f:
        f.write(f"P3\n{width} {height}\n{max_value}\n")
        np.savetxt(f, rgb, fmt="%d")


def display_image(img, ips=1):
    cv2.imshow("Image", img)  # display image
    cv2.waitKey(round(max(1, 1000 / ips)))


def handle_directories(input, out, save, display, ips):
    if not os.path.exists(input):
        raise Exception("Invalid path")
    if os.path.isfile(input):
        img = convert(input)
        if save:
            write_file(out, 255, img)
        if display:
            display_image(img, ips)
    else:
        if save and not os.path.exists(out):
            os.makedirs(out)
        image_pile = []

        names = os.listdir(input)
        sorted_names = []
        for name in names:
            if not name.endswith(".pgm"):
                continue
            sorted_names.append(int(name.split(".")[0]))  # remove extention

        sorted_names = sorted(sorted_names)

        for i, e in enumerate(sorted_names):
            if i % 10 == 0:
                print(f"image {i}...")
            e = str(e)
            e += ".pgm"
            img = convert(os.path.join(input, e))
            if save:
                output_name = os.path.join(out, os.path.splitext(e)[0] + ".ppm")
                write_file(output_name, 255, img)
            if display:
                image_pile.append(img)
        if display:
            for image in image_pile:
                display_image(image, ips)
            cv2.destroyAllWindows()
        print("Done :)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_in")
    parser.add_argument("--save", nargs="?", const="", default=None)
    parser.add_argument("--display", action="store_true")
    parser.add_argument("--ips", type=int, default=None)
    args = parser.parse_args()
    frame_period = os.path.join(args.file_in, "frame_period.txt")
    ips = args.ips
    if ips is None and os.path.exists(frame_period):
        with open(frame_period, "r") as fp:
            ips = round(27000000 / float(fp.read()))
    elif args.ips is None:
        ips = 25
    if os.path.isdir(args.file_in):
        default_out = "out"
    else:
        default_out = "out.ppm"
    if args.save == "" or (args.save is None and not args.display):
        args.save = default_out

    handle_directories(
        args.file_in, args.save, args.save is not None, args.display, ips
    )
