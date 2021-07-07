import sys
def add_scan(f, f_out):
	fr = open(f, 'r')
	fw = open(f_out, 'w')
	lines = fr.readlines()
	for l in lines:
		fw.write(l)
		if l.startswith('TITLE'):
			scan = l.split('.')[-2]
			fw.write('SCANS=%s\n' % scan)
	fr.close()
	fw.close()
args = sys.argv
mgf_file_name, mgf_out = args[1:]
add_scan(mgf_file_name, mgf_out)
