from pathlib import Path

from efface.config import digest, load, load_all

CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"


def test_all_configs_load():
    configs = load_all(CONFIG_DIR)
    assert set(configs) == {"generators", "attackers", "tactics", "search", "metrics"}


def test_search_config_matches_preregistration():
    search = load(CONFIG_DIR / "search.yaml")
    assert search["beam_width"] == 8
    assert search["max_depth"] == 3
    assert search["semantic_floor"] == 0.80
    assert search["split_seed"] == 20261117


def test_digest_is_stable():
    path = CONFIG_DIR / "search.yaml"
    assert digest(path) == digest(path)
    assert len(digest(path)) == 64


def test_attacker_roles_and_ablation():
    attackers = load(CONFIG_DIR / "attackers.yaml")
    assert set(attackers["attackers"]) == {"deepseek_flash", "sonnet"}
    assert attackers["roles"]["paraphrase"] == "deepseek_flash"
    assert attackers["roles"]["translation"] == "deepseek_flash"
    assert attackers["roles"]["infill"]["local"] is True
    assert attackers["ablation"]["attacker"] == "sonnet"
    assert attackers["ablation"]["top_chains"] == 5


def test_non_mapping_is_rejected(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")
    try:
        load(path)
    except ValueError as error:
        assert "mapping" in str(error)
    else:
        raise AssertionError("expected ValueError")
