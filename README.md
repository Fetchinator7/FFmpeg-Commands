## This repository primarily stores the code for ffmpeg methods I use in other projects.

To install ffmpeg on a mac run this command in the terminal:
```
brew install ffmpeg
```
See [Download Homebrew](https://brew.sh/) and [Download ffmpeg](https://ffmpeg.org/)

Python3 is also required. See [Download Python3](https://www.python.org/downloads/).

Some code is still in experimental stages, but everything in the `FileOperations` class should be ready for use.
## Using it:

The module is setup to only accept pathlib paths so that will need to be imported into any files you'll be using to call the ffmpeg commands from.
``` python
import pathlib
import ffmpeg_cmds as fc

input_folder = pathlib.Path('Input_Folder')
output_folder = pathlib.Path('Different_Folder')
```
See [Python Pathlib](https://docs.python.org/3/library/pathlib.html) for more path info.

An input file and different output folder always have to be specified in the class initiation.
I personally find it easiest to specify an input folder and loop the files so the individual file paths don't have to be specified with a simple loop.
```python
for file in input_folder.iterdir():
```

But there are more optional arguments.
For example, to extract the artwork from a file and include the entire ffmpeg output do:
```python
fc.FileOperations(file, generic_dir, print_ren_info=True).extract_artwork()
```
All output messages can be toggled. See the [FileOperations __init__](https://github.com/Fetchinator7/System-Commands/blob/master/ffmpeg_cmds.py#L39-L49)

**(Required class initiation arguments have been omitted in the following method calls for the sake of conciseness.)**

Other methods have multiple arguments that have defaults but still require at least one to be specified like the `trim` method arguments:

```python
fc.FileOperations().trim(start_timecode='', stop_timecode='', codec_copy=False)
```

For example, to trim a video so it starts 30 seconds in and gos until the end do:

```python
fc.FileOperations().trim(start_timecode='30')
```

But to stop the video 1 hour, 6 minutes and 5.7 seconds in do:

```python
fc.FileOperations().trim(stop_timecode='1:06:05.7')
```

So despite the arguments having defaults, running `trim` without specifying either `start_timecode` or `stop_timecode` will still result in an error.
Others method arguments are mutually exclusive like `loop` can either have the `num_loop_times` or `loop_to_hours` argument, but it should display errors if a mutually exclusive argument is given twice.

```python
loop(num_loop_times=0, loop_to_hours=0, codec_copy=False):
```

**NOTE:**
This isn't magic. This ffmpeg script is pretty good at verifying valid input, but there are some circumstances where the user has to fix the input such as a corrupted input.

## Advanced uses:

This can be hooked up for advanced uses such as calling a render method from a node.js server using the command line by passing in the right arguments:

```shellscript
path/to/file.py "input_file" "output_folder" "render_method" "render_method_argument"
```

Then in a python file to interpret the command line inputs:

```python
import pathlib
import ffmpeg_cmds as fc
import sys

input_file = pathlib.Path(sys.argv[1])
output_folder = pathlib.Path(sys.argv[2])
render_method = sys.argv[3]
render_method_argument = sys.argv[4]
getattr(fc.FileOperations(input_file, output_folder), render_method)(render_method_argument)
```

For example to trim so it stops after 30 seconds:

```python
python3 calling_ffmpeg.py Input.mp4 /out_folder "trim" "30"
```

(The '' is there because the stop_timecode is the second optional argument.)

```python
getattr(fc.FileOperations(input_file, output_folder), render_method)('', render_method_argument)
```
