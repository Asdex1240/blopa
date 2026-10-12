import time

from app.errors import BlopaError
from app.factory import build_agent

EXIT_COMMANDS = {"/salir", "/exit", "salir"}
RESET_COMMANDS = {"/reset", "/nuevo"}


def run(agent, read=input, write=print):
    write("BLOPA: Hola, ¿en qué te ayudo? (/reset para empezar de nuevo, /salir para terminar)")
    while True:
        try:
            text = read("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            write("")
            return
        if not text:
            continue
        if text.lower() in EXIT_COMMANDS:
            return
        if text.lower() in RESET_COMMANDS:
            agent.reset()
            write("BLOPA: Listo, empezamos de nuevo.")
            continue
        write(f"BLOPA: {answer(agent, text)}")


def answer(agent, text):
    started = time.monotonic()
    try:
        reply = agent.reply(text)
    except BlopaError as error:
        return f"[error] {error}"
    tools = f"[{', '.join(reply.tools_used)}] " if reply.tools_used else ""
    return f"{tools}{reply.text}  ({time.monotonic() - started:.1f} s)"


if __name__ == "__main__":
    run(build_agent())
