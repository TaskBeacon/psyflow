from psychopy.visual import TextStim, Circle, Rect, Polygon, ImageStim, ShapeStim, TextBox2, MovieStim
from psychopy import event, core

# set this if sounddevice is not working
# from psychopy import prefs 
# prefs.hardware['audioLib'] = ['pyo', 'pygame']
import asyncio
import edge_tts
from psychopy.sound import Sound
from typing import Callable, Dict, Any, Type, Optional
import yaml
import inspect
import os

# Mapping string names in YAML to actual PsychoPy classes
STIM_CLASSES: Dict[str, Type] = {
    "text": TextStim,
    "textbox": TextBox2,
    "circle": Circle,
    "rect": Rect,
    "polygon": Polygon,
    "image": ImageStim,
    "shape": ShapeStim,
    "movie": MovieStim, 
    "sound": Sound,
}


class StimBank:
    """
    A hybrid stimulus management system for PsychoPy experiments.

    `StimBank` supports:
    - Manual registration of stimuli via decorators (@registry.define("name"))
    - Loading stimuli from YAML or Python dictionaries
    - Centralized retrieval, lazy instantiation, and batch preview
    """

    def __init__(self, win, config: Optional[dict] = None):
        """
        Initialize the stimulus bank with a PsychoPy Window.

        Parameters
        ----------
        win : psychopy.visual.Window
            The window object used to instantiate visual stimuli.
        config : dict, optional
            Dictionary of stimuli to load at initialization.
        """
        self.win = win
        self._registry: Dict[str, Callable[[Any], Any]] = {}
        self._instantiated: Dict[str, Any] = {}
        if config:
            self.add_from_dict(config)

    def define(self, name: str):
        """
        Register a stimulus generator function using a decorator.

        Parameters
        ----------
        name : str
            Name to register the stimulus under.

        Returns
        -------
        Callable
            A decorator to wrap the stimulus function.
        """
        def decorator(func: Callable[[Any], Any]):
            self._registry[name] = func
            return func
        return decorator

    def preload_all(self):
        """Instantiate all registered stimuli.

        Returns
        -------
        StimBank
            The object itself for method chaining.
        """
        for name, factory in self._registry.items():
            if name not in self._instantiated:
                self._instantiated[name] = factory(self.win)
        return self

    def get(self, name: str):
        """
        Get a stimulus by name, instantiating it if needed.

        Parameters
        ----------
        name : str
            Registered stimulus name.

        Returns
        -------
        Any
            Instantiated PsychoPy stimulus object.

        Raises
        ------
        KeyError
            If the stimulus is not registered.
        """
        if name not in self._instantiated:
            if name not in self._registry:
                raise KeyError(f"Stimulus '{name}' not defined.")
            self._instantiated[name] = self._registry[name](self.win)
        return self._instantiated[name]

    def get_and_format(self, name: str, **format_kwargs):
        """
        Return a fresh TextStim or TextBox2 with formatted text, keeping other properties unchanged.

        Parameters
        ----------
        name : str
            Name of the registered stimulus (TextStim or TextBox2).
        **format_kwargs
            Formatting variables to apply to the `text` field.

        Returns
        -------
           TextStim or TextBox2
            A new formatted visual text stimulus.
        Raises
        ------
        TypeError
            If the stimulus is not a TextStim.
        """
        original = self.get(name)
        if  isinstance(original, TextStim):
            sig = inspect.signature(TextStim.__init__)
            valid_args = {k for k in sig.parameters if k not in ('self', 'win')}

            copied_kwargs = {
                k: original.__dict__[k]
                for k in valid_args
                if k in original.__dict__
            }

            copied_kwargs["text"] = original.text.format(**format_kwargs)
            return TextStim(win=self.win, **copied_kwargs)
        elif isinstance(original, TextBox2):
            sig = inspect.signature(TextBox2.__init__)
            valid_args = {k for k in sig.parameters if k not in ('self', 'win')}

            copied_kwargs = {
                k: original.__dict__[k]
                for k in valid_args
                if k in original.__dict__
            }

            copied_kwargs["text"] = original.text.format(**format_kwargs)
            return TextBox2(win=self.win, **copied_kwargs)
        else:
            raise TypeError(f"Stimulus '{name}' is not a supported text type (TextStim/TextBox2).")
    

    def rebuild(self, name: str, update_cache: bool = False, **overrides):
        """
        Rebuild a stimulus with optional updated parameters.

        Parameters
        ----------
        name : str
            Registered stimulus name.
        update_cache : bool
            Whether to overwrite the existing cached version.
        **overrides : dict
            New keyword arguments to override the original parameters.

        Returns
        -------
        Any
            A fresh stimulus object.
        """
        if name not in self._registry:
            raise KeyError(f"Stimulus '{name}' not defined.")

        new_stim = self._registry[name](self.win, **overrides)

        if update_cache:
            self._instantiated[name] = new_stim

        return new_stim

    def get_group(self, prefix: str) -> Dict[str, Any]:
        """
        Retrieve a dictionary of stimuli whose names start with a given prefix.

        Parameters
        ----------
        prefix : str
            Common prefix to match.

        Returns
        -------
        dict
            A dictionary of {name: stimulus} pairs.
        """
        return {k: self.get(k) for k in self._registry if k.startswith(prefix)}

    def get_selected(self, keys: list[str]) -> Dict[str, Any]:
        """
        Retrieve a subset of named stimuli.

        Parameters
        ----------
        keys : list of str
            List of stimulus names to retrieve.

        Returns
        -------
        dict
            A dictionary of {name: stimulus} pairs.
        """
        return {k: self.get(k) for k in keys}

    def preview_all(self, wait_keys: bool = True):
        """
        Preview all registered stimuli one by one.

        Parameters
        ----------
        wait_keys : bool
            Wait for key press after last stimulus.
        """
        keys = list(self._registry.keys())
        for i, name in enumerate(keys):
            self._preview(name, wait_keys=wait_keys)

    def preview_group(self, prefix: str, wait_keys: bool = True):
        """
        Preview all stimuli that match a name prefix.

        Parameters
        ----------
        prefix : str
            Prefix string to filter stimuli.
        wait_keys : bool
            Wait for key press after final stimulus.
        """
        matches = [k for k in self._registry if k.startswith(prefix)]
        if not matches:
            print(f"No stimuli found starting with '{prefix}'")
        for i, name in enumerate(matches):
            self._preview(name, wait_keys=(i == len(matches) - 1))

    def preview_selected(self, keys: list[str], wait_keys: bool = True):
        """
        Preview selected stimuli by name.

        Parameters
        ----------
        keys : list of str
            Stimulus names to preview.
        wait_keys : bool
            Wait for key press after final stimulus.
        """
        for i, name in enumerate(keys):
            self._preview(name, wait_keys=(i == len(keys) - 1))

    # def _preview(self, name: str, wait_keys: bool = True):
    #     """
    #     Internal utility to preview a single stimulus.

    #     Parameters
    #     ----------
    #     name : str
    #         Stimulus name.
    #     wait_keys : bool
    #         Wait for key press after preview.
    #     """
    #     try:
    #         stim = self.get(name)
    #         self.win.flip(clearBuffer=True)
    #         stim.draw()
    #         self.win.flip()
    #         print(f"Preview: '{name}'")
    #         if wait_keys:
    #             event.waitKeys()
    #     except Exception as e:
    #         print(f"[Preview Error] Could not preview '{name}': {e}")

    def _preview(self, name: str, wait_keys: bool = True):
        """
        Internal utility to preview a single stimulus (image or sound).

        Parameters
        ----------
        name : str
            Stimulus name.
        wait_keys : bool
            Wait for key press after preview (only for visual).
        """
        try:
            stim = self.get(name)
            self.win.flip(clearBuffer=True)

            if hasattr(stim, "draw") and callable(stim.draw):
                stim.draw()
                self.win.flip()
                print(f"Preview (visual): '{name}'")
                if wait_keys:
                    event.waitKeys()
            elif hasattr(stim, "play") and callable(stim.play):
                stim.play()
                print(f"Preview (sound): '{name}'")
                core.wait(stim.getDuration())  # wait for playback to finish
                stim.stop()
                del stim  # important! immediately free stream after play
            else:
                print(f"[Preview Warning] Stimulus '{name}' is neither drawable nor playable.")
        except Exception as e:
            print(f"[Preview Error] Could not preview '{name}': {e}")


    def keys(self) -> list[str]:
        """
        List all registered stimulus names.

        Returns
        -------
        list of str
        """
        return list(self._registry.keys())

    def has(self, name: str) -> bool:
        """
        Check whether a stimulus is registered.

        Parameters
        ----------
        name : str

        Returns
        -------
        bool
        """
        return name in self._registry

    def describe(self, name: str):
        """
        Print accepted arguments for a registered stimulus.

        Parameters
        ----------
        name : str
            Name of the stimulus to describe.
        """
        if name not in self._registry:
            print(f"❌ No such stimulus: {name}")
            return

        try:
            stim = self.get(name)
            cls = type(stim)
        except Exception:
            for prefix in STIM_CLASSES:
                if prefix in name:
                    cls = STIM_CLASSES[prefix]
                    break
            else:
                print(f"Could not infer class for '{name}'")
                return

        sig = inspect.signature(cls.__init__)
        params = {k: v for k, v in sig.parameters.items() if k not in ('self', 'win')}

        print(f"🧾 Description of '{name}' ({cls.__name__})")
        for k, v in params.items():
            default = "required" if v.default is inspect.Parameter.empty else f"default={v.default!r}"
            print(f"  - {k}: {default}")

    def export_to_yaml(self, path: str):
        """
        Export YAML-defined stimuli (but not decorator-defined) to file.

        Parameters
        ----------
        path : str
            Path to save the YAML file.
        """
        yaml_defs = {}
        for name, factory in self._registry.items():
            try:
                source = factory.__closure__[0].cell_contents
                if not isinstance(source, dict):
                    continue
                yaml_defs[name] = source
            except Exception:
                continue

        with open(path, 'w') as f:
            yaml.dump(yaml_defs, f)
        print(f"✅ Exported {len(yaml_defs)} YAML stimuli to {path}")

    def make_factory(self, cls, base_kwargs: dict, name: str):
        """
        Create a factory function for a given stimulus class.

        Parameters
        ----------
        cls : type
            PsychoPy stimulus class (e.g., TextStim).
        base_kwargs : dict
            Default keyword arguments.
        name : str
            Stimulus name (used for error messages).

        Returns
        -------
        Callable
            A factory function that accepts (win, **overrides)
        """
        def _factory(win, **override_kwargs):
            try:
                merged = dict(base_kwargs)
                merged.update(override_kwargs)

                # Special case for sound: pass file/filename as positional value
                if cls.__name__.lower().startswith("sound"):
                    file_value = merged.pop("file")  # remove 'file' from kwargs
                    return cls(file_value, **merged) 

                return cls(win, **merged)
            except Exception as e:
                raise ValueError(f"[StimBank] Failed to build '{name}': {e}")
        return _factory

    def add_from_dict(self, named_specs: Optional[dict] = None, **kwargs):
        """
        Add stimuli from a dictionary or keyword-based specifications.

        Parameters
        ----------
        named_specs : dict, optional
            Dictionary where keys are stimulus names and values are stimulus specs.
        kwargs : dict
            Additional stimuli as keyword-based name=spec entries.
        """
        all_specs = {}
        if named_specs:
            all_specs.update(named_specs)
        all_specs.update(kwargs)

        for name, spec in all_specs.items():
            stim_type = spec.get("type")
            stim_class = STIM_CLASSES.get(stim_type)
            if not stim_class:
                raise ValueError(f"[StimBank] Unknown stim type '{stim_type}' in '{name}'")

            kwargs = {k: v for k, v in spec.items() if k != "type"}
            self._registry[name] = self.make_factory(stim_class, kwargs, name)
        return self

    def validate_dict(self, config: dict, strict: bool = False):
        """
        Validate a dictionary of stimulus definitions.

        Parameters
        ----------
        config : dict
            Dictionary of stimulus specs.
        strict : bool
            If True, raise errors; otherwise print warnings only.
        """
        print(f"\n🔍 Validating stimulus dictionary\n{'-' * 40}")

        for name, spec in config.items():
            stim_type = spec.get("type")
            if stim_type not in STIM_CLASSES:
                msg = f"❌ [{name}] Unsupported type '{stim_type}'"
                if strict:
                    raise ValueError(msg)
                print(msg)
                continue

            stim_class = STIM_CLASSES[stim_type]
            kwargs = {k: v for k, v in spec.items() if k != "type"}

            sig = inspect.signature(stim_class.__init__)
            params = sig.parameters
            accepted = {k for k in params if k not in ('self', 'win')}
            required = {
                k for k, v in params.items()
                if k not in ('self', 'win') and v.default is inspect.Parameter.empty
            }

            unknown_args = [k for k in kwargs if k not in accepted]
            missing_args = [k for k in required if k not in kwargs]

            if unknown_args:
                msg = f"⚠️ [{name}] Unknown arguments: {unknown_args}"
                if strict:
                    raise ValueError(msg)
                print(msg)
            if missing_args:
                msg = f"⚠️ [{name}] Missing required arguments: {missing_args}"
                if strict:
                    raise ValueError(msg)
                print(msg)
            if not unknown_args and not missing_args:
                print(f"✅ [{name}] OK")



    def convert_to_voice(self,
                         keys: list[str] | str,
                         overwrite: bool = False,
                         voice: str = "zh-CN-YunyangNeural"):
        """
        Convert specified TextStim/TextBox2 stimuli to speech (MP3) and register them
        as new Sound stimuli in this StimBank.

        Parameters
        ----------
        keys : list[str]
            List of registered stimulus names to convert.
        overwrite : bool
            If True, overwrite existing MP3 files (default False).
        voice : str
            Name of the TTS voice to use (default 'zh-CN-YunyangNeural').
            edge-tts --list-voices
        """
        if isinstance(keys, str):
            keys = [keys]
        assets_dir = "assets"
        # create the assets folder only if it doesn't already exist
        if not os.path.isdir(assets_dir):
            os.mkdir(assets_dir)

        for key in keys:
            # try to retrieve the registered stimulus
            try:
                stim = self.get(key)
            except KeyError:
                print(f"[Error] Stimulus '{key}' is not defined. Skipping.")
                continue

            # only convert if the stimulus has a .text attribute
            text = getattr(stim, "text", None)
            if not isinstance(text, str):
                print(f"[Warning] '{key}' has no text property. Skipping.")
                continue

            # determine output MP3 path
            mp3_filename = f"{key}_voice.mp3"
            mp3_path = os.path.join(assets_dir, mp3_filename)

            if os.path.isfile(mp3_path) and not overwrite:
                print(f"[Info] '{mp3_filename}' exists and overwrite=False. Skipping generation.")
            else:
                print(f"[Info] Generating TTS for '{key}' → '{mp3_filename}' …")

                async def _generate():
                    await edge_tts.Communicate(text=text, voice=voice).save(mp3_path)

                try:
                    # run the async TTS generation
                    asyncio.run(_generate())
                except Exception as e:
                    print(f"[Error] Failed to generate speech for '{key}': {e}")
                    print("Possible reasons:")
                    print(" • No internet connection or unstable network")
                    print(" • HTTPS proxies not supported by edge-tts")
                    print(" • Incorrect or unsupported voice name")
                    print(" • edge-tts not installed or version mismatch")
                    continue

            # register the new MP3 as a Sound stimulus
            self._registry[f"{key}_voice"] = lambda win, p=mp3_path: Sound(p)
            # clear any cached instance so get() picks up the new Sound
            self._instantiated.pop(f"{key}_voice", None)
            print(f"[Success] Registered new stimulus '{key}_voice'")
        return self


    def add_voice(self,
                  stim_label: str,
                  text: str,
                  overwrite: bool = False,
                  voice: str = "zh-CN-XiaoxiaoNeural"):
        """
        Convert arbitrary text to speech (MP3) and register it as a new Sound stimulus.

        Parameters
        ----------
        stim_label : str
            The name under which to register the new voice stimulus, 
            and the base filename for the MP3 (e.g. 'welcome_voice' → 'assets/welcome_voice.mp3').
        text : str
            The text to synthesize.
        overwrite : bool
            If True, overwrite an existing MP3 file. Default is False.
        voice : str
            The TTS voice to use (default "zh-CN-XiaoxiaoNeural").
            edge-tts --list-voices
        """
        # 1. Ensure the assets directory exists
        assets_dir = "assets"
        if not os.path.isdir(assets_dir):
            os.mkdir(assets_dir)

        # 2. Build the full path for the MP3
        mp3_filename = f"{stim_label}.mp3"
        mp3_path = os.path.join(assets_dir, mp3_filename)

        # 3. Synthesize if needed
        if os.path.isfile(mp3_path) and not overwrite:
            print(f"[Info] '{mp3_filename}' already exists (overwrite=False). Skipping synthesis.")
        else:
            print(f"[Info] Generating TTS for '{stim_label}' → '{mp3_filename}' …")

            async def _generate():
                await edge_tts.Communicate(text=text, voice=voice).save(mp3_path)

            try:
                asyncio.run(_generate())
            except Exception as e:
                print(f"[Error] Failed to generate speech for '{stim_label}': {e}")
                print("Possible reasons:")
                print(" • No internet connection or unstable network")
                print(" • HTTPS proxies not supported by edge-tts")
                print(" • Incorrect or unsupported voice name")
                print(" • edge-tts not installed or version mismatch")
                return

        # 4. Register the new MP3 as a Sound stimulus
        self._registry[stim_label] = lambda win, p=mp3_path: Sound(p)
        # 5. Clear any cached instance so future get() returns the new Sound
        self._instantiated.pop(stim_label, None)

        print(f"[Success] Registered new voice stimulus '{stim_label}'")

        return self