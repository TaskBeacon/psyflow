import unittest

from click.testing import CliRunner


class TestRootCLI(unittest.TestCase):
    def test_root_help_lists_subcommands(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["--help"])
        self.assertEqual(res.exit_code, 0, msg=res.output)
        self.assertIn("init", res.output)
        self.assertNotIn("qa", res.output)
        self.assertNotIn("sim", res.output)

    def test_qa_not_available_from_root(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["qa"])
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("No such command", res.output)

    def test_sim_not_available_from_root(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["sim"])
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("No such command", res.output)


if __name__ == "__main__":
    unittest.main()
