import pathlib as paths

class VerifyInputType:
	def is_type_or_print_err_and_quit(self, in_type, target_type, in_type_str):
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
