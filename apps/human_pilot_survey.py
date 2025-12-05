"""
Human Pilot Survey App
======================
A Gradio-based survey for collecting warmth, competence, and trust ratings
on short human-agent dialogues.
"""
import csv
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "human_pilot"
DIALOGUE_FILE = DATA_DIR / "dialogues.json"
RESPONSES_FILE = DATA_DIR / "pilot_ratings.csv"


def load_dialogues() -> list[dict]:
    if not DIALOGUE_FILE.exists():
        raise FileNotFoundError(f"Dialogue file not found at {DIALOGUE_FILE}")
    with DIALOGUE_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


DIALOGUES = load_dialogues()


def ensure_response_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RESPONSES_FILE.exists():
        with RESPONSES_FILE.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "timestamp",
                    "dialogue_id",
                    "agent_type",
                    "warmth",
                    "competence",
                    "trust",
                    "completion_code",
                ]
            )


def save_response(
    dialogue: dict, warmth: int, competence: int, trust: int, completion_code: str
) -> None:
    ensure_response_store()
    with RESPONSES_FILE.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                dialogue["id"],
                dialogue["agent_type"],
                warmth,
                competence,
                trust,
                completion_code,
            ]
        )


def format_dialogue(text: str) -> str:
    """Format dialogue text with clear line breaks and speaker labels."""
    formatted = text.strip()
    formatted = formatted.replace("Human:", "\n\n👤 **Human:**")
    formatted = formatted.replace("Agent:", "\n\n🤖 **Agent:**")
    return formatted.strip()


def start_study() -> tuple:
    """Initialize a new study session with randomized dialogue order."""
    order = random.sample(DIALOGUES, len(DIALOGUES))
    completion_code = f"HUMTOM{random.randint(1000, 9999)}"
    session = {"order": order, "index": 0, "completion_code": completion_code}
    first_dialogue = order[0]

    return (
        gr.update(value=format_dialogue(first_dialogue["text"])),
        gr.update(value=f"**Dialogue 1 of {len(order)}**"),
        gr.update(visible=False),  # Hide instructions
        gr.update(visible=True),   # Show study
        gr.update(visible=False),  # Hide thank-you
        gr.update(value=4),        # Reset warmth
        gr.update(value=4),        # Reset competence
        gr.update(value=4),        # Reset trust
        gr.update(value=""),     # Clear thank-you message
        session,
    )


def record_and_next(
    warmth: int, competence: int, trust: int, session: dict | None
) -> tuple:
    """Record current ratings and advance to next dialogue."""
    if not session or "order" not in session:
        return (
            gr.update(value=""),
            gr.update(value=""),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value=""),
            gr.update(value=4),
            gr.update(value=4),
            gr.update(value=4),
            {},
        )

    order = session["order"]
    index = session.get("index", 0)

    # Save the current response
    if index < len(order):
        current = order[index]
        save_response(current, warmth, competence, trust, session["completion_code"])

    next_index = index + 1
    session["index"] = next_index

    # Check if we're done
    if next_index >= len(order):
        completion_message = f"""
---

### 🎊 Congratulations!

You have completed all **{len(order)} dialogues**.

---

**Your completion code:**

<div style="
    background: #ffffff;
    border: 2px dashed #28a745;
    border-radius: 8px;
    padding: 16px 32px;
    font-size: 1.5rem;
    font-weight: bold;
    font-family: monospace;
    color: #155724;
    display: inline-block;
    margin: 16px 0;
">{session['completion_code']}</div>

---

*Please copy this code and paste it in Prolific to confirm your participation.*

Thank you for your valuable contribution to our research! 🙏
"""
        return (
            gr.update(value=""),
            gr.update(value=""),
            gr.update(visible=False),  # Hide study
            gr.update(visible=True),   # Show thank-you
            gr.update(value=completion_message),
            gr.update(value=4),
            gr.update(value=4),
            gr.update(value=4),
            session,
        )

    # Load next dialogue
    next_dialogue = order[next_index]
    return (
        gr.update(value=format_dialogue(next_dialogue["text"])),
        gr.update(value=f"**Dialogue {next_index + 1} of {len(order)}**"),
        gr.update(visible=True),   # Keep study visible
        gr.update(visible=False),  # Keep thank-you hidden
        gr.update(value=""),
        gr.update(value=4),        # Reset sliders
        gr.update(value=4),
        gr.update(value=4),
        session,
    )


CUSTOM_CSS = """
/* Welcome section */
.welcome-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    padding: 32px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 12px;
}

.welcome-box h1, .welcome-box h2, .welcome-box h3, .welcome-box p {
    color: white !important;
    margin: 0;
}

/* Info cards */
.info-card {
    background: #f0f5ff;
    border: 2px solid #d4e0ff;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    color: #1a1a1a !important;
}

.info-card strong {
    color: #0066cc !important;
}

/* Dialogue display */
.dialogue-container {
    background: #ffffff;
    border: 2px solid #d4e0ff;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    font-size: 1.05rem;
    line-height: 1.7;
    color: #1a1a1a !important;
}

/* Progress badge */
.progress-badge {
    background: #d4e0ff;
    color: #0050cc !important;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 12px;
    border: 1px solid #a8c5ff;
    font-size: 0.9rem;
}

/* Rating section */
.rating-card {
    background: #f8faff;
    border: 2px solid #e0ecff;
    border-radius: 12px;
    padding: 16px;
    margin: 10px 0;
}

.rating-label {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0050cc !important;
    margin-bottom: 2px;
}

.rating-hint {
    font-size: 0.8rem;
    color: #404040 !important;
    margin-bottom: 8px;
    font-weight: 500;
}

/* Thank you section */
.thankyou-container {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white !important;
    padding: 32px;
    border-radius: 16px;
    text-align: center;
}

.thankyou-container h1, .thankyou-container h2, .thankyou-container h3 {
    color: white !important;
    margin: 4px 0;
}

/* Scale labels */
.scale-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #404040 !important;
    margin-top: -6px;
    padding: 0 8px;
    font-weight: 600;
}
"""


def build_interface() -> gr.Blocks:
    """Build the complete Gradio interface."""
    demo = gr.Blocks()
    
    with demo:
        # Add custom CSS
        gr.HTML(f"<style>{CUSTOM_CSS}</style>")

        # ═══════════════════════════════════════════════════════════════
        # WELCOME / CONSENT SCREEN
        # ═══════════════════════════════════════════════════════════════
        instructions_column = gr.Column()
        with instructions_column:
            gr.HTML(
                """
                <div class="welcome-box">
                    <h1 style="margin: 0 0 4px 0; font-size: 2.2rem; color: white !important;">👋 Welcome!</h1>
                    <p style="font-size: 1.05rem; opacity: 0.95; margin: 0; color: white !important;">
                        Human-Agent Dialogue Rating Study
                    </p>
                </div>
                """
            )

            gr.HTML(
                """
                <div class="info-card">
                    <strong style="font-size: 1rem; color: #0050cc !important;">What You'll Do</strong>
                    <div style="font-size: 0.95rem; line-height: 1.5; margin-top: 6px; color: #1a1a1a !important;">
                        Read short dialogues and rate each agent on <strong>warmth</strong>, <strong>competence</strong>, and <strong>trust</strong>.
                    </div>
                </div>
                """
            )

            gr.HTML(
                """
                <div class="info-card" style="background: #f0f8ff; border-color: #4da6ff;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                        <tr>
                            <td style="padding: 6px 8px; width: 30px; vertical-align: top; color: #1a1a1a;">🤝</td>
                            <td style="padding: 6px 8px; color: #1a1a1a;"><strong style="color: #0050cc !important;">Warmth</strong> — Friendly & empathetic?</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 8px; vertical-align: top; color: #1a1a1a;">🧠</td>
                            <td style="padding: 6px 8px; color: #1a1a1a;"><strong style="color: #0050cc !important;">Competence</strong> — Capable & intelligent?</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 8px; vertical-align: top; color: #1a1a1a;">🔒</td>
                            <td style="padding: 6px 8px; color: #1a1a1a;"><strong style="color: #0050cc !important;">Trust</strong> — Would you trust them?</td>
                        </tr>
                    </table>
                </div>
                """
            )

            gr.HTML(
                """
                <div class="info-card" style="background: #fff8e6; border-color: #ffcc00; font-size: 0.9rem; line-height: 1.6; color: #1a1a1a !important;">
                    <strong style="color: #cc8800 !important;">📋 Study Info:</strong> ~7 min • Anonymous • No data collected • 12 dialogues
                </div>
                """
            )

            gr.HTML(
                """
                <div class="info-card" style="background: #e6f7e6; border-color: #28a745; font-size: 0.85rem; line-height: 1.5; color: #1a1a1a !important;">
                    ✅ By clicking <strong>Start</strong>, you confirm you are 18+ and agree to participate voluntarily.
                </div>
                """
            )

            start_button = gr.Button(
                "🚀 Start the Study",
                variant="primary",
                size="lg",
            )

        # ═══════════════════════════════════════════════════════════════
        # STUDY / RATING SCREEN
        # ═══════════════════════════════════════════════════════════════
        study_column = gr.Column(visible=False)
        with study_column:
            # Progress indicator
            progress_text = gr.Markdown("**Dialogue 1 of 12**")

            gr.Markdown("### 💬 Read the dialogue:")
            dialogue_display = gr.Markdown("", elem_classes=["dialogue-container"])

            gr.Markdown("---")
            gr.Markdown("### 📊 Rate this assistant")
            gr.Markdown("*Use the sliders (1 = low, 7 = high):*")

            # Warmth Rating
            gr.Markdown("**🤝 Warmth** — Friendly & empathetic?")
            warmth_slider = gr.Slider(
                minimum=1,
                maximum=7,
                value=4,
                step=1,
                label="",
                show_label=False,
            )

            # Competence Rating
            gr.Markdown("**🧠 Competence** — Capable & intelligent?")
            competence_slider = gr.Slider(
                minimum=1,
                maximum=7,
                value=4,
                step=1,
                label="",
                show_label=False,
            )

            # Trust Rating
            gr.Markdown("**🔒 Trust** — Would you trust them?")
            trust_slider = gr.Slider(
                minimum=1,
                maximum=7,
                value=4,
                step=1,
                label="",
                show_label=False,
            )

            gr.Markdown("---")

            next_button = gr.Button(
                "Next Dialogue ➡️",
                variant="primary",
                size="lg",
            )

        # ═══════════════════════════════════════════════════════════════
        # THANK YOU SCREEN
        # ═══════════════════════════════════════════════════════════════
        thankyou_column = gr.Column(visible=False)
        with thankyou_column:
            gr.HTML('<div class="thankyou-container">')
            gr.Markdown("# 🎉 Thank You!")
            gr.HTML("</div>")
            thankyou_message = gr.Markdown("")

        # ═══════════════════════════════════════════════════════════════
        # SESSION STATE & EVENT HANDLERS
        # ═══════════════════════════════════════════════════════════════
        session_state = gr.State()

        start_button.click(
            start_study,
            inputs=None,
            outputs=[
                dialogue_display,
                progress_text,
                instructions_column,
                study_column,
                thankyou_column,
                warmth_slider,
                competence_slider,
                trust_slider,
                thankyou_message,
                session_state,
            ],
        )

        next_button.click(
            record_and_next,
            inputs=[warmth_slider, competence_slider, trust_slider, session_state],
            outputs=[
                dialogue_display,
                progress_text,
                study_column,
                thankyou_column,
                thankyou_message,
                warmth_slider,
                competence_slider,
                trust_slider,
                session_state,
            ],
        )

    return demo


def main() -> None:
    """Entry point for the survey app."""
    ensure_response_store()
    demo = build_interface()
    demo.launch(share=True)


if __name__ == "__main__":
    main()