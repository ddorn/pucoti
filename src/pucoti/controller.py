import functools
import threading
import zmq
import typer
import traceback

from . import constants
from . import time_utils
from .context import Context


def get_ctx() -> Context:
    from . import app

    try:
        return app.App.current_state().ctx
    except AttributeError:
        return None


def send_message(data: dict):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{constants.CONTROLER_PORT}")

    socket.send_json(data)
    # Wait 1s for a response - or fail
    socket.poll(timeout=1000)
    try:
        message = socket.recv(zmq.NOBLOCK).decode("utf-8")
        print(message)
    except zmq.ZMQError:
        print("No response from controller. Is pucoti running?")
    finally:
        socket.close(0)
        context.term()


cli = typer.Typer(no_args_is_help=True, add_completion=False)


COMMANDS = {}


def remote_if_not_in_main_app(func):

    COMMANDS[func.__name__] = func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if get_ctx():  # In the main pucoti instance
            return func(*args, **kwargs)
        else:  # As script to send message
            send_message(
                {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                }
            )

    return wrapper


@cli.command()
@remote_if_not_in_main_app
def set_purpose(purpose: str):
    """Set the pupose in the current pucoti session"""
    print(f"Controller: Setting purpose to {purpose}")
    get_ctx().set_purpose(purpose)


@cli.command()
@remote_if_not_in_main_app
def set_timer(timer: str):
    """Set the timer in the current pucoti session. E.g. "1h 30m"."""
    print(f"Controller: Setting timer to {timer}")
    get_ctx().set_timer_to(time_utils.human_duration(timer))


@cli.command()
@remote_if_not_in_main_app
def task_track_from_marvin(timer: int, purpose: list[str]):
    """Set the timer and purpose in the current pucoti session.

    This was made specifically for use with Amazing Marvin to
    set the purpose and timer of pucoti when you start tracking the time
    in Marvin.

    To use it, go to Marvin > Strategies > Start Time Tracking Task
        and enter
        pucoti-msg task-track-from-marvin $TASK_TIME_ESTIMATE $TASK_TITLE
        Then follow the instructions in the app.
    """

    if timer:
        get_ctx().set_timer_to(timer / 1000)
    get_ctx().set_purpose(" ".join(purpose))


@cli.command()
@remote_if_not_in_main_app
def mark_done_from_marvin(task: list[str]):
    """End the current purpose when a Marvin task with the same name is marked as done.

    To use it, go to Marvin > Strategies > Task Completed and enter
        pucoti-msg mark-done-from-marvin $TASK_TITLE
        Then follow the instructions in the app.
    """

    ctx = get_ctx()
    if ctx.purpose == " ".join(task):
        ctx.set_purpose("")
    else:
        print("Purpose does not match current task.")
        print(f"Current purpose: {ctx.purpose}")


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
                message = socket.recv_json(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                continue

            print(f"Received request: {message}")

            try:
                match message:
                    case {
                        "function": func_name,
                        "args": args,
                        "kwargs": kwargs,
                    }:
                        func = COMMANDS[func_name]
                        func(*args, **kwargs)
                        socket.send(b"OK")

            except Exception as e:
                traceback.print_exc()
                socket.send(b"Error: " + str(e).encode("utf-8"))


if __name__ == "__main__":
    cli()
