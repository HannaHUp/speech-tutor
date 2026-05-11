"""REQ-02 - Session frozen-snapshot and prompt_builder tests."""


def test_build_user_turn_with_prosody_emits_fenced_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody(
        "I went to the park yesterday.",
        {
            "pace": "1.8 wps (slow)",
            "pitch": "rising_final (possible question intonation)",
            "hesitations": '1 (before "yesterday", 640ms)',
            "stress": "-",
        },
    )

    assert "```prosody" in out
    assert "pace: 1.8 wps (slow)" in out
    assert "stress: -" in out


def test_build_user_turn_without_prosody_omits_block(dummy_settings):
    from server.prompt_builder import build_user_turn_with_prosody

    out = build_user_turn_with_prosody("Just text.", {})

    assert out == "Just text."
    assert "```prosody" not in out


def test_user_turn_context_preserves_raw_and_edited_text_for_future_audit():
    from server.prompt_builder import UserTurnContext

    turn = UserTurnContext.from_voice(
        edited_text="I went to school yesterday.",
        stt_text="I go to school yesterday.",
        prosody={"pace": "slow", "pitch": "flat"},
    )

    assert turn.source == "voice"
    assert turn.edited_text == "I went to school yesterday."
    assert turn.stt_text == "I go to school yesterday."
    assert turn.to_llm_content().startswith("I went to school yesterday.")
    assert "```prosody" in turn.to_llm_content()


def test_user_turn_context_text_input_has_no_stt_or_prosody():
    from server.prompt_builder import UserTurnContext

    turn = UserTurnContext.from_text("Typed practice sentence.")

    assert turn.source == "text"
    assert turn.stt_text is None
    assert turn.prosody == {}
    assert turn.to_llm_content() == "Typed practice sentence."


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
    from server.prompt_builder import UserTurnContext
    from server.session import Session

    session = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    turn = UserTurnContext.from_voice(
        edited_text="Hello.",
        stt_text="Hello.",
        prosody={
            "pace": "2.0 wps (normal)",
            "pitch": "flat",
            "hesitations": "0",
            "stress": "-",
        },
    )
    session.append_user(turn)

    assert len(session.messages) == 1
    assert session.messages[0]["role"] == "user"
    assert "```prosody" in session.messages[0]["content"]


def test_session_messages_is_copy_not_internal_ref(dummy_settings):
    from server.session import Session

    session = Session(llm_model="claude-haiku-4-5-20251001", settings=dummy_settings)
    session.append_user_text("Hi")
    external = session.messages
    external.append({"role": "user", "content": "injected"})

    assert len(session.messages) == 1
