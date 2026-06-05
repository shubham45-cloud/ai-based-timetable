"""
SIH AI TIMETABLE ENGINE  –  v2.0
─────────────────────────────────────────────────────────────────────────────
Key upgrades over v1
  • Theory  (L+T)  →  single-period classroom slots
  • Lab     (P/2)  →  consecutive 2-period lab slots  (no mid-pair theory gap)
  • Online subjects (8th sem) are skipped entirely
  • Combined sections (4ABC, 6AB) block all constituent sections
    when their shared subject is scheduled
  • Room-type enforcement: classrooms ↔ theory, labs ↔ practical
─────────────────────────────────────────────────────────────────────────────
"""

from ortools.sat.python import cp_model
from sqlalchemy.orm import Session

from app import crud
from app.models import RoomTypeEnum, SubjectTypeEnum


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def generate_timetable_logic(db: Session):

    # ── pre-flight audit ──────────────────────────────────────────────────────
    issues = run_data_audit(db)
    if issues:
        return {"status": "error", "message": "Data Audit Failed", "details": issues}

    # ── 1. Fetch everything ───────────────────────────────────────────────────
    teachers            = crud.get_all_teachers(db)
    subjects            = crud.get_all_subjects(db)
    rooms               = crud.get_all_rooms(db)
    time_slots          = crud.get_all_time_slots(db)
    teacher_subject_links = crud.get_all_teacher_subjects(db)
    combined_links      = crud.get_combined_section_links(db)   # NEW in crud.py

    # ── 2. Derived helpers ────────────────────────────────────────────────────

    # Room buckets
    classrooms   = [r for r in rooms if r.room_type == RoomTypeEnum.CLASSROOM]
    lab_rooms    = [r for r in rooms if r.room_type == RoomTypeEnum.LAB]

    # Subject buckets  (skip online subjects completely)
    active_subjects  = [s for s in subjects if not s.is_online]
    theory_subjects  = [s for s in active_subjects if s.subject_type == SubjectTypeEnum.THEORY]
    lab_subjects     = [s for s in active_subjects if s.subject_type == SubjectTypeEnum.LAB]

    # Teacher → subjects map
    teacher_for_subject: dict[int, list[int]] = {}
    for link in teacher_subject_links:
        teacher_for_subject.setdefault(link.subject_id, []).append(link.teacher_id)

    # Combined dept → list of constituent dept ids
    combined_map: dict[int, list[int]] = {}
    for lnk in combined_links:
        combined_map.setdefault(lnk.combined_dept_id, []).append(lnk.constituent_dept_id)

    # All "real" (non-combined) sections that need rooms
    all_dept_ids        = set(s.dept_id for s in active_subjects)
    combined_dept_ids   = set(combined_map.keys())
    real_dept_ids       = all_dept_ids - combined_dept_ids

    # ── 3. Lab pair slots ─────────────────────────────────────────────────────
    # Group consecutive same-day period pairs: (P1,P2), (P3,P4), (P5,P6), (P7,P8)
    # Each pair is one "lab slot unit".
    day_order = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
    days      = sorted(set(ts.day_of_week for ts in time_slots),
                       key=lambda d: day_order.index(d) if d in day_order else 99)

    lab_pairs: list[tuple[int, str, int, int]] = []
    # (pair_idx, day, ts1_id, ts2_id)
    for day in days:
        day_slots = sorted(
            [ts for ts in time_slots if ts.day_of_week == day],
            key=lambda x: x.period_no
        )
        for i in range(0, len(day_slots) - 1, 2):   # step 2 → fixed pairs
            lab_pairs.append((
                len(lab_pairs),
                day,
                day_slots[i].timeslot_id,
                day_slots[i + 1].timeslot_id,
            ))

    pair_idx_map = {pi: (ts1, ts2) for (pi, _, ts1, ts2) in lab_pairs}

    # Reverse: timeslot_id → set of pair_idxs that contain it
    ts_to_pairs: dict[int, list[int]] = {}
    for (pi, _, ts1, ts2) in lab_pairs:
        ts_to_pairs.setdefault(ts1, []).append(pi)
        ts_to_pairs.setdefault(ts2, []).append(pi)

    # ── diagnostics ───────────────────────────────────────────────────────────
    print("─── SIH AI ENGINE v2 DIAGNOSTICS ───")
    print(f"Real sections   : {len(real_dept_ids)}")
    print(f"Combined sections: {len(combined_dept_ids)}  {dict(combined_map)}")
    print(f"Theory subjects : {len(theory_subjects)}")
    print(f"Lab subjects    : {len(lab_subjects)}")
    print(f"Classrooms      : {len(classrooms)}")
    print(f"Labs            : {len(lab_rooms)}")
    print(f"Time slots      : {len(time_slots)}  Lab pairs: {len(lab_pairs)}")

    # ══════════════════════════════════════════════════════════════════════════
    #  4. CP-SAT MODEL
    # ══════════════════════════════════════════════════════════════════════════
    model = cp_model.CpModel()

    # ── Decision variables ────────────────────────────────────────────────────
    # Theory  : t_var[sub_id, ts_id,   room_id]   (classroom)
    # Lab     : l_var[sub_id, pair_idx, room_id]  (lab room)

    t_var: dict[tuple, cp_model.IntVar] = {}
    for sub in theory_subjects:
        for ts in time_slots:
            for r in classrooms:
                key = (sub.subject_id, ts.timeslot_id, r.room_id)
                t_var[key] = model.NewBoolVar(f"th_{sub.subject_id}_{ts.timeslot_id}_{r.room_id}")

    l_var: dict[tuple, cp_model.IntVar] = {}
    for sub in lab_subjects:
        for (pi, _, _, _) in lab_pairs:
            for lr in lab_rooms:
                key = (sub.subject_id, pi, lr.room_id)
                l_var[key] = model.NewBoolVar(f"lab_{sub.subject_id}_{pi}_{lr.room_id}")

    # ── Helper lambdas ────────────────────────────────────────────────────────
    # Sum of all theory vars for a subject list at a specific timeslot
    def theory_sum_at(sub_ids, ts_id):
        return sum(
            t_var[k] for k in t_var
            if k[0] in sub_ids and k[1] == ts_id
        )

    # Sum of all lab vars for a subject list at a specific pair index
    def lab_sum_at(sub_ids, pi):
        return sum(
            l_var[k] for k in l_var
            if k[0] in sub_ids and k[1] == pi
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  5. HARD CONSTRAINTS
    # ══════════════════════════════════════════════════════════════════════════

    # ── C1 : Weekly count – theory ────────────────────────────────────────────
    for sub in theory_subjects:
        model.Add(
            sum(t_var[k] for k in t_var if k[0] == sub.subject_id)
            == sub.lectures_per_week
        )

    # ── C2 : Weekly count – lab (sessions) ───────────────────────────────────
    for sub in lab_subjects:
        model.Add(
            sum(l_var[k] for k in l_var if k[0] == sub.subject_id)
            == sub.lectures_per_week
        )

    # ── C3 : Classroom uniqueness (one class per room per period) ─────────────
    for r in classrooms:
        for ts in time_slots:
            model.AddAtMostOne(
                t_var[k] for k in t_var
                if k[1] == ts.timeslot_id and k[2] == r.room_id
            )

    # ── C4 : Lab-room uniqueness (one lab per room per pair slot) ─────────────
    for lr in lab_rooms:
        for (pi, _, _, _) in lab_pairs:
            model.AddAtMostOne(
                l_var[k] for k in l_var
                if k[1] == pi and k[2] == lr.room_id
            )

    # ── C5 : Section conflict – no two theory classes for same dept at same ts ─
    for dept_id in all_dept_ids:
        dept_th_ids = [s.subject_id for s in theory_subjects if s.dept_id == dept_id]
        for ts in time_slots:
            overlapping = [
                t_var[k] for k in t_var
                if k[0] in dept_th_ids and k[1] == ts.timeslot_id
            ]
            if overlapping:
                model.AddAtMostOne(overlapping)

    # ── C6 : Section conflict – no two lab sessions for same dept at same pair ─
    for dept_id in all_dept_ids:
        dept_lab_ids = [s.subject_id for s in lab_subjects if s.dept_id == dept_id]
        for (pi, _, _, _) in lab_pairs:
            overlapping = [
                l_var[k] for k in l_var
                if k[0] in dept_lab_ids and k[1] == pi
            ]
            if overlapping:
                model.AddAtMostOne(overlapping)

    # ── C7 : No theory AND lab clash within the same pair for same section ────
    #
    # If a section has lab at pair (ts1, ts2), it cannot have theory at ts1 or ts2.
    # Linearised:  theory_at_ts1 + theory_at_ts2 + 2 * lab_in_pair  ≤  2
    #   →  when lab_in_pair=1: ts1 & ts2 both forced to 0
    #   →  when lab_in_pair=0: no extra restriction
    for dept_id in all_dept_ids:
        dept_th_ids  = [s.subject_id for s in theory_subjects if s.dept_id == dept_id]
        dept_lab_ids = [s.subject_id for s in lab_subjects    if s.dept_id == dept_id]
        if not dept_lab_ids:
            continue
        for (pi, _, ts1, ts2) in lab_pairs:
            th1 = theory_sum_at(dept_th_ids, ts1)
            th2 = theory_sum_at(dept_th_ids, ts2)
            lb  = lab_sum_at(dept_lab_ids, pi)
            model.Add(th1 + th2 + 2 * lb <= 2)

    # ── C8 : Combined sections block their constituents ───────────────────────
    #
    # When combined subject (4ABC/6AB) is scheduled at ts:
    #   (a) No constituent-section theory at ts
    #   (b) No constituent-section lab whose pair contains ts
    for comb_dept, constituents in combined_map.items():
        comb_th_ids = [s.subject_id for s in theory_subjects if s.dept_id == comb_dept]

        for sub_id in comb_th_ids:
            for ts in time_slots:
                # Sum over classrooms → 0 or 1 due to C5
                comb_at_ts = sum(
                    t_var.get((sub_id, ts.timeslot_id, r.room_id), 0)
                    for r in classrooms
                )

                for const_dept in constituents:
                    const_th_ids  = [s.subject_id for s in theory_subjects
                                     if s.dept_id == const_dept]
                    const_lab_ids = [s.subject_id for s in lab_subjects
                                     if s.dept_id == const_dept]

                    # (a) no theory clash
                    const_theory = theory_sum_at(const_th_ids, ts.timeslot_id)
                    model.Add(comb_at_ts + const_theory <= 1)

                    # (b) no lab whose pair spans ts
                    for pi in ts_to_pairs.get(ts.timeslot_id, []):
                        const_lab = lab_sum_at(const_lab_ids, pi)
                        model.Add(comb_at_ts + const_lab <= 1)

    # ── C9 : Teacher uniqueness – theory (can't be in two places at once) ─────
    for t in teachers:
        t_sub_ids = set(
            sub_id for sub_id, tlist in teacher_for_subject.items()
            if t.teacher_id in tlist
        )
        t_th_ids  = [s.subject_id for s in theory_subjects if s.subject_id in t_sub_ids]
        t_lab_ids = [s.subject_id for s in lab_subjects    if s.subject_id in t_sub_ids]

        # theory: at most one per timeslot
        for ts in time_slots:
            model.AddAtMostOne(
                t_var[k] for k in t_var
                if k[0] in t_th_ids and k[1] == ts.timeslot_id
            )

        # lab: at most one per pair slot
        for (pi, _, _, _) in lab_pairs:
            model.AddAtMostOne(
                l_var[k] for k in l_var
                if k[0] in t_lab_ids and k[1] == pi
            )

        # teacher can't teach theory while running a lab in the same pair
        for (pi, _, ts1, ts2) in lab_pairs:
            t_th1 = theory_sum_at(t_th_ids, ts1)
            t_th2 = theory_sum_at(t_th_ids, ts2)
            t_lb  = lab_sum_at(t_lab_ids, pi)
            model.Add(t_th1 + t_th2 + 2 * t_lb <= 2)

    # ── C10 : Teacher daily load  (theory periods + 2×lab sessions ≤ 4) ───────
    MAX_PER_DAY = 4
    for t in teachers:
        t_sub_ids = set(
            sub_id for sub_id, tlist in teacher_for_subject.items()
            if t.teacher_id in tlist
        )
        t_th_ids  = [s.subject_id for s in theory_subjects if s.subject_id in t_sub_ids]
        t_lab_ids = [s.subject_id for s in lab_subjects    if s.subject_id in t_sub_ids]

        for day in days:
            day_ts_ids    = {ts.timeslot_id for ts in time_slots if ts.day_of_week == day}
            day_pair_idxs = [pi for (pi, d, _, _) in lab_pairs if d == day]

            theory_today = sum(
                t_var[k] for k in t_var
                if k[0] in t_th_ids and k[1] in day_ts_ids
            )
            labs_today = sum(
                l_var[k] for k in l_var
                if k[0] in t_lab_ids and k[1] in day_pair_idxs
            )
            # each lab session occupies 2 periods
            model.Add(theory_today + 2 * labs_today <= MAX_PER_DAY)

    # ── C11 : No 3+ consecutive theory periods for same teacher ───────────────
    for t in teachers:
        t_sub_ids = set(
            sub_id for sub_id, tlist in teacher_for_subject.items()
            if t.teacher_id in tlist
        )
        t_th_ids = [s.subject_id for s in theory_subjects if s.subject_id in t_sub_ids]
        if not t_th_ids:
            continue
        for day in days:
            day_slots = sorted(
                [ts for ts in time_slots if ts.day_of_week == day],
                key=lambda x: x.period_no
            )
            for i in range(len(day_slots) - 2):
                ts1, ts2, ts3 = day_slots[i], day_slots[i+1], day_slots[i+2]
                window = sum(
                    t_var[k] for k in t_var
                    if k[0] in t_th_ids
                    and k[1] in {ts1.timeslot_id, ts2.timeslot_id, ts3.timeslot_id}
                )
                model.Add(window <= 2)
    # ── C11 : No 3+ consecutive theory periods for same teacher ───────────────
    # ... (your existing C11 code is here) ...

    # ── C12 : Max 2 lab sessions (4 periods) per day per section ──────────────
    for dept_id in all_dept_ids:
        dept_lab_ids = [s.subject_id for s in lab_subjects if s.dept_id == dept_id]
        if not dept_lab_ids:
            continue
            
        for day in days:
            # Find all lab pair slots for this specific day
            day_pair_idxs = [pi for (pi, d, _, _) in lab_pairs if d == day]
            
            # Count how many lab sessions this section is taking today
            labs_today = sum(
                l_var[k] for k in l_var 
                if k[0] in dept_lab_ids and k[1] in day_pair_idxs
            )
            
            # Enforce the college rule: At most 2 lab sessions (4 periods) per day
            model.Add(labs_today <= 2)

    # ══════════════════════════════════════════════════════════════════════════
    #  6. SOLVE
    # ══════════════════════════════════════════════════════════════════════════
    # ── C12 : Max 2 lab sessions (4 periods) per day per section ──────────────
    # ... (your existing C12 code) ...

    # ── C13 : No two consecutive free periods for any student section ─────────
    for dept_id in real_dept_ids:
        # Get normal theory and lab subjects for this section
        dept_th_ids  = [s.subject_id for s in theory_subjects if s.dept_id == dept_id]
        dept_lab_ids = [s.subject_id for s in lab_subjects    if s.dept_id == dept_id]
        
        # Find combined subjects (like AICE/Django) that include this section
        my_comb_th_ids = []
        for comb_dept, constituents in combined_map.items():
            if dept_id in constituents:
                my_comb_th_ids.extend(
                    [s.subject_id for s in theory_subjects if s.dept_id == comb_dept]
                )

        # Helper to calculate if the section is in ANY class during a specific timeslot
        def section_busy_at(ts_id):
            th_busy = sum(t_var[k] for k in t_var if k[0] in dept_th_ids and k[1] == ts_id)
            
            # Labs cover 2 timeslots; find if this timeslot belongs to a scheduled lab pair
            lab_pairs_for_ts = ts_to_pairs.get(ts_id, [])
            lb_busy = sum(l_var[k] for k in l_var if k[0] in dept_lab_ids and k[1] in lab_pairs_for_ts)
            
            cmb_busy = sum(t_var[k] for k in t_var if k[0] in my_comb_th_ids and k[1] == ts_id)
            
            return th_busy + lb_busy + cmb_busy

        # Loop through each day and check every pair of consecutive periods
        for day in days:
            day_slots = sorted(
                [ts for ts in time_slots if ts.day_of_week == day],
                key=lambda x: x.period_no
            )
            for i in range(len(day_slots) - 1):
                busy1 = section_busy_at(day_slots[i].timeslot_id)
                busy2 = section_busy_at(day_slots[i+1].timeslot_id)
                
                # Out of any 2 consecutive periods, at least 1 MUST be a scheduled class.
                # (This completely forbids [Free] -> [Free])
                model.Add(busy1 + busy2 >= 1)

    # ══════════════════════════════════════════════════════════════════════════
    #  6. SOLVE
    # ══════════════════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════════════════
    #  6. SOLVE
    # ══════════════════════════════════════════════════════════════════════════
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 90
    solver.parameters.num_search_workers  = 4    # parallel threads
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "status": "error",
            "message": (
                "INFEASIBLE: Solver could not schedule all subjects. "
                "Check teacher loads, room counts, or relax constraints."
            )
        }

    # ── 7. Persist results ────────────────────────────────────────────────────
    crud.clear_timetable(db)
    ts_day_period = {ts.timeslot_id: (ts.day_of_week, ts.period_no) for ts in time_slots}

    saved = 0

    # Theory entries (1 row per assigned slot)
    for (sub_id, ts_id, r_id), var in t_var.items():
        if solver.Value(var) == 1:
            day, period = ts_day_period[ts_id]
            teacher_id  = teacher_for_subject.get(sub_id, [None])[0]
            if teacher_id:
                crud.save_timetable_entry(db, {
                    "day_of_week": day,
                    "period_no":   period,
                    "subject_id":  sub_id,
                    "teacher_id":  teacher_id,
                    "room_id":     r_id,
                })
                saved += 1

    # Lab entries (2 rows per session – front-end merges them visually)
    for (sub_id, pi, r_id), var in l_var.items():
        if solver.Value(var) == 1:
            ts1_id, ts2_id = pair_idx_map[pi]
            teacher_id     = teacher_for_subject.get(sub_id, [None])[0]
            if teacher_id:
                for ts_id in (ts1_id, ts2_id):
                    day, period = ts_day_period[ts_id]
                    crud.save_timetable_entry(db, {
                        "day_of_week": day,
                        "period_no":   period,
                        "subject_id":  sub_id,
                        "teacher_id":  teacher_id,
                        "room_id":     r_id,
                    })
                    saved += 1

    db.commit()
    return {
        "status":  "success",
        "message": f"Timetable generated successfully! ({saved} total period-slots scheduled)",
    }


# ══════════════════════════════════════════════════════════════════════════════
#  DATA AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def run_data_audit(db: Session) -> list[str]:
    warnings: list[str] = []

    subjects        = crud.get_all_subjects(db)
    rooms           = crud.get_all_rooms(db)
    time_slots      = crud.get_all_time_slots(db)
    teacher_subjects = crud.get_all_teacher_subjects(db)

    active_subjects = [s for s in subjects if not s.is_online]
    classrooms      = [r for r in rooms if r.room_type == RoomTypeEnum.CLASSROOM]
    lab_rooms       = [r for r in rooms if r.room_type == RoomTypeEnum.LAB]

    # At least 1 classroom and 1 lab must exist
    if not classrooms:
        warnings.append("CRITICAL: No classrooms found. Add rooms with room_type=CLASSROOM.")
    if not lab_rooms:
        warnings.append("CRITICAL: No lab rooms found. Add rooms with room_type=LAB.")

    # Every active subject needs at least one teacher assigned
    assigned_subject_ids = {ts.subject_id for ts in teacher_subjects}
    for sub in active_subjects:
        if sub.subject_id not in assigned_subject_ids:
            warnings.append(
                f"MISSING TEACHER: '{sub.subject_name}' (code: {sub.subject_code}) "
                f"has no teacher assigned."
            )

    # Lab subjects must have lectures_per_week ≥ 1
    for sub in active_subjects:
        if sub.subject_type == "LAB" and sub.lectures_per_week < 1:
            warnings.append(
                f"BAD DATA: Lab subject '{sub.subject_name}' has lectures_per_week < 1."
            )

    # Enough lab-pair slots for all lab sessions
    # (rough check: total lab sessions vs available pairs × labs)
    days        = set(ts.day_of_week for ts in time_slots)
    periods_per_day = {}
    for ts in time_slots:
        periods_per_day[ts.day_of_week] = periods_per_day.get(ts.day_of_week, 0) + 1
    total_pairs = sum(p // 2 for p in periods_per_day.values()) * len(lab_rooms)
    total_lab_sessions = sum(
        s.lectures_per_week for s in active_subjects if s.subject_type == "LAB"
    )
    if total_lab_sessions > total_pairs:
        warnings.append(
            f"OVERLOADED: {total_lab_sessions} lab sessions required but only "
            f"{total_pairs} lab-room-pair slots available. Add more labs or reduce load."
        )

    return warnings