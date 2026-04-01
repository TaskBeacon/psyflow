"""Tests for psyflow.sim.loader — responder resolution and import helpers."""

import unittest

from psyflow.sim.loader import _deep_get, _import_attr, _resolve_spec


class TestDeepGet(unittest.TestCase):
    """_deep_get() nested dictionary traversal."""

    def test_single_key(self):
        self.assertEqual(_deep_get({"a": 1}, ("a",)), 1)

    def test_nested_keys(self):
        self.assertEqual(_deep_get({"a": {"b": {"c": 3}}}, ("a", "b", "c")), 3)

    def test_missing_key_returns_default(self):
        self.assertIsNone(_deep_get({"a": 1}, ("x",)))
        self.assertEqual(_deep_get({"a": 1}, ("x",), "fallback"), "fallback")

    def test_none_mapping(self):
        self.assertEqual(_deep_get(None, ("a",), "d"), "d")

    def test_non_dict_intermediate(self):
        self.assertEqual(_deep_get({"a": 42}, ("a", "b"), "d"), "d")


class TestImportAttr(unittest.TestCase):
    """_import_attr() dynamic import from dotted or colon-separated paths."""

    def test_colon_syntax(self):
        cls = _import_attr("collections:OrderedDict")
        from collections import OrderedDict
        self.assertIs(cls, OrderedDict)

    def test_dot_syntax(self):
        cls = _import_attr("collections.OrderedDict")
        from collections import OrderedDict
        self.assertIs(cls, OrderedDict)

    def test_invalid_module_raises(self):
        with self.assertRaises(ModuleNotFoundError):
            _import_attr("nonexistent_module_xyz:Foo")


class TestResolveSpec(unittest.TestCase):
    """_resolve_spec() config → (type, kwargs, source) resolution."""

    def test_human_mode_returns_none(self):
        spec, kwargs, source = _resolve_spec("human", {})
        self.assertIsNone(spec)
        self.assertEqual(source, "disabled")

    def test_default_is_scripted(self):
        spec, kwargs, source = _resolve_spec("sim", {})
        self.assertEqual(spec, "scripted")
        self.assertEqual(source, "default")

    def test_config_type_used(self):
        cfg = {"responder": {"type": "my_module:MyResponder", "kwargs": {"rt": 0.5}}}
        spec, kwargs, source = _resolve_spec("qa", cfg)
        self.assertEqual(spec, "my_module:MyResponder")
        self.assertEqual(kwargs, {"rt": 0.5})
        self.assertEqual(source, "config.type")

    def test_empty_type_falls_back_to_scripted(self):
        cfg = {"responder": {"type": "  "}}
        spec, kwargs, source = _resolve_spec("sim", cfg)
        self.assertEqual(spec, "scripted")

    def test_non_dict_responder_ignored(self):
        cfg = {"responder": "not_a_dict"}
        spec, kwargs, source = _resolve_spec("sim", cfg)
        self.assertEqual(spec, "scripted")


if __name__ == "__main__":
    unittest.main()
