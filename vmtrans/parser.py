from vmtrans.instructions import InstructionFactory


class Parser(object):
    def __init__(self, filename):
        self.filename = filename
        self.factory = InstructionFactory(filename[:-3].split('/')[-1])

    def parse(self):
        with open(self.filename, 'r') as source:
            for line in source:

                line = line.strip()

                if not line or line.startswith('//'):
                    continue

                yield self.factory.create_instruction(line)
