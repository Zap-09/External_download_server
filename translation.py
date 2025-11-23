from deep_translator import GoogleTranslator
import threading
import time


_translator = GoogleTranslator(source="auto", target="en")
_sema = threading.BoundedSemaphore(8)

def translate_external(text: str):
    attempts = 3
    delay = 0.3
    for i in range(attempts):
        try:
            with _sema:
                return _translator.translate(text), True
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(delay)
            delay *= 2
    return "unreachable", False

