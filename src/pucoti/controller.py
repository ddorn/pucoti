import functools
import sys
import threading
import zmq
import typer
import shlex
import traceback

from pucoti import constants


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
    socket.connect(f"tcp://localhost:{constants.CONTROLER_PORT}")

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


class Controller:
    def __init__(self):
        self.stop_event = threading.Event()
        self.handle = None

    def start(self):
        self.handle = threading.Thread(target=self.server).start()

    def stop(self):
        self.stop_event.set()
        if self.handle:
            self.handle.join()

    def server(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        runner = CliRunner()

        try:
            socket.bind(f"tcp://*:{constants.CONTROLER_PORT}")
        except zmq.error.ZMQError as e:
            print("Error:", e)
            print(
                "An other instance of Pucoti might be running. Not starting remote controller for this one."
            )
            return

        while not self.stop_event.is_set():
            # Check for messages - non-blocking
            socket.poll(timeout=400)
            try:
                message = socket.recv(flags=zmq.NOBLOCK).decode("utf-8")
            except zmq.ZMQError:
                continue

            print("Received request: %s" % shlex.split(message))

            try:
                result = runner.invoke(cli, shlex.split(message))
                if result.exit_code != 0:
                    print("Result:", result)
                    print("Exit code:", result.exit_code)
                    print("Output:", result.stdout)
                    raise Exception(result.stdout)
                else:
                    socket.send(b"OK")
            except Exception as e:
                traceback.print_exc()
                socket.send(b"Error: " + str(e).encode("utf-8"))


if __name__ == "__main__":
    cli()
