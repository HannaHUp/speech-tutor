"""REQ-02 - Session frozen-snapshot and prompt_builder tests."""


def test_build_user_turn_with_prosody_emits_fenced_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody(
        "I went to the park yesterday.",
        {
            "pace": "1.8 wps (slow)",
            "pitch": "rising_final (possible question intonation)",
            "hesitations": "1 (before \"yesterday\", 640ms)",
            "stress": "—",
        },
    )

    assert "```prosody" in out
    assert "pace: 1.8 wps (slow)" in out
    assert "stress: —" in out


def test_build_user_turn_without_prosody_omits_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody("Just text.", {})

    assert out == "Just text."
    assert "```prosody" not in out


def test_session_system_prompt_is_frozen(dummy_settings, tmp_path, monkeypatch):
    from server import prompt_builder
    from server.session import Session

    fake_soul = tmp_path / "SOUL.md"
    fake_soul.write_text("First persona", encoding="utf-8")
    monkeypatch.setattr(prompt_builder, "_SOUL_PATH", fake_soul)

    session = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    first = session.system_prompt
    fake_soul.write_text("Second persona", encoding="utf-8")

    assert session.system_prompt == first
    assert "First persona" in first


def test_session_append_user_includes_prosody(dummy_settings):
    from server.session import Session

    session = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    session.append_user(
        "Hello.",
        {"pace": "2.0 wps (normal)", "pitch": "flat", "hesitations": "0", "stress": "—"},
    )

    assert len(session.messages) == 1
    assert session.messages[0]["role"] == "user"
    assert "```prosody" in session.messages[0]["content"]


def test_session_messages_is_copy_not_internal_ref(dummy_settings):
    from server.session import Session

    session = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    session.append_user("Hi", {})
    external = session.messages
    external.append({"role": "user", "content": "injected"})

    assert len(session.messages) == 1
