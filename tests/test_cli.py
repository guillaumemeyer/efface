from efface.cli import main


def test_smoke_passes(capsys):
    assert main(["smoke"]) == 0
    assert "smoke: ok" in capsys.readouterr().out


def test_unimplemented_command_exits_two(capsys):
    assert main(["generate"]) == 2
    assert "not implemented" in capsys.readouterr().err
