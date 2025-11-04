from GembaFileUpToDater.parse_args import parse_args, should_show_debug
parse_args()
print(f'Should show debug: {should_show_debug()}')

from GembaFileUpToDater.download_from_server import download_new_files

download_new_files()
