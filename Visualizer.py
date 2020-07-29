import pathlib as paths
import subprocess as sub

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
