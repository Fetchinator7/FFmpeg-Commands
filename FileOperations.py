import datetime as dates
import math
import pathlib as paths
import shutil

from VerifyInputType import VerifyInputType
from MetadataAcquisition import MetadataAcquisition
from Render import Render

class FileOperations(VerifyInputType):
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
		self.is_type_or_print_err_and_quit(type(out_dir), paths.Path, 'out_dir')
		self.is_type_or_print_err_and_quit(type(print_success), bool, 'print_success')
		self.is_type_or_print_err_and_quit(type(print_err), bool, 'print_err')
		self.is_type_or_print_err_and_quit(type(print_ren_info), bool, 'print_ren_info')
		self.is_type_or_print_err_and_quit(type(print_ren_time), bool, 'print_ren_time')
		self.is_type_or_print_err_and_quit(type(open_after_ren), bool, 'open_after_ren')
		
		# Pathlib path to a input file for the terminal command.
		self.in_path = in_path
		# Pathlib path to an already existing output directory.
		self.out_dir = out_dir
		
		# The concat method requires a list input, but otherwise it should just be one path.
		if type(in_path) is not list:
			self.is_type_or_print_err_and_quit(type(in_path), paths.Path, 'in_path')
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

		self.is_type_or_print_err_and_quit(type(copy_this_metadata_file), paths.Path, 'copy_this_metadata_file')
		self.is_type_or_print_err_and_quit(type(copy_chapters), bool, 'copy_chapters')

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-i', copy_this_metadata_file]
		if copy_chapters is False:
			ffmpeg_cmd += ('-map_chapters', '-1')
		ffmpeg_cmd += ['-map', '0', '-c', 'copy', '-map_metadata', '1', self.standard_out_path]

		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()
		
	def rm_metadata(self):
		"""This method will not maintain any metadata values from the input to the output."""

		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy', '-map_chapters', '-1', '-map_metadata', '-1', '-map', '-0:s', self.standard_out_path]

		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success, self.print_err,
		       self.print_ren_info, self.print_ren_time, self.open_after_ren).check_depend_then_ren()

	def change_file_name_and_meta_title(self, new_title):
		"""This method changes the filename and metadata title of a file."""

		self.is_type_or_print_err_and_quit(type(new_title), str, 'new_title')
		
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
		
		self.is_type_or_print_err_and_quit(type(in_artwork), paths.Path, 'in_artwork')

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
		if art_stream is None or art_stream is False and self.print_err is True:
			print(f'Error, no artwork found in input:\n{self.in_path}\nFor output:\n{self.standard_out_path}')
			return False
		else:
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-c', 'copy']
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
			ffmpeg_cmd.append(self.standard_out_path)
			
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren(append_faststart=False)
		return True
	
	def change_ext(self, new_ext, codec_copy=False):
		"""This method changes the self.in_path extension to new_ext."""
		
		self.is_type_or_print_err_and_quit(type(new_ext), str, 'new_ext')

		# Path to output file with the new target extension.
		new_ext_out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem + new_ext)
		
		ffmpeg_cmd = ['ffmpeg', '-i', self.in_path]
		if codec_copy is True:
			ffmpeg_cmd += ('-c', 'copy')
		ffmpeg_cmd.append(new_ext_out_path)
		
		# Confirm the target output extension isn't the same as the input extension.
		# If it is the same extension then print a message and just copy the file.
		if self.in_path.suffix == new_ext_out_path.suffix:
			shutil.copy2(self.in_path, new_ext_out_path)
			print(f'Error, target output extension, "{new_ext_out_path.suffix}" is the same as '
			      f'the input extension so the target output file, "{new_ext_out_path}" was just copied.')
		else:
			Render(self.in_path, new_ext_out_path, ffmpeg_cmd, self.print_success, self.print_err, self.print_ren_info,
			       self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
	
	def trim(self, start_timecode='', stop_timecode='', codec_copy=False, verify_trim_ranges=True):
		"""This method changes the duration of the input from start_timecode to stop_timecode\n
		Timecode format = "00:00:00.00" (hours, minutes, seconds, and fractions of seconds.)\n
		At least start_timecode or stop_timecode must be set, but if one of them isn't set it will
		default to the beginning or the end respectively.
		So if stop_timecode="0:35" then start at the beginning and keep everything until it's 35 seconds in.\n
		codec_copy toggles copying the codec for the output which is False by default because
		otherwise there's a few second margin of error for some codecs (such as .mp4).\n
		NOTE: This method will remove any already existing chapter(s)
		from the input because otherwise the output won't be trimmed."""
		
		self.is_type_or_print_err_and_quit(type(start_timecode), str, 'start_timecode')
		self.is_type_or_print_err_and_quit(type(stop_timecode), str, 'stop_timecode')
		self.is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')

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
				print(f'Error, no video or audio streams to trim were found from input\n"{self.in_path}"')
			return False
		
		ffmpeg_cmd = ['ffmpeg']
		if verify_trim_ranges == True:
			sec_dur = self._return_input_duration_in_sec()
			if sec_dur is None or sec_dur < 1:
				if self.print_err is True:
					print(f'''Error, there's no length to trim from input "{self.in_path}"\n''')
				return False

			# -ss is the timecode to begin file at and -to is the timecode to end at.
			# (There's also the -t option which is a relative trim, i.e. 15 seconds after the start timecode but -t isn't
			# used for this method.)
			start_duration_seconds = ''
			if start_timecode != '':
				start_duration_seconds = self._return_input_duration_in_sec(start_timecode)
				if start_duration_seconds > sec_dur:
					if self.print_err is True:
						print(f'''Error, the starting timecode "{start_timecode}" is greater than the length of input:\n"{self.in_path}"\n''')
					return False
			stop_duration_seconds = ''
			if stop_timecode != '':
				stop_duration_seconds = self._return_input_duration_in_sec(stop_timecode)
				if stop_duration_seconds > sec_dur:
					if self.print_err is True:
						print(f'''Error, the output won't go until the end timecode "{stop_timecode}" '''
							f'''because that's greater than the length of the input:\n"{self.in_path}"\n''')
			if start_timecode != '' and stop_timecode != '':
				if stop_duration_seconds < start_duration_seconds:
					if self.print_err is True:
						print(f'Error, the output timecode "{stop_timecode}" has to be after the input timecode "{start_timecode}"')
					return False
		# If the trim ranges were verified and turned out to be invalid
		# it will return false so this block wouldn't be reached.
		ffmpeg_cmd += ('-ss', start_timecode, '-to', stop_timecode)

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

		self.is_type_or_print_err_and_quit(type(num_loop_times), int, 'num_loop_times')
		self.is_type_or_print_err_and_quit(type(loop_to_hours), int, 'loop_to_hours')
		self.is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')

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

		self.is_type_or_print_err_and_quit(type(playback_speed), float, 'playback_speed')

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
		
		self.is_type_or_print_err_and_quit(type(in_aud_path_list), list, 'in_aud_path')
		for aud_path in in_aud_path_list:
			self.is_type_or_print_err_and_quit(type(aud_path), paths.Path, 'aud_path')
		self.is_type_or_print_err_and_quit(type(shortest), bool, 'shortest')

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
		
		self.is_type_or_print_err_and_quit(type(in_aud_path_list), list, 'in_aud_path_list')
		for aud_path in in_aud_path_list:
			self.is_type_or_print_err_and_quit(type(aud_path), paths.Path, 'aud_path')
		self.is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')
		self.is_type_or_print_err_and_quit(type(length_vid), bool, 'length_vid')

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
		
		self.is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		self.is_type_or_print_err_and_quit(type(aud_only), bool, 'aud_only')
		self.is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')

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
		self.is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		self.is_type_or_print_err_and_quit(type(aud_only), bool, 'aud_only')
		self.is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')
		self.is_type_or_print_err_and_quit(type(_do_render), bool, '_do_render')
		
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
				vol_db_change = 'volume=' + vol_level
				if custom_db[0] == '-':
					vol_change_keyword = 'decreased'
				else:
					vol_change_keyword = 'increased'
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
		
		self.is_type_or_print_err_and_quit(type(out_aud_ext), str, 'out_aud_ext')
		self.is_type_or_print_err_and_quit(type(order_out_names), bool, 'order_out_names')

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
		for strm_index, strm in enumerate(strm_types):
			# Map the output if it's an audio stream.
			if strm == 'Audio':
				ffmpeg_cmd += ('-map', f'0:{strm_index}')
				# Only embed input artwork if it exists and the output extension is ".mp3"
				if art_exists is True and out_ext == '.mp3':
					ffmpeg_cmd += ('-map', f'0:v:{art_strm_index}')
				if order_out_names is True:
					out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem
					                                 + f'-Audio Track {strm_index + 1}' + out_ext)
				else:
					out_path = paths.Path().joinpath(self.out_dir, self.in_path.stem + out_ext)
				ffmpeg_cmd.append(out_path)
				out_paths_list.append(out_path)
			
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

		self.is_type_or_print_err_and_quit(type(fade_vid), bool, 'fade_vid')
		self.is_type_or_print_err_and_quit(type(fade_aud), bool, 'fade_aud')
		self.is_type_or_print_err_and_quit(type(fade_begin), bool, 'fade_begin')
		self.is_type_or_print_err_and_quit(type(fade_end), bool, 'fade_end')
		self.is_type_or_print_err_and_quit(type(fade_dur_sec), int, 'fade_dur_sec')
		self.is_type_or_print_err_and_quit(type(fade_out_at_sec), int, 'fade_out_at_sec')

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

		self.is_type_or_print_err_and_quit(type(pan_strm), list, 'pan_strm')

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

		self.is_type_or_print_err_and_quit(type(right_aud_in_path), paths.Path, 'right_aud_in_path')

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

		self.is_type_or_print_err_and_quit(type(keep_aspect_ratio_input_width), str, 'scale_dim')
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
		they will be cropped out. However, this has issues calculating the right dimensions if the source video is dark."""
		# Get the dimensions to crop out black bars.
		# Return crop_detect as the first thing in the list, then get the first (and only) item in that list; the crop dimensions.
		crop_dim = MetadataAcquisition(self.in_path, print_scan_time=self.print_ren_time).return_metadata(crop_detect=1)[0]

		if crop_dim is None:
			if self.print_err is True:
				print(f'''Error, there's no video footage to crop found from input:\n"{self.in_path}"\n''')
			return False

		# The dimensions are returned with pixel trim/offset indicated at the end so if both of those
		# 	are 0 then there's nothing to trim. 1920:1080:0:0
		# See https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg#4571
		# https://www.bogotobogo.com/FFMpeg/ffmpeg_cropdetect_ffplay.php
		if crop_dim[-4:] == ':0:0':
			if self.print_err is True:
				print(f'Error, no black bars to crop were found in input "{self.in_path}"')
			return False

		elif crop_dim is not None:
			print(crop_dim)
			# Filter to crop the output.
			ffmpeg_cmd = ['ffmpeg', '-i', self.in_path, '-map', '0', '-filter:v',
			              f'crop={crop_dim}', '-c:a', 'copy', '-c:s', 'copy']

			# Remove any already existing artwork stream.
			ffmpeg_cmd = self._add_to_ren_cmd__rm_art_stream_index_selector(ffmpeg_cmd)
					
			ffmpeg_cmd.append(self.standard_out_path)
			Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
				   self.print_err, self.print_ren_info, self.print_ren_time,
			       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata(artwork=True)
	
	def rotate_vid_frame(self, rotate_frame_by_degrees='90'):
		"""This method rotates the input frame by rotate_by_degrees degrees.\n
		NOTE: rotate_by_degrees can only be set to 90, 180, or 270, otherwise nothing changes."""

		self.is_type_or_print_err_and_quit(type(rotate_frame_by_degrees), str, 'rotate_by_degrees')

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

		self.is_type_or_print_err_and_quit(type(rotate_footage_by_degrees), str, 'rotate_footage_by_degrees')
		self.is_type_or_print_err_and_quit(type(hflip), bool, 'hflip')
		self.is_type_or_print_err_and_quit(type(vflip), bool, 'vflip')

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
		At this point just use the rm_chapters method before running it through this one.\n
		NOTE: This method requires that self.in_path be a list containing every path to concatenate to output
			in order of index. ("[in_1, in_2'")\n
		NOTE: All input files must have the same streams (same codecs, same time base, etc.)
			but can be wrapped in different container formats because otherwise it won't work.\n
		NOTE: This method will remove any already existing chapters because otherwise it won't work.\n
		_loop_times is local because it's only designed to be used by FileOperations.loop\n
		See "https://trac.ffmpeg.org/wiki/Concatenate" for ffmpeg concatenation documentation."""
		
		self.is_type_or_print_err_and_quit(type(new_basename), str, 'new_basename')
		self.is_type_or_print_err_and_quit(type(new_ext), str, 'new_ext')
		self.is_type_or_print_err_and_quit(type(codec_copy), bool, 'codec_copy')
		self.is_type_or_print_err_and_quit(type(_loop_times), int, '_loop_times')
		
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
	
	def compress_using_h265_and_norm_aud(self, new_res_dimensions='0000:0000',
										 insert_pixel_format=False, video_only=False, custom_db='',
										 print_vol_value=True, maintain_multiple_aud_strms=True,
										 speed_preset=''):
		"""This method compresses the input video using the H.265 (HEVC) codec.
		See https://trac.ffmpeg.org/wiki/Encode/H.265 for more info

		Args:
			new_res_dimensions (str, optional): Can be specified to alter the output video resolution. Defaults to '0000:0000'.
			insert_pixel_format (bool, optional): Will set the outout pixel format to yuv420p. This is disabled by
				default because usually it isn't necessary, but certain input encoders like "Apple ProRes 422 HQ"
				need the pixel format specified for the computer to play it natively. Defaults to False.
			video_only (bool, optional): This only exports video so it won't keep audio tracks(s). Defaults to False.
			custom_db (str, optional): This method automatically normalizes the output audio, but custom_db can be set
				to have a custom output dB level ("-3 dB"/"3 dB"). Defaults to ''.
			print_vol_value (bool, optional): Toggles whether or not to display the dB amount the output volume was changed by. Defaults to True.
			maintain_multiple_aud_strms (bool, optional): toggles whether or not to maintain multiple input audio streams.
				For example if there was an english and french track ut would only keep the english one by default.
				NOTE: the loudnorm only checks the first audio channel and raises every audio channel by that amount so the other
				audio streams could end up clipping depending on their different volume levels. Defaults to True.
			speed_preset (str, optional):
				This command is setup to use the "speed" preset to determine how quickly the output will be rendered
				(which impacts the output size and quality). It defaults to "fast" but this way it can be made faster or slower if desired.
				fast, superfast, slow, etc. See https://trac.ffmpeg.org/wiki/Encode/H.265 for the complete list.
				Defaults to ''.

		Returns:
			True: It was successful.
			False: Received invalid input file extension.
		"""
		
		# Confirm all the inputs are the correct types.
		self.is_type_or_print_err_and_quit(type(new_res_dimensions), str, 'new_res_dimensions')
		self.is_type_or_print_err_and_quit(type(insert_pixel_format), bool, 'insert_pixel_format')
		self.is_type_or_print_err_and_quit(type(video_only), bool, 'video_only')
		self.is_type_or_print_err_and_quit(type(custom_db), str, 'custom_db')
		self.is_type_or_print_err_and_quit(type(print_vol_value), bool, 'print_vol_value')
		self.is_type_or_print_err_and_quit(type(maintain_multiple_aud_strms), bool, 'maintain_multiple_aud_strms')
		self.is_type_or_print_err_and_quit(type(speed_preset), str, 'speed_preset')

		# The input file extension is referenced multiple times so give it a variable.
		in_ext = self.in_path.suffix

		# Check if the input extension is compatible with H265 compression.
		if in_ext != '.mp4' and in_ext != '.mov' and in_ext != '.mkv':
			print(f'\nError, H.265 compression is not supported for input extension "{in_ext}" '
			      f'from input:\n"{self.in_path}"\n')
			return False
		
		if speed_preset != '':
			speed = speed_preset
		else:
			speed = 'fast'

		# Remove all metadata for this output because for some reason it can cause weird bugs when trying to convert
		# the file afterwards and '-tag:v', 'hvc1' tells macs that it can play the output video file.
		ffmpeg_cmd = ['ffmpeg', '-ss', '0:0', '-i', self.in_path, '-map_metadata', '-1', '-map', '0:v', '-c:s', 'copy',
					  '-c:v', 'libx265', '-preset', speed, '-crf', '20', '-tag:v', 'hvc1']
		
		# * Add '-pix_fmt', 'yuv420p' in case the input video is prores or some other weird encoder.
		if insert_pixel_format is True:
			ffmpeg_cmd += ('-pix_fmt', 'yuv420p')

		if video_only is True:
			ffmpeg_cmd.append('-an')
		else:
			# Be default this render only maintains one audio stream so if
			# there are multiple audio streams they have to be mapped manually.
			if maintain_multiple_aud_strms:
				ffmpeg_cmd = self._add_to_ren_cmd__map_all_strms_of_type(self.in_path, 'Audio', ffmpeg_cmd)
			else:
				ffmpeg_cmd += ('-map', '0:a?')
			
			# Scan input file for dB amount to increase by and method returns ffmpeg audio cmds.
			# If it's already at 0.0 dB then it will return None.
			audio_cmd = FileOperations.loudnorm_stereo(self, _do_render=False, print_vol_value=print_vol_value,
			                                           custom_db=custom_db)
			if audio_cmd is not None and audio_cmd is not False:
				ffmpeg_cmd += audio_cmd
		
		# If a new resolution was specified then append that to ren_cmd.
		if new_res_dimensions != '0000:0000':
			ffmpeg_cmd += ('-vf', 'scale=' + new_res_dimensions)
		
		# Append the output path.
		ffmpeg_cmd.append(self.standard_out_path)
		
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd, self.print_success,
			   self.print_err, self.print_ren_info, self.print_ren_time,
		       self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()

		return True

	def embed_subs(self, in_subs_list):
		"""This method will embed the input subtitle file(s) into the output.\n
		in_subs_list must be a list of pathlib paths to the subtitle files to embed."""
		self.is_type_or_print_err_and_quit(type(in_subs_list), list, 'in_subs_list')
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
		ffmpeg_cmd += ('-c', 'copy', '-c:s', 'mov_text', self.standard_out_path)
		Render(self.in_path, self.standard_out_path, ffmpeg_cmd,
			   self.print_success, self.print_err, self.print_ren_info,
			   self.print_ren_time, self.open_after_ren).check_depend_then_ren_and_embed_original_metadata()
	
	def extract_subs(self, include_other_metadata=False):
		"""This method will extract subtitles from the input then output each language to its own file.\n
		By default metadata is included (artist, chapters, etc.)
		but include_other_metadata can be set to False to disable this."""
		self.is_type_or_print_err_and_quit(type(include_other_metadata), bool, 'include_other_metadata')

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
		self.is_type_or_print_err_and_quit(type(timecode_title_list), list, 'timecode_title_list')
		self.is_type_or_print_err_and_quit(type(add_chap_headings), bool, 'add_chap_headings')

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

		self.is_type_or_print_err_and_quit(type(convert_str_timecode_to_sec), str, 'convert_str_timecode_to_sec')

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
				      f'in a "00:00:00.00" format, with a minimum of one number, no more than 2 digits after a period (".00") '
					  f'and if fractions of a second are specified they must have a leading number ("0.4")')
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

	def _add_to_ren_cmd__map_all_strms_of_type(self, in_path, strm_type, ffmpeg_cmd):
		"""."""
		# Extract all the different stream types for the input.
		strm_types = MetadataAcquisition(in_path).return_stream_types()
		if strm_types != None:
			for strm_index, strm in enumerate(strm_types):
				# Map the output if it's an audio stream.
				if strm == strm_type:
					ffmpeg_cmd += ['-map', f'0:{strm_index}']
		else:
			if self.print_err is True:
				print(f'Error, no "{strm_type}" streams were found to maintain for input:\n"{in_path}""')

		return ffmpeg_cmd
