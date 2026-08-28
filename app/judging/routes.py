from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import judging_bp
from app.extensions import db
from app.models import (
    Hackathon, Submission, JudgingCriteria, Score, Team
)


@judging_bp.route("/judging/hackathon/<int:hackathon_id>")
@login_required
def judging_dashboard(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)

    if hackathon.created_by != current_user.id and current_user.role not in ("judge", "admin"):
        flash("You do not have access to judging.", "error")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon_id))

    submissions = Submission.query.filter_by(hackathon_id=hackathon_id).all()
    criteria = JudgingCriteria.query.filter_by(hackathon_id=hackathon_id).all()

    return render_template(
        "judging_dashboard.html",
        hackathon=hackathon,
        submissions=submissions,
        criteria=criteria,
    )


@judging_bp.route("/judging/hackathon/<int:hackathon_id>/criteria", methods=["POST"])
@login_required
def manage_criteria(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    if hackathon.created_by != current_user.id:
        flash("Only the organizer can manage criteria.", "error")
        return redirect(url_for("judging.judging_dashboard", hackathon_id=hackathon_id))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    max_score = request.form.get("max_score", 10, type=int)

    if name:
        criterion = JudgingCriteria(
            hackathon_id=hackathon_id,
            name=name,
            description=description,
            max_score=max_score,
        )
        db.session.add(criterion)
        db.session.commit()
        flash(f"Criterion '{name}' added.", "success")

    return redirect(url_for("judging.judging_dashboard", hackathon_id=hackathon_id))


@judging_bp.route("/judging/submission/<int:submission_id>", methods=["GET", "POST"])
@login_required
def judge_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    hackathon = submission.hackathon

    if hackathon.created_by != current_user.id and current_user.role not in ("judge", "admin"):
        flash("You do not have permission to score this submission.", "error")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    if request.method == "POST":
        criteria_id = request.form.get("criteria_id", type=int)
        score_val = request.form.get("score", type=int)
        feedback = request.form.get("feedback", "").strip()

        if not criteria_id or score_val is None:
            flash("Criteria and score are required.", "error")
            return redirect(url_for("judging.judge_submission", submission_id=submission_id))

        criterion = JudgingCriteria.query.get_or_404(criteria_id)
        if score_val < 0 or score_val > criterion.max_score:
            flash(f"Score must be between 0 and {criterion.max_score}.", "error")
            return redirect(url_for("judging.judge_submission", submission_id=submission_id))

        existing = Score.query.filter_by(
            submission_id=submission_id, criteria_id=criteria_id, judge_id=current_user.id
        ).first()
        if existing:
            existing.score = score_val
            existing.feedback = feedback
        else:
            score = Score(
                submission_id=submission_id,
                criteria_id=criteria_id,
                judge_id=current_user.id,
                score=score_val,
                feedback=feedback,
            )
            db.session.add(score)

        db.session.commit()
        flash("Score saved!", "success")
        return redirect(url_for("judging.judge_submission", submission_id=submission_id))

    criteria = JudgingCriteria.query.filter_by(hackathon_id=hackathon.id).all()
    my_scores = {
        s.criteria_id: s
        for s in Score.query.filter_by(submission_id=submission_id, judge_id=current_user.id).all()
    }
    return render_template(
        "judge_submission.html",
        submission=submission,
        hackathon=hackathon,
        criteria=criteria,
        my_scores=my_scores,
    )


@judging_bp.route("/results/hackathon/<int:hackathon_id>")
def results(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    submissions = Submission.query.filter_by(hackathon_id=hackathon_id).all()

    results_data = []
    for sub in submissions:
        total = sub.total_score
        avg = sub.average_score
        team_name = sub.team.name if sub.team else "Individual"
        results_data.append({
            "submission": sub,
            "total_score": total,
            "average_score": avg,
            "team_name": team_name,
        })

    results_data.sort(key=lambda x: x["total_score"], reverse=True)

    for i, r in enumerate(results_data):
        r["rank"] = i + 1

    return render_template(
        "results.html",
        hackathon=hackathon,
        results_data=results_data,
    )
