from hydra.domain.models import HydraState, PaneConfig, SessionConfig, default_session


def test_default_session_matches_product_contract():
    session = default_session()
    assert session.name == "Social"
    assert session.layout == "2x3"
    assert len(session.panes) == 5
    assert session.panes[0].profile == "conta_1"


def test_state_guarantees_active_session():
    session = SessionConfig("Teste")
    state = HydraState([session])
    state.ensure_valid()
    assert state.active_session_id == session.id


def test_state_recovers_from_missing_sessions():
    state = HydraState([])
    state.ensure_valid()
    assert len(state.sessions) == 1
    assert state.active_session_id == state.sessions[0].id


def test_pane_clone_has_new_identity():
    pane = PaneConfig("X", "https://x.com", "perfil")
    clone = pane.clone()
    assert clone.id != pane.id
    assert clone.profile == pane.profile
