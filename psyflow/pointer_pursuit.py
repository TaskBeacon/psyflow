"""Opt-in circular pursuit geometry, duration-weighted metrics and capture.

Coordinates are software pixels, center origin, positive y upward. Samples use
actual display-update timestamps; command timestamps remain separately recorded.
"""
from math import cos, sin, pi, hypot, sqrt, isfinite


def validate_pursuit(orbit_radius, target_radius, rotations_per_second, duration, max_gap_s):
    for value in (orbit_radius, target_radius, rotations_per_second, duration, max_gap_s):
        if not isfinite(float(value)) or float(value) <= 0:
            raise ValueError("pursuit geometry, speed, duration and max_gap_s must be finite positive")


def pursuit_position(t, orbit_radius, rotations_per_second):
    angle = 2 * pi * float(rotations_per_second) * float(t)
    return [float(orbit_radius) * sin(angle), float(orbit_radius) * cos(angle)]


def evaluate_pursuit(samples, duration, target_radius, max_gap_s=0.1):
    """Left hold on intervals with valid endpoints, clipped to [0,duration].

    Entire gaps above max_gap_s are missing. Never bridge invalidation. A terminal
    sample beyond duration closes the previous interval but adds no extra time.
    Duplicate/nonmonotonic timestamps are rejected, not silently reweighted.
    """
    validate_pursuit(1, target_radius, 1, duration, max_gap_s)
    duration = float(duration)
    last_t = -1.0
    reasons = {}
    for sample in samples:
        t = float(sample['t'])
        if not isfinite(t) or t < 0 or t <= last_t:
            raise ValueError('pursuit sample times must be finite, nonnegative and strictly increasing')
        last_t = t
        if sample.get('valid', False):
            for key in ('cursor', 'target'):
                point = sample.get(key)
                if point is None or len(point) != 2 or not all(isfinite(float(x)) for x in point):
                    raise ValueError('valid pursuit samples need finite cursor and target points')
        else:
            reason = str(sample.get('reason') or 'unknown')
            reasons[reason] = reasons.get(reason, 0) + 1
    observed = on_target = squared = 0.0
    max_gap = 0.0
    for previous, current in zip(samples, samples[1:]):
        gap = float(current['t']) - float(previous['t'])
        max_gap = max(max_gap, gap)
        dt = max(0.0, min(duration, float(current['t'])) - min(duration, float(previous['t'])))
        if (gap > float(max_gap_s) + 1e-10 or not previous.get('valid') or not current.get('valid')
                or previous.get('epoch',0) != current.get('epoch',0)):
            continue
        error = hypot(previous['cursor'][0] - previous['target'][0], previous['cursor'][1] - previous['target'][1])
        if not isfinite(error) or not isfinite(error*error*dt):
            raise ValueError('pursuit coordinate magnitude overflows weighted error')
        observed += dt
        on_target += dt if error <= float(target_radius) else 0.0
        squared += error * error * dt
        if not isfinite(squared):
            raise ValueError('pursuit weighted error accumulator overflow')
    observed = min(duration, observed)
    return dict(observed_duration=observed, missing_duration=max(0.0, duration-observed),
                on_target_duration=on_target, on_target_proportion=on_target/duration,
                observed_on_target_proportion=on_target/observed if observed > 0 else None,
                rms_error=sqrt(squared/observed) if observed > 0 else None,
                coverage=observed/duration, max_gap=max_gap, sample_count=len(samples),
                invalid_sample_reasons=reasons, integration_method='left_hold_valid_endpoints_v1')


def simulated_pursuit(duration, orbit_radius, target_radius, rotations_per_second, profile):
    if profile not in ('accurate', 'offtarget', 'omission'):
        raise ValueError('unknown pursuit simulation profile')
    count = max(2, int(float(duration)*120)+1)
    result = []
    for i in range(count):
        t = float(duration)*i/(count-1)
        target = pursuit_position(t, orbit_radius, rotations_per_second)
        cursor = list(target) if profile == 'accurate' else [0.0, 0.0]
        result.append(dict(t=t, target_command_time=t, cursor_sample_time=t,
                           target=target, cursor=cursor if profile != 'omission' else None,
                           valid=profile != 'omission', reason='synthetic_omission' if profile == 'omission' else None))
    return result


def capture_pursuit(unit, *, target, cursor, orbit_radius, target_radius,
                    rotations_per_second, duration, max_gap_s=0.1,
                    onset_trigger=None, offset_trigger=None):
    """Framework-owned capture used by StimUnit.capture_pointer_pursuit."""
    from psychopy import event, visual
    from .sim.context import get_context
    from .sim.adapter import ResponderAdapter
    from .sim.contracts import Observation

    validate_pursuit(orbit_radius, target_radius, rotations_per_second, duration, max_gap_s)
    if unit.win.units != 'pix' or target.units != 'pix' or cursor.units != 'pix':
        raise ValueError('capture_pointer_pursuit requires explicit pix window and stimuli')
    if not isinstance(target, visual.BaseVisualStim) or not isinstance(cursor, visual.BaseVisualStim):
        raise TypeError('target and cursor must be PsychoPy stimuli')
    used, _, scaled = unit._qa_scale_duration(float(duration))
    if scaled:
        unit.set_state(duration_nominal=float(duration), duration_scaled=used)
    unit.set_state(duration=used, orbit_radius=orbit_radius, target_radius=target_radius,
                   rotations_per_second=rotations_per_second, coordinate_units='software_px',
                   sampling_policy='per_display_update_elapsed_time', max_gap_s=max_gap_s)
    ctx = get_context()
    responder = getattr(ctx, 'responder', None) if ctx and ctx.mode in ('qa', 'sim') else None
    stims = [s for s in unit.stimuli if callable(getattr(s, 'draw', None))]
    target.pos = pursuit_position(0, orbit_radius, rotations_per_second)
    for stim in stims:
        stim.draw()
    target.draw()
    unit.win.callOnFlip(unit.clock.reset)
    unit.win.callOnFlip(unit._stamp_onset, onset_trigger)
    unit._emit_trigger(onset_trigger, when='flip', wait=False, name=f'{unit.label}_onset', meta={'kind':'onset'})
    first_flip = unit.win.flip()
    unit.set_state(flip_time=first_flip)
    samples = []
    actual_elapsed = 0.0
    watch_supported = False
    aborted = False
    if responder:
        adapter = ResponderAdapter(policy=str(getattr(ctx.config, 'sim_policy', 'warn') or 'warn'),
                                   default_rt_s=0.05, clamp_rt=True, logger=getattr(ctx,'sim_logger',None), session=getattr(ctx,'session',None))
        observation = Observation(mode=ctx.mode, trial_id=unit.get_state('trial_id'), block_id=unit.get_state('block_id'),
                                  phase=unit.label, deadline_s=used, response_window_open=True, response_window_s=used,
                                  valid_keys=['pursuit'], t_phase_onset=unit.get_state('onset_time'),
                                  t_phase_onset_global=unit.get_state('onset_time_global'),
                                  stim_id=unit.get_state('stim_id'), stim_features=unit.get_state('stim_features'),
                                  condition_id=unit.get_state('condition_id'), task_factors=dict(unit.get_state('task_factors') or {}))
        action = adapter.handle_response(observation,responder).used_action
        profile = str((action.meta or {}).get('pursuit_profile','accurate')) if action.key == 'pursuit' else 'omission'
        samples = simulated_pursuit(used, orbit_radius, target_radius, rotations_per_second, profile)
        actual_elapsed = float(unit.clock.getTime())
    else:
        handle = unit.win.winHandle
        state = {'valid':False, 'reason':'awaiting_mouse_motion', 'resized':False, 'epoch':0}
        def invalidate(reason):
            state.update(valid=False,reason=reason,epoch=state['epoch']+1)
        def motion(*args):
            if not state['resized']:
                state.update(valid=True,reason=None)
        def resize(*args):
            state['resized'] = True
            invalidate('resize')
        handlers = dict(on_mouse_motion=motion, on_mouse_drag=motion,
                        on_mouse_leave=lambda *a: invalidate('pointerleave'),
                        on_deactivate=lambda *a: invalidate('blur'), on_resize=resize)
        visible = bool(unit.win.mouseVisible)
        mouse = event.Mouse(win=unit.win,visible=False)
        try:
            if callable(getattr(handle,'push_handlers',None)):
                handle.push_handlers(**handlers)
                watch_supported = True
            while True:
                if unit.kb.getKeys(keyList=['escape'],waitRelease=False):
                    aborted = True
                    break
                cursor_t = float(unit.clock.getTime())
                pos = [float(v) for v in mouse.getPos()]
                width,height = unit.win.size
                valid = state['valid'] and watch_supported and abs(pos[0]) <= width/2 and abs(pos[1]) <= height/2
                sample_epoch = state['epoch']
                command_t = max(0.0,float(unit.win.getFutureFlipTime(clock=unit.clock)))
                commanded = pursuit_position(command_t,orbit_radius,rotations_per_second)
                target.pos = commanded
                cursor.pos = pos
                for stim in stims:
                    stim.draw()
                target.draw()
                if valid:
                    cursor.draw()
                flip = unit.win.flip()
                t = max(0.0,float(flip-first_flip))
                # A flip can dispatch focus/resize/leave events. Do not combine
                # an old valid cursor with the newer post-invalidation epoch.
                invalidated_during_flip = sample_epoch != state['epoch']
                valid = valid and state['valid'] and not invalidated_during_flip
                if not samples or t > samples[-1]['t']:
                    samples.append(dict(t=t, target_command_time=command_t, cursor_sample_time=cursor_t,
                                        target=list(commanded), cursor=pos if valid else None, valid=bool(valid),
                                        reason=None if valid else ('invalidation_during_flip' if invalidated_during_flip else state['reason'] or 'outside_surface'), epoch=state['epoch']))
                actual_elapsed = t
                if t >= used:
                    break
        finally:
            if watch_supported:
                handle.remove_handlers(**handlers)
            unit.win.mouseVisible = visible
    # Offset is a genuine blank flip; the final interval is clipped to used.
    unit.win.callOnFlip(unit._stamp_close)
    unit._emit_trigger(offset_trigger,when='flip',wait=False,name=f'{unit.label}_offset',meta={'kind':'offset'})
    offset_flip = unit.win.flip()
    metrics = evaluate_pursuit(samples,used,target_radius,max_gap_s)
    unit.set_state(**metrics, pursuit_samples=samples, actual_elapsed=actual_elapsed,
                   offset_flip_time=offset_flip, synthetic_input=bool(responder),
                   native_focus_watch_supported=watch_supported, aborted=aborted,
                   response=None, capture_status='recorded' if metrics['observed_duration'] > 0 else 'no_observation',
                   key_press=False, rt=None, response_time=None, completed=not aborted,
                   timeout_trigger=None, offset_trigger=offset_trigger)
    unit.log_unit()
    if aborted:
        raise KeyboardInterrupt('Pursuit aborted by Escape; phase remains logged')
    return unit
