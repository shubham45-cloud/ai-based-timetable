let directoryDatabase = [
    { id: "FAC-01", name: "Dr. Arun Kumar Tripathi", dept: "CSE", load: "16 hrs/w", tier: "Professor" },
    { id: "FAC-02", name: "Dr. Sangeeta Arora", dept: "CSE", load: "14 hrs/w", tier: "Associate Prof." },
    { id: "FAC-03", name: "Mr. Vivek Ranjan", dept: "IT", load: "16 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-04", name: "Dr. Deepak Upreti", dept: "CSE", load: "12 hrs/w", tier: "Professor" },
    { id: "FAC-05", name: "Dr. Kanika Singhal", dept: "CSE", load: "14 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-06", name: "Dr. Divya Singhal", dept: "IT", load: "16 hrs/w", tier: "Associate Prof." },
    { id: "FAC-07", name: "Ms. Nishu Niharika", dept: "CSE", load: "18 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-08", name: "Mr. Ajay Kumar", dept: "CSE", load: "14 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-09", name: "Ms. Pooja Sharma", dept: "IT", load: "12 hrs/w", tier: "Lecturer" },
    { id: "FAC-10", name: "Ms. Madhu", dept: "CSE", load: "16 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-11", name: "Mr. Anshul Varshney", dept: "CSE", load: "14 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-12", name: "Ms. Pooja Gupta", dept: "IT", load: "16 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-13", name: "Mr. Anurag Mishra", dept: "CSE", load: "12 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-14", name: "Ms. Arhina Ghosh", dept: "CSE", load: "14 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-15", name: "Ms. Bharti Kaushik", dept: "IT", load: "16 hrs/w", tier: "Associate Prof." },
    { id: "FAC-16", name: "Mr. Apoorv Jain", dept: "CSE", load: "18 hrs/w", tier: "Assistant Prof." },
    { id: "FAC-17", name: "Ms. Prashansa", dept: "CSE", load: "14 hrs/w", tier: "Lecturer" }
];

const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const cseSubjects = ["BCSE302L (Algo)", "BCSE401L (DBMS)", "BCSE202T (Java)", "BCSE409L (AI)"];
const itSubjects = ["BITE204L (Networks)", "BITE305L (Web Dev)", "BITE402P (Cloud)"];

function refreshAnalyticsCounters(currentSet) {
    document.getElementById("countFacultyMetric").innerText = currentSet.length;
    
    let completeAccumulatedHours = 0;
    currentSet.forEach(instructor => {
        const structuralIntNum = parseInt(instructor.load) || 0;
        completeAccumulatedHours += structuralIntNum;
    });
    
    document.getElementById("totalCombinedLoadDisplay").innerText = `${completeAccumulatedHours} hrs`;
}

function buildEngineGrid(activeSet) {
    const outputTarget = document.getElementById("facultyGridSystem");
    outputTarget.innerHTML = "";
    
    refreshAnalyticsCounters(directoryDatabase);

    if (activeSet.length === 0) {
        outputTarget.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 60px; font-weight: 600;">No records matching filter parameters.</div>`;
        return;
    }

    activeSet.forEach(item => {
        const structuralBlock = document.createElement("div");
        structuralBlock.className = "profile-container-card";
        const calculatedInitial = item.name.replace("Dr. ", "").replace("Mr. ", "").replace("Ms. ", "").charAt(0);

        structuralBlock.innerHTML = `
            <div>
                <div class="card-top-flex-header">
                    <div class="avatar-frame-box">
                        ${calculatedInitial}
                        <span class="live-status-dot"></span>
                    </div>
                    <button class="remove-faculty-action-btn" title="Remove Faculty Member" onclick="removeFacultyNode('${item.id}')">
                        <div class="trash-lid"></div>
                        <div class="trash-container"></div>
                    </button>
                </div>
                <div class="top-meta-block">
                    <h3>${item.name}</h3>
                    <div class="system-id-label">Identifier Token: <strong>${item.id}</strong></div>
                    <div class="pills-group">
                        <span class="tag-pill">${item.dept} Hub</span>
                        <span class="tag-pill alt">${item.tier}</span>
                    </div>
                </div>
            </div>
            <div>
                <div class="matrix-data-row">
                    <span>Weekly Constraint:</span>
                    <strong>${item.load}</strong>
                </div>
                <button class="view-schedule-btn" onclick="openMatrixSchedule('${item.id}', '${item.name}', '${item.dept}', '${item.tier}')">
                    View Matrix Schedule →
                </button>
            </div>
        `;
        outputTarget.appendChild(structuralBlock);
    });
}

function removeFacultyNode(targetId) {
    if (confirm(`Are you sure you want to remove the faculty member (${targetId})?`)) {
        directoryDatabase = directoryDatabase.filter(faculty => faculty.id !== targetId);
        
        const activeSearchToken = document.getElementById("liveSearchEngine").value.toLowerCase().trim();
        const filteredSet = directoryDatabase.filter(node => 
            node.name.toLowerCase().includes(activeSearchToken) || node.id.toLowerCase().includes(activeSearchToken)
        );
        
        buildEngineGrid(filteredSet);
    }
}

// Mapped Schedules Visual Modal Builder
function openMatrixSchedule(facultyId, facultyName, department, tier) {
    document.getElementById("modalFacultyName").innerText = facultyName;
    document.getElementById("modalFacultyId").innerText = `${tier} • ${department} Department Hub • ID: ${facultyId}`;
    const tableBody = document.getElementById("modalTimetableBody");
    tableBody.innerHTML = ""; 

    const facultyNumericSeed = parseInt(facultyId.split('-')[1]) || 7;
    const subjectPool = (department === "CSE") ? cseSubjects : itSubjects;

    daysOfWeek.forEach((day, dayIndex) => {
        const row = document.createElement("tr");
        let slotsContent = [];

        for (let slotIndex = 1; slotIndex <= 3; slotIndex++) {
            const patternFactor = (facultyNumericSeed * slotIndex + dayIndex) % 4;
            if (patternFactor === 1) {
                const targetBatch = `${department}-${(facultyNumericSeed % 2 === 0) ? 'A' : 'B'}`;
                const subject = subjectPool[(facultyNumericSeed + slotIndex) % subjectPool.length];
                slotsContent.push(`<span class="matrix-slot-badge busy">${subject} [${targetBatch}]</span>`);
            } else if (patternFactor === 2) {
                slotsContent.push(`<span class="matrix-slot-badge busy">Lab Session</span>`);
            } else {
                slotsContent.push(`<span class="matrix-slot-badge">Available</span>`);
            }
        }

        row.innerHTML = `<td style="font-weight:600;">${day}</td><td>${slotsContent[0]}</td><td>${slotsContent[1]}</td><td>${slotsContent[2]}</td>`;
        tableBody.appendChild(row);
    });
    document.getElementById("scheduleModalOverlay").classList.add("active");
}

/* CONTROLLERS FOR REGISTER FORM DYNAMICS */
const addFacultyFormOverlay = document.getElementById("addFacultyFormOverlay");

document.getElementById("openAddFacultyFormBtn").addEventListener("click", () => {
    addFacultyFormOverlay.classList.add("active");
});

function closeRegistrationForm() {
    addFacultyFormOverlay.classList.remove("active");
    document.getElementById("newInstructorRegistrationForm").reset();
}

document.getElementById("closeFormAction").addEventListener("click", closeRegistrationForm);

document.getElementById("newInstructorRegistrationForm").addEventListener("submit", (e) => {
    e.preventDefault();

    const nameVal = document.getElementById("inputFacultyName").value.trim();
    const deptVal = document.getElementById("selectDepartment").value;
    const tierVal = document.getElementById("selectTier").value;
    const loadVal = document.getElementById("inputWorkload").value;

    const sequenceToken = directoryDatabase.length + 1;
    const computedId = `FAC-${sequenceToken < 10 ? '0' + sequenceToken : sequenceToken}`;

    const newlyCreatedNode = {
        id: computedId,
        name: nameVal,
        dept: deptVal,
        load: `${loadVal} hrs/w`,
        tier: tierVal
    };

    directoryDatabase.unshift(newlyCreatedNode);
    buildEngineGrid(directoryDatabase);
    closeRegistrationForm();
});

document.getElementById("closeModalAction").addEventListener("click", () => {
    document.getElementById("scheduleModalOverlay").classList.remove("active");
});

document.getElementById("liveSearchEngine").addEventListener("input", (e) => {
    const structuralToken = e.target.value.toLowerCase().trim();
    const operationalOutput = directoryDatabase.filter(node => 
        node.name.toLowerCase().includes(structuralToken) || node.id.toLowerCase().includes(structuralToken)
    );
    buildEngineGrid(operationalOutput);
});

buildEngineGrid(directoryDatabase);