"""
Human Pilot Survey App - Enhanced UI
=====================================
A beautifully designed Gradio-based survey for collecting warmth, competence, 
and trust ratings on short human-agent dialogues.
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
    formatted = formatted.replace("Human:", '<div style="margin: 20px 0;"><span style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; margin-bottom: 12px;">👤 Human</span><div style="background: #f8f9ff; padding: 20px; border-radius: 12px; margin-top: 8px; line-height: 1.8; color: #1e293b; border-left: 4px solid #667eea;">')
    formatted = formatted.replace("Agent:", '</div></div><div style="margin: 20px 0;"><span style="display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; margin-bottom: 12px;">🤖 Agent</span><div style="background: #fff5f7; padding: 20px; border-radius: 12px; margin-top: 8px; line-height: 1.8; color: #1e293b; border-left: 4px solid #f093fb;">')
    formatted += '</div></div>'
    return formatted


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
        gr.update(value=""),       # Clear thank-you message
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
<div style="text-align: center; padding: 40px 20px;">
    <div style="font-size: 4rem; margin-bottom: 20px;">🎊</div>
    <h1 style="color: #1e293b; font-size: 2.5rem; margin-bottom: 16px; font-weight: 700;">Congratulations!</h1>
    <p style="font-size: 1.2rem; color: #475569; margin-bottom: 32px;">You have completed all <strong style="color: #0f172a;">{len(order)} dialogues</strong>.</p>
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 32px; border-radius: 20px; margin: 32px auto; max-width: 500px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);">
        <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;">Your Completion Code</p>
        <div style="background: white; padding: 20px 32px; border-radius: 12px; font-size: 2rem; font-weight: 800; color: #667eea; font-family: 'Courier New', monospace; letter-spacing: 3px;">{session['completion_code']}</div>
    </div>
    
    <p style="font-size: 1rem; color: #475569; max-width: 500px; margin: 0 auto; line-height: 1.6;">Please copy this code and paste it in Prolific to confirm your participation.</p>
    
    <div style="margin-top: 40px; padding-top: 32px; border-top: 2px solid #e2e8f0;">
        <p style="font-size: 1.1rem; color: #1e293b;">Thank you for your valuable contribution to our research! 🙏</p>
    </div>
</div>
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Force light background */
body, .gradio-container {
    background: #f8fafc !important;
}

/* Global container styling */
.gradio-container {
    width: 1400px !important;
    max-width: 98% !important;
    margin: 0 auto !important;
    padding: 16px !important;
}

/* Force consistent width for all columns */
.gradio-container > div {
    width: 100% !important;
}

/* Study layout - side by side */
.study-layout {
    display: flex !important;
    flex-direction: row !important;
    gap: 20px !important;
    min-height: 450px !important;
}

.study-left-panel {
    flex: 0 0 380px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
}

.study-right-panel {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow-y: auto !important;
}

/* Welcome section */
.welcome-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    padding: 48px 32px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 32px;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
}

.welcome-box h1 {
    font-size: 3rem !important;
    font-weight: 800 !important;
    margin: 0 0 12px 0 !important;
    color: white !important;
}

.welcome-box p {
    font-size: 1.2rem !important;
    opacity: 0.95;
    margin: 0 !important;
    color: white !important;
    font-weight: 500;
}

/* Info cards */
.info-card {
    background: white;
    border: none;
    border-radius: 16px;
    padding: 24px;
    margin: 16px 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
}

.info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.info-card strong {
    color: #667eea !important;
    font-size: 1.1rem;
}

/* Dialogue display */
.dialogue-container {
    background: white;
    border: none;
    border-radius: 20px;
    padding: 28px 32px;
    margin: 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    font-size: 1.05rem;
    line-height: 1.7;
    width: 100% !important;
    box-sizing: border-box !important;
    flex: 1 !important;
    overflow-y: auto !important;
}

/* Progress section */
.progress-display {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white !important;
    padding: 16px 32px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(240, 147, 251, 0.3);
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

.progress-display p, .progress-display strong {
    color: white !important;
    margin: 0 !important;
    font-size: 1.6rem !important;
}

/* Rating section */
.rating-section {
    background: white;
    border-radius: 20px;
    padding: 32px;
    margin: 32px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    width: 100% !important;
    box-sizing: border-box !important;
}

.rating-header {
    text-align: center;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f4f8;
}

.rating-header h2 {
    font-size: 1.2rem !important;
    color: #1e293b !important;
    margin: 0 0 2px 0 !important;
    font-weight: 700 !important;
}

.rating-header p {
    color: #475569 !important;
    font-size: 0.8rem !important;
    margin: 0 !important;
}

.rating-item {
    background: white;
    border-radius: 16px;
    padding: 18px 20px;
    margin: 8px 0;
    border: 2px solid #e2e8f0;
    transition: all 0.3s;
    width: 100% !important;
    box-sizing: border-box !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.rating-item:hover {
    border-color: #667eea;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
}

.rating-label {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-bottom: 10px !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.rating-label span {
    color: #0f172a !important;
}

.rating-scale {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
    padding: 0 4px;
}

.rating-scale span {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
}

/* Slider styling */
input[type="range"] {
    height: 6px !important;
    border-radius: 6px !important;
    background: #e2e8f0 !important;
    margin: 8px 0 !important;
}

input[type="range"]::-webkit-slider-thumb {
    width: 28px !important;
    height: 28px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    box-shadow: 0 2px 16px rgba(102, 126, 234, 0.4) !important;
    cursor: pointer !important;
    border: 4px solid white !important;
    transition: all 0.2s !important;
}

input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6) !important;
}

input[type="range"]::-moz-range-thumb {
    width: 28px !important;
    height: 28px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    box-shadow: 0 2px 16px rgba(102, 126, 234, 0.4) !important;
    cursor: pointer !important;
    border: 4px solid white !important;
    transition: all 0.2s !important;
}

input[type="range"]::-moz-range-thumb:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6) !important;
}

input[type="range"]::-webkit-slider-runnable-track {
    background: #e2e8f0 !important;
    border-radius: 6px !important;
}

input[type="range"]::-moz-range-track {
    background: #e2e8f0 !important;
    border-radius: 6px !important;
}

/* Buttons */
button {
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 32px !important;
    border-radius: 10px !important;
    transition: all 0.3s !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25) !important;
    color: #0f172a !important;
}

.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

/* Thank you section */
.thankyou-container {
    background: white;
    border-radius: 24px;
    padding: 48px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

/* Spacing improvements */
.block {
    margin: 16px 0 !important;
}

/* Remove default Gradio label styling */
label {
    display: none !important;
}
"""

CUSTOM_JS = """
<script>
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add event listeners to buttons after a short delay to ensure they're loaded
setTimeout(function() {
    // Find all buttons and add scroll to top on click
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        const buttonText = button.textContent;
        if (buttonText.includes('Start the Study') || buttonText.includes('Next Dialogue')) {
            button.addEventListener('click', function() {
                setTimeout(scrollToTop, 100);
            });
        }
    });
}, 1000);
</script>
"""


def build_interface() -> gr.Blocks:
    """Build the complete Gradio interface."""
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="pink",
        neutral_hue="slate",
    ).set(
        body_background_fill="#f8fafc",
        body_background_fill_dark="#f8fafc",
    )
    
    with gr.Blocks(css=CUSTOM_CSS, theme=theme) as demo:
        # Add JavaScript for auto-scroll
        gr.HTML(CUSTOM_JS)
        
        # ═══════════════════════════════════════════════════════════════
        # WELCOME / CONSENT SCREEN
        # ═══════════════════════════════════════════════════════════════
        instructions_column = gr.Column(visible=True)
        with instructions_column:
            gr.HTML("""
                <div class="welcome-box">
                    <h1>👋 Welcome!</h1>
                    <p>Human-Agent Dialogue Rating Study</p>
                </div>
            """)

            gr.HTML("""
                <div class="info-card">
                    <strong>📖 What You'll Do</strong>
                    <p style="margin-top: 12px; line-height: 1.7; color: #475569; font-size: 1rem;">
                        You'll read <strong style="color: #334155;">12 short dialogues</strong> between humans and AI agents. 
                        For each dialogue, you'll rate the agent on three dimensions using simple sliders.
                    </p>
                </div>
            """)

            gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #f8f9ff 0%, #fff5f7 100%);">
                    <strong style="color: #1e293b !important; display: block; margin-bottom: 16px;">Rating Dimensions</strong>
                    <div style="display: grid; gap: 16px;">
                        <div style="display: flex; align-items: start; gap: 16px;">
                            <span style="font-size: 2rem;">🤝</span>
                            <div>
                                <strong style="color: #667eea !important; font-size: 1rem;">Warmth</strong>
                                <p style="margin: 4px 0 0 0; color: #475569; font-size: 0.95rem;">How friendly and empathetic is the agent?</p>
                            </div>
                        </div>
                        <div style="display: flex; align-items: start; gap: 16px;">
                            <span style="font-size: 2rem;">🧠</span>
                            <div>
                                <strong style="color: #667eea !important; font-size: 1rem;">Competence</strong>
                                <p style="margin: 4px 0 0 0; color: #475569; font-size: 0.95rem;">How capable and intelligent does the agent seem?</p>
                            </div>
                        </div>
                        <div style="display: flex; align-items: start; gap: 16px;">
                            <span style="font-size: 2rem;">🔒</span>
                            <div>
                                <strong style="color: #667eea !important; font-size: 1rem;">Trust</strong>
                                <p style="margin: 4px 0 0 0; color: #475569; font-size: 0.95rem;">Would you trust this agent with important tasks?</p>
                            </div>
                        </div>
                    </div>
                </div>
            """)

            gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #fef5e7 0%, #fff9e6 100%); border-left: 4px solid #f6ad55;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span style="font-size: 1.5rem;">⏱️</span>
                        <strong style="color: #7c2d12 !important;">Quick Study Info</strong>
                    </div>
                    <div style="display: grid; gap: 8px; color: #0f172a;">
                        <p style="margin: 0; line-height: 1.6;"><strong style="color: #0f172a;">Duration:</strong> <span style="color: #0f172a;">~7 minutes</span></p>
                        <p style="margin: 0; line-height: 1.6;"><strong style="color: #0f172a;">Dialogues:</strong> <span style="color: #0f172a;">12 total</span></p>
                        <p style="margin: 0; line-height: 1.6;"><strong style="color: #0f172a;">Privacy:</strong> <span style="color: #0f172a;">Completely anonymous</span></p>
                        <p style="margin: 0; line-height: 1.6;"><strong style="color: #0f172a;">Data:</strong> <span style="color: #0f172a;">Only ratings collected (no personal info)</span></p>
                    </div>
                </div>
            """)

            gr.HTML("""
                <div class="info-card" style="background: linear-gradient(135deg, #e6f7e6 0%, #f0fff4 100%); border-left: 4px solid #48bb78;">
                    <p style="margin: 0; color: #1e293b; line-height: 1.7; font-size: 0.95rem;">
                        ✅ By clicking <strong style="color: #0f172a;">Start</strong>, you confirm that you are 18 years or older 
                        and agree to participate voluntarily in this research study.
                    </p>
                </div>
            """)

            start_button = gr.Button(
                "🚀 Start the Study",
                variant="primary",
                size="lg",
                elem_classes=["primary"]
            )

        # ═══════════════════════════════════════════════════════════════
        # STUDY / RATING SCREEN
        # ═══════════════════════════════════════════════════════════════
        study_column = gr.Column(visible=False)
        with study_column:
            # Progress indicator at top
            progress_text = gr.Markdown("**Dialogue 1 of 12**", elem_classes=["progress-display"])
            
            # Side-by-side layout
            with gr.Row(elem_classes=["study-layout"]):
                # LEFT PANEL - Rating sliders
                with gr.Column(scale=1, elem_classes=["study-left-panel"]):
                    gr.HTML("""
                        <div class="rating-header">
                            <h2>📊 Rate This Agent</h2>
                            <p>Use the sliders (1 = low, 7 = high)</p>
                        </div>
                    """)

                    # Warmth Rating
                    gr.HTML('<div class="rating-item"><div class="rating-label"><span style="font-size: 1.4rem;">🤝</span> <span style="color: #0f172a; font-weight: 700;">Warmth</span></div>')
                    warmth_slider = gr.Slider(
                        minimum=1,
                        maximum=7,
                        value=4,
                        step=1,
                        show_label=False,
                    )
                    gr.HTML('<div class="rating-scale"><span>Not friendly</span><span>Neutral</span><span>Very friendly</span></div></div>')

                    # Competence Rating
                    gr.HTML('<div class="rating-item"><div class="rating-label"><span style="font-size: 1.4rem;">🧠</span> <span style="color: #0f172a; font-weight: 700;">Competence</span></div>')
                    competence_slider = gr.Slider(
                        minimum=1,
                        maximum=7,
                        value=4,
                        step=1,
                        show_label=False,
                    )
                    gr.HTML('<div class="rating-scale"><span>Not capable</span><span>Neutral</span><span>Very capable</span></div></div>')

                    # Trust Rating
                    gr.HTML('<div class="rating-item"><div class="rating-label"><span style="font-size: 1.4rem;">🔒</span> <span style="color: #0f172a; font-weight: 700;">Trust</span></div>')
                    trust_slider = gr.Slider(
                        minimum=1,
                        maximum=7,
                        value=4,
                        step=1,
                        show_label=False,
                    )
                    gr.HTML('<div class="rating-scale"><span>No trust</span><span>Neutral</span><span>Full trust</span></div></div>')

                    gr.HTML('<div style="margin-top: 8px;"></div>')

                    next_button = gr.Button(
                        "Next Dialogue ➡️",
                        variant="primary",
                        size="md",
                        elem_classes=["primary"]
                    )

                # RIGHT PANEL - Dialogue display
                with gr.Column(scale=2, elem_classes=["study-right-panel"]):
                    gr.HTML('<div style="text-align: center; margin-bottom: 12px;"><h2 style="color: #1e293b; font-size: 1.4rem; font-weight: 700; margin: 0;">💬 Read the Dialogue</h2></div>')
                    dialogue_display = gr.HTML("", elem_classes=["dialogue-container"])

        # ═══════════════════════════════════════════════════════════════
        # THANK YOU SCREEN
        # ═══════════════════════════════════════════════════════════════
        thankyou_column = gr.Column(visible=False)
        with thankyou_column:
            thankyou_message = gr.HTML("")

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