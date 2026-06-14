let curriculumDatabase = [
    { id: "101", title: "AICE", type: "THEORY", credits: 3, allocation: "CSE - 6th Sem", aiRule: "Preferred Morning Slot", eligibleFaculty: ["Dr. Arun Kumar Tripathi", "Dr. Deepak Upreti"] },
    { id: "102", title: "Foundations of CyberSec", type: "THEORY", credits: 4, allocation: "CSE - 4th Sem", aiRule: "Max 1 Per Day Limit", eligibleFaculty: ["Dr. Sangeeta Arora", "Mr. Anshul Varshney"] },
    { id: "103", title: "Django Framework", type: "THEORY", credits: 3, allocation: "IT - 4th Sem", aiRule: "Requires Smart Room", eligibleFaculty: ["Mr. Vivek Ranjan", "Ms. Pooja Gupta"] },
    { id: "111", title: "DBMS", type: "THEORY", credits: 3, allocation: "CSE - 4th Sem", aiRule: "Standard Slot Allocation", eligibleFaculty: ["Dr. Kanika Singhal", "Ms. Madhu"] },
    { id: "112", title: "DSA-II", type: "THEORY", credits: 4, allocation: "CSE - 4th Sem", aiRule: "Consecutive Rule Checked", eligibleFaculty: ["Mr. Ajay Kumar", "Mr. Anurag Mishra"] },
    { id: "113", title: "Big Data Analytics", type: "THEORY", credits: 3, allocation: "CSE - 6th Sem", aiRule: "Preferred Afternoon", eligibleFaculty: ["Dr. Divya Singhal", "Ms. Arhina Ghosh"] },
    { id: "114", title: "Data Analytics", type: "THEORY", credits: 3, allocation: "IT - 4th Sem", aiRule: "Standard Slot Allocation", eligibleFaculty: ["Ms. Pooja Sharma", "Ms. Bharti Kaushik"] },
    { id: "115", title: "DBMS Lab", type: "LAB", credits: 1, allocation: "CSE - 4th Sem", aiRule: "Continuous 2-Slot Rule", eligibleFaculty: ["Dr. Kanika Singhal", "Ms. Madhu"] },
    { id: "116", title: "DSA-II Lab", type: "LAB", credits: 2, allocation: "CSE - 4th Sem", aiRule: "Continuous 2-Slot Rule", eligibleFaculty: ["Mr. Ajay Kumar", "Ms. Prashansa"] },
    { id: "117", title: "Web Tech Lab", type: "LAB", credits: 1, allocation: "IT - 4th Sem", aiRule: "Continuous 2-Slot Rule", eligibleFaculty: ["Mr. Vivek Ranjan", "Ms. Pooja Gupta"] },
    { id: "118", title: "Mini Project", type: "LAB", credits: 2, allocation: "CSE - 6th Sem", aiRule: "Continuous 3-Slot Rule", eligibleFaculty: ["Dr. Arun Kumar Tripathi", "Ms. Nishu Niharika"] }
];

let currentActiveFilter = "all";

function updateAnalyticsDashboard(dataset) {
    document.getElementById("countSubjectsMetric").innerText = dataset.length;
    document.getElementById("countTheoryMetric").innerText = dataset.filter(item => item.type === "THEORY").length;
    document.getElementById("countLabMetric").innerText = dataset.filter(item => item.type === "LAB").length;
}

function renderCurriculumMatrixGrid(activeSet) {
    const targetGrid = document.getElementById("subjectsGridSystem");
    targetGrid.innerHTML = ""; 

    updateAnalyticsDashboard(curriculumDatabase);

    if (activeSet.length === 0) {
        targetGrid.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:#94a3b8; padding:50px; font-weight:600;">No curriculum records matching criteria parameters.</div>`;
        return;
    }

    activeSet.forEach(module => {
        const structuralCard = document.createElement("div");
        structuralCard.className = "subject-container-card";
        const typeBadgeStyle = module.type.toLowerCase() === 'theory' ? 'theory' : 'lab';

        structuralCard.innerHTML = `
            <div>
                <div class="card-top-flex-header">
                    <div class="subject-id-token">Code/ID: ${module.id}</div>
                    <button class="remove-subject-action-btn" title="Purge Curriculum Module" onclick="removeSubjectNode('${module.id}')">
                        <div class="trash-lid"></div>
                        <div class="trash-container"></div>
                    </button>
                </div>
                <div class="subject-title">${module.title}</div>
                <div class="dept-semester-label">Target Scheme: <strong>${module.allocation}</strong></div>
            </div>
            <div>
                <div class="pills-group">
                    <span class="tag-pill ${typeBadgeStyle}">${module.type}</span>
                    <span class="tag-pill credit">${module.credits} Credits</span>
                    <span class="tag-pill ai-rule">⚙️ ${module.aiRule}</span>
                </div>
                <button class="faculty-eligibility-trigger" onclick="openFacultyMapping('${module.title}', '${module.eligibleFaculty.join(',')}')">
                    <span>Eligible Instructors</span>
                    <strong>${module.eligibleFaculty.length} Map →</strong>
                </button>
            </div>
        `;
        targetGrid.appendChild(structuralCard);
    });
}

function applySmartFilter(filterType, element) {
    currentActiveFilter = filterType;
    document.querySelectorAll('.filter-pill-btn').forEach(btn => btn.classList.remove('active'));
    if(element) element.classList.add('active');
    runMasterFiltersPipeline();
}

function runMasterFiltersPipeline() {
    const searchToken = document.getElementById("subjectLiveSearch").value.toLowerCase().trim();
    const dropdownSem = document.getElementById("dropdownSemesterFilter").value;
    
    let processedResults = curriculumDatabase.filter(module => 
        module.title.toLowerCase().includes(searchToken) || module.id.includes(searchToken)
    );

    // Dropdown structural alignment logic
    if (dropdownSem !== "all") {
        processedResults = processedResults.filter(module => module.allocation === dropdownSem);
    }

    // Horizontal pills sorting filter mapping
    if (currentActiveFilter !== "all") {
        if (currentActiveFilter === "THEORY" || currentActiveFilter === "LAB") {
            processedResults = processedResults.filter(module => module.type === currentActiveFilter);
        } else {
            const parsedCreditLimit = parseInt(currentActiveFilter);
            processedResults = processedResults.filter(module => module.credits === parsedCreditLimit);
        }
    }
    renderCurriculumMatrixGrid(processedResults);
}

// INTERACTIVE POPUP MODAL MAPPING SYSTEM FOR ELIGIBLE FACULTIES
function openFacultyMapping(subjectTitle, facultyString) {
    document.getElementById("modalMappingTitle").innerText = `Eligible for: ${subjectTitle}`;
    const listContainer = document.getElementById("modalFacultyListContainer");
    listContainer.innerHTML = ""; // Purge oldest stack

    const facultyArray = facultyString.split(",");
    facultyArray.forEach(prof => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `<span class="dot-icon"></span> ${prof}`;
        listContainer.appendChild(listItem);
    });

    document.getElementById("facultyMappingOverlay").classList.add("active");
}

function closeMappingModal() {
    document.getElementById("facultyMappingOverlay").classList.remove("active");
}

function removeSubjectNode(targetId) {
    if (confirm(`Remove course routing parameters for module asset validation ID: (${targetId})?`)) {
        curriculumDatabase = curriculumDatabase.filter(item => item.id !== targetId);
        runMasterFiltersPipeline();
    }
}

// POPUP FORM SYSTEM CONTROLLERS
const addSubjectFormOverlay = document.getElementById("addSubjectFormOverlay");
document.getElementById("openAddSubjectFormBtn").addEventListener("click", () => addSubjectFormOverlay.classList.add("active"));
function closeFormWindow() { addSubjectFormOverlay.classList.remove("active"); document.getElementById("newSubjectRegistrationForm").reset(); }
document.getElementById("closeFormAction").addEventListener("click", closeFormWindow);

document.getElementById("newSubjectRegistrationForm").addEventListener("submit", (e) => {
    e.preventDefault();

    const idVal = document.getElementById("inputSubjectId").value.trim();
    const titleVal = document.getElementById("inputSubjectTitle").value.trim();
    const semVal = document.getElementById("selectSemesterMapping").value;
    const typeVal = document.getElementById("selectSubjectType").value;
    const creditsVal = document.getElementById("selectCredits").value;

    if(curriculumDatabase.some(item => item.id === idVal)) {
        alert("A course template node matching this track verification token identifier already exists.");
        return;
    }

    curriculumDatabase.unshift({
        id: idVal,
        title: titleVal,
        type: typeVal,
        credits: parseInt(creditsVal),
        allocation: semVal,
        aiRule: typeVal === "LAB" ? "Continuous 2-Slot Rule" : "Standard Slot Allocation",
        eligibleFaculty: ["Dr. Arun Kumar Tripathi", "Dr. Sangeeta Arora"] // Default assign for new records demo
    });

    runMasterFiltersPipeline();
    closeFormWindow();
});

document.getElementById("subjectLiveSearch").addEventListener("input", runMasterFiltersPipeline);

renderCurriculumMatrixGrid(curriculumDatabase);