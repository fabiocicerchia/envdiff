from envdiff import diff, looks_secret, main, mask, parse_env_text


def test_parse_handles_dotenv_quirks():
    env = parse_env_text('# comment\nexport FOO=bar\nBAZ="quoted"\n\nBROKEN_LINE\n')
    assert env == {"FOO": "bar", "BAZ": "quoted"}


def test_secret_detection_by_key_and_entropy():
    assert looks_secret("DB_PASSWORD", "hunter2")
    assert looks_secret("SOMETHING", "sk-9fXk2LmQ8vZt4Rw7Yb1NcE3H")  # high entropy
    assert not looks_secret("LOG_LEVEL", "debug")


def test_mask_is_stable_fingerprint():
    a = mask("API_TOKEN", "same-value-here-123")
    b = mask("API_TOKEN", "same-value-here-123")
    assert a == b and a.startswith("<masked:") and "same-value" not in a


def test_diff_and_ignore():
    a = {"A": "1", "B": "2", "HOSTNAME": "x"}
    b = {"A": "1", "B": "3", "C": "4", "HOSTNAME": "y"}
    added, removed, changed = diff(a, b, ignore=["HOSTNAME"])
    assert added == {"C": "4"} and removed == {} and changed == {"B": ("2", "3")}


def test_cli_fail_on_diff(tmp_path, capsys):
    left, right = tmp_path / "a.env", tmp_path / "b.env"
    left.write_text("X=1\n")
    right.write_text("X=2\n")
    assert main([str(left), str(right), "--fail-on-diff"]) == 1
    assert "~ X: 1 -> 2" in capsys.readouterr().out
