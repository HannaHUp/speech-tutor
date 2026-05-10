"""REQ-02 - Session frozen-snapshot and prompt_builder tests."""
import pytest


@pytest.mark.skip(reason="W0 stub - implemented in Plan 05 (Session + prompt_builder)")
def test_build_user_turn_with_prosody_emits_fenced_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody(
        "Hi",
        {
            "pace": "2.0 wps (normal)",
            "pitch": "flat",
            "hesitations": "0",
            "stress": "-",
        },
    )
    assert "```prosody" in out


@pytest.mark.skip(reason="W0 stub - implemented in Plan 05")
def test_build_user_turn_without_prosody_omits_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody("Just text.", {})
    assert out == "Just text."
    assert "```prosody" not in out


@pytest.mark.skip(reason="W0 stub - implemented in Plan 05")
def test_session_system_prompt_is_frozen(dummy_settings):
    from server.session import Session

    s = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    first = s.system_prompt
    second = s.system_prompt
    assert first == second
