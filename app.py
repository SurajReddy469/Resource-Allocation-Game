"""
═══════════════════════════════════════════════════════════════════════
  CFAI — Cognitive Framework for Adversarial Intelligence
  Main Flask Application

  A professional AI strategy simulator and game theory platform.
  Serves the SPA frontend and provides REST API endpoints for
  game management, AI execution, reasoning traces, and analytics.

  Run: python app.py
  Visit: http://localhost:5000
═══════════════════════════════════════════════════════════════════════
"""

from flask import Flask, render_template, jsonify, request, Response
from services.game_manager import GameManager
from services.analytics_engine import AnalyticsEngine

app = Flask(__name__)

# ── Singleton instances ──
game = GameManager()
analytics = AnalyticsEngine()


# ═══════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the main SPA."""
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════
#  GAME API
# ═══════════════════════════════════════════════════════════════

@app.route("/api/maps", methods=["GET"])
def get_maps():
    """Return available territory maps."""
    return jsonify(game.get_available_maps())


@app.route("/api/game/start", methods=["POST"])
def start_game():
    """Start a new game session."""
    data = request.get_json(silent=True) or {}
    state = game.start_game(
        map_key=data.get("map", "standard"),
        total_turns=data.get("total_turns", 10),
        starting_resources=data.get("starting_resources", 200),
        regen=data.get("regen", 15),
        ai_mode=data.get("ai_mode", "auto"),
    )
    return jsonify(state)


@app.route("/api/game/state", methods=["GET"])
def get_state():
    """Return current game state."""
    return jsonify(game.get_state())


@app.route("/api/game/play", methods=["POST"])
def play_turn():
    """Play one turn with player allocations."""
    data = request.get_json(silent=True) or {}
    allocations = data.get("allocations", [])
    result = game.play_turn(allocations)
    return jsonify(result)


@app.route("/api/game/history", methods=["GET"])
def get_history():
    """Return full game history."""
    return jsonify(game.get_history())


# ═══════════════════════════════════════════════════════════════
#  REASONING API
# ═══════════════════════════════════════════════════════════════

@app.route("/api/reasoning/traces", methods=["GET"])
def get_traces():
    """Return all reasoning traces."""
    return jsonify(game.get_reasoning_traces())


@app.route("/api/reasoning/trace/<int:turn>", methods=["GET"])
def get_trace(turn):
    """Return reasoning trace for a specific turn."""
    trace = game.reasoning.get_trace(turn)
    if trace:
        return jsonify(trace)
    return jsonify({"error": "Turn not found"}), 404


@app.route("/api/reasoning/summary", methods=["GET"])
def get_summary():
    """Return reasoning summary."""
    return jsonify(game.get_reasoning_summary())


@app.route("/api/reasoning/export", methods=["GET"])
def export_log():
    """Export full reasoning log as text."""
    log = game.export_reasoning_log()
    return Response(log, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment; filename=cfai_reasoning_log.txt"})


# ═══════════════════════════════════════════════════════════════
#  ANALYTICS API
# ═══════════════════════════════════════════════════════════════

@app.route("/api/analytics/live", methods=["GET"])
def live_analytics():
    """Return real-time analytics for the current game."""
    state = game.get_state()
    data = analytics.compute_live_analytics(
        history=game.get_history(),
        territories=game.territories,
        player_resources=state["player_resources"],
        ai_resources=state["ai_resources"],
        turns_remaining=state["turns_remaining"],
        total_turns=state["total_turns"],
    )
    return jsonify(data)


@app.route("/api/analytics/report", methods=["GET"])
def session_report():
    """Generate a complete post-game session report."""
    summary = game.get_reasoning_summary()
    report = analytics.compute_session_report(
        reasoning_summary=summary,
        history=game.get_history(),
        territories=game.territories,
        territory_names=game.territory_names,
        map_name=game.map_name,
    )
    return jsonify(report)


@app.route("/api/analytics/sessions", methods=["GET"])
def session_history():
    """Return summaries of all past sessions."""
    return jsonify(analytics.get_session_history())


@app.route("/api/analytics/export-csv", methods=["GET"])
def export_csv():
    """Export game data as CSV."""
    csv = analytics.export_analytics_csv(game.get_history())
    return Response(csv, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=cfai_analytics.csv"})


# ═══════════════════════════════════════════════════════════════
#  ADMIN API
# ═══════════════════════════════════════════════════════════════

@app.route("/api/admin/reasoning-logs", methods=["GET"])
def admin_reasoning_logs():
    """Admin: return all reasoning traces for inspection."""
    return jsonify({
        "traces": game.get_reasoning_traces(),
        "summary": game.get_reasoning_summary(),
        "session_history": analytics.get_session_history(),
    })


@app.route("/api/admin/fairness", methods=["GET"])
def admin_fairness():
    """Admin: resource allocation fairness analysis."""
    history = game.get_history()
    if not history:
        return jsonify({"message": "No data"})

    p_totals = [sum(h["player_allocations"]) for h in history]
    a_totals = [sum(h["ai_allocations"]) for h in history]

    return jsonify({
        "player_avg_spend": round(sum(p_totals) / len(p_totals), 1) if p_totals else 0,
        "ai_avg_spend": round(sum(a_totals) / len(a_totals), 1) if a_totals else 0,
        "player_spend_variance": round(
            sum((x - sum(p_totals)/len(p_totals))**2 for x in p_totals) / len(p_totals), 2
        ) if p_totals else 0,
        "ai_spend_variance": round(
            sum((x - sum(a_totals)/len(a_totals))**2 for x in a_totals) / len(a_totals), 2
        ) if a_totals else 0,
        "fairness_ratio": round(
            min(sum(p_totals), sum(a_totals)) / max(sum(p_totals), sum(a_totals), 1), 3
        ),
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # When deployed in the cloud, bind to 0.0.0.0. Locally, bind to 127.0.0.1
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    
    print("\n" + "=" * 60)
    print("  CFAI — Cognitive Framework for Adversarial Intelligence")
    print(f"  Starting server at http://{host}:{port}")
    print("=" * 60 + "\n")
    
    app.run(debug=False if os.environ.get("PORT") else True, host=host, port=port)
