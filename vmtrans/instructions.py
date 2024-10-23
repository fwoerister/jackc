from codegen import load_to_a_register, do_c_instruction, push_on_stack, pop_from_stack, conditional_execution


class VMInstruction:
    def __init__(self, cmd, arg1, arg2, filename):
        self.cmd = cmd
        self.arg1 = arg1
        self.arg2 = arg2
        self.filename = filename

    def to_hack_code(self):
        raise NotImplementedError()

    def args_to_base_and_offset(self) -> (str, int):
        if self.arg1 == 'constant':
            return str(self.arg2), 0
        elif self.arg1 == 'static':
            return f'{self.filename}.{self.arg2}', 0
        elif self.arg1 == 'pointer':
            return 'THIS' if self.arg2 == 0 else 'THAT', 0
        elif self.arg1 == 'argument':
            return 'ARG', self.arg2
        elif self.arg1 == 'local':
            return 'LCL', self.arg2
        elif self.arg1 == 'temp':
            return 'TMP', self.arg2


class PushInstruction(VMInstruction):
    def to_hack_code(self):
        base, offset = self.args_to_base_and_offset()
        return push_on_stack(base, offset)


class PopInstruction(VMInstruction):
    def to_hack_code(self):
        base, offset = self.args_to_base_and_offset()
        return pop_from_stack(base, offset)


class AddInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
        ]

        return ''.join(machine_instructions)


class SubInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
        ]

        return ''.join(machine_instructions)


class NegInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '!M'),
        ]

        return ''.join(machine_instructions)


class EqualInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = EqualInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]

        return '\n'.join(machine_instructions)


class GreaterThanInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = GreaterThanInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JGT',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]

        return '\n'.join(machine_instructions)


class LessThanInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = LessThanInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JLT',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return '\n'.join(machine_instructions)


class AndInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = AndInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
            do_c_instruction('M', 'M+1'),
            do_c_instruction('M', 'M+1'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return '\n'.join(machine_instructions)


class OrInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = OrInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            pop_from_stack('R13'),
            load_to_a_register('R13'),
            do_c_instruction('D', 'M'),
            load_to_a_register('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JNE',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return '\n'.join(machine_instructions)


class NotInstruction(VMInstruction):
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        super().__init__(cmd, arg1, arg2, filename)
        self.id = NotInstruction.count
        EqualInstruction.count += 1

    def to_hack_code(self):
        code_true = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_to_a_register('SP', 0),
            do_c_instruction('A', 'A-1'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return '\n'.join(machine_instructions)


class InstructionFactory:
    commands = {
        'push': PushInstruction,
        'pop': PopInstruction,
        'add': AddInstruction,
        'sub': SubInstruction,
        'neg': NegInstruction,
        'eq': EqualInstruction,
        'greater': GreaterThanInstruction,
        'less': LessThanInstruction,
        'and': AndInstruction,
        'or': OrInstruction,
        'not': NotInstruction,
    }

    def __init__(self, filename):
        self.filename = filename

    def create_instruction(self, instruction):
        stripped_inst = instruction.strip()
        command_tokens = stripped_inst.split(' ')

        cmd = command_tokens[0]
        arg1 = command_tokens[1] if len(command_tokens) == 2 else None
        arg2 = command_tokens[2] if len(command_tokens) == 2 else None

        command_cls = InstructionFactory.commands[cmd]
        return command_cls(cmd, arg1, arg2, self.filename)
