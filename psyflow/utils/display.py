"""Timing/display helper utilities."""

from psychopy import core, visual


def count_down(win, seconds=3, **stim_kwargs):
    """Display a frame-accurate countdown using TextStim."""
    cd_clock = core.Clock()
    for i in reversed(range(1, seconds + 1)):
        stim = visual.TextStim(win=win, text=str(i), **stim_kwargs)
        cd_clock.reset()
        while cd_clock.getTime() < 1.0:
            stim.draw()
            win.flip()

