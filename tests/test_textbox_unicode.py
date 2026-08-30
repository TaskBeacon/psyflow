from unittest.mock import patch
from psyflow.textbox import TextBox2, PsychoPyTextBox2


def test_multicharacter_input_advances_native_caret_per_codepoint():
    box=object.__new__(TextBox2)
    calls=[]
    with patch.object(PsychoPyTextBox2,'addCharAtCaret',lambda self,char:calls.append(char)):
        box.addCharAtCaret('中文；ABC\n')
    assert calls==list('中文；ABC\n')


def test_single_character_and_empty_commit():
    box=object.__new__(TextBox2)
    calls=[]
    with patch.object(PsychoPyTextBox2,'addCharAtCaret',lambda self,char:calls.append(char)):
        box.addCharAtCaret('好')
        box.addCharAtCaret('')
    assert calls==['好']
