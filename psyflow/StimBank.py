from psychopy.visual import TextStim, Circle, Rect, Polygon, ImageStim, ShapeStim, TextBox2, MovieStim
from psychopy import event
from typing import Callable, Dict, Any, Type, Optional
import yaml
import inspect

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
}


class StimBank:
    """
    A hybrid stimulus management system for PsychoPy experiments.

    `StimBank` supports:
    - Manual registration of stimuli via decorators (@registry.define("name"))
    - Loading stimuli from YAML or Python dictionaries
    - Centralized retrieval, lazy instantiation, and batch preview
    """

    def __init__(self, win):
        """
        Initialize the stimulus bank with a PsychoPy Window.

        Parameters
        ----------
        win : psychopy.visual.Window
            The window object used to instantiate visual stimuli.
        """
        self.win = win
        self._registry: Dict[str, Callable[[Any], Any]] = {}
        self._instantiated: Dict[str, Any] = {}

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

    def build_all(self):
        """
        Instantiate all registered stimuli and cache them internally.
        """
        for name, factory in self._registry.items():
            if name not in self._instantiated:
                self._instantiated[name] = factory(self.win)

    def preload_all(self):
        """
        Alias for `build_all()`, used to clarify preload intent in experiment setup.
        """
        self.build_all()

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

    # def get_and_format(self, name: str, **format_kwargs) -> TextStim:
    #     """
    #     Return a fresh TextStim with formatted text, keeping other properties unchanged.

    #     Parameters
    #     ----------
    #     name : str
    #         Name of the registered TextStim.
    #     **format_kwargs
    #         Formatting variables to apply to the `text` field.

    #     Returns
    #     -------
    #     TextStim
    #         A new TextStim object with formatted content.

    #     Raises
    #     ------
    #     TypeError
    #         If the stimulus is not a TextStim.
    #     """
    #     original = self.get(name)
    #     if not isinstance(original, TextStim):
    #         raise TypeError(f"Stimulus '{name}' is not a TextStim.")

    #     sig = inspect.signature(TextStim.__init__)
    #     valid_args = {k for k in sig.parameters if k not in ('self', 'win')}

    #     copied_kwargs = {
    #         k: original.__dict__[k]
    #         for k in valid_args
    #         if k in original.__dict__
    #     }

    #     copied_kwargs["text"] = original.text.format(**format_kwargs)
    #     return TextStim(win=self.win, **copied_kwargs)


    def get_and_format(self, name: str, **format_kwargs):
        """
        Return a fresh TextStim or TextBox2 with formatted text, keeping other properties unchanged.

        Parameters
        ----------
        name : str
            Name of the registered stimulus.
        **format_kwargs
            Formatting variables to apply to the `text` field.

        Returns
        -------
        TextStim or TextBox2
            A new formatted visual text stimulus.

        Raises
        ------
        TypeError
            If the stimulus is not a supported text type.
        """
        original = self.get(name)

        if isinstance(original, TextStim):
            cls = TextStim
        elif isinstance(original, TextBox2):
            cls = TextBox2
        else:
            raise TypeError(f"Stimulus '{name}' is not a supported text type (TextStim/TextBox2).")

        sig = inspect.signature(cls.__init__)
        valid_args = {k for k in sig.parameters if k not in ('self', 'win')}

        copied_kwargs = {
            k: getattr(original, k)
            for k in valid_args
            if hasattr(original, k)
        }

        copied_kwargs["text"] = original.text.format(**format_kwargs)
        return cls(win=self.win, **copied_kwargs)
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

    def _preview(self, name: str, wait_keys: bool = True):
        """
        Internal utility to preview a single stimulus.

        Parameters
        ----------
        name : str
            Stimulus name.
        wait_keys : bool
            Wait for key press after preview.
        """
        try:
            stim = self.get(name)
            self.win.flip(clearBuffer=True)
            stim.draw()
            self.win.flip()
            print(f"Preview: '{name}'")
            if wait_keys:
                event.waitKeys()
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
