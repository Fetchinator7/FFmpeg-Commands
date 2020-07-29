import FileOperations

import pathlib as paths
import subprocess as sub
import time

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
				FileOperations.FileOperations(out_path, temp_directory_to_embed_metadata, False,
				               self.print_ren_info, False, False).copy_over_metadata(in_meta_file, copy_chapters)
				if temp_out_file.exists() is False:
					if self.print_err is True:
						print(f'Error, input file to extract metadata silently from "{out_path}" not found.')
					paths.Path(temp_directory_to_embed_metadata).rmdir()
				else:
					out_path.unlink()
					temp_out_file.rename(out_path)
				if artwork is True:
					temp_art = FileOperations.FileOperations(in_meta_file, temp_directory_to_embed_metadata, False,
								self.print_ren_info, False, False).extract_artwork()
					if temp_art is not False:
						if temp_art.exists():
							FileOperations.FileOperations(out_path, temp_directory_to_embed_metadata, False,
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
