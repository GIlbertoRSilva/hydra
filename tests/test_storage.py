from hydra.domain.models import HydraState, PaneConfig, SessionConfig
from hydra.infrastructure.storage import SessionStore


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "sessions.json"
    store = SessionStore(path)
    session = SessionConfig(
        "Trabalho",
        "2x2",
        [PaneConfig("GitHub", "https://github.com", "trab", 60, True)],
    )
    state = HydraState([session], active_session_id=session.id)
    store.save(state)
    loaded = store.load()

    assert loaded.active_session_id == session.id
    assert loaded.sessions[0].name == "Trabalho"
    assert loaded.sessions[0].panes[0].profile == "trab"
    assert loaded.sessions[0].panes[0].auto_reload_s == 60
    assert loaded.sessions[0].panes[0].mute is True


def test_legacy_payload_without_ids_is_migrated(tmp_path):
    path = tmp_path / "sessions.json"
    path.write_text(
        '{"sessions":[{"name":"Social","emoji":"🌙","layout":"2x3","panes":[{"name":"X","url":"https://x.com","profile":"conta_1"}]}]}',
        encoding="utf-8",
    )
    loaded = SessionStore(path).load()
    assert loaded.sessions[0].name == "Social"
    assert loaded.sessions[0].panes[0].profile == "conta_1"
    assert loaded.sessions[0].id
    assert loaded.sessions[0].panes[0].id


def test_corrupted_file_falls_back_to_backup(tmp_path):
    path = tmp_path / "sessions.json"
    backup = tmp_path / "sessions.json.bak"
    backup.write_text(
        '{"sessions":[{"name":"Backup","layout":"1x1","panes":[]}]}',
        encoding="utf-8",
    )
    path.write_text("not-json", encoding="utf-8")
    loaded = SessionStore(path, backup).load()
    assert loaded.sessions[0].name == "Backup"


def test_corrupted_files_fall_back_to_default(tmp_path):
    path = tmp_path / "sessions.json"
    path.write_text("not-json", encoding="utf-8")
    loaded = SessionStore(path).load()
    assert loaded.sessions[0].name == "Social"
