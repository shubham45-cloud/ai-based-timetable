let infrastructureDatabase = [
    { name: "CR-101", type: "CLASSROOM", capacity: 60, status: "Available" },
    { name: "CR-102", type: "CLASSROOM", capacity: 60, status: "Available" },
    { name: "CR-103", type: "CLASSROOM", capacity: 65, status: "Occupied" },
    { name: "CR-104", type: "CLASSROOM", capacity: 70, status: "Available" },
    { name: "CR-105", type: "CLASSROOM", capacity: 60, status: "Available" },
    { name: "LAB-101", type: "LAB", capacity: 40, status: "Available" },
    { name: "LAB-102", type: "LAB", capacity: 45, status: "Occupied" },
    { name: "LAB-103", type: "LAB", capacity: 35, status: "Available" }
];

let currentActiveFilter = "all";

function updateAnalyticsDashboard(dataset) {
    document.getElementById("countRoomsMetric").innerText = dataset.length;
    document.getElementById("countClassroomsMetric").innerText = dataset.filter(item => item.type === "CLASSROOM").length;
    document.getElementById("countLabsMetric").innerText = dataset.filter(item => item.type === "LAB").length;
}

function renderResourceMatrixGrid(activeSet) {
    const targetGrid = document.getElementById("roomsGridSystem");
    targetGrid.innerHTML = "";

    updateAnalyticsDashboard(infrastructureDatabase);

    if (activeSet.length === 0) {
        targetGrid.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:#94a3b8; padding:50px; font-weight:600;">No asset items match your parameters.</div>`;
        return;
    }

    activeSet.forEach(asset => {
        const structuralCard = document.createElement("div");
        structuralCard.className = "room-container-card";

        const typeBadgeStyle = asset.type.toLowerCase() === 'classroom' ? 'classroom' : 'lab';
        const statusBadgeStyle = asset.status.toLowerCase() === 'available' ? 'available' : 'occupied';

        structuralCard.innerHTML = `
            <div>
                <div class="card-top-flex-header">
                    <div class="room-tag-name">${asset.name}</div>
                    <button class="remove-room-action-btn" title="Purge Asset Location" onclick="removeAssetNode('${asset.name}')">
                        <div class="trash-lid"></div>
                        <div class="trash-container"></div>
                    </button>
                </div>
                <div class="pills-group">
                    <span class="tag-pill ${typeBadgeStyle}">${asset.type}</span>
                    <!-- FEATURE 2: CLICK TO TOGGLE STATUS (Conflict Avoidance Manual Override) -->
                    <span class="tag-pill ${statusBadgeStyle}" title="Click to manually override status link" onclick="toggleAssetStatus('${asset.name}')">${asset.status}</span>
                </div>
            </div>
            <div>
                <div class="matrix-data-row">
                    <span>Routing Limit:</span>
                    <strong>${asset.capacity} Max Seats</strong>
                </div>
                <!-- FEATURE 3: ALLOCATED ROW TIMELINE TRACKER -->
                <button class="room-timeline-btn" onclick="openSpaceTimeline('${asset.name}', '${asset.type}')">View Allocated Grid Tracker →</button>
            </div>
        `;
        targetGrid.appendChild(structuralCard);
    });
}

// TOGGLE ACTION CORE LOGIC (Changes available to occupied on fly click)
function toggleAssetStatus(roomName) {
    const itemIndex = infrastructureDatabase.findIndex(room => room.name === roomName);
    if(itemIndex !== -1) {
        infrastructureDatabase[itemIndex].status = (infrastructureDatabase[itemIndex].status === "Available") ? "Occupied" : "Available";
        runMasterFiltersPipeline();
    }
}

// FEATURE 1: ONE-CLICK QUICK MULTI-STAGE FILTERS SYSTEM
function applySmartFilter(filterType, element) {
    currentActiveFilter = filterType;
    document.querySelectorAll('.filter-pill-btn').forEach(btn => btn.classList.remove('active'));
    if(element) element.classList.add('active');
    runMasterFiltersPipeline();
}

function runMasterFiltersPipeline() {
    const searchToken = document.getElementById("roomLiveSearch").value.toLowerCase().trim();
    
    let processedResults = infrastructureDatabase.filter(room => 
        room.name.toLowerCase().includes(searchToken)
    );

    if (currentActiveFilter !== "all") {
        if (currentActiveFilter === "CLASSROOM" || currentActiveFilter === "LAB") {
            processedResults = processedResults.filter(room => room.type === currentActiveFilter);
        } else if (currentActiveFilter === "Available" || currentActiveFilter === "Occupied") {
            processedResults = processedResults.filter(room => room.status === currentActiveFilter);
        }
    }
    renderResourceMatrixGrid(processedResults);
}

// SPACE ALLOCATED TIMELINE CONTROLLER POPUP SYSTEM (AI Matrix Data)
function openSpaceTimeline(roomName, type) {
    document.getElementById("timelineTargetTitle").innerText = `Allocation Timeline: ${roomName}`;
    const tBody = document.getElementById("timelineTableBody");
    tBody.innerHTML = "";

    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    
    // Creates a pseudo-deterministic dynamic row footprint layout per room indexing values
    const roomSeed = roomName.charCodeAt(roomName.length - 1) || 5;

    days.forEach((day, index) => {
        const row = document.createElement("tr");
        
        const slot1State = ((roomSeed + index) % 3 === 0) ? `<span class="slot-pill allocated">Assigned (CSE-A)</span>` : `<span class="slot-pill free">Vacant / Idle</span>`;
        const slot2State = ((roomSeed * index) % 2 === 0) ? `<span class="slot-pill allocated">Assigned (IT-B)</span>` : `<span class="slot-pill free">Vacant / Idle</span>`;
        const slot3State = (index === 2 || index === 4) ? `<span class="slot-pill allocated">Lab Practice</span>` : `<span class="slot-pill free">Vacant / Idle</span>`;

        row.innerHTML = `
            <td style="font-weight:700; color:var(--text-main);">${day}</td>
            <td>${slot1State}</td>
            <td>${slot2State}</td>
            <td>${slot3State}</td>
        `;
        tBody.appendChild(row);
    });

    document.getElementById("roomTimelineOverlay").classList.add("active");
}

function closeTimelineModal() {
    document.getElementById("roomTimelineOverlay").classList.remove("active");
}

function removeAssetNode(targetRoomName) {
    if (confirm(`Purge infrastructure resource location (${targetRoomName}) from core router paths?`)) {
        infrastructureDatabase = infrastructureDatabase.filter(room => room.name !== targetRoomName);
        runMasterFiltersPipeline();
    }
}

// ADD RESOURCE TRIGGER HANDLERS
const addRoomFormOverlay = document.getElementById("addRoomFormOverlay");
document.getElementById("openAddRoomFormBtn").addEventListener("click", () => addRoomFormOverlay.classList.add("active"));
function closeFormWindow() { addRoomFormOverlay.classList.remove("active"); document.getElementById("newRoomRegistrationForm").reset(); }
document.getElementById("closeFormAction").addEventListener("click", closeFormWindow);

document.getElementById("newRoomRegistrationForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const nameVal = document.getElementById("inputRoomName").value.trim().toUpperCase();
    const typeVal = document.getElementById("selectRoomType").value;
    const capacityVal = document.getElementById("inputCapacity").value;
    const statusVal = document.getElementById("selectStatus").value;

    if(infrastructureDatabase.some(room => room.name === nameVal)) {
        alert("An asset record matching this room tag reference token already exists.");
        return;
    }

    infrastructureDatabase.unshift({ name: nameVal, type: typeVal, capacity: parseInt(capacityVal), status: statusVal });
    runMasterFiltersPipeline();
    closeFormWindow();
});

document.getElementById("roomLiveSearch").addEventListener("input", runMasterFiltersPipeline);

// Initialize setup execution
renderResourceMatrixGrid(infrastructureDatabase);