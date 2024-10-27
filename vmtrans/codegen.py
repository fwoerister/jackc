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


def pop_from_stack(d_reg_only=False):
    machine_instructions = [
        do_c_instruction('D', 'A'),
        load_symbol('R13'),
        do_c_instruction('M', 'D'),
        load_symbol('SP'),
        do_c_instruction('AM', 'M-1'),
        do_c_instruction('D', 'M'),
    ]

    if not d_reg_only:
        machine_instructions.extend([
            resolve_symbol('R13'),
            do_c_instruction('M', 'D'),
        ])

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


def jump(target=None, value='0', condition='JMP'):
    if target:
        machine_instructions = [
            f'@{target}',
            f'{value};{condition}',
        ]
    else:
        machine_instructions = [
            f'{value};{condition}',
        ]

    return '\n'.join(machine_instructions)


def bootstrap_code():

    machine_instructions = [
        load_symbol('256'),
        do_c_instruction('D', 'A'),
        load_symbol('SP'),
        do_c_instruction('M', 'D'),
        # push return Address
        load_symbol(f'Sys.init$ret.1'),
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
        load_symbol('ARG'),
        do_c_instruction('M', 'D'),
        # LCL = SP
        load_symbol('SP'),
        do_c_instruction('D', 'M'),
        load_symbol('LCL'),
        do_c_instruction('M', 'D'),
        # goto f
        jump(f'Sys.init'),
        # ( returnAddress )
        f'(Sys.init$ret.1)',

    ]

    return '\n'.join(machine_instructions)
