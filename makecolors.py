import os
import re
import sys

if __name__ == '__main__':
    source = 'rgb.txt'
    with open('colors.py', 'w') as colors:
        colors.write('# Auto-generated from {0} by {1}, do not edit\n\n'.format(
            source, os.path.basename(sys.argv[0])))

        colors.write('colordict = {\n')

        with open('rgb.txt', 'r') as rgb:

            digits_caps_uk = re.compile('[0-9]|[A-Z]|grey')

            for line in rgb.readlines():
                if not len(line) or line[0] == '!':
                    continue

                parts = line.split()
                r,g,b = parts[0:3]
                name = ' '.join(parts[3:])
       
                if digits_caps_uk.search(name) is not None:
                    continue

                colors.write("    ({0},{1},{2}) : _('{3}'),\n".format(
                    r,g,b,name))

        colors.write('    }\n')
