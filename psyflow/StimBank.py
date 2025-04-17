from psychopy.visual import TextStim, Circle, Rect, Polygon, ImageStim
from psychopy import event
from typing import Callable, Dict, Any, Type, Optional
import yaml
import inspect

# Mapping string names in YAML to actual PsychoPy classes
STIM_CLASSES: Dict[str, Type] = {
    "text": TextStim,
    "circle": Circle,
    "rect": Rect,
    "polygon": Polygon,
    "image": ImageStim
}


class StimBank:
    """
    A hybrid stimulus registry system for PsychoPy.

    Allows users to:
    - Register stimuli manually via decorators (@registry.define("name"))
    - Load stimulus definitions from YAML configuration
    - Preload (instantiate) all stimuli at once
    - Retrieve, preview, or rebuild individual or grouped stimuli
    """

    def __init__(self, win):
        """
        Initialize the registry with a PsychoPy Window.
        """
        self.win = win
        self._registry: Dict[str, Callable[[Any], Any]] = {}
        self._instantiated: Dict[str, Any] = {}

    def define(self, name: str):
        """
        Register a stimulus using a decorator.

        Example:
        >>> @registry.define("fix")
        >>> def make_fix(win):
        >>>     return TextStim(win, text="+")
        """
        def decorator(func: Callable[[Any], Any]):
            self._registry[name] = func
            return func
        return decorator

    def build_all(self):
        """
        Instantiate all registered stimuli.
        """
        for name, factory in self._registry.items():
            if name not in self._instantiated:
                self._instantiated[name] = factory(self.win)

    def preload_all(self):
        """
        Alias for build_all(). Intention is clearer for experiment setup.
        """
        self.build_all()

    def get(self, name: str):
        """
        Return an instantiated stimulus (lazy-loaded if needed).
        """
        if name not in self._instantiated:
            if name not in self._registry:
                raise KeyError(f"Stimulus '{name}' not defined.")
            self._instantiated[name] = self._registry[name](self.win)
        return self._instantiated[name]

   
    def get_and_format(self, name: str, **format_kwargs) -> TextStim:
        """
        Return a fresh TextStim with formatted text.
        All other attributes are copied from the original.
        """
        original = self.get(name)

        if not isinstance(original, TextStim):
            raise TypeError(f"Stimulus '{name}' is not a TextStim.")

        # Get __init__ argument names (excluding 'self' and 'win')
        sig = inspect.signature(TextStim.__init__)
        valid_args = {k for k in sig.parameters if k not in ('self', 'win')}

        copied_kwargs = {
            k: original.__dict__[k]
            for k in valid_args
            if k in original.__dict__
        }

        copied_kwargs["text"] = original.text.format(**format_kwargs)

        return TextStim(win=self.win, **copied_kwargs)

    def rebuild(self, name: str, update_cache: bool = True, **overrides):
        """
        Rebuild a stimulus with new parameters.

        Parameters:
        - name: stimulus name
        - update_cache: if True, replace the cached instance with the rebuilt one
        - **overrides: keyword arguments to override default parameters

        Returns:
        - The new stimulus instance
        """
        if name not in self._registry:
            raise KeyError(f"Stimulus '{name}' not defined.")

        new_stim = self._registry[name](self.win, **overrides)

        if update_cache:
            self._instantiated[name] = new_stim

        return new_stim

    def get_group(self, prefix: str) -> Dict[str, Any]:
        """
        Get all stimuli starting with a prefix as a dictionary.
        """
        return {k: self.get(k) for k in self._registry if k.startswith(prefix)}

    def get_selected(self, keys: list[str]) -> Dict[str, Any]:
        """
        Get a selected list of stimuli by name as a dictionary.
        """
        return {k: self.get(k) for k in keys}

    def preview_all(self, wait_keys: bool = True):
        """
        Preview all registered stimuli.
        """
        keys = list(self._registry.keys())
        for i, name in enumerate(keys):
            self._preview(name, wait_keys=(i == len(keys) - 1))

    def preview_group(self, prefix: str, wait_keys: bool = True):
        """
        Preview stimuli whose names start with a prefix.
        """
        matches = [k for k in self._registry if k.startswith(prefix)]
        if not matches:
            print(f"No stimuli found starting with '{prefix}'")
        for i, name in enumerate(matches):
                self._preview(name, wait_keys=(i == len(matches) - 1))

    def preview_selected(self, keys: list[str], wait_keys: bool = True):
        """
        Preview a selected list of stimuli by name.
        """
        for i, name in enumerate(keys):
            self._preview(name, wait_keys=(i == len(keys) - 1))

    def _preview(self, name: str, wait_keys: bool = True):
        """
        Internal helper to preview a stimulus by name.
        """
        try:
            stim = self.get(name)
            self.win.flip(clearBuffer=True)
            stim.draw()
            self.win.flip()
            print(f"Preview: '{name}'")
            if not wait_keys:
                event.waitKeys()
        except Exception as e:
            print(f"[Preview Error] Could not preview '{name}': {e}")

    def keys(self):
        """
        Return a list of all registered stimulus keys.
        """
        return list(self._registry.keys())
    

    def has(self, name: str) -> bool:
        """Check whether a stimulus is registered (defined)."""
        return name in self._registry


    def describe(self, name: str):
        """
        Print the accepted and required arguments for the given stimulus type.
        """
        if name not in self._registry:
            print(f"❌ No such stimulus: {name}")
            return

        # Try to resolve the constructor
        try:
            stim = self.get(name)
            cls = type(stim)
        except Exception:
            # fallback to stim class if YAML-based
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
        Save all YAML-defined stimuli to a file (if originally loaded from YAML).
        Does NOT include @define-registered stimuli.
        """
        yaml_defs = {}
        for name, factory in self._registry.items():
            try:
                source = factory.__closure__[0].cell_contents  # dict from make_factory()
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
        Create a stimulus factory with support for dynamic overrides at call time.

        Parameters:
        - cls: the PsychoPy stimulus class (e.g., TextStim, Circle)
        - base_kwargs: default arguments to use
        - name: for error messages

        Returns:
        - a callable factory(win, **overrides)
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
        Add stimulus definitions from a dictionary.

        Parameters
        ----------
        named_specs : dict, optional
            A dictionary of stimulus definitions.
        kwargs :
            Alternatively, pass stimulus definitions as keyword arguments.
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
        Validate a dictionary of stimulus definitions for compatibility.

        Parameters:
        - config: dictionary containing stimulus definitions
        - strict: if True, raises ValueError on issues (default: False = just print warnings)
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

