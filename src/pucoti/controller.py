import functools
import sys
import zmq
import typer
import shlex
import traceback


from . import app
from . import time_utils
from .context import Context
from typer.testing import CliRunner


def get_ctx() -> Context:
    try:
        return app.App.current_state().ctx
    except AttributeError:
        return None


def send_message(*parts: str):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_string(shlex.join(parts))
    message = socket.recv()
    print(message.decode("utf-8"))


cli = typer.Typer()


def remote(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if not get_ctx():
                args = sys.argv[1:]  # 0 is pucoti, 1 is "msg", 2+ are the arguments
                send_message(*args)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print("Error:", e)
            raise

    return wrapper


@cli.command()
@remote
def set_purpose(purpose: str):
    print(f"Controller: Setting purpose to {purpose}")
    get_ctx().set_purpose(purpose)


@cli.command()
@remote
def set_timer(timer: str):
    print(f"Controller: Setting timer to {timer}")
    get_ctx().set_timer_to(time_utils.human_duration(timer))


@cli.command()
def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    runner = CliRunner()

    while True:
        message = socket.recv()
        print("Received request: %s" % message)

        try:
            message = message.decode("utf-8")
            result = runner.invoke(cli, shlex.split(message))
            print("Message:", shlex.split(message))
            print("Result:", result)
            print("Exit code:", result.exit_code)
            print("Output:", result.stdout)
            if result.exit_code != 0:
                raise Exception(result.stdout)
            else:
                socket.send(b"OK")
        except Exception as e:
            import traceback

            traceback.print_exc()
            socket.send(b"Error: " + str(e).encode("utf-8"))


if __name__ == "__main__":
    cli()
