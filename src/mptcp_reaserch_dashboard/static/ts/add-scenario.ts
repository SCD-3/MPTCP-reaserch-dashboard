interface NetworkPath {
    name: string;
    bandwidthMbps: number;
    delayMs: number;
    jitterMs: number;
    packetLossPercent: number;
}

interface Scenario {
    name: string;
    description: string;
    durationSeconds: number;
    repetitions: number;
    receiverConsumptionMbps: number;
    paths: NetworkPath[];
}

const scenarioIdPattern = /^[a-z](?:[a-z0-9-]*[a-z0-9])?$/;

const form = document.querySelector<HTMLFormElement>("#scenario-form");
const pathsList = document.querySelector<HTMLDivElement>("#paths-list");
const addPathButton = document.querySelector<HTMLButtonElement>("#add-path");
const pathsError = document.querySelector<HTMLParagraphElement>("#paths-error");
const formMessage = document.querySelector<HTMLDivElement>("#form-message");
const submitButton = document.querySelector<HTMLButtonElement>("#submit-button");

const scenarioIdInput = document.querySelector<HTMLInputElement>("#scenario-id");
const nameInput = document.querySelector<HTMLInputElement>("#name");
const descriptionInput = document.querySelector<HTMLTextAreaElement>("#description");
const durationInput = document.querySelector<HTMLInputElement>("#duration-seconds");
const repetitionsInput = document.querySelector<HTMLInputElement>("#repetitions");
const receiverConsumptionInput = document.querySelector<HTMLInputElement>("#receiver-consumption");

if (
    !form ||
    !pathsList ||
    !addPathButton ||
    !pathsError ||
    !formMessage ||
    !submitButton ||
    !scenarioIdInput ||
    !nameInput ||
    !descriptionInput ||
    !durationInput ||
    !repetitionsInput ||
    !receiverConsumptionInput
) {
    throw new Error("Scenario form elements are missing.");
}

function showMessage(message: string, isError: boolean = false): void {
    formMessage!.textContent = message;
    formMessage!.classList.toggle("error", isError);
}

function clearMessage(): void {
    formMessage!.textContent = "";
    formMessage!.classList.remove("error");
}

function addPath(): void {
    const row = document.createElement("div");
    row.className = "parameter-row path-row";

    row.innerHTML = `
        <div class="field-grid">
            <div class="field">
                <label>Path name</label>
                <input type="text" data-field="name" placeholder="Path 1" required>
            </div>

            <div class="field">
                <label>Bandwidth (Mbps)</label>
                <input type="number" data-field="bandwidthMbps" min="0" step="any" value="100" required>
            </div>

            <div class="field">
                <label>Delay (ms)</label>
                <input type="number" data-field="delayMs" min="0" step="any" value="20" required>
            </div>

            <div class="field">
                <label>Jitter (ms)</label>
                <input type="number" data-field="jitterMs" min="0" step="any" value="2" required>
            </div>

            <div class="field">
                <label>Packet loss (0–1)</label>
                <input type="number" data-field="packetLossPercent" min="0" max="1" step="any" value="0" required>
            </div>
        </div>

        <button type="button" class="remove-parameter" aria-label="Remove path">
            Remove
        </button>
    `;

    const removeButton = row.querySelector<HTMLButtonElement>(".remove-parameter");

    removeButton!.addEventListener("click", () => {
        row.remove();
        validatePaths();
    });

    row.querySelectorAll("input").forEach(input => {
        input.addEventListener("input", validatePaths);
    });

    pathsList!.appendChild(row);
    validatePaths();
}

function getPathRows(): HTMLDivElement[] {
    return Array.from(pathsList!.querySelectorAll<HTMLDivElement>(".path-row"));
}

function getPathInput(row: HTMLDivElement, field: string): HTMLInputElement {
    return row.querySelector<HTMLInputElement>(`[data-field="${field}"]`)!;
}

function validatePaths(): boolean {
    const rows = getPathRows();
    let valid = true;

    pathsError!.textContent = "";

    if (rows.length === 0) {
        pathsError!.textContent = "At least one network path is required.";
        return false;
    }

    for (const row of rows) {
        const name = getPathInput(row, "name");
        const bandwidth = getPathInput(row, "bandwidthMbps");
        const delay = getPathInput(row, "delayMs");
        const jitter = getPathInput(row, "jitterMs");
        const packetLoss = getPathInput(row, "packetLossPercent");

        const inputs = [name, bandwidth, delay, jitter, packetLoss];

        for (const input of inputs) {
            input.setCustomValidity("");
        }

        if (name.value.trim().length === 0) {
            name.setCustomValidity("Path name is required.");
            valid = false;
        }

        for (const input of [bandwidth, delay, jitter, packetLoss]) {
            if (!Number.isFinite(input.valueAsNumber) || input.valueAsNumber < 0) {
                input.setCustomValidity("Enter a number greater than or equal to zero.");
                valid = false;
            }
        }

        if (packetLoss.valueAsNumber > 1) {
            packetLoss.setCustomValidity("Packet loss must be between 0 and 1.");
            valid = false;
        }
    }

    return valid;
}

function validateForm(): boolean {
    let valid = true;

    clearMessage();

    scenarioIdInput!.setCustomValidity("");
    nameInput!.setCustomValidity("");
    durationInput!.setCustomValidity("");
    repetitionsInput!.setCustomValidity("");
    receiverConsumptionInput!.setCustomValidity("");

    if (!scenarioIdPattern.test(scenarioIdInput!.value)) {
        scenarioIdInput!.setCustomValidity(
            "ID must start with a lowercase letter and contain only lowercase letters, numbers, and hyphens."
        );
        valid = false;
    }

    if (nameInput!.value.trim().length === 0) {
        nameInput!.setCustomValidity("Scenario name is required.");
        valid = false;
    }

    if (!Number.isFinite(durationInput!.valueAsNumber) || durationInput!.valueAsNumber < 0) {
        durationInput!.setCustomValidity("Duration must be a non-negative number.");
        valid = false;
    }

    if (
        !Number.isSafeInteger(repetitionsInput!.valueAsNumber) ||
        repetitionsInput!.valueAsNumber < 1
    ) {
        repetitionsInput!.setCustomValidity("Repetitions must be a positive integer.");
        valid = false;
    }

    if (
        !Number.isFinite(receiverConsumptionInput!.valueAsNumber) ||
        receiverConsumptionInput!.valueAsNumber < 0
    ) {
        receiverConsumptionInput!.setCustomValidity(
            "Receiver consumption must be a non-negative number."
        );
        valid = false;
    }

    if (!validatePaths()) {
        valid = false;
    }

    return valid;
}

function buildScenario(): Record<string, Scenario> {
    const paths: NetworkPath[] = getPathRows().map(row => ({
        name: getPathInput(row, "name").value.trim(),
        bandwidthMbps: getPathInput(row, "bandwidthMbps").valueAsNumber,
        delayMs: getPathInput(row, "delayMs").valueAsNumber,
        jitterMs: getPathInput(row, "jitterMs").valueAsNumber,
        packetLossPercent: getPathInput(row, "packetLossPercent").valueAsNumber
    }));

    const scenario: Scenario = {
        name: nameInput!.value.trim(),
        description: descriptionInput!.value,
        durationSeconds: durationInput!.valueAsNumber,
        repetitions: repetitionsInput!.valueAsNumber,
        receiverConsumptionMbps: receiverConsumptionInput!.valueAsNumber,
        paths
    };

    return {
        [scenarioIdInput!.value.trim()]: scenario
    };
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    if (!validateForm()) {
        form!.reportValidity();
        return;
    }

    clearMessage();
    submitButton!.disabled = true;
    submitButton!.textContent = "Creating...";

    try {
        const response = await fetch(form!.action, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(buildScenario())
        });

        if (!response.ok) {
            const result = await response.json().catch(() => null);
            throw new Error(result?.error ?? `Request failed with status ${response.status}.`);
        }

        window.location.href = form!.dataset.successUrl!;
    } catch (error) {
        showMessage(
            error instanceof Error ? error.message : "An unexpected error occurred.",
            true
        );

        submitButton!.disabled = false;
        submitButton!.textContent = "Create Scenario";
    }
});

addPathButton.addEventListener("click", addPath);

// Start with one path, since the schema requires at least one.
addPath();

export {};