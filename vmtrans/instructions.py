from vmtrans.codegen import resolve_symbol, do_c_instruction, push_on_stack, pop_from_stack, conditional_execution, \
    load_symbol, jump


class VMInstruction:
    count = 1

    def __init__(self, cmd, arg1, arg2, filename, func_name):
        self.cmd = cmd
        self.arg1 = arg1
        self.arg2 = arg2
        self.filename = filename
        self.func_symbol = func_name

        VMInstruction.count += 1

    def to_hack_code(self):
        return f'//{self.cmd} {self.arg1 if self.arg1 else ''} {self.arg2 if self.arg2 else ''}\n'

    def args_to_symbol_and_offset(self) -> (str, int, bool):
        if self.arg1 == 'constant':
            return str(self.arg2), 0
        elif self.arg1 == 'static':
            return f'{self.filename}.{self.arg2}', 0
        elif self.arg1 == 'pointer':
            return 'THIS', int(self.arg2)
        elif self.arg1 == 'this':
            return 'THIS', int(self.arg2)
        elif self.arg1 == 'that':
            return 'THAT', int(self.arg2)
        elif self.arg1 == 'argument':
            return 'ARG', int(self.arg2)
        elif self.arg1 == 'local':
            return 'LCL', int(self.arg2)
        elif self.arg1 == 'temp':
            return f'R{5 + int(self.arg2)}', 0

    def do_symbol_deref(self):
        return self.arg1 in ['this', 'that', 'argument', 'local']


class StackOperation(VMInstruction):

    def load_target_address(self):
        symbol, offset = self.args_to_symbol_and_offset()
        machine_instructions = []

        if offset > 1:
            machine_instructions.extend([
                load_symbol(offset),
                do_c_instruction('D', 'A')
            ])

        machine_instructions.append(load_symbol(symbol))

        if self.do_symbol_deref():
            machine_instructions.append('A=M')

        if offset == 1:
            machine_instructions.append(do_c_instruction('A', 'A+1'))
        elif offset > 1:
            machine_instructions.append(do_c_instruction('A', 'D+A'))

        return '\n'.join(machine_instructions) + '\n'

    def load_target_value(self):
        if self.arg1 == 'constant':
            return self.load_target_address() + 'D=A\n'
        else:
            return self.load_target_address() + 'D=M\n'


class PushInstruction(StackOperation):
    def to_hack_code(self):
        return super().to_hack_code() + self.load_target_value() + push_on_stack()


class PopInstruction(StackOperation):
    def to_hack_code(self):
        return super().to_hack_code() + self.load_target_address() + pop_from_stack()


class AddInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D+M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class SubInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
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
            do_c_instruction('M', 'M+1')
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
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('D', 'D-M'),
            conditional_execution(tag=f'EQ_{self.count}', value='D', condition='JEQ',
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
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('D', 'M-D'),
            conditional_execution(tag=f'EQ_{self.count}', value='D', condition='JGT',
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
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('D', 'M-D'),
            conditional_execution(tag=f'EQ_{self.count}', value='D', condition='JLT',
                                  code='\n'.join(code_true), else_code='\n'.join(code_false))
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class AndInstruction(VMInstruction):

    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D&M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class OrInstruction(VMInstruction):

    def to_hack_code(self):
        machine_instructions = [
            load_symbol('R13'),
            pop_from_stack(),
            load_symbol('R13'),
            do_c_instruction('D', 'M'),
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', 'D|M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class NotInstruction(VMInstruction):

    def to_hack_code(self):
        machine_instructions = [
            resolve_symbol('SP'),
            do_c_instruction('A', 'A-1'),
            do_c_instruction('M', '!M'),
        ]

        return super().to_hack_code() + '\n'.join(machine_instructions)


class ConditionalBranchInstruction(VMInstruction):
    def to_hack_code(self):
        return super().to_hack_code() + '\n'.join([
            pop_from_stack(d_reg_only=True),
            jump(f'{self.func_symbol}${self.arg1}', 'D', 'JNE')
        ])


class UnconditionalBranchInstruction(VMInstruction):
    def to_hack_code(self):
        return super().to_hack_code() + jump(f'{self.func_symbol}${self.arg1}')


class LabelInstruction(VMInstruction):
    def to_hack_code(self):
        if self.func_symbol:
            return super().to_hack_code() + f'({self.func_symbol}${self.arg1})'
        else:
            return super().to_hack_code() + f'({self.arg1})'


class CallFunctionInstruction(VMInstruction):
    def to_hack_code(self):
        return super().to_hack_code() + '\n'.join([
            # push return Address
            load_symbol(f'{self.arg1}$ret.{self.count}'),
            do_c_instruction('D', 'A'),
            push_on_stack(),
            # push LCL
            load_symbol('LCL'),
            do_c_instruction('D', 'M'),
            push_on_stack(),
            # push ARG
            load_symbol('ARG'),
            do_c_instruction('D', 'M'),
            push_on_stack(),
            # push THIS
            load_symbol('THIS'),
            do_c_instruction('D', 'M'),
            push_on_stack(),
            # push THAT
            load_symbol('THAT'),
            do_c_instruction('D', 'M'),
            push_on_stack(),
            # ARG = SP - 5 - nArgs
            load_symbol('SP'),
            do_c_instruction('D', 'M'),
            load_symbol('5'),
            do_c_instruction('D', 'D-A'),
            load_symbol(f'{self.arg2}'),
            do_c_instruction('D', 'D-A'),
            load_symbol('ARG'),
            do_c_instruction('M', 'D'),
            # LCL = SP
            load_symbol('SP'),
            do_c_instruction('D', 'M'),
            load_symbol('LCL'),
            do_c_instruction('M', 'D'),
            # goto f
            jump(f'{self.arg1}'),
            # ( returnAddress )
            f'({self.arg1}$ret.{self.count})',
        ])


class DefineFunctionInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [
            f'({self.func_symbol})',
            do_c_instruction('D', '0'),
        ]

        machine_instructions.extend([push_on_stack(is_constant=True)] * int(self.arg2))

        return super().to_hack_code() + '\n'.join(machine_instructions)


class ReturnInstruction(VMInstruction):
    def to_hack_code(self):
        machine_instructions = [

            # R13 = return Address
            load_symbol('LCL'),
            do_c_instruction('D', 'M'),
            load_symbol('5'),
            do_c_instruction('A', 'D-A'),
            do_c_instruction('D', 'M'),
            load_symbol('R14'),
            do_c_instruction('M', 'D'),

            # *ARG = pop()
            load_symbol('ARG'),
            do_c_instruction('A', 'M'),
            pop_from_stack(),
            # SP = ARG + 1
            load_symbol('ARG'),
            do_c_instruction('D', 'M+1'),
            load_symbol('SP'),
            do_c_instruction('M', 'D'),
            # THAT = *(frame - 1)
            load_symbol('LCL'),
            do_c_instruction('AM', 'M-1'),
            do_c_instruction('D', 'M'),
            load_symbol('THAT'),
            do_c_instruction('M', 'D'),
            # THIS = *(frame - 2)
            load_symbol('LCL'),
            do_c_instruction('AM', 'M-1'),
            do_c_instruction('D', 'M'),
            load_symbol('THIS'),
            do_c_instruction('M', 'D'),
            # ARG  = *(frame - 3)
            load_symbol('LCL'),
            do_c_instruction('AM', 'M-1'),
            do_c_instruction('D', 'M'),
            load_symbol('ARG'),
            do_c_instruction('M', 'D'),
            # LCL  = *(frame - 4)
            load_symbol('LCL'),
            do_c_instruction('AM', 'M-1'),
            do_c_instruction('D', 'M'),
            load_symbol('LCL'),
            do_c_instruction('M', 'D'),
            # goto retAddr
            load_symbol('R14'),
            do_c_instruction('A', 'M'),
            jump(),
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
        'label': LabelInstruction,
        'goto': UnconditionalBranchInstruction,
        'if-goto': ConditionalBranchInstruction,
        'call': CallFunctionInstruction,
        'function': DefineFunctionInstruction,
        'return': ReturnInstruction,
    }

    def __init__(self, namespace):
        self.namespace = namespace
        self.active_func = None

    def create_instruction(self, instruction):
        if "//" in instruction:
            stripped_inst = instruction[:instruction.index("//")].strip()
        else:
            stripped_inst = instruction.strip()

        command_tokens = stripped_inst.split(' ')

        cmd = command_tokens[0]
        arg1 = command_tokens[1] if len(command_tokens) >= 2 else None
        arg2 = command_tokens[2] if len(command_tokens) >= 3 else None

        if cmd == 'function':
            self.active_func = arg1

        command_cls = InstructionFactory.commands[cmd]
        return command_cls(cmd, arg1, arg2, self.namespace, self.active_func)
