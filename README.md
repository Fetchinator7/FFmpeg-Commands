# This repository primarily stores the code for ffmpeg methods I use in other projects

[Video-Upload-Editor](https://github.com/Fetchinator7/Video-Upload-Editor)

## Methods

This just lists the different methods available. See the files themselves for method explanations.

### [FileOperations init](hhttps://github.com/Fetchinator7/FFmpeg-Commands/blob/ecb1ef73118d1ad490acaf511a442a73ef2a4ec4/FileOperations.py#L13-L21)

- loudnorm_stereo(custom_db=**String**, aud_only=**Boolean**, print_vol_value=**True**, _do_render=**Boolean**)

- embed_artwork(in_artwork=**FilePath**)
- concat(self, new_basename=**String**, new_ext=**String**, codec_copy=**Boolean**):
- compress_using_h265_and_norm_aud(self, new_res_dimensions=**String**, insert_pixel_format=**Boolean**, video_only=**Boolean**, custom_db=**String**, print_vol_value=**Boolean**, maintain_multiple_aud_strms=**Boolean**):
- rm_begin_end_silence()
- fade_begin_and_or_end__audio_and_or_video(fade_vid=**Boolean**, fade_aud=**Boolean**, fade_begin=**Boolean**, fade_end=**Boolean**, fade_dur_sec=**Int**, fade_out_at_sec=**Int**)
- change_metadata(metadata_keyword=**String**, ...)
- trim(start_timecode=**'String timecode'**, stop_timecode=**'String timecode'**, codec_copy=**Bool**, verify_trim_ranges=**Bool**)
- loop(num_loop_times=**Int**, loop_to_hours=**Int**, codec_copy=**Bool**)
- speed(playback_speed=**String**, add_speed_to_basename=**Boolean**)
- reverse()
- extract_artwork()
- copy_over_metadata(copy_this_metadata_file=**FilePath**, copy_chapters=**Boolean**)
- change_volume(custom_db=**String**, aud_only=**Boolean**, print_vol_value=**Boolean**)
- change_file_name_and_meta_title(new_title=**String**)
- rm_artwork()
- change_ext(new_ext=**String**)
- extract_frames(new_out_dir=**Boolean** Or **FilePath**)
- change_vid_aud(in_aud_path_list=**List**, shortest=**Boolean**)
- add_aud_stream_to_vid(in_aud_path_list=**List**, codec_copy=**Boolean**, length_vid=**Boolean**)
- extract_audio(out_aud_ext=**String**, order_out_names=**Boolean**)
- pan_audio(pan_strm=**List**)
- change_image_resolution(keep_aspect_ratio_input_width=**String**, conform_to_dimensions=**String**)
- crop_detect_black_bars()
- rotate_vid_frame(rotate_frame_by_degrees=**String**)
- rotate_footage(self, rotate_footage_by_degrees=**String**, hflip=**Boolean**, vflip=**Boolean**
- embed_subs(in_subs_list)
- extract_subs(self, include_other_metadata=**Boolean**):
- rm_subs()
- embed_chapters(self, timecode_title_list=**List**, add_chap_headings=**Boolean**, print_new_chapters=**Boolean**):
- rm_chapters():

Still in development:

- two_separate_stereo_aud_files_to_one_stereo_aud_file(right_aud_in_path=**FilePath**)
- crop()

### MetadataAcquisition init)

- return_metadata(metadata_keyword=**String**, ...):
- return_stream_types()
- extract_metadata_txt_file()

Note: The `Visualizer` code is still in experimental stages, but everything else should be ready for use.

## Installation

To install ffmpeg on a mac run this command in the terminal:

```shellscript
brew install ffmpeg
```

See [Download Homebrew](https://brew.sh/) and [Download ffmpeg](https://ffmpeg.org/)

Python3 is also required. See [Download Python3](https://www.python.org/downloads/).

## Using it

The module is setup to only accept pathlib paths so that will need to be imported into any files you'll be using to call the ffmpeg commands from.

``` python
import pathlib
import ffmpeg_cmds as fc

input_folder = pathlib.Path('Input_Folder')
output_folder = pathlib.Path('Different_Folder')
```

See [Python Pathlib](https://docs.python.org/3/library/pathlib.html) for more pathlib info.

An input file and different output folder always have to be specified in the class initiation.

```python
fc.FileOperations(file, output_directory)
```

I personally find it easiest to specify an input folder and loop through the folder's contents so the individual file paths don't have to be specified. For example, to extract the artwork for each file in the `input_folder` do:

```python
for file in input_folder.iterdir():
    fc.FileOperations(file, output_directory).extract_artwork()
```

But there are more optional arguments.
For example, to extract the artwork from a file and include the entire ffmpeg output do:

```python
fc.FileOperations(file, output_directory, print_ren_info=True).extract_artwork()
```

All output messages can be toggled. For more details see the [FileOperations __init__](hhttps://github.com/Fetchinator7/FFmpeg-Commands/blob/ecb1ef73118d1ad490acaf511a442a73ef2a4ec4/FileOperations.py#L13-L21)

## **(Required class initiation arguments have been omitted in the following method calls for the sake of conciseness.)**

Some methods also take input parameters, such as the `trim` method.

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

However, some methods like the `trim` method have multiple arguments with default values, but still require at least one argument to be specified.

```python
fc.FileOperations().trim(start_timecode='', stop_timecode='', codec_copy=False)
```

So despite the arguments having defaults, running `trim` without specifying either `start_timecode` or `stop_timecode` will still result in an error.

Others method arguments are mutually exclusive like `loop` can either have the `num_loop_times` or `loop_to_hours` argument, but it should display errors if a mutually exclusive argument is given twice.

```python
loop(num_loop_times=0, loop_to_hours=0, codec_copy=False):
```

**NOTE:**
This isn't magic. This ffmpeg script is pretty good at verifying valid input, but there are some circumstances where the user has to fix the input such as a corrupted input.

## Advanced uses

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
