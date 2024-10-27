import ntpath
import os

import click

from vmtrans.codegen import bootstrap_code
from vmtrans.parser import Parser


@click.command()
@click.option('--no-bootstrap', is_flag=True, default=False)
@click.argument('source', type=click.Path(exists=True, readable=True))
def parse_source(no_bootstrap, source):
    if os.path.isdir(source):
        if source.endswith('/') or source.endswith('\\'):
            source = source[:-1]

        target_name = os.path.join(source, f'{ntpath.basename(source)}.asm')
    else:
        target_name = f'{source[:-3]}.asm'

    if not no_bootstrap:
        with open(target_name, 'w') as target:
            target.write(bootstrap_code() + '\n')

    if os.path.isdir(source):
        compile_dir(source, target_name)
    else:
        if not source.endswith('.vm'):
            raise Exception('Source must end with ".vm"')
        compile_file(source, target_name)


def compile_file(source_file, target_name):
    with open(target_name, 'a') as target:
        for instruction in Parser.parse(source_file):
            target.write(f'{instruction.to_hack_code()}\n')


def compile_dir(source_dir, target_name):
    with open('target_name', 'a') as target:
        for file in os.listdir(source_dir):
            if file.endswith('.vm'):
                compile_file(os.path.join(source_dir, file), target_name)


if __name__ == '__main__':
    parse_source()
