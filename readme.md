# Run conversion.py
```
uv sync
uv run conversion.py image_path [--display --save output_file.ppm]
```
`--display`: optional parameter, display image in window. \
`--save`: optional parameter, save image in `output_file.ppm` if specified or `out.ppm` if no file provided. \
`--ips`: optional parameter, usefull only if display flag is active and if a pile of image is in input. image displaying rate. 

If no parameters passed, image is save in `out.ppm` but is not displayed