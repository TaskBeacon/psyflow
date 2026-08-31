"""Real capture orchestration with fake window/event delivery; no GUI proof."""
from types import SimpleNamespace
from psyflow.pointer_pursuit import capture_pursuit

def test_flip_invalidation_and_reentry_invalidates_pending_sample(monkeypatch):
    import psychopy.event
    import psychopy.visual
    import psyflow.sim.context
    class Stim:
        units='pix'
        pos=(0,0)
        def draw(self):pass
    class Window:
        units='pix';size=(1000,800);mouseVisible=True
        def __init__(self):self.winHandle=self;self.t=0;self.n=0;self.calls=[];self.handlers={}
        def push_handlers(self,**h):self.handlers=h;h['on_mouse_motion']()
        def remove_handlers(self,**h):self.handlers={}
        def callOnFlip(self,fn,*args):self.calls.append((fn,args))
        def getFutureFlipTime(self,clock):return self.t+.02
        def flip(self):
            self.n+=1;self.t+=.02
            for fn,args in self.calls:fn(*args)
            self.calls=[]
            if self.n==2:
                self.handlers['on_deactivate']();self.handlers['on_mouse_motion']()
            return self.t
    win=Window();states={}
    unit=SimpleNamespace(win=win,kb=SimpleNamespace(getKeys=lambda **k:[]),stimuli=[],label='tracking',
                         clock=SimpleNamespace(reset=lambda:None,getTime=lambda:win.t),
                         _qa_scale_duration=lambda d:(d,0,False),set_state=lambda **k:states.update(k),
                         get_state=lambda k,*args:states.get(k),_stamp_onset=lambda *a:None,
                         _stamp_close=lambda:None,_emit_trigger=lambda *a,**k:None,log_unit=lambda:None)
    monkeypatch.setattr(psychopy.visual,'BaseVisualStim',Stim)
    monkeypatch.setattr(psychopy.event,'Mouse',lambda **k:SimpleNamespace(getPos=lambda:[0,0]))
    monkeypatch.setattr(psyflow.sim.context,'get_context',lambda:None)
    capture_pursuit(unit,target=Stim(),cursor=Stim(),orbit_radius=253,target_radius=25,rotations_per_second=.13,duration=.05)
    assert states['pursuit_samples'][0]['valid'] is False
    assert states['pursuit_samples'][1]['valid'] is True
    assert states['observed_duration']<=.011
    assert not win.handlers
