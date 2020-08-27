import pathlib as paths
import time
import subprocess as sub

from VerifyInputType import VerifyInputType
from Render import Render


class MetadataAcquisition(VerifyInputType):
	"""This class provides methods to get file metadata.
	NOTE: return_metadata is the only method designed to be used.\n"""
	
	def __init__(self, in_path, print_all_info=False, print_scan_time=False, print_meta_value=False):
		"""Requires a path object to an input file and optional file info printing"""
		
		# Run function to print an error and quit if the input type is not valid.
		self.is_type_or_print_err_and_quit(type(in_path), paths.Path, 'in_path')
		self.is_type_or_print_err_and_quit(type(print_all_info), bool, 'print_all_info')
		self.is_type_or_print_err_and_quit(type(print_scan_time), bool, 'print_scan_time')
		self.is_type_or_print_err_and_quit(type(print_meta_value), bool, 'print_meta_value')
		
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
				# The render failed, print an error message.
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

		self.is_type_or_print_err_and_quit(type(check_file), bool, 'check_file')
		
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
