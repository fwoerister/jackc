def conditional_execution(tag, value, condition, code=None, else_code=None):
    machine_instructions = [
        jump(f'{tag}_TRUE', value, condition),
        else_code,
        jump(f'{tag}_END'),
        f'({tag}_TRUE)',
        code,
        f'({tag}_END)',
    ]

    return '\n'.join(machine_instructions)


def push_on_stack(is_constant=False):
    machine_instructions = []

    machine_instructions.extend([
        resolve_symbol('SP'),
        do_c_instruction('M', 'D'),
        load_symbol('SP'),
        do_c_instruction('M', 'M+1'),
    ])

    return '\n'.join(machine_instructions)


def pop_from_stack():
    machine_instructions = [
        do_c_instruction('D', 'A'),
        load_symbol('R13'),
        do_c_instruction('M', 'D'),
        load_symbol('SP'),
        do_c_instruction('AM', 'M-1'),
        do_c_instruction('D', 'M'),
        resolve_symbol('R13'),
        do_c_instruction('M', 'D'),
    ]

    return '\n'.join(machine_instructions)


def resolve_symbol(symbol, offset=0):
    machine_instructions = []

    if offset > 1:
        machine_instructions.extend([
            load_symbol(offset),
            do_c_instruction('D', 'A'),
        ])

    machine_instructions.append(f'@{symbol}')
    machine_instructions.append(do_c_instruction('A', 'M'))

    if offset == 1:
        machine_instructions.append(do_c_instruction('A', 'A+1'))
    elif offset > 1:
        machine_instructions.append(do_c_instruction('A', 'D+A'))

    return '\n'.join(machine_instructions)


def load_symbol(symbol):
    return f'@{symbol}'


def do_c_instruction(dest, comp):
    return f'{dest}={comp}'


def jump(target, value='0', condition='JMP'):
    machine_instructions = [
        f'@{target}',
        f'{value};{condition}',
    ]

    return '\n'.join(machine_instructions)


def infinity_loop():
    machine_instructions = [
        '(END)',
        jump('END'),
    ]

    return '\n'.join(machine_instructions)
