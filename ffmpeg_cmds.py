# This script is to provide functions/automation for ffmpeg commands I typically use. Dependencies: ffmpeg (and ffprobe).
# AtomicParsley, and of course python with its built in modules.

import datetime as dates
import math
import pathlib as paths
import shutil
import subprocess as sub
import time


def _is_type_or_print_err_and_quit(in_type, target_type, in_type_str):
	"""Function to confirm method input(s) are the correct type """
	if in_type is not target_type:
		if target_type is paths.Path:
			# To keep this cross-platform the target_type = paths.Path() so it knows which type to check
			# and then confrim it's actually a Posix or Windows path.
			if in_type is not paths.PosixPath and in_type is not paths.WindowsPath:
				target_type_err_str = 'a pathlib PosixPath or WindowsPath'
			else:
				return False
		elif target_type is int:
			target_type_err_str = 'an int'
		elif target_type is float:
			target_type_err_str = 'a float'
		elif target_type is bool:
			target_type_err_str = 'True or False'
		elif target_type is str:
			target_type_err_str = 'a str'
		elif target_type is list:
			target_type_err_str = 'a list'
		else:
			print(f'Error, "{target_type}," is not a type that can be checked in _is_type_or_print_err yet.')
			quit()
		print(f'Error, {in_type_str} must be {target_type_err_str} not "{in_type}"')
		quit()

class FileOperations:
	def __init__(self, in_path, out_dir, print_success=True, print_err=True,
	             print_ren_info=False, print_ren_time=True, open_after_ren=False):
		"""This class contains many different methods for altering video/audio files.\n
		in_path (path to the input file) and out_dir (path to a separate output folder)
		are both required for all methods and must be pathlib paths.\n
		print_success and print_err toggle printing success or error messages in the console.\n
		NOTE: If print_success is False then print_ren_time will automatically be set to False.\n
		print_ren_info will print all the file and render info ffmpeg produces.\n
		print_ren_time will display how long the output took to render
		(and if a method requires scanning the file first it will print how long that took).\n
		open_after_ren is True it will automatically open the output file(s) after they're done rendering."""
		
		# Run function to print an error and quit if the input type is not the correct type.
		_is_type_or_print_err_and_quit(type(out_dir), paths.Path, 'out_dir')
		_is_type_or_print_err_and_quit(type(print_success), bool, 'print_success')
		_is_type_or_print_err_and_quit(type(print_err), bool, 'print_err')
		_is_type_or_print_err_and_quit(type(print_ren_info), bool, 'print_ren_info')
		_is_type_or_print_err_and_quit(type(print_ren_time), bool, 'print_ren_time')
		_is_type_or_print_err_and_quit(type(open_after_ren), bool, 'open_after_ren')
		
		# Pathlib path to a input file for the terminal command.
		self.in_path = in_path
		# Pathlib path to an already existing output directory.
		self.out_dir = out_dir
		
		# The concat method requires a list input, but otherwise it should just be one path.
		if type(in_path) is not list:
			_is_type_or_print_err_and_quit(type(in_path), paths.Path, 'in_path')
			# Path to standard ffmpeg output file which is just the name of the input file in a different directory.
			self.standard_out_path = paths.Path().joinpath(self.out_dir, self.in_path.name)
		
		# Boolean to toggle the terminal outputting a successful messages (with output path)
		self.print_success = print_success
		# Boolean to toggle the terminal outputting error messages.
		self.print_err = print_err
		# Boolean value to toggle on or off displaying how long it took to render the file.
		if print_success is False:
			self.print_ren_time = False
		else:
			self.print_ren_time = print_ren_time
		# Boolean to toggle the terminal output the input file information and output streams.
		self.print_ren_info = print_ren_info
		# Boolean value to toggle on or off opening the output file once it finishes rendering.
		self.open_after_ren = open_after_ren

	def change_metadata(self, artist_author='', album='', description='', lyrics='', genre='', composer='', performer='',
	                    track_num='', disc_num='', date_y_m_d='', comment='', title='', arbitrary_key_value_pair=''):
		"""This method changes metadata values of files. The only valid input types are str() and None.\n
		If it's a string then the value will be changed to that value.\n
		However, if the input value is None then it will remove that value
			(if the value is already non-existent then nothing will happen.)\n
		arbitrary_key_value_pair should be a string in the form of "key=value"\n
		NOTE: At least one new value must be specified or this method will print an error and return False."""
		
		# Dictionary to store the ffmpeg metadata value keywords.
		meta_dict = dict([
			(artist_author, 'artist='),
			(album, 'album='),
			(description, 'description='),
			(lyrics, 'lyrics='),
			(genre, 'genre='),
			(composer, 'composer='),
			(performer, 'performer='),
			(track_num, 'track='),
			(disc_num, 'disc='),
			(date_y_m_d, 'date='),
			(comment, 'comment='),
			(title, 'title='),
			(arbitrary_key_value_pair, ''),
		])
		
		# Check if all input values are the same and is so print an error.
		all_inputs_are_equal = all(meta_dict.keys())
		if all_inputs_are_equal is True:
			print('Error, at least one value must be specified for any metadata to be changed.')
			return False

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy']
		
		# Any values to change will be appended with the keyword "-metadata" before each using a
		# for loop going over all possible values from the dictionary.
		for meta_value in meta_dict.keys():
			# If the key (user input) is not an empty string then append that option to the ffmpeg command.
			if type(meta_value) is str and meta_value != '':
				ffmpeg_cmd += ('-metadata', meta_dict[meta_value] + meta_value)
			# If the meta_value type is None then set the value for that key (user input)
			# to nothing (so that key will not have a value in the output.)
			# e.g., -metadata artist= as apposed to -metadata artist="Artist"
			elif meta_value is None:
				ffmpeg_cmd += ('-metadata', (meta_dict[meta_value]))
			# If a metadata value is set to the default empty string skip that empty value and continue the loop.
			elif meta_value == '':
				continue
			else:
				if self.print_err is True:
					(f'Error, metadata values can only be a string or None, but "{meta_value}" is {type(meta_value)}')
				quit()
		
		# Append output path to the ffmpeg_cmd list.
		ffmpeg_cmd.append(self.standard_out_path)
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def copy_over_metadata(self, copy_this_metadata_file, copy_chapters=True):
		"""This method will copy any metadata values from copy_this_metadata_file to the output."""

		_is_type_or_print_err_and_quit(type(copy_this_metadata_file), paths.Path, 'copy_this_metadata_file')
		_is_type_or_print_err_and_quit(type(copy_chapters), bool, 'copy_chapters')

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-i', copy_this_metadata_file]
		if copy_chapters is False:
			ffmpeg_cmd += ('-map_chapters', '-1')
		ffmpeg_cmd += ['-map', '0', '-c', 'copy', '-map_metadata', '1', self.standard_out_path]

		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()

	def change_file_name_and_meta_title(self, new_title):
		"""This method changes the filename and metadata title of a file."""

		_is_type_or_print_err_and_quit(type(new_title), str, 'new_title')
		
		# path object to rename the output basename.
		full_out_path = paths.Path().joinpath(self.out_dir, new_title + self.in_path.suffix)
		# If there are video, audio, or subtitle streams copy those to the output and change the -metadata title.
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c',
		              'copy', '-metadata', 'title=' + new_title, full_out_path]
		
		# Run the check_depend_then_ren method in the Render class to check that the input file and output directory
		#   exist then render the output file with the given ffmpeg command.
		Render(self.in_path, full_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def embed_artwork(self, in_artwork):
		"""This method embeds artwork into the output file.\n
		in_artwork is required.
		NOTE: This method does not work if the input is a .m4a file and has chapters embedded."""
		
		_is_type_or_print_err_and_quit(type(in_artwork), paths.Path, 'in_artwork')

		# The input artwork file does not have the ".jpg" extension so print an error.
		if in_artwork.exists() and in_artwork.suffix != '.jpg':
			print(f'Error, input artwork "{in_artwork}" is not a ".jpg" file.')
			return False
		# The artwork input file doesn't exist so print an error.
		elif in_artwork.exists() is False:
			print(f'Error, input artwork "{in_artwork}" not found.')
			return False
		
		# The input file may already have artwork, so create a temporary file that will have the artwork removed
		# (if it had any in the first place,) so that temporary file can be used as the input for the desired output
		# file with the new artwork. This is because if the input file already
		# has artwork then the output artwork may not be changed.
		temp_rm_art_exists = FileOperations(self.in_path, self.out_dir, False, False, False, False).rm_artwork()
		# The input file doesn't have any artwork so copy the file to use the same logic below.
		if temp_rm_art_exists is False:
			shutil.copy2(self.in_path, self.standard_out_path)
		
		# Rename the temporary output with no artwork and use that as the input.
		temp_rm_artwork_path = paths.Path().joinpath(self.out_dir, self.in_path.stem
		                                             + '-temp_rm_art_before_renaming' + self.in_path.suffix)
		self.standard_out_path.rename(temp_rm_artwork_path)

		# If the input extension is ".mp4" or ".mp3" then render with ffmpeg, but if it's a different valid format then
		# render with AtomicParsley. Otherwise print an error that the input file extension isn't valid.
		if self.in_path.suffix == '.mp3' or self.in_path.suffix == '.mp4':
			# '-map', '0', '-c', 'copy', says to copy every stream from the first input (video/audio file).
			#   '-map', '1', '-c:v:1' selects the video stream for the output,
			#   and 'png', '-disposition:v:1', 'attached_pic' is to embed the artwork.
			ffmpeg_cmd = ['ffmpeg', '-i', temp_rm_artwork_path, '-i', in_artwork, '-map', '0', '-c', 'copy',
			              '-map', '1', '-c:v:1', 'png', '-disposition:v:1', 'attached_pic', self.standard_out_path]
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time).check_depend_then_ren()
			# Delete the temporary file that didn't have any artwork that was used as the input to embed the artwork.
			temp_rm_artwork_path.unlink()
		# If the input file extension is a different valid extension then use AtomicParsley to embed artwork.
		elif self.in_path.suffix == '.m4v' or self.in_path.suffix == '.m4a':
			# AtomicParsley command syntax (change the artwork of the output file directly without creating another
			# file.)
			atomic_parsley_cmd = ['AtomicParsley', temp_rm_artwork_path, '--overWrite', '--artwork', in_artwork]
			# Render with AtomicParsley
			ren_result = Render(temp_rm_artwork_path, self.standard_out_path, atomic_parsley_cmd, 
			                    self.print_success, self.print_err, self.print_ren_info, self.print_ren_time,
			                    self.open_after_ren).run_terminal_cmd(append_hide_banner=False, append_faststart=False)
			# AtomicParsley creates a duplicate artwork file NAME-resized-0000.jpg so delete that temporary file.
			for file in in_artwork.parent.iterdir():
				if file.stem.startswith(in_artwork.stem):
					# Scan string beginning after the length of the original input to see if it has the keyword -resized-
					# filename<HERE>-resized-0000.jpg (the number is randomized.)
					if str(file.stem[len(in_artwork.stem):]).startswith('-resized-') and file.suffix == '.jpg':
						file.unlink()
			
			# Custom output message to specify the problem occurred with AtomicParsley and not ffmpeg.
			if ren_result is False and self.print_err is True:
				print('\nError, a problem occurred with AtomicParsley while rendering:')
				print(f'Terminal input command: {atomic_parsley_cmd}')
			
			# Rename temporary output file (originally with no artwork) to the out_path name since it has the artwork now.
			temp_rm_artwork_path.rename(self.standard_out_path)
		else:
			# Target output extension is not supported for artwork embedding so print an error and return False.
			if self.print_err is True:
				print(f'\nError, artwork embedding is not supported for target output extension "{self.in_path.suffix}"'
				      f'\nPlease convert "{self.in_path}"\nto a valid extension (.mp3, .mp4, .m4v, .m4a) '
				      f'for artwork embedding.\n')
			return False
	
	def extract_artwork(self):
		"""This method extracts the artwork from the input file and exports it to a ".jpg" file."""
		
		# Artwork extracting is not supported for the target output extension so print an error and return False.
		if self.in_path.suffix != '.mp3' and self.in_path.suffix != '.mp4' \
			and self.in_path.suffix != '.m4a' and self.in_path.suffix != '.m4v' and self.print_err is True:
			print(f'\nError, artwork extraction is not supported for input extension "{self.in_path.suffix}"'
			      f'\nPlease convert "{self.in_path}" to a valid extension (.mp3, .mp4, .m4v, .m4a) for artwork extraction '
			      f'(if it has artwork in the first place).\n')
			return False

		# path to output file with the same name as the input, but with the ".jpg" extension.
		art_ext_out_path = paths.Path.joinpath(self.out_dir, self.in_path.stem + '.jpg')
		
		# -map select the artwork stream if it exists ('0:v'),
		# then deselect every other video stream except the artwork stream ("-0:V") and output to a jpg file.
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0:v?', '-map', '-0:V?', '-c', 'copy', art_ext_out_path]

		in_strms = MetadataAcquisition(self.in_path).return_stream_types()
		art_exists = 'Artwork' in in_strms
		if art_exists is False:
			if self.print_err is True:
				print(f'\nError, no artwork found in input:\n"{self.in_path}"\nFor output:\n"{art_ext_out_path}"\n')
			return False
		
		# Run command to create new .jpg file from input artwork.
		# exists_result will either be True or False depending on whether or not the output file exists.
		exists_result = Render(self.in_path, art_ext_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		                       self.print_ren_info, self.print_ren_time,
		                       self.open_after_ren).check_depend_then_ren(append_faststart=False)
		return art_ext_out_path
	
	def rm_artwork(self):
		"""This method removes any already existing artwork from video and audio files.\n
		NOTE: This method will not quit if the input does not have any artwork."""
		
		# If the extension is .m4v or .m4a use AtomicParsley to remove the artwork
		if self.in_path.suffix == '.m4v' or self.in_path.suffix == '.m4a':
			shutil.copy2(self.in_path, self.standard_out_path)
			# AtomicParsley command syntax (change the artwork of the output file directly
			# without creating another file.)
			atomic_parsley_cmd = ['AtomicParsley', self.standard_out_path, '--artwork', 'REMOVE_ALL', '--overWrite']
			ren_result = Render(self.in_path, self.standard_out_path, atomic_parsley_cmd, self.print_success,
								self.print_err, self.print_ren_info, self.print_ren_time,
			                    self.open_after_ren).run_terminal_cmd(append_hide_banner=False, append_faststart=False)
			return ren_result

		# Print an error if the input doesn't have artwork and copy to output.
		stream_types = MetadataAcquisition(self.in_path, self.print_ren_info, False, False).return_stream_types()
		art_stream = 'Artwork' in stream_types
		if art_stream is None:
			return False
		else:
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy']
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
			ffmpeg_cmd.append(self.standard_out_path)
			
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren(append_faststart=False)
		return True
	
	def change_ext(self, new_ext):
		"""This method changes the self.in_path extension to new_ext."""
		
		_is_type_or_print_err_and_quit(type(new_ext), str, 'new_ext')

		# Path to output file with the new target extension.
		new_ext_out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem + new_ext)
		
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, new_ext_out_path]
		
		# Confirm the target output extension isn't the same as the input extension.
		# If it is the same extension then print a message and just copy the file.
		if self.in_path.suffix == new_ext_out_path.suffix:
			shutil.copy2(self.in_path, new_ext_out_path)
			print(f'Error, target output extension, "{new_ext_out_path.suffix}" is the same as '
			      f'the input extension so the target output file, "{new_ext_out_path}" was just copied.')
		else:
			Render(self.in_path, new_ext_out_path, ffmpeg_cmd, self.print_success, self.print_err, self.print_ren_info,
			       self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
	
	def trim(self, start_timecode='', stop_timecode='', codec_copy=False):
		"""This method changes the duration of the input from start_timecode to stop_timecode\n
		Timecode format = "00:00:00.00" (hours, minutes, seconds, and fractions of seconds.)\n
		At least start_timecode or stop_timecode must be set, but if one of them isn't set it will
		default to the beginning or the end respectively.
		So if stop_timecode="0:35" then start at the beginning and keep everything until it's 35 seconds in.\n
		codec_copy toggles copying the codec for the output which is False by default because
		otherwise there's a few second margin of error for some codecs (such as .mp4).\n
		NOTE: This method will remove any already existing chapter(s)
		from the input because otherwise the output won't be trimmed."""
		
		_is_type_or_print_err_and_quit(type(start_timecode), str, 'start_timecode')
		_is_type_or_print_err_and_quit(type(stop_timecode), str, 'stop_timecode')
		_is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')

		if start_timecode == '' and stop_timecode == '':
			if self.print_err is True:
				print('Error, at least start_timecode or stop_timecode must be set for the output to be changed.')
			return False
		elif start_timecode == stop_timecode:
			if self.print_err is True:
				print(f'Error, start_timecode and stop_timecode are both set to "{start_timecode}" so no output will be produced.')
			return False
		
		stream_types = MetadataAcquisition(self.in_path, self.print_ren_info,
										   False, False).return_stream_types()
		has_vid_stream = 'Video' in stream_types
		has_aud_stream = 'Audio' in stream_types
		if has_vid_stream is False and has_aud_stream is False:
			if self.print_err is True:
				print(f'Error, no video or audio to trim were found from input\n"{self.in_path}"')
			return False
		
		sec_dur = self._return_input_duration_in_sec()
		if sec_dur is None or sec_dur < 1:
			if self.print_err is True:
				print(f'''Error, there's no length to trim from input "{self.in_path}"\n''')
			return False
		
		if start_timecode != '':
			if self._return_input_duration_in_sec(start_timecode) > sec_dur:
				if self.print_err is True:
					print(f'''Error, the starting timecode "{start_timecode}" is greater than the length of input:\n"{self.in_path}"\n''')
				return False
		if stop_timecode != '':
			if self._return_input_duration_in_sec(stop_timecode) > sec_dur:
				if self.print_err is True:
					print(f'''Error, the output won't go until end timecode "{stop_timecode}" '''
					      f'''because that's greater than the length of input:\n"{self.in_path}"\n''')

		# -ss is the timecode to begin file at and -to is the timecode to end at.
		# (There's also the -t option which is a relative trim, i.e. 15 seconds after the start timecode but -t isn't
		# used for this method.)
		ffmpeg_cmd = ['ffmpeg']
		if start_timecode != '':
			ffmpeg_cmd += ('-ss', start_timecode)
		if stop_timecode != '':
			ffmpeg_cmd += ('-to', stop_timecode)
		ffmpeg_cmd += ('-i', self.in_path)
		end_cmd = ['-shortest', '-map_chapters', '-1', self.standard_out_path]
		if self.in_path.suffix == '.m4a':
			ffmpeg_cmd += ('-c', 'copy')
			ffmpeg_cmd += end_cmd
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren()
		elif codec_copy is True:
			ffmpeg_cmd += ('-map', '0', '-c', 'copy')
			ffmpeg_cmd += end_cmd
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd,
                   self.print_success, self.print_err, self.print_ren_info,
				   self.print_ren_time, self.open_after_ren).check_depend_then_ren()
		else:
			ffmpeg_cmd += end_cmd
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)

	def loop(self, num_loop_times=0, loop_to_hours=0, codec_copy=False):
		"""This method loops the input the given number of times.\n
		num_loop_times is the default number of times to repeat.\n
		loop_to_hours automatically determines how many times to loop the input
		so the output is at least one hour in length.\n
		codec_copy toggles whether or not to copy the input codec(s)"""

		_is_type_or_print_err_and_quit(type(num_loop_times), int, 'num_loop_times')
		_is_type_or_print_err_and_quit(type(loop_to_hours), int, 'loop_to_hours')
		_is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')

		stream_types = MetadataAcquisition(self.in_path, self.print_ren_info,
                                    	   False, False).return_stream_types()
		has_vid_stream = 'Video' in stream_types
		has_aud_stream = 'Audio' in stream_types
		if has_vid_stream is False and has_aud_stream is False:
			if self.print_err is True:
				print(f'Error, no video or audio to loop was found from input:\n"{self.in_path}"')
			return False

		if num_loop_times == 0 and loop_to_hours == 0:
			print("Error, num_loop_times and loop_to_hours can't both be set to 0, nothing would change.")
			return False
		elif num_loop_times != 0 and loop_to_hours != 0:
			print("Error, num_loop_times and loop_to_hours are mutually exclusive but both were specified.")
			return False
		elif num_loop_times != 0:
			# Confirm the num_loop_times is more then 2 because otherwise the output wouldn't be changed.
			if num_loop_times < 2:
				print(f'Error, num_loop_times must be at least 2, not "{num_loop_times}"')
				return False
			else:
				FileOperations.concat(self, codec_copy=codec_copy, _loop_times=num_loop_times)
				if self.print_success is True:
					print(f'(Looped {num_loop_times} times.)')
		elif loop_to_hours != 0:
			# Loop input to be X hour(s) in length:
			if loop_to_hours < 0:
				print(f'''Error, loop_to_hours ("{loop_to_hours}") can't be a negative value, it must be 1 (hour) or greater.''')
				return False
			# There are 3600 seconds in one hour, so multiply that times the number of how many hours long the output
			# should be because ffmpeg requires that the output be specified in seconds.
			target_total_sec = loop_to_hours * 3600
			actual_sec_length = self._return_input_duration_in_sec()
			# See if the input has no duration, like if it was a static image.
			if actual_sec_length is None:
				return False
			else:
				if actual_sec_length > target_total_sec:
					print(f'Error, the input is already greater than or equal to '
						  f'"{loop_to_hours}" hour(s) in length for input:\n"{self.in_path}"')
				else:
					# Divide the target output seconds by the actual length and round that number up
					# so the output is <= target_total_sec.
					loop_times = int(math.ceil(target_total_sec / actual_sec_length))
					ren_result = FileOperations.concat(self, codec_copy=codec_copy, _loop_times=loop_times)
					if self.print_success is True and ren_result is True:
						if loop_to_hours != 0:
							# Default to looping for multiple hours, but remove the "s" if it only loops for 1 hour.
							hour_singular_or_plural = 'hours'
							if loop_to_hours == 1:
								hour_singular_or_plural = hour_singular_or_plural[:-1]
							print(f'Looped ({loop_times} times) to be at least {loop_to_hours} {hour_singular_or_plural} long.')

	def speed(self, playback_speed, add_speed_to_basename=True):
		"""This method changes the playback speed of the input video/audio. (The pitch is not altered.)\n
		playback_speed must be a float number in the "1.25" format. e.g., 1.25x playback speed.\n
		add_speed_to_basename can add the amount the playback speed was altered by to the output's basename
		(Output Basename-1.50x.mp3).
		NOTE: This method only works with up to one audio and one video track."""

		_is_type_or_print_err_and_quit(type(playback_speed), float, 'playback_speed')

		stream_types = MetadataAcquisition(self.in_path, self.print_ren_info, False, False).return_stream_types()
		if 'Video' in stream_types is False and 'Audio' in stream_types is False:
			if self.print_err is True:
				print(f'\nError, there are not any video or audio streams to change the speed for from input:\n"{self.in_path}"\n')
				return False

		# I couldn't get the "atempo=2.0,atempo=2.0" system to work but I left the outline here.
		# new_aud_speed_cmd_num = playback_speed
		# aud_speed_cmd_keyword = 'atempo='
		# aud_speed_cmd = aud_speed_cmd_keyword
		# if new_aud_speed_cmd_num > 2:
		# 	change_until_devisable = new_aud_speed_cmd_num
		# 	while change_until_devisable > 2:
		# 		aud_speed_cmd += '2.0,' + aud_speed_cmd_keyword
		# 		change_until_devisable -= 2
		# 	if change_until_devisable != 0:
		# 		aud_speed_cmd += str(change_until_devisable)
		# 	else:
		# 		aud_speed_cmd += '0.0'
		# elif new_aud_speed_cmd_num < 0.5:
		# 	change_until_devisable = new_aud_speed_cmd_num
		# 	aud_speed_cmd = ''
		# 	while change_until_devisable < 0.5:
		# 		aud_speed_cmd = aud_speed_cmd + '0.5'
		# 		change_until_devisable += 2.5
		# 	if change_until_devisable != 0:
		# 		aud_speed_cmd = aud_speed_cmd + str(new_aud_speed_cmd_num)
		# else:
		# 	aud_speed_cmd = aud_speed_cmd + str(new_aud_speed_cmd_num)

		aud_speed_cmd = f'atempo={playback_speed}'
		vid_speed_cmd = f'setpts={1 / playback_speed}*PTS'

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map_chapters', '-1', '-map_metadata', '0', '-filter_complex']
		vid = False
		aud = False
		fil_com_cmd = ''

		if 'Video' in stream_types:
			fil_com_cmd += f'[0:V]{vid_speed_cmd}[v];'
			vid = True
		if 'Audio' in stream_types:
			fil_com_cmd += f'[0:a]{aud_speed_cmd}[a];'
			aud = True

		ffmpeg_cmd.append(fil_com_cmd[:-1])
		if vid is True:
			ffmpeg_cmd += ('-map', '[v]')
		if aud is True:
			ffmpeg_cmd += ('-map', '[a]')
		ffmpeg_cmd.append(self.standard_out_path)

		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err, self.print_ren_info,
			   self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
		# Rename the output to have the new speed on the end.
		# Rename it here became the original output loses artwork,
		# and the above method extracts artwork with the same basename as the input, so it couldn't match that artwork
		# with this output if this output has a different name (because the speed would be on the end.)
		# (e.g., it can't match "filename.jpg" with "filename-2x.mp3" so rename it afterwards.)
		if add_speed_to_basename is True:
			if self.standard_out_path.exists():
				out_path = paths.Path().joinpath(self.standard_out_path.parent, self.standard_out_path.stem +
				                                 f'-{playback_speed}x' + self.standard_out_path.suffix)
				self.standard_out_path.rename(out_path)

	def reverse(self):
		"""This method will change the output to play backwards (even with multiple audio streams).
		NOTE: This automatically removes subtitles and chapters."""
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-map', '-0:s']

		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		input_has_video = 'Video' in strm_types
		input_has_aud = 'Audio' in strm_types
		input_has_art = 'Artwork' in strm_types

		if input_has_aud is True and input_has_video is not True:	
			ffmpeg_cmd += ('-af', 'areverse')
		elif input_has_video is True and input_has_aud is not True:
			ffmpeg_cmd += ('-vf', 'reverse')
		else:
			ffmpeg_cmd += ('-vf', 'reverse', '-af', 'areverse')
		
		# The reverse video filter doesn't work if there's an artwork stream so if there is one
		# remove it from this output (artwork will be added after the input is reversed).
		if input_has_art is True:
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)

		ffmpeg_cmd.append(self.standard_out_path)
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
			   False).check_depend_then_ren_and_embed_original_metadata(artwork=True)

	def extract_frames(self, new_out_dir=False):
		"""This method will export every frame in the input video into its own image in an accessending order."""

		if new_out_dir is not False and type(new_out_dir) is not paths.PosixPath\
			and type(new_out_dir) is not paths.WindowsPath:
			print(f'Error, new_out_dir can only be a pathlib Path or a False, not {type(new_out_dir)} "{new_out_dir}"')
			return False

		if self.open_after_ren is True:
			print(f"Error, self.open_after_ren can't be True when extracting the frames from a video.")
		
		# Confirm input has a video stream and if so export each frame as an image.
		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		vid_exists = 'Video' in strm_types
		if vid_exists is False:
			print(f'''\nError, there's no video stream to extract frames from for input:\n"{self.in_path}"\n''')
		else:
			if new_out_dir is False:
				out_path_frame_num = paths.Path.joinpath(self.out_dir, f'{self.in_path.stem}-%1d.jpg')
			else:
				out_path_frame_num = paths.Path.joinpath(new_out_dir, f'{self.in_path.stem}-%1d.jpg')

			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-q:v', '1', out_path_frame_num]

			# Don't open after rendering (it doesn't have the path to the new images)
			# and don't print the standard success message; use a custom one instead.
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd,
				   False, self.print_err, self.print_ren_info,
				   self.print_ren_time, False).check_depend_then_ren(append_faststart=False)
			if self.print_success is True:
				print(f'All of the frames from input:\n"{self.in_path}" have rendered successfully!')
	
	def change_vid_aud(self, in_aud_path_list, shortest=True):
		"""This method replaces the audio for the input video.\n
		in_aud_path_list needs to be a list containing pathlib paths to every audio track to add to the output.\n
		shortest sets the length of the output video to the length of the shortest input.\n
		If omitted/set to False then the length of the output will be the length of the longest input."""
		
		_is_type_or_print_err_and_quit(type(in_aud_path_list), list, 'in_aud_path')
		for aud_path in in_aud_path_list:
			_is_type_or_print_err_and_quit(type(aud_path), paths.Path, 'aud_path')
		_is_type_or_print_err_and_quit(type(shortest), bool, 'shortest')

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-map', '-0:a']
		
		# This doesn't work if the input has artwork so remove it for this output (it will be added again after this).
		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		has_art_stream = 'Artwork' in strm_types
		has_vid_stream = 'Video' in strm_types
		if has_vid_stream is False:
			if self.print_err is True:
				print('Error, no video stream to keep (because this method only changes the audio) '
					  f'was found from input:\n"{self.in_path}"\n')
			return False
		if has_art_stream is True:
			ffmpeg_cmd = _add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)

		for in_aud_path in in_aud_path_list:
			ffmpeg_cmd += ('-i', in_aud_path)
		for in_aud_index, in_aud_path in enumerate(in_aud_path_list):
			ffmpeg_cmd += ('-map', f'{in_aud_index + 1}:a')
		ffmpeg_cmd.append(self.standard_out_path)

		if shortest is True:
			ffmpeg_cmd.append('-shortest')
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				self.print_err, self.print_ren_info, self.print_ren_time,
				self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True, copy_chapters=True)

	def add_aud_stream_to_vid(self, in_aud_path_list, codec_copy=False, length_vid=True):
		"""This method adds audio stream(s) to the input video.\n
		in_aud_path_list must be a list with the paths to the different audio tracks to add to the output video.
		codec_copy toggles whether or not to copy the input codecs.\n
		I've had issues with it working so codec_copy is False by default.\n
		length_vid sets the length of the output to the length of the original video.
		If omitted/set to False then the length of the output will be the length of the longest input.\n
		NOTE: This method also works for .m4a audio (but not .mp3).
		NOTE: This method only works for inputs with one audio stream, not multiple. To work around this
		use the extract_audio method before running this method since that's a very rare circumstance."""
		# Future reader, multiple audio channels from the input could be retained by running
		# MetadataAcquisition().return_stream_types() and specifying to copy over every audio stream individually.
		
		_is_type_or_print_err_and_quit(type(in_aud_path_list), list, 'in_aud_path_list')
		for aud_path in in_aud_path_list:
			_is_type_or_print_err_and_quit(type(aud_path), paths.Path, 'aud_path')
		_is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')
		_is_type_or_print_err_and_quit(type(length_vid), bool, 'length_vid')

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path]

		num_valid_in_aud = 0
		# Sort input audio paths and add an ffmpeg input for each audio input path.
		in_aud_path_list.sort()
		
		# Confirm the input has a video stream.
		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		has_vid_stream = 'Video' in strm_types
		if has_vid_stream is False:
			if self.print_err is True:
				print(f'Error, no video stream to keep found from input:\n{self.in_path}')
			return False
		
		# Confirm each input audio track actually has audio.
		for aud_path in in_aud_path_list:
			strm_types = MetadataAcquisition(aud_path).return_stream_types()
			has_aud_stream = 'Audio' in strm_types
			if has_aud_stream is False:
				if self.print_err is True:
					print(f'Error, no audio stream to add found from input:\n{aud_path}')
				return False
		else:
			ffmpeg_cmd += ('-i', aud_path)
			num_valid_in_aud += 1

		# Copy over any video, audio, and subtitle streams from the original video input and set audio language to
		# English. https://ffmpeg.org/ffmpeg.html#Stream-specifiers-1
		ffmpeg_cmd += ['-map', '0', '-c', 'copy', f'-metadata:s', 'language=eng']

		# Set codec for output audio tracks (to allow for multiple audio tracks) and set the audio language to English.
		for aud_path_num in range(num_valid_in_aud):
			# f'-metadata:s:a:{aud_path_num}', 'title=' could be added to the end of this command, but since it can't
			# account for already existing audio streams and it's only visible in VLC I didn't bother.
			ffmpeg_cmd += ['-map', f'{aud_path_num + 1}:a', '-c:a', 'aac', f'-metadata:s', 'language=eng']

		# Trim to the length of the video (in case a separate audio track is longer than the video).
		if length_vid is True:
			ffmpeg_cmd += ('-to', f'{MetadataAcquisition(self.in_path).return_metadata(duration=1)[0]}')
		ffmpeg_cmd.append(self.standard_out_path)
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
			   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def change_volume(self, custom_db='3 dB', aud_only=False, print_vol_value=True):
		"""This method will change the volume of the input audio/video with audio.\n
		custom_db can be set to a string to change the file volume by that amount ('-0.0 dB' or '0.0 dB')\n
		if print_vol_value is set to True then print the dB number the volume was changed by.\n"""
		
		_is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		_is_type_or_print_err_and_quit(type(aud_only), bool, 'aud_only')
		_is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')

		# Set the custom_db from the loudnorm_stereo method to change the output volume.
		FileOperations.loudnorm_stereo(self, custom_db=custom_db, aud_only=aud_only, print_vol_value=print_vol_value)
	
	def loudnorm_stereo(self, custom_db='', aud_only=False, print_vol_value=True, _do_render=True):
		"""This method will run the input through a loudness normalization filter.\n
		custom_db can be set to a string to change the file volume by that amount ('-0.0 dB' or '0.0 dB')\n
		if print_vol_value is set to True then print the dB number the volume was changed by.\n
		_do_render dictates if this method will render the output or not.
		It can be set to False for methods that just need the command such as compress_h265_norm_aud\n
		NOTE: This method only works for one audio track. If the input has multiple audio tracks only one will be output.\n
		NOTE: This method does not retain all subtitle tracks."""
		
		# Confirm input types are valid.
		_is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		_is_type_or_print_err_and_quit(type(aud_only), bool, 'aud_only')
		_is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')
		_is_type_or_print_err_and_quit(type(_do_render), bool, '_do_render')
		
		if _do_render is False and aud_only is True:
			print('Error, in order for _do_render to be False aud_only must also be False.')
			quit()
		
		if custom_db != '':
			vol_level = custom_db
			print()
		else:
			# Get the max volume for the input.
			vol_level = MetadataAcquisition(self.in_path, self.print_ren_info, self.print_ren_time,
			                                print_meta_value=False).return_metadata(max_volume=1)[0]
		
		# If the volume is already 0 then quit, otherwise increase the volume to get to 0dB automatically.
		if vol_level == '0.0 dB' and custom_db == '' or vol_level == '-0.0 dB' and custom_db == '':
			# If _do_render is True print an error,
			# otherwise return None (no command) for the compress_h265_norm_aud method.
			if _do_render is True:
				print('Error, the output file was just copied because '
					  f'the audio is already normalized for input:\n"{self.in_path}"\n')
				shutil.copy2(self.in_path, self.standard_out_path)
				return False
			elif _do_render is False:
				return None
		elif custom_db == '0.0 dB' or custom_db == '-0.0 dB':
			print(f'''Error, setting custom_db to "{custom_db}" won't do anything.''')
			quit()
		
		# The metadata value max_volume wasn't found so vol_level is None. Therefore, return False (it didn't work
		# because the input doesn't have any audio.)
		if vol_level is None:
			return False
		else:
			if custom_db != '':
				if custom_db[0] == '-':
					vol_change_keyword = 'decreased'
					vol_db_change = 'volume=-' + vol_level
				else:
					vol_change_keyword = 'increased'
					vol_db_change = 'volume=' + vol_level
			elif vol_level[0] == '-':
				vol_change_keyword = 'increased'
				vol_db_change = 'volume=' + vol_level[1:]
			else:
				print(f'Error, unable to find suitable output decibel amount for volume level "{vol_level}" '
				      f'with custom dB "{custom_db}".')
				quit()
			
			# String of decibel amount to raise by.
			if vol_level[0] == '-':
				db_amount = vol_level[1:]
			else:
				db_amount = vol_level
			
			# Boolean to allow for retrieving the dB info without rendering for the compress_h265_norm_aud method.
			if _do_render is False:
				if print_vol_value is True:
					print(f'The volume was {vol_change_keyword} by {db_amount}')
				return ['-af', vol_db_change, '-ac', '2']
			
			# Set the output extension to out_ext or default (.mp3) and render.
			elif aud_only is True:
				out_path = self.standard_out_path.with_suffix('.mp3')
				ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-vn', '-sn', '-af', vol_db_change, '-ac', '2', out_path]
			else:
				out_path = self.standard_out_path
				ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-af', vol_db_change, '-ac', '2',
				              '-c:v', 'copy', '-c:s', 'copy', '-map_metadata', '0', self.standard_out_path]
			
			if _do_render is True:
				ren_result = Render(self.in_path, out_path, ffmpeg_cmd, self.print_success, self.print_err,
									self.print_ren_info, self.print_ren_time,
									self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
				if print_vol_value is True and ren_result is True:
					print(f'The volume was {vol_change_keyword} by {db_amount}\n')
	
	def extract_audio(self, out_aud_ext='', order_out_names=True):
		"""This method extracts audio track(s) from the input.\n
		This is primarily intended for use with video files that have multiple audio tracks
		because otherwise you can just use the change_ext method.
		out_aud_ext allows you sto specify the the output extension should be.
		order_out_names will append "-Audio Track {number}" to the output basename(s)"""
		
		_is_type_or_print_err_and_quit(type(out_aud_ext), str, 'out_aud_ext')
		_is_type_or_print_err_and_quit(type(order_out_names), bool, 'order_out_names')

		# Option to change the extension for the output audio.
		if out_aud_ext == '':
			out_ext = '.mp3'
		else:
			out_ext = out_aud_ext

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path]

		# Determine what the artwork index may be and get stream types.
		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		art_exists = 'Artwork' in strm_types

		# There are no audio streams in the input file to extract so return False.
		audio_exists = 'Audio' in strm_types
		if audio_exists is False:
			if self.print_err is True:
				print(f'''Error, input "{self.in_path}" doesn't have any audio streams to extract.''')
			return False
		
		# Determine what index artwork would be (0 for no video, and 1 if there is video.)
		if 'Video' in strm_types:
			art_strm_index = '1'
		else:
			art_strm_index = '0'
		
		# Empty list that will have the audio output paths appended to it enabling it to print a success message.
		out_paths_list = []
		num_aud_stream = 1
		for strm_index, strm in enumerate(strm_types):
			# Map the output if it's an audio stream.
			if strm == 'Audio':
				ffmpeg_cmd += ('-map', f'0:{strm_index}')
				# Only embed input artwork if it exists and the output extension is ".mp3"
				if art_exists is True and out_ext == '.mp3':
					ffmpeg_cmd += ('-map', f'0:v:{art_strm_index}')
				if order_out_names is True:
					out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem
					                                 + f'-Audio Track {num_aud_stream}' + out_ext)
				else:
					out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem + out_ext)
				ffmpeg_cmd.append(out_path)
				out_paths_list.append(out_path)
				num_aud_stream += 1
			
		Render(self.in_path, out_paths_list, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def rm_begin_end_silence(self):
		"""This method will remove the silence from the beginning and end of audio tracks.
		NOTE: This method will remove any already existing subtitles and chapters."""
		ffmpeg_cmd = ['ffmpeg', '-i',
		              self.in_path, '-map', '0', '-c:v', 'copy', '-map_chapters', '-1', '-map', '-0:s', '-af',
		              'silenceremove=start_periods=1:start_duration=0:start_threshold=-60dB:detection=peak'
		              ',aformat=dblp,areverse,silenceremove=start_periods=1:start_duration=0:'
		              'start_threshold=-60dB:detection=peak,aformat=dblp,areverse', self.standard_out_path]
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
		       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
	
	def fade_begin_and_or_end__audio_and_or_video(self, fade_vid=True, fade_aud=True, fade_begin=False,
												  fade_end=True, fade_dur_sec=3, fade_out_at_sec=0):
		"""This method will fade the input audio from full to 0 dB and fade video to black.\n
		NOTE: This method does not work with .m4a audio files which contain artwork.\n
		fade_vid and fade_aud can be set to True or False to fade video or audio respectively.\n
		fade_begin and fade_end toggle whether or not to fade audio/video at the beginning or end of the input respectively.\n
		fade_dur_sec controls how long it will take the audio to go from max to 0 dB or footage to fade to black.\n
		fade_out_at_sec can be specified for a certain second into the input to override
		the automatically computed second to begin fading at the end of the input.
		e.g., start fading at 1 minute and 9 seconds in = "69", then the rest of the duration would be black/silent."""

		_is_type_or_print_err_and_quit(type(fade_vid), bool, 'fade_vid')
		_is_type_or_print_err_and_quit(type(fade_aud), bool, 'fade_aud')
		_is_type_or_print_err_and_quit(type(fade_begin), bool, 'fade_begin')
		_is_type_or_print_err_and_quit(type(fade_end), bool, 'fade_end')
		_is_type_or_print_err_and_quit(type(fade_dur_sec), int, 'fade_dur_sec')
		_is_type_or_print_err_and_quit(type(fade_out_at_sec), int, 'fade_out_at_sec')

		if fade_dur_sec <= 0:
			print(f'Error, fade_dur_sec has to be greater than 0 seconds, not "{fade_dur_sec}"')
			quit()
		elif fade_out_at_sec < 0:
			print(f'Error, fade_out_at_sec has to be greater than 0 seconds, not "{fade_dur_sec}"')
			quit()
		elif fade_begin is False and fade_end is False:
			print('Error, either fade_begin and/or fade_end must be specified for anything to change.')
			quit()
		else:
			# Get the duration for the input video and or audio in seconds.
			total_length_sec = self._return_input_duration_in_sec()

			# Either begin ending fade at fade_out_at_sec if it's specified or,
			# begin ending fade at the automatically calculated time,
			# so it's fade_dur_sec from the end of the video/audio.
			if fade_out_at_sec != 0:
				fade_out_sec = fade_out_at_sec - fade_dur_sec
			else:
				fade_out_sec = total_length_sec - fade_dur_sec

			# Generate the specific ffmpeg commands to fade the beginning and/or ending audio and/or video.
			# fade_begin_cmd can be used for video or audio
			# (by adding "a" at the beginning of the audio command if fade_aud is True)
			# so the video and audio don't need their own specifc command.
			fade_begin_cmd = f'fade=in:st=0:d={fade_dur_sec}'
			# Subtract 0.2 seconds from the ending fade start time because otherwise the video doesn't get
			# all the way to black.
			fade_end_vid_cmd = f'fade=out:st={fade_out_sec - 0.2}:d={fade_dur_sec}'
			# Generate the equivalent fade ending audio command.
			fade_end_aud_cmd = f'afade=out:st={fade_out_sec}:d={fade_dur_sec}'
			# If fade_begin=True and fade_end=True then they need both parts of the command or,
			# if fade_out_at_sec is specified then it needs the beginning and ending command.
			fade_both_vid_cmd = fade_begin_cmd + ',' + fade_end_vid_cmd
			fade_both_aud_cmd = 'a' + fade_begin_cmd + ',' + fade_end_aud_cmd
			# Remove artwork.
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0']
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
			
			# Append command to fade video.
			if fade_vid is True:
				ffmpeg_cmd.append('-vf')
				# Either fade beginning, end, or both.
				if fade_begin is True and fade_end is True:
					ffmpeg_cmd.append(fade_both_vid_cmd)
				elif fade_begin is True:
					if fade_out_at_sec != 0:
						ffmpeg_cmd.append(fade_both_vid_cmd)
					else:
						ffmpeg_cmd.append(fade_begin_cmd)
				elif fade_end is True:
					ffmpeg_cmd.append(fade_end_vid_cmd)

			# Append command to fade audio.
			if fade_aud is True:
				ffmpeg_cmd.append('-af')
				# Either fade beginning, end, or both.
				if fade_begin is True and fade_end is True:
					ffmpeg_cmd.append(fade_both_aud_cmd)
				elif fade_begin is True:
					if fade_out_at_sec != 0:
						ffmpeg_cmd.append(fade_both_aud_cmd)
					else:
						ffmpeg_cmd.append('a' + fade_begin_cmd)
				elif fade_end is True:
					ffmpeg_cmd.append(fade_end_aud_cmd)

			# The entire command is there so append the output path.
			ffmpeg_cmd.append(self.standard_out_path)
			
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd,
			       self.print_success, self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
	
	def pan_audio(self, pan_strm=[]):
		"""Input list set to R or L and the percentage, and a new item on te list ofr each audio channel.
		[L100, R100, L75] pan the first audio channel all the way to the left, the second audio channel all the way to
		the right, and the third channel 75% of the way to the left."""

		_is_type_or_print_err_and_quit(type(pan_strm), list, 'pan_strm')

		# Confirm input is valid (such as L100).
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, 'pan command']
		for strm in pan_strm:
			if type(strm) != str:
				if self.print_err is True:
					print(f'Error, input "{strm}" is not a string.')
			elif strm[0] != 'L' and strm[0] != 'R':
				if self.print_err is True:
					print(f'Error, the first character of the input must be "L" or "R" to specify which '
						  f'direction to pan the audio, but "{strm[0]}" was received.')
			else:
				try:
					pan_percentage = int(strm[:-1])
				except:
					if self.print_err is True:
						print(f'Error, after specifing which direction to pan (L or R), '
							  f'the percentage to pan by must be a number between 1-100, not "{strm[:-1]}"')
				if pan_percentage < 1 or pan_percentage > 100:
						if self.print_err is True:
							print(f'Error, the percentage to pan by must be between 1-100, not "{pan_percentage}"')
				else:
					ffmpeg_cmd.append()

		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		has_aud = 'Audio' in strm_types
		if has_aud is False:
			if self.print_err is True:
				print(f'''Error, there's no audio stream(s) to pan from input "{self.in_path.suffix}"''')
			return False
		else:
			for strm_index, stream_type in enumerate(strm_types):
				if stream_type == 'Audio':
					ffmpeg_cmd.append(f'0:{strm_index}')
		pass

	def two_separate_stereo_aud_files_to_one_stereo_aud_file(self, right_aud_in_path):
		"""This method will pan the main input stereo audio to the left, and the second stereo input audio to the right for one stereo output.
		NOTE: The default self.in_path will be used as the input for the left audio channel."""

		_is_type_or_print_err_and_quit(type(right_aud_in_path), paths.Path, 'right_aud_in_path')

		main_in_strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		main_in_has_aud = 'Audio' in main_in_strm_types
		right_aud_in_strm_types = MetadataAcquisition(right_aud_in_path).return_stream_types()
		right_aud_in_has_aud = 'Audio' in right_aud_in_strm_types
		if main_in_has_aud is False:
			if self.print_err is True:
				print(f'''Error, there's no stereo audio stream to assign to the left audio channel from input "{self.in_path.suffix}"''')
			return False
		elif right_aud_in_has_aud is False:
			if self.print_err is True:
				print(f'''\nError, there's no stereo audio stream to assign to the right audio channel from input "{right_aud_in_path}"\n''')
			return False
		else:
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-i', right_aud_in_path, '-map', '0', '-c', 'copy']
			# ffmpeg -i input1.wav -i input2.wav -filter_complex "[0:a][1:a]amerge=inputs=2,pan=stereo|c0<c0+c2|c1<c1+c3[a]" -map "[a]" output.mp3
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
				   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()

	def change_image_resolution(self, keep_aspect_ratio_input_width='', conform_to_dimensions=''):
		"""This method will change the resolution of an image (which includes file artwork).
		keep_aspect_ratio_width can only contain one number, but conform_to_dimensions
		must contain two numbers seperated by a colon\n
		"1920" vs "1920:1080"."""

		_is_type_or_print_err_and_quit(type(keep_aspect_ratio_input_width), str, 'scale_dim')
		if keep_aspect_ratio_input_width != '' and conform_to_dimensions != '':
			print('Error, keep_aspect_ratio_width and conform_to_dimensions are mutually exclusive but both were specified.')
			return False
		elif keep_aspect_ratio_input_width == '' and conform_to_dimensions == '':
			print('Error, either keep_aspect_ratio_width or conform_to_dimensions must be specified.')
			return False
		scale = ''
		# conform_to_dimensions must 
		if conform_to_dimensions != '':
			# Confirm there aren't any characters besides one ":" and the dimension numbers.
			try:
				int(conform_to_dimensions.replace(':', ''))
			except ValueError:
				print(f'Error, conform_to_dimensions can only contain two numbers separated by a ":", not "{conform_to_dimensions}"')
				return False

			colon_count = conform_to_dimensions.count(':')
			if colon_count != 1:
				print(f'Error, conform_to_dimensions input "{conform_to_dimensions}" must have 1 colon, but {colon_count} were found.')
				return False
			# Check if the first characer is a ":" instead of a number like it should be (input=":100").
			elif conform_to_dimensions[0] == ':':
				print(f'Error, a number must be specified before the colon for conform_to_dimensions "[HERE]{conform_to_dimensions}"')
				return False
			# Check if the last characer is a ":" instead of a number like it should be (input="100:").
			elif conform_to_dimensions[-1:] == ':':
				print(f'Error, a number must be specified after the colon for conform_to_dimensions "{conform_to_dimensions}[HERE]"')
				return False
			else:
				scale = conform_to_dimensions
		else:
			# keep_aspect_ratio_width only allows for one number so see if it can be converted to an int.
			try:
				int(keep_aspect_ratio_input_width)
				scale = keep_aspect_ratio_input_width + ':-1'
			except ValueError:
				print(f'Error, keep_aspect_ratio_width can only contain one number, not "{keep_aspect_ratio_input_width}"')
				return False
		
		# If there are video, audio, or subtitle streams copy those to the output and change -metadata title value.
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-vf', 'scale='+scale, self.standard_out_path]
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def crop(self, scale_dim):
		"""Crop"""
		pass
		# TODO: Add trim by aspect ratio? Make crop_detect a separate mode of one crop method?
		# _is_type_or_print_err(type(scale_dim), str, 'scale_dim')
		# if input has : then it's an aspect ratio (16:9), otherwise it should be the dimensions (1920x1080)
		# If input != contain ':' and input != contain 'x' print error, it mus be in one of those two formats.
		
		# # If there are video, audio, or subtitle streams copy those to the output and change -metadata title value.
		# ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-vf', 'scale='+scale_dim+':-1', self.standard_out_path]
		
		# Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
		# 		 self.print_err, self.print_ren_info, self.print_ren_time,
		#        self.open_after_ren).check_depend_then_ren(append_faststart=False)
	
	def crop_detect_black_bars(self):
		"""If any black bars from the input video are detected (like if the footage is 4:3 but the frame is 16:9)
		they will be cropped out."""
		# Get the dimensions to crop out black bars.
		crop_dim = MetadataAcquisition(self.in_path, print_scan_time=self.print_ren_time).return_metadata(crop_detect=1)[0]

		if crop_dim is None:
			if self.print_err is True:
				print(f'''Error, there's no video footage to crop found from input:\n"{self.in_path}"\n''')
			return False

		# The dimensions are returned with pixel trim/offset indicated at the end so if both of those
		#   are 0 then there's nothing to trim. 920:1080:0:0
		# See https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg#4571
		# https://www.bogotobogo.com/FFMpeg/ffmpeg_cropdetect_ffplay.php
		if crop_dim[-4:] == ':0:0':
			if self.print_err is True:
				print(f'Error, no black bars to crop were found in input "{self.in_path}"')
			return False

		elif crop_dim is not None:
			# Filter to crop the output.
			# ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-filter:v',
			#               f'crop={crop_dim[0]}', '-c:a', 'copy', '-c:s', 'copy']
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-filter:v',
			              f'crop=960:720:160:0', '-c:a', 'copy', '-c:s', 'copy']

			# Remove any already existing artwork stream.
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
					
			ffmpeg_cmd.append(self.standard_out_path)
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
	
	def rotate_vid_frame(self, rotate_frame_by_degrees='90'):
		"""This method rotates the input frame by rotate_by_degrees degrees.\n
		NOTE: rotate_by_degrees can only be set to 90, 180, or 270, otherwise nothing changes."""

		_is_type_or_print_err_and_quit(type(rotate_frame_by_degrees), str, 'rotate_by_degrees')

		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		has_vid = 'Video' in strm_types
		if has_vid is False:
			if self.print_err is True:
				print(f'''\nError, there's no video frame to rotate from input:\n"{self.in_path}"\n''')
			return False

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-metadata:s:v',
		              f'rotate=-{rotate_frame_by_degrees}', '-c', 'copy', self.standard_out_path]

		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
			   self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)

	def rotate_footage(self, rotate_footage_by_degrees='0', hflip=False, vflip=False):
		"""This method rotates the input video footage by rotate_footage_by_degrees degrees.\n
		hflip flips the footage horizontally and vflip flips the footage vertically.\n
		NOTE: This method doesn't preserve video artwork."""

		_is_type_or_print_err_and_quit(type(rotate_footage_by_degrees), str, 'rotate_footage_by_degrees')
		_is_type_or_print_err_and_quit(type(hflip), bool, 'hflip')
		_is_type_or_print_err_and_quit(type(vflip), bool, 'vflip')

		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		has_vid = 'Video' in strm_types
		if has_vid is False:
			if self.print_err is True:
				print(f'''\nError, there's no video footage to rotate from input:\n"{self.in_path}"\n''')
			return False
		elif rotate_footage_by_degrees == '0' and hflip is False and vflip is False:
			print('Error, at least one rotation value must be specified for the output to change, '
			      'but all were left with the default values.')
			return False

		# Start of command and determine to add hflip/vflip keywords or not.
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0']
		if hflip is True:
			hflip_cmd = 'hflip,'
		else:
			hflip_cmd = ''
		if vflip is True:
			vflip_cmd = 'vflip,'
		else:
			vflip_cmd = ''

		# Remove any artwork stream.
		ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
		ffmpeg_cmd += ['-vf', hflip_cmd + vflip_cmd + f'rotate={rotate_footage_by_degrees}*(PI/180)',
		               '-metadata:s:v','rotate=0', '-c:a', 'copy', self.standard_out_path]  
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
		       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
		
	def concat(self, new_basename='', new_ext='', codec_copy=True, _loop_times=0):
		"""This method concatenates multiple files together to form one long continuous file.\n
		WARNING: This method will not work if any of the input files have multiple audio tracks.\n
		WARNING: This method will not work if any of the input files have chapters.
		At this point just use the rm_chapters method before running it through this one.\n
		NOTE: This method requires that self.in_path be a list containing every path to concatenate to output
			in order of index. ("[in_1, in_2'")\n
		NOTE: All input files must have the same streams (same codecs, same time base, etc.)
			but can be wrapped in different container formats because otherwise it won't work.\n
		NOTE: This method will remove any already existing chapters because otherwise it won't work.\n
		_loop_times is local because it's only designed to be used by FileOperations.loop\n
		See "https://trac.ffmpeg.org/wiki/Concatenate" for ffmpeg concatenation documentation."""
		
		_is_type_or_print_err_and_quit(type(new_basename), str, 'new_basename')
		_is_type_or_print_err_and_quit(type(new_ext), str, 'new_ext')
		_is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')
		_is_type_or_print_err_and_quit(type(_loop_times), int, '_loop_times')
		
		# Set in_path_list to a list of inputs from self.in_path for the sake of code clarity.
		in_path_list = self.in_path
		
		if _loop_times != 0:
			full_out_path = self.standard_out_path
		else:
			if type(in_path_list) is not list:
				print(f'Error, for the concat method the in_path must be a list containing the paths of files '
			    	  f'to concatenate in order (0, is first one, 1 is second, etc.), '
				      f'not {type(self.in_path)} {self.in_path}')
		
			# There were 0 or 1 valid input paths so nothing could be concatenated so print an error and quit.
			if len(in_path_list) == 0 or len(in_path_list) == 1:
				print(f'\nError, at least two files must be provided for the "self.in_path" list in order to append '
					  f'one file to another, but only \n"', sep='', end='')
				for input_path in self.in_path:
					print(str(input_path), sep=',', end='')
				print('" was given.\n')
				return False
			
			# Assign first path in list to "path_list_item_0" for the default output path.
			path_list_item_0 = paths.Path(self.in_path[0])
			
			# If new_ext is not the default value of '' assign the value of new_ext to out_ext.
			if new_ext != '':
				out_ext = new_ext
			# new_ext is the default '' so set out_ext to extension of path_list_item_0.
			else:
				out_ext = path_list_item_0.suffix
			
			# If new_basename is not the default value of '' assign the value of new_basename to out_basename.
			if new_basename != '':
				out_basename = new_basename
			else:
				# new_basename is the default '' so set out_basename to basename (no extension) of path_list_item_0
				out_basename = path_list_item_0.stem
			
			# Path to new file with basename out_basename with extension out_ext in the directory self.out_dir.
			full_out_path = paths.Path.joinpath(self.out_dir, out_basename + out_ext)

		# Generate text for a temporary file so ffmpeg can read it to know the locations of the files.
		paths_str = ''
		if _loop_times != 0:
			for index in range(_loop_times):
				paths_str = paths_str + f"file '{str(self.in_path)}'\n"
				# Ignore faulty "Unused Variable" error.
				index = index
		else:
			first_file_ext = in_path_list[0].suffix
			for in_concat_path in in_path_list:
				paths_str = paths_str + f"file '{str(in_concat_path)}'\n"
				if first_file_ext != in_concat_path.suffix:
					if codec_copy is True:
						if self.print_err is True:
							print(f'Error, in order to concat files and copy the codec all input files must have '
							      f'the same extension, but extension "{first_file_ext}" and '
							      f'"{in_concat_path.suffix}" do not match.')
							return False
					elif codec_copy is False:
						if self.print_err is True:
							print(f'Error, extension "{first_file_ext}" and "{in_concat_path.suffix}" '
							      f'do not match so the concatenated output may not include every input.')
		
		# Create temporary .txt file with the paths to the input files in order from top to bottom.
		temp_paths_txt_file = full_out_path.with_name('temp_paths_txt_file_for_' + full_out_path.stem + '.txt')
		temp_paths_txt_file.touch()
		# Write the paths string to the file.
		temp_paths_txt_file.write_text(paths_str)

		ffmpeg_cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_paths_txt_file, '-map', '0']

		# Copy input codec by default, but otherwise omit those keywords.
		if codec_copy is True:
			ffmpeg_cmd += ('-c', 'copy')
		else:
			# If the input has artwork remove it because otherwise it may not render properly.
			ffmpeg_cmd += ('-map_metadata', '-1')
			ffmpeg_cmd = FileOperations(self.in_path[0], self.out_dir, self.print_success,
										self.print_err, self.print_ren_info,
										self.print_ren_time)._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
		
		if _loop_times != 0:
			# Determine if the input has an artwork stream or not.
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
		ffmpeg_cmd.append(full_out_path)
		
		ren_result = Render(in_path_list, full_out_path, ffmpeg_cmd, self.print_success,
			   				self.print_err, self.print_ren_info, self.print_ren_time,
		       				self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
		# Delete the temporary file
		temp_paths_txt_file.unlink()
		return ren_result
	
	def compress_using_h265_and_norm_aud(self, new_res_dimensions='0000:0000', new_ext='',
										 video_only=False, custom_db='', print_vol_value=True):
		"""This method compresses the input video using the H.265 (HEVC) codec.\n
		See https://trac.ffmpeg.org/wiki/Encode/H.265 for more info/\n
		new_res_dimensions can be specified to alter the output video resolution.\n
		new_ext can be specified to output with a different extension (".mp4")\n
		This method automatically normalizes the output audio, but custom_db can be set to have a custom output dB level
		("-3 dB"/"3 dB")\n
		print_vol_value toggles whether or not to display the dB amount the output volume was changed by."""
		
		# Confirm all the inputs are the correct types.
		_is_type_or_print_err_and_quit(type(new_res_dimensions), str, 'new_res_dimensions')
		_is_type_or_print_err_and_quit(type(new_ext), str, 'new_ext')
		_is_type_or_print_err_and_quit(type(video_only), bool, 'video_only')
		_is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		_is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')
		
		# Confirm new_ext is valid.
		if self.in_path.suffix != '.mp4' and self.in_path.suffix != '.mov' and self.in_path.suffix != '.mkv':
			print(f'\nError, H.265 compression is not supported for input extension "{self.in_path.suffix}" '
			      f'from input:\n"{self.in_path}"\n')
			return False
		# Invalid input extension
		elif new_ext != '' and new_ext != '.mp4' and new_ext != '.mov' and new_ext != '.mkv':
			print(f'Error, target output extension, "{new_ext}" '
			      f'is not supported for H.265 compression but the input extension "{self.in_path.suffix}" '
			      'is valid so the output extension will not be modified.')
		
		# new_ext was not specified and or input extension is valid so output path is the standard output path.
		out_path = self.standard_out_path
		
		# '-pix_fmt', 'yuv420p' is specified in case the input video is prores, and '-tag:v', 'hvc1' tells macs that
		#  it can play the output video file.
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map_metadata', '0', '-pix_fmt', 'yuv420p', '-c:s', 'copy', '-c:v',
		              'libx265', '-preset', 'slow', '-crf', '18', '-start_at_zero', '-tag:v', 'hvc1']
		
		# Add the audio part of the command by scanning input for dB amount to raise by.
		if video_only is True:
			ffmpeg_cmd.append('-an')
		else:
			ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '48k']
			
			# Scan input file for dB amount to increase by and method returns ffmpeg audio cmds.
			# If it's already at 0.0 dB then it will return None.
			audio_cmd = FileOperations.loudnorm_stereo(self, _do_render=False, print_vol_value=print_vol_value,
			                                           custom_db=custom_db)
			if audio_cmd is not None and audio_cmd is not False:
				ffmpeg_cmd += audio_cmd
		
		# If a new resolution was specified then append that to ren_cmd, else, append empty list (nothing)
		if new_res_dimensions != '0000:0000':
			new_res_cmd = ['-vf', 'scale=' + new_res_dimensions]
		else:
			new_res_cmd = []
		for res_cmd in new_res_cmd:
			ffmpeg_cmd.append(res_cmd)
		
		# Append the output path.
		ffmpeg_cmd.append(out_path)
		
		Render(self.in_path, out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
		       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
		
		return True

	def embed_subs(self, in_subs_list):
		"""This method will embed the input subtitle file(s) into the output.\n
		in_subs_list must be a list of pathlib paths to the subtitle files to embed."""
		_is_type_or_print_err_and_quit(type(in_subs_list), list, 'in_subs_list')
		# temp_sub_dir = paths.Path.joinpath(self.out_paths_list, 'temp_directory_to_embed_subtitle_files.')
		# paths.Path.mkdir(temp_sub_dir)
		#
		# in_sub_dir = paths.Path(in_sub_dir)
		
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path]
		for sub_file in in_subs_list:
			if sub_file.suffix != '.vtt':
				if self.print_err is True:
					print(f'Error, the input "{sub_file}" is not a subtitle file so it will be omitted.')
			else:
				ffmpeg_cmd += ('-i', sub_file)
		ffmpeg_cmd += ('-map', '0')
		for sub_file_index, sub_file in enumerate(in_subs_list):
			ffmpeg_cmd += ('-map', f'{sub_file_index + 1}:0', f'-metadata:s:s:{sub_file_index}',
						   f'language={MetadataAcquisition(sub_file)._return_sub_lang()}')
			# -metadata:s:s:0 language=eng
			# ffmpeg -i input.mp4 -f srt -i input.srt -i input2.srt\ -map 0:0 -map 0:1 -map 1:0 -map 2:0
		# -c:v copy -c:a copy \ -c:s srt -c:s srt output.mkv
		ffmpeg_cmd += ['-c', 'copy', '-c:s', 'mov_text']
		ffmpeg_cmd.append(self.standard_out_path)
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd,
			   self.print_success, self.print_err, self.print_ren_info,
			   self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
	
	def extract_subs(self, include_other_metadata=False):
		"""This method will extract subtitles from the input then output each language to its own file.\n
		By default metadata is included (artist, chapters, etc.)
		but include_other_metadata can be set to False to disable this."""
		_is_type_or_print_err_and_quit(type(include_other_metadata), bool, 'include_other_metadata')

		out_paths_list = []
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-y']
		# Get all the streams form the input.
		strm_types = MetadataAcquisition(self.in_path).return_stream_types()
		# Get language extension and ffmpeg keyword dictionary.
		lang_key_dict = MetadataAcquisition(self.in_path)._return_sub_lang(check_file=False)
		for strm_index, strm_cont in enumerate(strm_types):
			# Subtitles from the streams list will be formatted as "Subtitle=xxx" so match by the beginning.
			if strm_cont.startswith('Subtitle='):
				# Remove the beginning "Subtitle=" and just keep the ffmpeg keyword on the end.
				ffmpeg_sub_key = strm_cont[-3:]
				for ext_key, cmd_key in lang_key_dict.items():
					if ffmpeg_sub_key == cmd_key:
						out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem + '.' + ext_key + '.vtt')
						ffmpeg_cmd += ('-map', f'0:{strm_index}')
						if include_other_metadata is False:
							ffmpeg_cmd += ('-map_metadata', '-1', '-map_chapters', '-1')
						ffmpeg_cmd.append(out_path)
						out_paths_list.append(out_path)
		if out_paths_list == [] and self.print_err is True:
			print(f'\nError, no subtitles to extract were found from input:\n"{self.in_path}"\n')
			return False
		Render(self.in_path, out_paths_list, ffmpeg_cmd, self.print_success, self.print_err,
			   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()

	def rm_subs(self):
		"""This method will remove any subtitles from the input."""
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy', '-map', '-0:s', self.standard_out_path]
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
			   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()		

	def embed_chapters(self, timecode_title_list, add_chap_headings=True, print_new_chapters=False):
		"""This method will assign the input timecodes to chapters for the output video.\n
		NOTE: This method overwrites any existing chapters.\n
		Chapters must be string timecodes and string titles in a list in a list:\n
		[['0:00.00', '0 Seconds in'], ['0:05.00', '5 Seconds in'], ['0:30.00', '30 seconds in']]\n
		NOTE: Timecodes can only be in one of these formats: 0:00.00 (minute, second, fraction of sec) or 00:00:00.00\n
		NOTE: The first chapter always has to be ['0:00.00', 'TITLE'] because otherwise it doesn't
		register the following chapter timecode.\n
		If add_chap_headings is True add a chapter heading in the format of: "Chapter 1: Title".
		If print_new_chapters is True print the timecode and title for each new chapter."""
		
		# Confirm all inputs are the correct type and if they aren't print an error and quit.
		_is_type_or_print_err_and_quit(type(timecode_title_list), list, 'timecode_title_list')
		_is_type_or_print_err_and_quit(type(add_chap_headings), bool, 'add_chap_headings')

		# Render temporary file of the input except with any already existing chapters removed.
		# Otherwise it just keeps the original chapters without allowing for new ones.
		temp_rm_chap_file = paths.Path().joinpath(self.out_dir, self.in_path.stem
		                                          + '-temp_rm_chapter' + self.in_path.suffix)
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy', '-map_chapters', '-1', temp_rm_chap_file]
		Render(self.in_path, temp_rm_chap_file, ffmpeg_cmd, False, self.print_err,
		       False, False, False).check_depend_then_ren()

		# Extract metadata from temp input without chapters, export it to a txt file, and read that data.
		meta_file_path = MetadataAcquisition(temp_rm_chap_file, self.print_ren_info,
		False, print_meta_value=False).extract_metadata_txt_file()
		existing_metadata = paths.Path(meta_file_path).read_text()
		
		# Lists for just string timecodes and just string titles.
		timecode_str_list = []
		chap_titles_list = []
		for timecode_title in timecode_title_list:
			if print_new_chapters is True:
				print(timecode_title[0], '-', timecode_title[1])
			timecode_str_list.append(timecode_title[0])
			chap_titles_list.append(timecode_title[1])
		
		# Convert string timecodes into equivalent total seconds as ints.
		# '0:05.00' = 5 (5 seconds in), '1:30.00' = 90 (1 minutes 30 seconds/90 seconds in).
		timecode_sec_int_list = []
		for timecode_str in timecode_str_list:
			timecode_sec_int_list.append(int(FileOperations(self.in_path, self.out_dir,
			print_ren_time=False)._return_input_duration_in_sec(convert_str_timecode_to_sec=timecode_str)))
		timecode_sec_int_list.append(int(FileOperations(self.in_path, self.out_dir,
		                                                print_ren_time=False)._return_input_duration_in_sec()))
		
		# Add chapter headings to all chapters (Chapter 1: TITLE).
		if add_chap_headings is True:
			for chp_num, title in enumerate(chap_titles_list):
				chap_titles_list[chp_num] = 'Chapter ' + str(chp_num + 1) + ': ' + title
		
		# Generate string of command to add chapter(s) in this ffmpeg format:
		# [CHAPTER]
		# TIMEBASE=1/1
		# START=0
		# END=5
		# title=0 Seconds in
		embed_chapters_cmd = ''
		start_timecode_int = 0
		for chapter_title in chap_titles_list:
			embed_chapters_cmd += f'\n[CHAPTER]\nTIMEBASE=1/1\nSTART={str(timecode_sec_int_list[start_timecode_int])}' \
								f'\nEND={str(timecode_sec_int_list[start_timecode_int + 1])}\ntitle={chapter_title}\n'
			start_timecode_int += 1
		embed_chapters_cmd = existing_metadata + embed_chapters_cmd
		paths.Path(meta_file_path).write_text(embed_chapters_cmd)
	
		# Main command and render.
		ffmpeg_cmd = ['ffmpeg', '-i', temp_rm_chap_file, '-i', meta_file_path, '-map_metadata',
		              '1', '-map', '0', '-c', 'copy', self.standard_out_path]
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
			   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()	
		
		# Delete temporary input with no chapters and delete temporary text file containing the other metadata from that
		#   temp no chapters input.
		meta_file_path.unlink()
		temp_rm_chap_file.unlink()
	
	def rm_chapters(self):
		"""This method removes chapters from the input (if there are any)."""
		
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map_chapters', '-1', '-c', 'copy',
		              '-map', '0:a?', '-map', '0:v?', '-map', '0:s?', self.standard_out_path]
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
			   self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
	
	def _return_input_duration_in_sec(self, convert_str_timecode_to_sec=''):
		"""Local method to return the duration of self.in_path vid/aud in seconds.\n
		if convert_str_timecode_to_sec is specified it will convert a string of a timecode into seconds,
		otherwise it's the self.in_path duration in seconds."""

		_is_type_or_print_err_and_quit(type(convert_str_timecode_to_sec), str, 'convert_str_timecode_to_sec')

		if convert_str_timecode_to_sec != '':
			duration = convert_str_timecode_to_sec
		else:
			duration = MetadataAcquisition(self.in_path, print_all_info=self.print_ren_info,
			                               print_scan_time=self.print_ren_time).return_metadata(duration=1)[0]

		if duration is None or duration == 'N/A':
			if self.print_err is True:
				print(f'''Error, no duration found for input:\n"{self.in_path}"\n''')
			return None

		# Use the string length of the timecode duration to determine what format it's in.
		timecode_format = ''
		try:
			has_dot = duration.find('.')
			if duration.find('.') == -1:
				if len(duration) > 6:
					timecode_format = '%H:%M:%S'
				elif len(duration) > 3:
					timecode_format = '%M:%S'
				elif len(duration) == 2 or len(duration) == 1:
					timecode_format =  '%S'
				else:
					raise ValueError
			else:
				if len(duration) > 9:
					timecode_format = '%H:%M:%S.%f'
				elif len(duration) > 5:
					timecode_format = '%M:%S.%f'
				elif len(duration) > 3:
					timecode_format='%S.%f'
				else:
					raise ValueError
			length = dates.datetime.strptime(duration, timecode_format).time()
		except ValueError:
			if self.print_err is True:
				print(f'Error, unable to calculate timecode duration for input "{duration}"\nTimecode numbers must be '
				      f'in a "00:00:00.00" format, down to "0", no more than ".00" digits, and if fractions of a second'
				      f'are specified they must have a leading "0" for example "0.4"')
			quit()

		# Add up total seconds (there are 3600 seconds in an hour and 60 seconds in a minute.)
		length_sec = int(length.hour * 3600) + int(length.minute * 60) + int(length.second)
		# The microsecond will have any leading zeros removed (20000 instead of the accurate 020000)
		# so if the input is 0.X seconds long, just add a decimal before appending the fractional seconds to the string.
		# However, if it's 0.0X seconds long it would omit that first zero immediately after the decimal,
		# so add a zero after the decimal for the length_sec string to have an accurate length.
		if len(str(length.microsecond)) == 6:
			length_sec = str(length_sec) + '.' + str(int(length.microsecond))
		else:
			length_sec = str(length_sec) + '.0' + str(int(length.microsecond))
		# Return string as a float number with trailing zeros removed.
		# e.g., str(length_sec) may be equal to "832.430000" seconds before being returned as a float.
		return float(length_sec)
	
	def _add_to_ren_cmd__rm_art_stream_index_selector(self, ffmpeg_cmd):
		"""This method determines if the main input has an artwork stream and what video index that would be.
		If there's a video stream then it's 1 (the second video stream) but if there's no video then its 0 (the first
		video stream.) Either way return the command."""
		# Extract all the different stream types for the input.
		stream_types = MetadataAcquisition(self.in_path).return_stream_types()

		# If an artwork stream exists continue, otherwise return False.
		art_stream = 'Artwork' in stream_types
		if art_stream is None:
			return ffmpeg_cmd

		# An artwork stream exists, so if a video stream exists remove the second video stream from the input.
		# ('-0:v:1' for video, and '-0:v:0' for audio.)
		# "-0:v:1" is saying to remove ("-") a stream of type video (":v:") in this case the second video stream.
		# Artwork is the only thing that could be in the second video stream of a video since the main stream (0)
		# is the video footage itself.
		# (The 1st video stream is video, but the second is artwork.)
		# Otherwise remove the first video stream
		# (because there's just the one video stream which is an artwork stream.)
		if 'Video' in stream_types:
			rm_strm = '1'
		else:
			rm_strm = '0'
		ffmpeg_cmd += ('-map', ('-0:v:'+rm_strm))
		return ffmpeg_cmd

class MetadataAcquisition:
	"""This class provides methods to get file metadata.
	NOTE: return_metadata is the only method designed to be used.\n"""
	
	def __init__(self, in_path, print_all_info=False, print_scan_time=False, print_meta_value=False):
		"""Requires a path object to an input file and optional file info printing"""
		
		# Run function to print an error and quit if the input type is not valid.
		_is_type_or_print_err_and_quit(type(in_path), paths.Path, 'in_path')
		_is_type_or_print_err_and_quit(type(print_all_info), bool, 'print_all_info')
		_is_type_or_print_err_and_quit(type(print_scan_time), bool, 'print_scan_time')
		_is_type_or_print_err_and_quit(type(print_meta_value), bool, 'print_meta_value')
		
		# Create path object of input file.
		self.in_path = paths.Path(in_path)
		
		# Boolean value for printing all file info provided by ffprobe (default is False.)
		self.print_all_info = print_all_info
		# Boolean value for printing all the metadata values generated.
		self.print_meta_value = print_meta_value
		# Boolean value for printing how long it took to scan in_path.
		self.print_scan_time = print_scan_time
	
	def _check_file_exists(self):
		"""Check that input file exists"""
		
		if self.in_path.exists() is False:
			# If the input file doesn't exist print an error message and return False.
			print(f'Error, input file, "{self.in_path}" not found.')
			quit()
		elif self.in_path.is_file() is False:
			# If the input exists, but isn't a file then print an error message and return False.
			print(f'Error, input "{self.in_path}" is not a file.')
			quit()
		else:
			# The file exists!
			return True
	
	def _term_return_file_info(self, custom_cmd=''):
		"""Run the terminal command to get the info from ffprobe.\n
		custom_cmd can be a list of a command to run in the terminal,
		but if it's not specified then return all file info."""
		
		if custom_cmd == '':
			info_cmd = ['ffprobe', '-i', self.in_path, '-hide_banner']
		else:
			info_cmd = custom_cmd
		
		try:
			start_time = time.perf_counter()
			info_process = sub.run(info_cmd, stdout=sub.PIPE, stderr=sub.PIPE, universal_newlines=True)
			# Run actual command and get output.
			end_time = time.perf_counter()
			if self.print_all_info is True:
				# Print all info from ffprobe.
				print(info_process.stderr)
			if self.print_scan_time is True:
				print('\n"', self.in_path, '"', sep='')
				duration = Render.terminal_render_timer(start_time, end_time, operation_keyword=' to scan')
				print(duration)
			return info_process.stderr + info_process.stdout
		# Return True (it worked.)
		except sub.CalledProcessError:
			# Unknown error occurred so print an error and return False.
			if self.print_all_info is True:
				# The rendering failed, print an error message.
				print(f'\nError, a problem occurred with metadata acquisition:')
				print(f'Terminal input command: {info_cmd}\n{info_process.stderr}')
				quit()
			return False
	
	def return_metadata(self, artist_author=False, album=False, description=False, lyrics=False, genre=False,
	                    composer=False, track_num=False, disc_num=False, date=False, start_offset=False, comment=False,
	                    title=False, duration=False, performer=False, max_volume=False, first_aud_strm_info=False,
	                    first_vid_strm_info=False, every_stream_info=False, crop_detect=False, vid_dim=False):
		"""This is the main method to get metadata values for files.\n
		NOTE: At least one new value must be specified.\n
		By default, all values are set to False so to return any of those preset values
		assign them an int in ascending order\n
		e.g. (title=1, lyrics=3, composer=2) will be returned with the list value: [title, composer, lyrics]."""
		
		# Dictionary to store the ffprobe keywords.
		meta_dict = dict([
			(artist_author, 'artist'),
			(album, 'album'),
			(description, 'description'),
			(lyrics, 'lyrics'),
			(genre, 'genre'),
			(composer, 'composer'),
			(track_num, 'track'),
			(disc_num, 'disc'),
			(date, 'date'),
			(start_offset, 'start'),
			(comment, 'comment'),
			(title, 'title'),
			(duration, 'Duration'),
			(performer, 'performer'),
			(max_volume, 'max_volume'),
			(first_aud_strm_info, 'Audio'),
			(first_vid_strm_info, 'Video'),
			(every_stream_info, 'Stream'),
			(crop_detect, 'crop'),
			(vid_dim, 'dimensions'),
		])
		
		# List to store all the possible return values for metadata for this method.
		in_meta_value_list = [artist_author, album, description, lyrics, genre, composer, track_num, disc_num,
		                      date, start_offset, comment, title, duration, performer, max_volume, first_aud_strm_info,
		                      first_vid_strm_info, every_stream_info, crop_detect, vid_dim]
		
		# Make sure at least one value to return was specified.
		all_input_equal = all(in_meta_value_list)
		if all_input_equal is True:
			print('Error, at least one metadata value must be specified to return anything.')
		
		# List to store the keywords to obtain the metadata values.
		in_meta_keyword_list = []
		# List to store the output order integers.
		out_order_int_list = []
		
		# Confirm input values are valid ints or False:
		for meta_key_int in in_meta_value_list:
			if type(meta_key_int) is not int and meta_key_int is not False:
				# Confirm that all metadata return values are False or type int.
				print(f'Error, metadata values to return can only be integers (in ascending order to return) '
				      f'or False, not {type(meta_key_int)} "{meta_key_int}"')
				quit()
			elif type(meta_key_int) is int:
				# Add each output order integer to a list and the input order integer
				# before the metadata keyword_with_int (e.g. "01title").
				out_order_int_list.append(meta_key_int)
				in_meta_keyword_list.append(f'{meta_key_int:02d}' + meta_dict[meta_key_int])
		
		# Remove the output order integer before the keyword_with_int (e.g. "01title")
		# now that the list has the correct order.
		in_meta_keyword_list.sort()
		out_order_int_list.sort()
		out_keyword_sorted_list = []
		for keyword_with_int in in_meta_keyword_list:
			out_keyword_sorted_list.append(keyword_with_int[2:])
		
		# Check if there are any duplicate output order integers.
		dup_int_scanned = {}
		dupe_in_int = []
		for in_int in out_order_int_list:
			if in_int not in dup_int_scanned:
				dup_int_scanned[in_int] = 1
			else:
				if dup_int_scanned[in_int] == 1:
					dupe_in_int.append(in_int)
				dup_int_scanned[in_int] += 1
		if len(dupe_in_int) > 0:
			print(f'Error, output order number "{dupe_in_int[0]}" can only be specified once.')
			quit()
		
		# Check if output order ints are within the valid range (1-4 if 4 metadata values to return are specified.)
		for meta_key_int in out_order_int_list:
			if meta_key_int < 1 or meta_key_int > len(out_order_int_list):
				print(f'Error, return order integer "{meta_key_int}" must be in range 1-{len(in_meta_keyword_list)}')
				quit()
		
		# Confirm file exists (it will quit if it doesn't.)
		self._check_file_exists()
		
		# Make an empty list to be returned so values can be appended.
		metadata_value_list = []
			
		# Determine null keyword_with_int for system based on the path type.
		if type(self.in_path) is paths.PosixPath:
			null_keyword = '/dev/null'
		else:
			null_keyword = 'NUL'
		
		# Nested function that runs a custom ffmpeg command that scans the input using a certain filter without
		# producing a file output.
		def calculate_metadata(format_str, filter_str, output_keyword):
			calculate_value_cmd = ['ffmpeg', '-i', self.in_path, format_str,
								   filter_str, '-f', 'null', null_keyword, '-hide_banner']
			info_with_calculated_value = self._term_return_file_info(calculate_value_cmd)
			calculate_result = self._find_meta_value(info_with_calculated_value, output_keyword)
			return calculate_result

		# Go over all the specified inputs to retrieve their values.
		for value_keyword in out_keyword_sorted_list:
			# Run the input through a filter to retrieve a special value.	
			if value_keyword == 'max_volume':
				current_key_value = calculate_metadata('-af', 'volumedetect', 'max_volume')
			elif value_keyword == 'crop':
				current_key_value = calculate_metadata('-vf', 'cropdetect', 'crop')
			elif value_keyword == 'Stream':
				file_info = self._term_return_file_info()
				current_key_value = self._find_meta_value(file_info, value_keyword)
			elif value_keyword == 'Duration':
				cal_dur_cmd = ['ffmpeg', '-i', self.in_path, '-f', 'null', '-']
				info_with_dur = self._term_return_file_info(cal_dur_cmd)
				current_key_value = self._find_meta_value(info_with_dur, value_keyword)
			
			# Run standard command that only returns the value of the input key.
			else:
				return_value_cmd = ['ffprobe', '-v', 'quiet', '-show_entries',
									f'format_tags={value_keyword}',
									'-of', 'default=nw=1:nk=1', self.in_path]
				value = self._term_return_file_info(return_value_cmd)
				if value == '':
					current_key_value = None
				else:
					# Remove the newline from the end of the value.
					current_key_value = value[:-1]
				# if self.print_meta_value is True:
				# print(f'\n{key}:\n{current_key_value}')
			
				# If the metadata keyword value isn't in the input file then potentially print an error.
				if self.print_meta_value is True:
					if current_key_value is None:
						print(f'\nError, metadata value "{value_keyword}" not found.')
					else:
						print(f'\n{value_keyword}:\n{current_key_value}')
			
		metadata_value_list.append(current_key_value)
		return metadata_value_list
	
	def return_stream_types(self):
		"""This method returns the type of input streams in order of their index."""
		
		# Get one long string of all the info about the input file then split that into a list.
		strm_types = self.return_metadata(every_stream_info=1)[0]
		strm_types = strm_types.splitlines()
		# List of the stream types from the input.
		strm_types_list = []
		for strm in strm_types:
			for stream_str_index in range(len(strm)):
				if strm[stream_str_index:stream_str_index + 5] == 'Video':
					if strm[-14:] == '(attached pic)':
						strm_types_list.append('Artwork')
						break
					else:
						strm_types_list.append('Video')
						break
				elif strm[stream_str_index:stream_str_index + 5] == 'Audio':
					strm_types_list.append('Audio')
					break
				elif strm[stream_str_index:stream_str_index + 4] == 'Data':
					strm_types_list.append('Chapter')
					break
				# If the stream is a subtitle then "restart" the loop and get the language before the "Stream" keyword.
				elif strm[stream_str_index:stream_str_index + 8] == 'Subtitle':
					for ffmpeg_strm_index, ffmpeg_strm_str in enumerate(strm):
						if ffmpeg_strm_str == '(':
							strm_types_list.append(f'Subtitle={strm[ffmpeg_strm_index + 1:ffmpeg_strm_index + 4]}')
							break
				else:
					pass
		return strm_types_list
	
	def extract_metadata_txt_file(self):
		"""This method extracts all the metadata from the input file into an output text file."""

		# Confirm file exists (it will quit if it doesn't.)
		MetadataAcquisition(self.in_path, self.print_all_info, self.print_scan_time,
		                    self.print_meta_value)._check_file_exists()
		
		ren_meta_txt_file = paths.Path.joinpath(self.in_path.parent, self.in_path.stem + '-METADATA.txt')
		ren_meta_txt_file_cmd = ['ffmpeg', '-i', self.in_path, '-f', 'ffmetadata', '-hide_banner', ren_meta_txt_file]

		ren_meta_txt_file = paths.Path(ren_meta_txt_file)

		if ren_meta_txt_file.exists():
			ren_meta_txt_file.unlink()

		MetadataAcquisition(self.in_path, self.print_all_info, self.print_scan_time,
		                    self.print_meta_value)._term_return_file_info(ren_meta_txt_file_cmd)
		
		return ren_meta_txt_file
	
	def _return_sub_lang(self, check_file=True):
		"""This method holds a dictionary to hold file and ffmpeg keywords for the different languages of subtitles.\n
		if check_file is True then this method will look at the second to last suffix for a .vtt subtitle file
			and return the equivalent subtitle language keyword for a ffmpeg command.\n
			e.g., "File Name-.en.vtt returns "eng" (english subtitles) = '-metadata:s:s: language=eng'\n
		if check_file is False return the dictionary."""

		_is_type_or_print_err_and_quit(type(check_file), bool, 'check_file')
		
		# Dictionary that holds a subtitle file extension which represents the language and the keyword
		# so ffmpeg can assign the metadata for that file to the correct language.
		# File_Name-.en.vtt
		# '-metadata:s:s: language=eng'
		lang_dict = dict([
			# English
			('en', 'eng'),
			('en-CA', 'eng'),
			('en-GB', 'eng'),
			('en-US', 'eng'),
			# Chinese
			('zh-Hans', 'zho'),
			('zh-Hant', 'zho'),
			('zh-TW', 'zho'),
			# Vietnamese
			('vi', 'vie'),
			# Catalan
			('ca', 'cat'),
			# Italian
			('it', 'ita'),
			# Hebrew
			('iw', 'heb'),
			# Arabic
			('ar', 'ara'),
			# Czech
			('cs', 'ces'),
			# Estonian
			('et', 'est'),
			# Indonesian
			('id', 'ind'),
			# Spanish
			('es', 'spa'),
			('es-419', 'spa'),
			# Russian
			('ru', 'rus'),
			# Dutch
			('nl', 'nld'),
			# Portuguese
			('pt', 'por'),
			# Norwegian
			('no', 'nor'),
			# Turkish
			('tr', 'tur'),
			# Lithuanian
			('lt', 'lit'),
			# Thai
			('th', 'tha'),
			# Romanian
			('ro', 'ron'),
			# Polish
			('pl', 'pol'),
			# French
			('fr', 'fra'),
			# Bulgarian
			('bg', 'bul'),
			# Ukrainian
			('uk', 'ukr'),
			# Slovenian
			('sl', 'slv'),
			# Croatian
			('hr', 'hrv'),
			# Hungarian
			('hu', 'hun'),
			# Portuguese
			('pt-BR', 'por'),
			# Finnish
			('fi', 'fin'),
			# Danish
			('da', 'dan'),
			# Japanese
			('ja', 'jpn'),
			# Serbian
			('sr', 'srp'),
			# Korean
			('ko', 'kor'),
			# Swedish
			('sv', 'swe'),
			# Slovak
			('sk', 'slk'),
			# German
			('de', 'deu'),
			# Malay
			('ms', 'msa'),
			# Greek/Modern
			# ('--', '---'),
		])

		if check_file is True:
			try:
				# Return the the second to last suffix which says which language the subtitles are.
				# File Name."en".vtt
				# (It's the second to last because if there's a "." in the file name that will be included in the suffixes list.)
				# The file suffixes will be a list ['.en', '.vtt'] with ".en" used for this example.
				# Select the file's second to last suffix [:-1] = ['.en'],
				# the first (and only) element of that list which is a string of the desired suffix [0] = '.en',
				# remove the first character from that string (the "." which says it's an extension) [1:] = 'en',
				# and return the value for the 'en' key from the lang_dict.
				return lang_dict[self.in_path.suffixes[:-1][0][1:]]
			except KeyError:
				if self.print_all_info is True or self.print_meta_value is True:
					print(f'Error, unknown language found for input "{self.in_path}"')
				return False
		elif check_file is False:
			return lang_dict

	def _find_meta_value(self, filter_output, keyword):
		"""Filter ffmpeg/ffprobe output to locate info about a file and return the "keyword" value if it was found."""
		# Empty list of metadata value(s) to return.
		return_metadata_value_list = []

		if self.print_all_info is True:
			print('\n' + filter_output, end='')

		# Boolean value stating if the metadata keyword value was found in the file at all.
		keyword_value_exists = keyword in filter_output

		# If the metadata keyword value isn't in the input file then print an error.
		if keyword_value_exists is False:
			if self.print_meta_value is True:
					print(f'\nError, metadata value "{keyword}" not found.')
			return None
		
		# The metadata keyword was found so append that value to return_metadata_value_list.
		# Create a list where each line in filter_output is an element, then remove all of the file info before that.
		file_info_after_keyword_list = filter_output.split(keyword, 1)[1].split('\n')
		# Add ' ' to the list so it's sure to iterate through the whole list.
		file_info_after_keyword_list.append(' ')
		# Empty string that will be replaced with the value of the specified metadata keyword.
		# (if the keyword is "title" then keyword_value will become something like "Song title"
		keyword_value = ''
		complete_key_value = ''
		
		# For loop going over every string in file_info_after_keyword_list
		#   to return metadata values that span more than one line.
		for info_after_key_list_index, info_line_str, in enumerate(file_info_after_keyword_list):
			# For loop that goes over every character in the filter_output line
			# (which starts at the line where the metadata keyword was found.)
			for info_line_str_index, info_line_str_value, in enumerate(info_line_str):
				# The "Stream" keyword has the index info before the : so don't start after:
				# Stream [AFTER HERE]#0:1(und): Audio: aac...
				if keyword == 'Stream':
					# The first input starts like " #0:1(und): Audio: aac..." so to start begin at #.
					if info_line_str_value == '#':
						keyword_value = info_line_str[info_line_str_index + 1:] + '\n'
						complete_key_value += keyword_value
						break
					# See if the current line starts with "Stream" and if so get the info from it.
					elif info_line_str[info_line_str_index:info_line_str_index + 6] == 'Stream':
						keyword_value = info_line_str[info_line_str_index + 8:] + '\n'
						complete_key_value += keyword_value
						break
					# The loop got to ' ' so if it looped again it would terminate without
					# adding the value(s) to the list, so add the Stream info to the return list
					# and stop the loop by clearing the lines list and string.
					elif info_after_key_list_index + 1 == len(file_info_after_keyword_list):
						if self.print_meta_value is True:
							print(f'\n{keyword}(s):\n{complete_key_value[:-1]}', end='')
						return_metadata_value_list.append(complete_key_value)
						file_info_after_keyword_list.clear()
						break
					elif info_line_str_value != ' ':
						break
				
				elif keyword == 'crop':
					if info_line_str[info_line_str_index:info_line_str_index + 4] == 'crop':
						keyword_value = info_line_str[info_line_str_index + 5:]
						if self.print_meta_value is True:
							# Don't print the "\n" on the end of the string.
							print(f'{keyword}:\n{keyword_value}', end='')
						return_metadata_value_list.append(keyword_value)
						file_info_after_keyword_list.clear()
						break

				# ffprobe returns excess spaces (which ffprobe uses to center values when printing)
				# so scan the line string until a : is encountered because the actual value begins after that.
				elif info_line_str_value == ':':
					keyword_value = keyword_value + info_line_str[info_line_str_index + 2:] + '\n'
					break
				
				# If the metadata value spans multiple lines then there will only be spaces between
				# each line with a : before the value of each line.
				# (description  : Description Line 1\n      : Description Line 2\n     [HERE]purl    :)
				# however if a different character is encountered then that's the beginning of the next metadata
				# keyword returned (see [HERE],) so ignore all characters for that line onward by clearing
				# the list because the complete value for the keyword has been saved in complete_keyword_value.
				# Plus if self.print_meta_value is True print the metadata value keyword followed by the value.
				elif info_line_str_value != ' ':
					complete_keyword_value = keyword_value.rstrip('\n')
					if keyword == 'start' or keyword == 'Duration':
						# The bitrate is specified after the timecode so split list at the comma and use first string in
						# list. (0.023021[HERE], bitrate: 122 kb/s)
						complete_keyword_value = complete_keyword_value.split(',')
						complete_keyword_value = complete_keyword_value[0].lstrip('0')
					# The metadata value wasn't found so print Null and/or return None.
					if keyword == 'Duration':
						# The duration returns an extra colon at the beginning because the input is not at least one
						# hour in length so remove it.
						if complete_keyword_value[:1] == ':':
							complete_keyword_value = complete_keyword_value[1:]
					if complete_keyword_value == '':
						if self.print_meta_value is True:
							print(f'{keyword}:\nError, metadata value "{keyword}" not found.')
						return_metadata_value_list.append(None)
					else:
						if self.print_meta_value is True:
							print(f'\n{keyword}:\n{complete_keyword_value}', end='')
						return_metadata_value_list.append(complete_keyword_value)
						file_info_after_keyword_list.clear()
						break
		if self.print_meta_value is True:
			print()
		# I think this only does one keyword at a time so return that one item
		# because I don't want to redo everything right now.
		return return_metadata_value_list[0]

class Visualizer:
	def __init__(self, in_path, out_dir, resolution='1920x1080', background=True, background_rgb='Default',
	             background_artwork_or_video=None, freq_rgb='Default', file_artwork='Input Artwork',
	             print_success=True, print_err=True, print_ren_info=False, print_ren_time=False, open_after_ren=False):
		"""Class for creating a visualizer from input audio\n
		NOTE:\n
			background type can be True (default black color) or False (transparent).\n
			background_rgb must be a RGB value string.\n
			background_artwork_or_video must be a path to an artwork file (default value is None).\n
			background_rgb and background_artwork_or_video are mutually exclusive.\n
			freq_rgb and background_rgb can change the color of the frequency indicator and background respectively,\n
			    Certain color keywords provide the rgb value, otherwise rgb input is treated as a rgb code
			    (see rgb_value_dict for keywords, but only one color can be set at a time.)\n
			file_artwork default ('Input Artwork') gets any potential file_artwork from the input,
				but can also be set to an artwork_file path.\n
			open_after_ren can be set to True (open output file with default application) False (don't open at all) or
				a string of an application name to open output file with said application,
				(PosixPath only because I'm not going to spend the time to learn the specific windows command.)
		"""
		
		# Path to input file for the ffmpeg cmd.
		self.in_path = paths.Path(in_path)
		# Path to output directory for ffmpeg cmd.
		self.out_dir = paths.Path(out_dir)
		# Path to standard ffmpeg output path which is just the original name of the input in a new directory.
		self.out_path = paths.Path.joinpath(self.out_dir, self.in_path.stem + '.mp4')
		# Set the resolution of the output video file (default is 1920x1080).
		self.resolution = resolution
		
		# Boolean value to determine whether or not to have a video background (as opposed to being transparent).
		if background is True:
			self.background = True
		# There should be a background, but if it's not specified then it will default to background_rgb (Black).
		elif background is False:
			self.background = False
		# There should be a transparent background, so print an error if a background artwork or RGB value is specified.
		else:
			print(f'Error, background must be True or False, not {background}')
			quit()
		
		# Dictionary to hold RGB values so they can easily be called by using a color keyword.
		rgb_value_dict = dict([
			('Green', 'green rgb'),
			('Black', 'Black'),
			('Yellow', 'yellow rgb'),
		])
		
		# Local method to return the RGB value if the rgb_keyword matches, otherwise just return rgb_keyword
		# (which is supposed to be a custom RGB color.)
		def get_rgb_value(rgb_keyword):
			for rgb_color_code in rgb_value_dict.keys():
				if rgb_keyword == rgb_color_code:
					return rgb_value_dict[rgb_color_code]
			else:
				return rgb_keyword
		
		# The video background can either be an image or an RGB color, so print an error if both are specified.
		if background_rgb != 'Default' and background_artwork_or_video is not None:
			print(f'Error, background_rgb and background_artwork_or_video are mutually exclusive.')
			quit()
		
		# Set video background to a custom RGB value with certain color presets available (see rgb_value_dict).
		if background is False and background_rgb != 'Default':
			print(f'Error, background is set to False (transparent), background must be set to True to change the RGB value.')
			quit()
		elif background_rgb == 'Default':
			# Nothing was specified so set background_rgb to default Black.
			self.background_rgb = rgb_value_dict['Black']
		elif type(background_rgb) is str and background_rgb != 'Default':
			self.background_rgb = get_rgb_value(background_rgb)
		# This is supposed to be a custom RGB input color.
		else:
			print(f'Error, background_rgb must be a RGB string, not "{background_rgb}"')
			quit()
		
		# Set video background to a custom image.
		if background is False and background_artwork_or_video is not None:
			print('Error, background is set to False (transparent),'
			      'background must be set to True to add background_artwork_or_video.')
			quit()
		elif background_artwork_or_video is None:
			self.back_art_or_video = None
		# background_artwork_or_video is in the default state of None so set self.background_art to None.
		else:
			# A value was specified so try to set self.background_art to path or artwork.
			try:
				art_path = paths.Path(background_artwork_or_video)
				if art_path.is_file():
					self.back_art_or_video = art_path
			except TypeError:
				print(f'Error, background_artwork_or_video must be a file path,'
				      f'not {type(background_artwork_or_video)} "{background_artwork_or_video}"')
		
		# String to change the frequency rgb value with certain color presets available (see rgb_value_dict).
		if freq_rgb == 'Default':
			# Set frequency RGB value to the default (Green).
			self.freq_rgb = rgb_value_dict['Green']
		elif type(freq_rgb) is not str:
			# Input is not type string so print an error.
			print(f'Error, freq_rgb needs to be a string, not {type(freq_rgb)}')
		elif freq_rgb != 'Default' and type(freq_rgb) is str:
			# A string value was specified so run get_rgb_value to see if freq_rgb is a valid RGB color keyword.
			self.freq_rgb = get_rgb_value(freq_rgb)
		else:
			print(f'Error, "{freq_rgb}"" is not a valid RGB frequency value.')
			quit()
		
		# Attempt to set the output file artwork to the artwork from the input.
		if file_artwork is True:
			self.file_artwork = True
		elif file_artwork is False:
			self.file_artwork = False
		elif type(file_artwork) is paths.PosixPath and file_artwork.exists() is True \
				or type(file_artwork) is paths.WindowsPath and file_artwork.exists() is True:
			self.file_artwork = file_artwork
		elif type(file_artwork) is paths.PosixPath and file_artwork.exists() is False \
				or type(file_artwork) is paths.WindowsPath and file_artwork.exists() is False:
			print(f'Error, input file: "{file_artwork}"', "doesn't exist.")
		else:
			print(f'Error, file_artwork must be True (default, embed input artwork to output artwork),'
			      f'False, or a pathlib path to new artwork, not {type(file_artwork)} {file_artwork}')
			quit()
		
		# Boolean value to toggle on or off the terminal output for ffmpeg error info.
		self.print_ren_info = print_ren_info
		# Boolean value to toggle on or off displaying how long it took to render the file.
		self.print_ren_time = print_ren_time
		
		# open_after_ren will atomically open the output file if set to True,
		# with a specific application if set a string, or not at all if set to False.
		if type(open_after_ren) is bool or type(open_after_ren) is str:
			self.open_after_ren = open_after_ren
		else:
			print(f'Error, open_after_ren must be True, False, or string of application name, not {type(open_after_ren)}'
			      f'{open_after_ren}')
		
		# Boolean value to toggle on or off the terminal output (file path or error message)
		self.print_success = print_success
		self.print_err = print_err
	
	def _eval_ren_cmd(self, render_cmd):
		"""This local method determines which rendering class/method to use based on the self.file_artwork and opens the
		output if self.open_after_ren is True/string"""
		
		if self.file_artwork is True:
			# Attempt to embed the artwork from the input file.
			Render(self.in_path, self.out_path, render_cmd, self.print_success, self.print_err, self.print_ren_info,
			       self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
		elif self.file_artwork is False:
			# Just render normally, don't attempt to embed any artwork.
			Render(self.in_path, self.out_path, render_cmd, self.print_success, self.print_err,
			       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
		elif self.file_artwork.is_file():
			# An artwork file was specified so embed that after the video finishes rendering.
			Render(self.in_path, self.out_path, render_cmd, self.print_success, self.print_err,
			       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
			# Do the standard render.
			temp_rename_file = self.out_path.with_name(self.out_path.stem + '-Remove This' + self.out_path.suffix)
			# Specify path to temporary file because otherwise it will try to output a file
			# with the same name as the original output which will raise an error.
			FileOperations(self.out_path, self.out_path.parent, self.print_success, self.print_err, self.print_ren_info,
			               self.open_after_ren).embed_artwork(self.file_artwork, append_to_basename='-Remove This')
			# Render new file with artwork embedded with temp name.
			temp_rename_file.rename(self.out_path)
		# Rename file with embedded artwork to the original output name.
		else:
			print('Unknown error occurred with self.file_artwork')
	
	def showfreqs(self):
		
		render_cmd = ['ffmpeg', '-f', 'lavfi', 'amovie=', self.in_path, 'asplit', '[a][out1];',
		              '[a]', 'showvolume=f=1:b=4:w=800:h=70', '[out0]', self.out_path]
		# render_cmd = ['ffmpeg', '-i', self.in_path, '-filter_complex',
		#               "[0:a]showspatial=win_func=bartlett,format=yuv420p[v]",
		#               '-map', '[v]', '-map', '0:a', '-c:a', 'aac', self.out_path]
		# render_cmd = ['ffmpeg', '-i', self.in_path, '-filter_complex',
		#               "[0:a]showfreqs=mode=line:fscale=log:ascale=cbrt:colors=Red|Orange|Red|Blue,format=yuv420p[v]",
		#               '-map', '[v]', '-map', '0:a', '-c:a', 'aac', self.out_path]
		# render_cmd = ['ffmpeg', '-i', self.in_path, '-filter_complex',
		#               "[0:a]showfreqs=mode=line:fscale=log,format=yuv420p[v]",
		#               '-map', '[v]', '-map', '0:a', '-c:a', 'aac', self.out_path]
		#-c:a copy -map 0:a -strict -2 -c:a aac
		
		# ffmpeg -i INPUT.wav -filter_complex
		# "[0:a]ahistogram=s=hd480:slide=scroll:scale=log,format=yuv420p[v]"
		# -map "[v]" -map 0:a
		# -b:a 360k OUTPUT.mp4
		
		# Evaluate which rendering method to use based on self.artwork being set to a file or default input artwork.
		Visualizer._eval_ren_cmd(self, render_cmd)
	
	def ahistogram(self):
		pass


class Render:
	"""This class runs the terminal command to achieve the desired output."""
	def __init__(self, input_path__pathlib_object_or_list, out_file_or_out_list, render_cmd, print_success=True,
				 print_err=True, print_ren_info=False, print_ren_time=True, open_after_ren=False):
		# Path to input file or list.
		self.in_path = input_path__pathlib_object_or_list
		# Path to output file (for printing success/error messages) but can be a list for multiple outputs.
		if type(out_file_or_out_list) is not list:
			self.out_paths_list = [out_file_or_out_list]
		else:
			self.out_paths_list = out_file_or_out_list
		# List containing all the required terminal words
		# (new strings in the list are interpreted as spaces in the subprocess call.)
		# ['ffmpeg', '-i', path] = "ffmpeg -i path"
		self.ren_cmd = render_cmd
		# Toggle printing the render result (with paths).
		self.print_success = print_success
		# Toggle printing errors.
		self.print_err = print_err
		# Toggle printing the input file metadata info.
		self.print_ren_info = print_ren_info
		# Toggle displaying how long it took to render the file.
		self.print_ren_time = print_ren_time
		# Toggle opening the file in the default application after it finishes rendering.
		self.open_after_ren = open_after_ren

	def check_depend_then_ren(self, append_faststart=True):
		"""Confirm the file dependencies exist, and if they do then call run_terminal_cmd.\n
		append_faststart is an option to optimize video playback,
		but if the command is for AtomicParsley omit this option."""
		
		# Make input a list (if it isn't already one) to use in a for loop.
		if type(self.in_path) is not list:
			input_path_list = [self.in_path]
		else:
			input_path_list = self.in_path
		
		# Confirm input path(s) exist.
		for in_path in input_path_list:
			in_path = paths.Path(in_path)
			if in_path.exists() is False:
				print(f'Error, input file, "{in_path}" not found.')
				quit()
			elif in_path.is_file() is False:
				print(f'Error, input "{in_path}" is not a file.')
				quit()
		
		# Confirm the output file doesn't already exist, and if it doesn't then render.
		for out_path in self.out_paths_list:
			if out_path.is_file():
				print(f'Error, target output file, "{out_path}" already exists.')
				quit()
			elif out_path.parent.exists() is False:
				print(f'Error, "{out_path.parent}" is not a valid output directory.')
				quit()
		exists_result = self.run_terminal_cmd(append_faststart=append_faststart)
		return exists_result
	
	def run_terminal_cmd(self, append_hide_banner=True, append_faststart=True):
		"""This method runs the actual command to render the output within the terminal.\n
		append_hide_banner will hide the excessive ffmpeg information produced when rendering, but since
		AtomicParsley is used once there's an option to set append_hide_banner to False.\n
		append_faststart is an option to optimize video playback, so if the output file is
		something other than a video then specify append_faststart=False in the method call."""
		# Potentially add keywords to render command.
		if append_hide_banner is True:
			self.ren_cmd.append('-hide_banner')
		if append_faststart is True:
			self.ren_cmd += ('-movflags', '+faststart')
		# Run the actual terminal command and keep a timer for how long it takes to render.
		try:
			# Start of timer.
			start_time = time.perf_counter()
			# Render process.
			render_process = sub.run(self.ren_cmd, stdout=sub.PIPE, stderr=sub.PIPE, universal_newlines=True)
			# Stop timer.
			end_time = time.perf_counter()
			# Check command output and potentially print more info.
			sub.CompletedProcess.check_returncode(render_process)
			if self.print_ren_info is True and self.out_paths_list[0].exists():
				print(f'\n{render_process.stderr}', end='')
			# Print what the output is supposed to be since AtomicParsley
			# was used and the actual output overwrote a temporary file.
			if self.print_success is True and append_faststart is False and append_hide_banner is False:
				for out_path in self.out_paths_list:
					print(f'"{out_path}" was rendered successfully!')
			elif self.print_success is True and self.out_paths_list[0].exists():
				for out_path in self.out_paths_list:
					print(f'"{out_path}" was rendered successfully!')
			if self.print_ren_time is True:
				# Run method to get the text to print how long it took to render.
				duration = Render.terminal_render_timer(start_time, end_time)
				print(duration)
			# If self.open_after_ren is True then open the output file in the default application.
			Render._check_open_after_ren(self)
			# Return True (it worked.)
			return True
		# The rendering failed, so probably print an error message.
		except sub.CalledProcessError:
			if self.print_err is True:
				# Return False (it didn't work).
				print('\nError, a problem occurred while rendering:')
				print(f'Terminal input command: {self.ren_cmd}')
				print(render_process.stderr)
				print()
			return False
	
	def check_depend_then_ren_and_embed_original_metadata(self, append_faststart=True, artwork=False,
	                                                      copy_chapters=False):
		"""This method will run the "check_dependencies_then_render" method and attempt to embed any artwork from the
		original file into the output (due to how ffmpeg works, the artwork can't always be copied in one command.)\n
		if artwork is True it will try to embed artwork from the input into the output specifically.
		This may happen if ffmpeg tries to output artwork to the first stream of an audio only file."""
		
		# Run standard command to render output.
		out_file_exists_result = self.check_depend_then_ren(append_faststart=append_faststart)
		
		if type(self.in_path) is list:
			in_meta_file = self.in_path[0]
		else:
			in_meta_file = self.in_path
		
		# If the output file exists then run the attempt_embed_metadata_silently method.
		if out_file_exists_result is True:
			# This will attempt to embed any metadata (mainly for artwork) from the original file into the output.
			# (Due to how ffmpeg works, the artwork can't always be copied in one command.)
			# Create temporary output file with the original metadata embedded, delete the original output without the metadata,
			# and rename this temporary output to the desired output.
			for out_path in self.out_paths_list:
				temp_directory_to_embed_metadata = paths.Path().joinpath(out_path.parent,
				                                                         '--temp_dir_to_embed_metadata_silently')
				paths.Path.mkdir(temp_directory_to_embed_metadata)
				temp_out_file = paths.Path().joinpath(temp_directory_to_embed_metadata, out_path.stem + out_path.suffix)
				FileOperations(out_path, temp_directory_to_embed_metadata, False,
				               self.print_ren_info, False, False).copy_over_metadata(in_meta_file, copy_chapters)
				if temp_out_file.exists() is False:
					if self.print_err is True:
						print(f'Error, input file to extract metadata silently from "{out_path}" not found.')
					paths.Path(temp_directory_to_embed_metadata).rmdir()
				else:
					out_path.unlink()
					temp_out_file.rename(out_path)
				if artwork is True:
					temp_art = FileOperations(in_meta_file, temp_directory_to_embed_metadata, False,
								self.print_ren_info, False, False).extract_artwork()
					if temp_art is not False:
						if temp_art.exists():
							FileOperations(out_path, temp_directory_to_embed_metadata, False,
										   self.print_ren_info, False, False).embed_artwork(temp_art)
							temp_art.unlink()
							out_path.unlink()
							temp_out_file.rename(out_path)
				temp_directory_to_embed_metadata.rmdir()
				return True

		else:
			# A problem occurred while rendering and no output file was created so quit.
			return False

	@staticmethod
	def terminal_render_timer(start, end, operation_keyword=''):
		"""Determine the appropriate text for printing how long it took the terminal to render."""
		
		total_ren_dur = f'{start - end:0.2f}'.lstrip('-')
		# How many fractions of a second it took.
		frac_sec = total_ren_dur[-3:]
		# How many seconds it took.
		seconds = int(total_ren_dur[:-3])
		# Assign how many minutes it took to render by taking the total amount of seconds
		# divided by 60 (60 seconds in a minute.)
		minutes, seconds = divmod(seconds, 60)
		# Assign how many hours it took to render by taking the total amount of minutes
		# divided by 60 (60 minutes in an hour.)
		hours, minutes = divmod(minutes, 60)
		# This method will either display how long it took to render a file, or scan a file,
		# so print the appropriate word.
		if operation_keyword == ' to scan':
			begin_word = 'took'
		else:
			begin_word = 'Over the course of'
		
		# It will either be a singular or plural of minutes, hours, and seconds so print the correct one.
		if hours == 1:
			hours_plural = ''
		else:
			hours_plural = 's'
		if minutes == 1:
			minutes_plural = ''
		else:
			minutes_plural = 's'
		if seconds == 1 and frac_sec == '.00':
			seconds_plural = ''
		else:
			seconds_plural = 's'
		
		# Strings to display the render duration.
		total_sec = f'{seconds:d}{frac_sec} second{seconds_plural}{operation_keyword}.'
		total_min = f'{minutes:d} minute{minutes_plural}'
		total_hr = f'{hours:d} hour{hours_plural}'
		start = f'{begin_word} '
		
		# Logic to determine what to show (if hours or minutes are 0 then don't show those.)
		if hours >= 1 and minutes >= 1:
			duration = f'{start}{total_hr}, {total_min}, and {total_sec}'
		elif minutes >= 1:
			duration = f'{start}{total_min} and {total_sec}'
		else:
			duration = f'{start}{total_sec}'
		return duration
	
	def _check_open_after_ren(self):
		"""Open the output file if self.open_after_ren=True.\n
		If True then it opens with the default application, or if it's set to a string it attempts to open
		it with the application specified in the string."""
		
		for out_path in self.out_paths_list:
			if type(self.open_after_ren) is str and type(out_path) == paths.WindowsPath:
				print('Error, a custom application for opening a video after it finishes rendering is not available'
				      ' for WindowsPath so self.open_after_ren must be True or False, not',
				      self.open_after_ren)
				return False
			
			# Determine which terminal keyword to use based on the path type.
			elif self.open_after_ren is True or type(self.open_after_ren) is str:
				# If the output path is a PosixPath then the keyword is "open" in the terminal.
				if type(out_path) is paths.PosixPath:
					open_keyword = 'open'
				# If the output path is a WindowsPath then the keyword is "start" in the terminal.
				elif type(out_path) is paths.WindowsPath:
					open_keyword = 'start'
				else:
					print("Error, output path is not a PosixPath or WindowsPath so it can't be opened automatically.")
					quit()
				
				# A custom application was specified to the Mac/Linux terminal to add that string to the command.
				if type(self.open_after_ren) is str and type(out_path) == paths.PosixPath:
					open_cmd = [open_keyword, '-a', str(self.open_after_ren), out_path]
				# No specific application was specified so just open with the default application.
				else:
					open_cmd = [open_keyword, out_path]
				
				# Run terminal command to open the output file.
				sub.run(open_cmd)
		return True
