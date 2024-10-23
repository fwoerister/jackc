import click

from vmtrans.codegen import infinity_loop
from vmtrans.parser import Parser


@click.command()
@click.option('--vm', default=False, is_flag=True)
@click.argument('source', type=click.Path(exists=True, readable=True))
def parse_source(vm, source):
    if vm and not source.endswith('.vm'):
        raise Exception('Source must end with ".vm"')
    elif not vm and not source.endswith('.jack'):
        raise Exception('Source must end with ".jack"')

    target_name = f'{source[:-3]}.hack'

    parser = Parser(source)

    with open(target_name, 'w') as target:
        for instruction in parser.parse():
            target.write(f'{instruction.to_hack_code()}\n')

        target.write(infinity_loop())



if __name__ == '__main__':
    parse_source()
