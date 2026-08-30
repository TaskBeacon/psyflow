"""TextBox2 adapter preserving caret/style state for multi-character text events."""
from psychopy.visual import TextBox2 as PsychoPyTextBox2


class TextBox2(PsychoPyTextBox2):
    """Handle complete Unicode input commits using the native per-character API.

    PsychoPy 2025.2.4 inserts an entire string in addCharAtCaret but advances
    the caret and styles by one character. IME/paste text events may contain
    multiple characters. Delegating one code point at a time preserves the
    native insertion, selection position and layout semantics without touching
    private state. Single-character input is unchanged.
    """

    def addCharAtCaret(self, text):
        for char in text:
            super().addCharAtCaret(char)
