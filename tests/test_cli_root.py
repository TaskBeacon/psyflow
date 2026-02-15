import unittest

from click.testing import CliRunner


class TestRootCLI(unittest.TestCase):
    def test_root_help_lists_subcommands(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["--help"])
        self.assertEqual(res.exit_code, 0, msg=res.output)
        self.assertIn("init", res.output)
        self.assertIn("qa", res.output)
        self.assertIn("sim", res.output)

    def test_qa_help_from_root(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["qa", "--help"])
        self.assertEqual(res.exit_code, 0, msg=res.output)
        self.assertIn("--runtime-cmd", res.output)

    def test_sim_help_from_root(self):
        from psyflow.cli import main

        runner = CliRunner()
        res = runner.invoke(main, ["sim", "--help"])
        self.assertEqual(res.exit_code, 0, msg=res.output)
        self.assertIn("--seed", res.output)


if __name__ == "__main__":
    unittest.main()

