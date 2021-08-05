"""
Creates .sh job files from LibKGE .yaml config files based on a provided template.
"""
import os
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Create job files from .yaml files.')
	parser.add_argument('files', metavar='F', type=str, nargs='+',
						help='.yaml files to process.')

	args = parser.parse_args()
	template_file_name = "template_gpu_script.sh"
	with open('/home/fu19841/LPComparison/scripts/templates/' + template_file_name) as f:
		template_file = f.read()


	path_to_experiments = '/bp1store/mrcieu1/users/fu19841/kge/local/experiments/'
	path_to_jobs = '/home/fu19841/jobs/'
	if 'all' in args.files:
		files_to_process = os.listdir(path_to_experiments)
	else:
		files_to_process = args.files

	for loc in files_to_process:
		if loc.endswith('.yaml') and not 'template' in loc:
			new_file_name = loc.split('.')[0] + '.sh'
			if new_file_name.count('/') > 0:
				new_file_name = new_file_name.split('/')[-1]
			new_file = template_file.replace('<file_name>', loc)
			with open(path_to_jobs + new_file_name, 'w+') as new_f:
				new_f.write(new_file)