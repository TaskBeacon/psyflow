"""No-window semantic tests; real GPU/timing checks are separate canaries."""
from importlib import import_module
from types import SimpleNamespace
import numpy as np
import pytest

module=import_module('psyflow.StimUnit')

class FakeGrating:
    def __init__(self,phase=(.25,.37)):self.phase=phase;self.drawn=[]
    @property
    def phase(self):return self._phase
    @phase.setter
    def phase(self,value):self._phase=np.array(value,dtype=float)
    def draw(self):self.drawn.append(self.phase.copy())

class Clock:
    def __init__(self,win):self.win=win;self.origin=0
    def reset(self):self.origin=self.win.time
    def getTime(self):return self.win.time-self.origin

class Window:
    monitorFramePeriod=.01
    def __init__(self):self.time=100;self.callbacks=[];self.flips=[]
    def callOnFlip(self,fn,*args,**kwargs):self.callbacks.append((fn,args,kwargs))
    def getFutureFlipTime(self,clock):return clock.getTime()+.01
    def flip(self):
        self.time+=.01
        callbacks,self.callbacks=self.callbacks,[]
        for fn,args,kwargs in callbacks:fn(*args,**kwargs)
        self.flips.append(self.time)
        return self.time

def make_unit(monkeypatch,stim):
    monkeypatch.setattr(module.visual,'GratingStim',FakeGrating)
    win=Window();unit=module.StimUnit('gabor',win,SimpleNamespace())
    unit.clock=Clock(win);unit.stimuli=[stim]
    return unit

def test_drift_preserves_y_base_and_actual_final_phase(monkeypatch):
    stim=FakeGrating();unit=make_unit(monkeypatch,stim)
    unit.show(.04,phase_drift_hz=-4)
    assert np.array(stim.drawn)[:,0]==pytest.approx([.25,.21,.17,.13])
    assert np.array(stim.drawn)[:,1]==pytest.approx([.37]*4)
    assert unit.get_state('drift_final_phases')[0]==pytest.approx([.13,.37])
    assert unit.get_state('drift_frame_count')==4
    # A following static show must hold the actual last phase, not recompute4*.04.
    unit.show(.02)
    assert stim.drawn[-1]==pytest.approx([.13,.37])

def test_phase_uses_elapsed_clock_not_frame_counter(monkeypatch):
    stim=FakeGrating((0,0));unit=make_unit(monkeypatch,stim)
    def predicted(clock):return clock.getTime()+.03
    unit.win.getFutureFlipTime=predicted
    unit.show(.05,phase_drift_hz=4)
    assert np.array(stim.drawn)[:,0]==pytest.approx([0,.12,.16])
    assert unit.get_state('drift_flip_times_s')==pytest.approx([0,.01,.02])

def test_late_prediction_does_not_submit_another_drift_frame(monkeypatch):
    stim=FakeGrating((0,0));unit=make_unit(monkeypatch,stim)
    original_flip=unit.win.flip
    def delayed_flip():
        if len(unit.win.flips)==1:unit.win.time+=.05
        return original_flip()
    unit.win.flip=delayed_flip
    unit.show(.05,phase_drift_hz=4)
    assert unit.get_state('drift_frame_count')==2
    assert unit.get_state('drift_late_close') is True
    assert unit.get_state('drift_sample_times_s')==pytest.approx([0,.01])

def test_late_before_second_flip_retains_initial_frame_and_resets_flag(monkeypatch):
    stim=FakeGrating();unit=make_unit(monkeypatch,stim)
    normal_prediction=unit.win.getFutureFlipTime
    unit.win.getFutureFlipTime=lambda clock:.1
    unit.show(.05,phase_drift_hz=4)
    assert unit.get_state('drift_frame_count')==1
    assert unit.get_state('drift_final_phases')[0]==pytest.approx([.25,.37])
    assert unit.get_state('offset_flip_time')==unit.get_state('flip_time')
    assert unit.get_state('drift_late_close') is True
    unit.win.getFutureFlipTime=normal_prediction
    unit.show(.02,phase_drift_hz=4)
    assert unit.get_state('drift_late_close') is False

def test_stalled_refresh_does_not_preserve_old_frame_budget(monkeypatch):
    stim=FakeGrating((0,0));unit=make_unit(monkeypatch,stim)
    original_flip=unit.win.flip
    def delayed_flip():
        if len(unit.win.flips)==1:unit.win.time+=.05
        return original_flip()
    unit.win.flip=delayed_flip
    unit.show(.1,phase_drift_hz=4)
    assert unit.get_state('drift_frame_count')==5
    assert unit.get_state('drift_flip_times_s')[-1]==pytest.approx(.09)
    assert unit.get_state('drift_max_frame_interval_s')==pytest.approx(.06)
    assert unit.get_state('drift_final_phases')[0][0]==pytest.approx(.36)

def test_default_show_does_not_drift(monkeypatch):
    stim=FakeGrating();unit=make_unit(monkeypatch,stim);unit.show(.03)
    assert all(np.array_equal(p,[.25,.37]) for p in stim.drawn)
    assert unit.get_state('drift_frame_count') is None

@pytest.mark.parametrize('value',[float('nan'),float('inf'),'4',True,False])
def test_rejects_invalid_frequency(monkeypatch,value):
    unit=make_unit(monkeypatch,FakeGrating())
    with pytest.raises(ValueError):unit.show(.03,phase_drift_hz=value)
    assert not unit.win.flips

def test_requires_grating_and_rejects_playable_companion(monkeypatch):
    unit=make_unit(monkeypatch,SimpleNamespace(draw=lambda:None))
    with pytest.raises(ValueError):unit.show(.03,phase_drift_hz=4)
    unit.stimuli=[FakeGrating(),SimpleNamespace(play=lambda:None)]
    with pytest.raises(ValueError):unit.show(.03,phase_drift_hz=4)
