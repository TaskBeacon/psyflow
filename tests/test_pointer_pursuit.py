import importlib.util
from pathlib import Path
import math
import pytest

spec = importlib.util.spec_from_file_location('pure_pursuit',Path(__file__).parents[1]/'psyflow/pointer_pursuit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def s(t,error=0,valid=True):
    return dict(t=t,cursor=[error,0] if valid else None,target=[0,0],valid=valid,reason='blur' if not valid else None)

def test_unequal_intervals_are_time_weighted():
    result=m.evaluate_pursuit([s(0,0),s(.01,20),s(.1,0)],.1,5)
    assert result['on_target_proportion']==pytest.approx(.1)
    assert result['rms_error']==pytest.approx(math.sqrt(360))

def test_missing_gaps_do_not_become_offtarget_or_fullscore():
    result=m.evaluate_pursuit([s(0),s(.01),s(.5),s(.51)],1,5)
    assert result['observed_duration']==pytest.approx(.02)
    assert result['on_target_proportion']==pytest.approx(.02)
    assert result['observed_on_target_proportion']==1
    assert result['missing_duration']==pytest.approx(.98)

def test_both_endpoints_required():
    result=m.evaluate_pursuit([s(0),s(.01,valid=False),s(.02),s(.03)],.03,5)
    assert result['observed_duration']==pytest.approx(.01)

def test_invalidation_between_two_valid_frames_is_missing():
    samples=[dict(s(0),epoch=0),dict(s(.01),epoch=1),dict(s(.02),epoch=1)]
    assert m.evaluate_pursuit(samples,.02,5)['observed_duration']==pytest.approx(.01)

def test_terminal_clipping_and_initial_missing():
    result=m.evaluate_pursuit([s(.02),s(.07),s(.12)],.1,5)
    assert result['observed_duration']==pytest.approx(.08)

def test_empty_means_missing():
    result=m.evaluate_pursuit([],1,5)
    assert result['rms_error'] is None and result['observed_on_target_proportion'] is None
    assert result['missing_duration']==1 and result['on_target_proportion']==0

@pytest.mark.parametrize('times',[[0,0],[.1,0],[-1,0],[0,float('nan')]])
def test_bad_times_rejected(times):
    with pytest.raises(ValueError):m.evaluate_pursuit([s(t) for t in times],1,5)

def test_exact_radius_inclusive():
    assert m.evaluate_pursuit([s(0,5),s(.1,5)],.1,5)['on_target_proportion']==1

def test_finite_but_overflowing_coordinates_fail_closed():
    samples=[dict(s(0),cursor=[1e308,0],target=[-1e308,0]),s(.1)]
    with pytest.raises(ValueError,match='overflow'):m.evaluate_pursuit(samples,.1,5)

@pytest.mark.parametrize('hz',[30,60,120,144])
def test_stationary_center_polls_and_rotation_elapsed(hz):
    samples=[]
    for i in range(hz+1):
        t=i/hz
        samples.append(dict(t=t,cursor=[0,0],target=m.pursuit_position(t,253,.13),valid=True))
    result=m.evaluate_pursuit(samples,1,25)
    assert result['coverage']==pytest.approx(1)
    assert result['rms_error']==pytest.approx(253)
    assert result['on_target_proportion']==0
    assert samples[-1]['target']==pytest.approx(m.pursuit_position(1,253,.13))

def test_clockwise_from_top():
    assert m.pursuit_position(0,253,.13)==[0,253]
    assert m.pursuit_position(1/(4*.13),253,.13)==pytest.approx([253,0])

@pytest.mark.parametrize('profile',['accurate','offtarget','omission'])
def test_synthetic_profiles_are_explicit(profile):
    result=m.evaluate_pursuit(m.simulated_pursuit(1,253,25,.13,profile),1,25)
    assert result['coverage']==(0 if profile=='omission' else 1)
    assert result['on_target_proportion']==(1 if profile=='accurate' else 0)
