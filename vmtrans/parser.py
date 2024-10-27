import ntpath

from vmtrans.instructions import InstructionFactory


class Parser(object):
    @staticmethod
    def parse(filename):
        basename = ntpath.basename(filename)
        if '.vm' in basename:
            basename = basename[:basename.index('.vm')]

        factory = InstructionFactory(basename)

        with open(filename, 'r') as source:
            for line in source:

                line = line.strip()

                if not line or line.startswith('//'):
                    continue

                yield factory.create_instruction(line)
