from vmtrans.codegen import resolve_symbol, do_c_instruction, push_on_stack, pop_from_stack, conditional_execution, \
    load_symbol


class VMInstruction:
    count = 1

    def __init__(self, cmd, arg1, arg2, filename):
        self.cmd = cmd
        self.arg1 = arg1
        self.arg2 = arg2
        self.filename = filename

        VMInstruction.count += 1

    def to_hack_code(self):
        return f'//{self.cmd} {self.arg1 if self.arg1 else ''} {self.arg2 if self.arg2 else ''}\n'

    def args_to_symbol_and_offset(self) -> (str, int):
        if self.arg1 == 'constant':
            return str(self.arg2), 0
        elif self.arg1 == 'static':
            return f'{self.filename}.{self.arg2}', 0
        elif self.arg1 == 'pointer':
            return 'THIS' if self.arg2 == 0 else 'THAT', 0
        elif self.arg1 == 'this':
            return 'THIS', int(self.arg2)
        elif self.arg1 == 'that':
            return 'THAT', int(self.arg2)
        elif self.arg1 == 'argument':
            return 'ARG', int(self.arg2)
        elif self.arg1 == 'local':
            return 'LCL', int(self.arg2)
        elif self.arg1 == 'temp':
            return 'TMP', int(self.arg2)


class PushInstruction(VMInstruction):
    def to_hack_code(self):
        symbol, offset = self.args_to_symbol_and_offset()
        symbol_handling_instructions = []

        if not symbol.isdigit():
            symbol_handling_instructions.append(resolve_symbol(symbol, offset))
        else:
            symbol_handling_instructions.append(load_symbol(symbol))

        symbol_handling_code = '\n'.join(symbol_handling_instructions) + '\n'

        return super().to_hack_code() + symbol_handling_code + push_on_stack(is_constant=symbol.isdigit())


class PopInstruction(VMInstruction):
    def to_hack_code(self):
        symbol, offset = self.args_to_symbol_and_offset()
        symbol_handling_instructions = []

        if not symbol.isdigit():
            symbol_handling_instructions.append(resolve_symbol(symbol, offset))
        else:
            symbol_handling_instructions.append(load_symbol(symbol))

        symbol_handling_code = '\n'.join(symbol_handling_instructions) + '\n'

        return super().to_hack_code() + symbol_handling_code + pop_from_stack()


class AddInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class SubInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'M-D'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class NegInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '!M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class EqualInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class GreaterThanInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JGT',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class LessThanInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JLT',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return super().to_hack_code() + '\n'.join(machine_instructions)


class AndInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
            do_c_instruction('M', 'M+1'),
            do_c_instruction('M', 'M+1'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return super().to_hack_code() + '\n'.join(machine_instructions)


class OrInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            load_symbol('R11'),
            pop_from_stack(),
            load_symbol('R11'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JNE',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return super().to_hack_code() + '\n'.join(machine_instructions)


class NotInstruction(VMInstruction):

    def to_hack_code(self):
        code_true = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '-1'),
        ]

        code_false = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '0'),
        ]

        machine_instructions = [
            resolve_symbol('SP', 0),
            do_c_instruction('A', 'A-1'),
            conditional_execution(tag=f'EQ_{self.count}', value='M', condition='JEQ',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]
        return super().to_hack_code() + '\n'.join(machine_instructions)


class InstructionFactory:
    commands = {
        'push': PushInstruction,
        'pop': PopInstruction,
        'add': AddInstruction,
        'sub': SubInstruction,
        'neg': NegInstruction,
        'eq': EqualInstruction,
        'gt': GreaterThanInstruction,
        'lt': LessThanInstruction,
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
        arg1 = command_tokens[1] if len(command_tokens) == 3 else None
        arg2 = command_tokens[2] if len(command_tokens) == 3 else None

        command_cls = InstructionFactory.commands[cmd]
        return command_cls(cmd, arg1, arg2, self.filename)
