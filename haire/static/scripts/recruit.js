document.addEventListener("DOMContentLoaded", () => {
    const jobSelector = document.getElementById("job-selector");
    const filterInput = document.getElementById("filter-input");
    const refreshButton = document.getElementById("refresh-button");
    const clearButton = document.getElementById("clear-button");
    const applicantList = document.getElementById("applicant-list");

    const totalApplicants = document.getElementById("total-applicants");
    const averageScore = document.getElementById("average-score");
    const highestScore = document.getElementById("highest-score");
    const lowestScore = document.getElementById("lowest-score");

    let allCandidates = [];

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function getSkillList(candidate) {
        if (Array.isArray(candidate.skill_list) && candidate.skill_list.length) {
            return candidate.skill_list.slice(0, 4);
        }

        if (Array.isArray(candidate.skills)) {
            return candidate.skills.slice(0, 4);
        }

        if (typeof candidate.skills === "string") {
            return candidate.skills
                .split(",")
                .map((skill) => skill.trim())
                .filter(Boolean)
                .slice(0, 4);
        }

        return [];
    }

    function getCandidateSummary(candidate) {
        return candidate.candidate_summary
            || candidate.professional_summary
            || candidate.personal_summary
            || "No summary available.";
    }

    function populateJobTitles(jobTitles) {
        const selectedJob = jobSelector.value || "all";
        const uniqueTitles = [...new Set(jobTitles || [])];

        jobSelector.innerHTML = '<option value="all">All Jobs</option>';

        uniqueTitles.forEach((title) => {
            const option = document.createElement("option");
            option.value = title;
            option.textContent = title;
            jobSelector.appendChild(option);
        });

        if (uniqueTitles.includes(selectedJob)) {
            jobSelector.value = selectedJob;
        } else {
            jobSelector.value = "all";
        }
    }

    function renderStats(candidates) {
        const total = candidates.length;
        const scores = candidates.map((candidate) => Number(candidate.match_score || 0));

        const avg = total ? scores.reduce((sum, value) => sum + value, 0) / total : 0;
        const highest = total ? Math.max(...scores) : 0;
        const lowest = total ? Math.min(...scores) : 0;

        totalApplicants.textContent = String(total);
        totalApplicants.setAttribute("aria-label", `Total applicants: ${total}`);

        averageScore.textContent = `${Math.round(avg)}%`;
        averageScore.setAttribute("aria-label", `Average score: ${Math.round(avg)} percent`);

        highestScore.textContent = `${Math.round(highest)}%`;
        highestScore.setAttribute("aria-label", `Highest score: ${Math.round(highest)} percent`);

        lowestScore.textContent = `${Math.round(lowest)}%`;
        lowestScore.setAttribute("aria-label", `Lowest score: ${Math.round(lowest)} percent`);
    }

    function applyFilters() {
        const selectedJob = jobSelector.value || "all";
        const sortMode = filterInput.value || "highest-score";

        let filtered = allCandidates;

        if (selectedJob !== "all") {
            filtered = filtered.filter((candidate) => {
                return (candidate.job_title || "").trim().toLowerCase() === selectedJob.trim().toLowerCase();
            });
        }

        if (sortMode === "alphabetical") {
            filtered = [...filtered].sort((a, b) => {
                const aName = (a.full_name || "Unknown Candidate").toLowerCase();
                const bName = (b.full_name || "Unknown Candidate").toLowerCase();
                return aName.localeCompare(bName);
            });
        } else {
            filtered = [...filtered].sort((a, b) => {
                return Number(b.match_score || 0) - Number(a.match_score || 0);
            });
        }

        renderStats(filtered);

        if (!filtered.length) {
            applicantList.innerHTML = '<p class="empty-state">No applicants match the current filters.</p>';
            return;
        }

        applicantList.innerHTML = filtered.map((candidate) => {
            const name = escapeHtml(candidate.full_name || "Unknown Candidate");
            const score = Math.round(Number(candidate.match_score || 0));
            const skills = getSkillList(candidate);
            const summary = escapeHtml(getCandidateSummary(candidate));
            const displaySkills = skills.length
                ? skills.map((skill) => `<li>${escapeHtml(skill)}</li>`).join("")
                : "<li>Role Match</li>";

            return `
                <article class="applicant-card">
                    <div class="applicant-header">
                        <h3 class="applicant-name">${name}</h3>

                        <span class="score" aria-label="Applicant match score: ${score} percent">
                            ${score}% Match
                        </span>

                        <label class="select-applicant">
                            <input type="checkbox" name="application" value="${escapeHtml(candidate.id ?? "")}">
                            <span></span>
                        </label>
                    </div>

                    <button
                        class="more-info-button"
                        type="button"
                        aria-expanded="false"
                        aria-label="View more information about ${name}"
                    >
                        View More Info
                    </button>

                    <div class="more-information">
                        <div class="description-section">
                            <h4>Description</h4>
                            <p>${summary}</p>
                        </div>

                        <div class="qualification-section">
                            <h4>Top Matches</h4>
                            <ul>${displaySkills}</ul>
                        </div>
                    </div>
                </article>
            `;
        }).join("");

        applicantList.querySelectorAll(".more-info-button").forEach((button) => {
            button.addEventListener("click", () => {
                const infoPanel = button.nextElementSibling;
                const isOpen = infoPanel.classList.toggle("show");
                button.setAttribute("aria-expanded", String(isOpen));
            });
        });

        applicantList.querySelectorAll('input[name="application"]').forEach((checkbox) => {
            checkbox.addEventListener("change", () => {
                const card = checkbox.closest(".applicant-card");
                if (card) {
                    card.classList.toggle("selected", checkbox.checked);
                }
            });
        });
    }

    async function fetchCandidates() {
        refreshButton.disabled = true;
        refreshButton.textContent = "Refreshing...";

        try {
            const response = await fetch("/api/candidates");
            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Unable to load candidates");
            }

            allCandidates = Array.isArray(data.candidates) ? data.candidates : [];
            populateJobTitles(data.job_titles || []);

            applyFilters();
        } catch (error) {
            console.error(error);
            applicantList.innerHTML = '<p class="empty-state">Unable to load applicants right now.</p>';
            renderStats([]);
        } finally {
            refreshButton.disabled = false;
            refreshButton.textContent = "Refresh";
        }
    }

    jobSelector.addEventListener("change", applyFilters);
    filterInput.addEventListener("change", applyFilters);

    refreshButton.addEventListener("click", () => {
        fetchCandidates();
    });

    clearButton.addEventListener("click", () => {
        applicantList.querySelectorAll('input[name="application"]').forEach((checkbox) => {
            checkbox.checked = false;
            checkbox.closest(".applicant-card")?.classList.remove("selected");
        });
    });

    fetchCandidates();
});