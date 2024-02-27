import os
import click
from storage import setup_db


@click.group()
def cli():
    pass


@click.command(help="Register a song or a directory of songs")
@click.argument("path")
def register(path):
    print("register")


@click.command(help="Recognise a song at a filename or using the microphone")
@click.argument("path", required=False)
@click.option("--listen", is_flag=True,
              help="Use the microphone to listen for a song")
def recognise(path, listen):
    print("recognise")
    


@click.command(
    help="Initialise the DB, needs to be done before other commands")
def initialise():
    print("initialise")
    setup_db()


cli.add_command(register)
cli.add_command(recognise)
cli.add_command(initialise)

if __name__ == "__main__":
    cli()
