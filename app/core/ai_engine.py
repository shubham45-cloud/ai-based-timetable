from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from .. import crud


def generate_timetable_logic(db: Session):

    audit_results = run_data_audit(db)
    if audit_results:
        return {
            "status": "error",
            "message": "Data Audit Failed",
            "details": audit_results
        }

    # ------------------------
    # 1️⃣ Fetch Data
    # ------------------------
    teachers = crud.get_all_teachers(db)
    subjects = crud.get_all_subjects(db)
    rooms = crud.get_all_rooms(db)
    time_slots = crud.get_all_time_slots(db)
    teacher_subject_links = crud.get_all_teacher_subjects(db)

    print(f"--- SIH AI DIAGNOSTICS ---")
    print(f"Branches: {len(set(s.dept_id for s in subjects))}")
    print(f"Subjects: {len(subjects)} | Teachers: {len(teachers)} | Rooms: {len(rooms)}")

    model = cp_model.CpModel()
    assignments = {}

    # ------------------------
    # Teacher–Subject map
    # ------------------------
    teacher_for_subject = {}
    for link in teacher_subject_links:
        teacher_for_subject.setdefault(link.subject_id, []).append(link.teacher_id)

    # ------------------------
    # 2️⃣ Decision Variables
    # x[sub, ts, room]
    # ------------------------
    for sub in subjects:
        for ts in time_slots:
            for r in rooms:
                assignments[(sub.subject_id, ts.timeslot_id, r.room_id)] = model.NewBoolVar(
                    f"s{sub.subject_id}_ts{ts.timeslot_id}_r{r.room_id}"
                )

    # ------------------------
    # 3️⃣ HARD CONSTRAINTS
    # ------------------------

    branches = set(s.dept_id for s in subjects)

    # 🔥 3a️⃣ EXACTLY ONE lecture per branch per slot (NO EMPTY BLOCKS)
    for branch in branches:
        branch_subjects = [
            s.subject_id for s in subjects if s.dept_id == branch
        ]

        for ts in time_slots:
            model.AddExactlyOne(
                assignments[k]
                for k in assignments
                if k[0] in branch_subjects and k[1] == ts.timeslot_id
            )

    # 3b️⃣ Room cannot be used twice at same time
    for r in rooms:
        for ts in time_slots:
            model.AddAtMostOne(
                assignments[k]
                for k in assignments
                if k[1] == ts.timeslot_id and k[2] == r.room_id
            )

    # 3c️⃣ Teacher cannot teach two classes at same time
    for t in teachers:
        for ts in time_slots:
            model.AddAtMostOne(
                assignments[k]
                for k in assignments
                if k[1] == ts.timeslot_id
                and t.teacher_id in teacher_for_subject.get(k[0], [])
            )

    # 3d️⃣ Weekly lecture requirement per subject
    for sub in subjects:
        model.Add(
            sum(
                assignments[k]
                for k in assignments
                if k[0] == sub.subject_id
            ) == sub.lectures_per_week
        )
        # ------------------------
# 👨‍🏫 MAX 2 LECTURES PER DAY PER TEACHER
# ------------------------
    MAX_LECTURES_PER_DAY = 4

    for t in teachers:
        for day in set(ts.day_of_week for ts in time_slots):
            model.Add(
                 sum(
                assignments[k]
                for k in assignments
                if t.teacher_id in teacher_for_subject.get(k[0], [])
                and any(
                    ts.timeslot_id == k[1] and ts.day_of_week == day
                    for ts in time_slots
                )
            ) <= MAX_LECTURES_PER_DAY
        )
    # ------------------------
# 👨‍🏫 NO MORE THAN 2 CONSECUTIVE PERIODS PER TEACHER
# ------------------------

    for t in teachers:
       for day in set(ts.day_of_week for ts in time_slots):

        # sort periods of the day
        day_slots = sorted(
            [ts for ts in time_slots if ts.day_of_week == day],
            key=lambda x: x.period_no
        )

        # sliding window of size 3
        for i in range(len(day_slots) - 2):
            ts1, ts2, ts3 = day_slots[i], day_slots[i+1], day_slots[i+2]

            model.Add(
                sum(
                    assignments[k]
                    for k in assignments
                    if k[1] in {ts1.timeslot_id, ts2.timeslot_id, ts3.timeslot_id}
                    and t.teacher_id in teacher_for_subject.get(k[0], [])
                ) <= 2
            )



    # ------------------------
    # 4️⃣ Solve
    # ------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        crud.clear_timetable(db)

        ts_map = {
            ts.timeslot_id: (ts.day_of_week, ts.period_no)
            for ts in time_slots
        }

        for (sub_id, ts_id, r_id), var in assignments.items():
            if solver.Value(var) == 1:
                day, period = ts_map[ts_id]

                teacher_id = teacher_for_subject[sub_id][0]

                entry = {
                    "day_of_week": day,
                    "period_no": period,
                    "subject_id": sub_id,
                    "teacher_id": teacher_id,
                    "room_id": r_id
                }
                crud.save_timetable_entry(db, entry)

        db.commit()
        return {
            "status": "success",
            "message": "FULL college-level timetable generated successfully!"
        }

    return {
        "status": "error",
        "message": "INFEASIBLE: Not enough teachers / rooms for full timetable"
    }


def run_data_audit(db: Session):
    warnings = []

    subjects = crud.get_all_subjects(db)
    rooms = crud.get_all_rooms(db)
    time_slots = crud.get_all_time_slots(db)
    teacher_subjects = crud.get_all_teacher_subjects(db)

    branches = set(s.dept_id for s in subjects)

    if len(branches) > len(rooms):
        warnings.append(
            f"CRITICAL: {len(branches)} branches but only {len(rooms)} rooms."
        )

    qualified_subjects = {ts.subject_id for ts in teacher_subjects}
    for sub in subjects:
        if sub.subject_id not in qualified_subjects:
            warnings.append(
                f"MISSING: No teacher assigned for {sub.subject_name}"
            )

    total_required = sum(s.lectures_per_week for s in subjects)
    total_available = len(branches) * len(time_slots)

    if total_required != total_available:
        warnings.append(
            f"LOAD MISMATCH: Required {total_required}, available {total_available}"
        )

    return warnings
