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
    # img = np.empty((int(Y_height), int(width), 3), dtype=np.uint8)

    # for i in range(Y_height):
    #     for j in range(width):
    #         y_current = int(Y[i, j]) - 16
    #         u_current = int(U[(i // 2), (j // 2)]) - 128
    #         v_current = int(V[(i // 2), (j // 2)]) - 128

    #         r_current = max(
    #             0,
    #             min(
    #                 round(y_current * 1.164 + 1.596 * v_current),
    #                 int(max_value),
    #             ),
    #         )
    #         g_current = max(
    #             0,
    #             min(
    #                 round(y_current * 1.164 - u_current * 0.392 - v_current * 0.813),
    #                 int(max_value),
    #             ),
    #         )
    #         b_current = max(
    #             0,
    #             min(round(y_current * 1.164 + 2.017 * u_current), int(max_value)),
    #         )

    #         img[i, j] = np.array([b_current, g_current, r_current])

    # return img

    # ==============================ATTENTION CODE IA==========================================
    # A SUPPRIMER ET DECOMMENTER LE CODE CI DESSUS.
    y = Y.astype(np.float32) - 16
    u = U.astype(np.float32) - 128
    v = V.astype(np.float32) - 128

    u = np.repeat(np.repeat(u, 2, axis=0), 2, axis=1)
    v = np.repeat(np.repeat(v, 2, axis=0), 2, axis=1)

    r = 1.164 * y + 1.596 * v
    g = 1.164 * y - 0.392 * u - 0.813 * v
    b = 1.164 * y + 2.017 * u

    img = np.stack([b, g, r], axis=-1)  # ordre BGR, forme (480, 720, 3)
    return np.clip(np.round(img), 0, int(max_value)).astype(np.uint8)
    # ==========================================================================================


def desentrelacement(field, top_field_first):
    top = field[0::2, :]
    bottom = field[1::2, :]
    top = np.repeat(top, 2, axis=0)
    bottom = np.repeat(bottom, 2, axis=0)

    return (top, bottom) if top_field_first else (bottom, top)


def convert(file_in, bob, flags, top_field_first_option):
    Y, U, V, Y_height, width, chroma_width, max_value = read_pgm(file_in)
    progressive_frame, top_field_first, reapeat_first_field = None, None, None
    if bob:
        if flags:
            flags = flags.split(" ")
            progressive_frame, top_field_first, reapeat_first_field = (
                int(flags[0]),
                int(flags[1]),
                int(flags[2]),
            )
            top_field_first = (
                top_field_first_option
                if (top_field_first_option is not None)
                else top_field_first
            )
            if not progressive_frame:
                top_Y, bottom_Y = desentrelacement(Y, top_field_first)
                top_U, bottom_U = desentrelacement(U, top_field_first)
                top_V, bottom_V = desentrelacement(V, top_field_first)

                img_top = YUV_to_RGB(
                    top_Y, top_U, top_V, Y_height, width, chroma_width, max_value
                )
                img_bottom = YUV_to_RGB(
                    bottom_Y,
                    bottom_U,
                    bottom_V,
                    Y_height,
                    width,
                    chroma_width,
                    max_value,
                )
                return [img_top, img_bottom]

    img = YUV_to_RGB(Y, U, V, Y_height, width, chroma_width, max_value)
    return [img]


def write_file(file_out, max_value, img):
    height, width, _ = img.shape
    rgb = img[:, :, ::-1].reshape(-1, 3)
    with open(file_out, "w") as f:
        f.write(f"P3\n{width} {height}\n{max_value}\n")
        np.savetxt(f, rgb, fmt="%d")


def display_image(img, ips=1):
    cv2.imshow("Image", img)  # display image
    cv2.waitKey(round(max(1, 1000 / ips)))


def handle_directories(input, out, save, display, ips, bob, top_field_first):
    if not os.path.exists(input):
        raise Exception("Invalid path")

    data_dir = input if os.path.isdir(input) else (os.path.dirname(input) or ".")
    flags = None
    flags_file = os.path.join(data_dir, "flags.txt")
    if bob and os.path.exists(flags_file):
        with open(flags_file, "r") as f:
            flags = f.readlines()

    if os.path.isfile(input):
        flag = None
        base = os.path.splitext(os.path.basename(input))[0]
        if flags is not None and base.isdigit() and int(base) < len(flags):
            flag = flags[int(base)]
        imgs = convert(input, bob, flag, top_field_first)
        if save:
            name, ext = os.path.splitext(out)
            write_file(f"{name}{ext}", 255, imgs[0])
            if len(imgs) == 2:
                write_file(f"{name}_1{ext}", 255, imgs[1])
        if display:
            for img in imgs:
                display_image(img, ips * len(imgs))
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
        index_img = 0
        for i, e in enumerate(sorted_names):
            if i % 10 == 0:
                print(f"image {i}...")
            e = str(e)
            e += ".pgm"
            flag = None
            if flags is not None:
                flag = flags[i]
            imgs = convert(os.path.join(input, e), bob, flag, top_field_first)
            if save:
                output_name = os.path.join(out, str(index_img) + ".ppm")
                index_img += 1
                write_file(output_name, 255, imgs[0])
                if len(imgs) == 2:  # bob
                    output_name = os.path.join(out, str(index_img) + ".ppm")
                    index_img += 1
                    write_file(output_name, 255, imgs[1])
            if display:
                for img in imgs:
                    image_pile.append((img, ips * len(imgs)))
        if display:
            for image, image_ips in image_pile:
                display_image(image, image_ips)
            cv2.destroyAllWindows()
        print("Done :)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_in")
    parser.add_argument("--save", nargs="?", const="", default=None)
    parser.add_argument("--display", action="store_true")
    parser.add_argument("--ips", type=int, default=None)
    parser.add_argument("--bottom_field_first", action="store_true", default=None)
    parser.add_argument("--bob", action="store_true")
    args = parser.parse_args()
    data_dir = (
        args.file_in
        if os.path.isdir(args.file_in)
        else (os.path.dirname(args.file_in) or ".")
    )
    frame_period = os.path.join(data_dir, "frame_period.txt")
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
        args.file_in,
        args.save,
        args.save is not None,
        args.display,
        ips,
        args.bob,
        (not args.bottom_field_first)
        if (args.bottom_field_first is not None)
        else None,
    )
