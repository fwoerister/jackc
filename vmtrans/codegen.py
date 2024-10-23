def conditional_execution(tag, value, condition, code=None, else_code=None):
    machine_instructions = [
        jump(f'@{tag}_TRUE', value, condition),
        else_code,
        jump(f'{tag}_END'),
        f'({tag}_TRUE)',
        code,
        f'({tag}_END)',
    ]

    return '\n'.join(machine_instructions)


def push_on_stack(base, offset=0):
    machine_instructions = [
        load_to_a_register(base, offset),
        do_c_instruction('D', 'M'),
        load_to_a_register('SP'),
        do_c_instruction('A', 'M'),
        do_c_instruction('M', 'D'),
        load_to_a_register('SP'),
        do_c_instruction('M', 'M+1'),
    ]

    return '\n'.join(machine_instructions)


def pop_from_stack(base, offset=0):
    machine_instructions = [
        load_to_a_register('SP'),
        do_c_instruction('A', 'M'),
        do_c_instruction('M', 'M-1'),
        do_c_instruction('D', 'M'),
        load_to_a_register(base, offset),
        do_c_instruction('M', 'D'),
    ]

    return '\n'.join(machine_instructions)


def load_to_a_register(symbol, offset=0):
    machine_instructions = []

    if offset != 0:
        machine_instructions.extend([
            f'@{offset}',
            do_c_instruction('D', 'A'),
        ])

    machine_instructions.append(f'@{symbol}')

    if offset != 0:
        machine_instructions.append(do_c_instruction('A', 'D+A'))

    return '\n'.join(machine_instructions)


def do_c_instruction(dest, comp):
    asm_instruction = f'{dest}=' if dest else ''
    asm_instruction += comp
    if jump:
        asm_instruction += f';{jump}'

    return asm_instruction


def jump(target, value='0', condition='JMP'):
    machine_instructions = [
        f'@{target}',
        f'{value};{condition}',
    ]

    return '\n'.join(machine_instructions)


def infinity_loop():
    machine_instructions = [
        '@END',
        '(END',
        '0;JMP',
    ]
    return '\n'.join(machine_instructions)
