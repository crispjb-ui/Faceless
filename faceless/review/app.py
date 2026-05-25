"""Human approval dashboard. Run with: streamlit run faceless/review/app.py

The approval gate is what keeps the channel clear of YouTube's mass-produced /
reused-content demonetization, so it stays in the loop even when everything else
is automated. Reviewing a short takes ~30-60s: watch it, skim the script and
compliance flags, then Approve / Reject.
"""
from __future__ import annotations

import streamlit as st

from faceless.config import get_settings
from faceless.db import JobStatus, VideoJob, get_session, init_db


def main() -> None:
    st.set_page_config(page_title="Faceless Review", layout="wide")
    st.title("Faceless — Review Queue")

    init_db()
    niche_id = st.text_input("Niche", value=get_settings().niche)

    with get_session() as s:
        jobs = (
            s.query(VideoJob)
            .filter(VideoJob.niche == niche_id, VideoJob.status == JobStatus.awaiting_review)
            .all()
        )
        rows = [
            {
                "id": j.id,
                "title": j.script.title if j.script else "",
                "body": j.script.body if j.script else "",
                "notes": j.compliance_notes,
                "video": j.video_path,
                "thumb": j.thumbnail_path,
            }
            for j in jobs
        ]

    st.caption(f"{len(rows)} awaiting review")

    if rows:
        ids = [r["id"] for r in rows]
        sel = st.multiselect("Bulk action on jobs", ids, key="bulk_sel")
        b1, b2, b3 = st.columns(3)
        if b1.button("Approve selected", disabled=not sel):
            _set_many(sel, JobStatus.approved)
            st.rerun()
        if b2.button("Reject selected", disabled=not sel):
            _set_many(sel, JobStatus.rejected)
            st.rerun()
        if b3.button(f"Approve ALL ({len(ids)})"):
            _set_many(ids, JobStatus.approved)
            st.rerun()
        st.divider()

    for row in rows:
        with st.expander(f"#{row['id']} — {row['title']}", expanded=False):
            cols = st.columns([2, 3])
            with cols[0]:
                if row["video"]:
                    try:
                        st.video(row["video"])
                    except Exception:
                        st.info(f"Video: {row['video']}")
                if row["thumb"]:
                    st.image(row["thumb"], caption="thumbnail", width=240)
            with cols[1]:
                if row["notes"]:
                    st.warning(f"Compliance: {row['notes']}")
                st.text_area("Script", row["body"], height=240, key=f"b{row['id']}")
                a, r = st.columns(2)
                if a.button("Approve", key=f"a{row['id']}"):
                    _set(row["id"], JobStatus.approved)
                    st.rerun()
                if r.button("Reject", key=f"r{row['id']}"):
                    _set(row["id"], JobStatus.rejected)
                    st.rerun()


def _set(job_id: int, status: JobStatus) -> None:
    with get_session() as s:
        s.get(VideoJob, job_id).status = status


def _set_many(job_ids: list[int], status: JobStatus) -> None:
    with get_session() as s:
        for job_id in job_ids:
            s.get(VideoJob, job_id).status = status


if __name__ == "__main__":
    main()
