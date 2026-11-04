
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
const messageBox = document.querySelector<HTMLDivElement>("#form-message");
const pathsError = document.querySelector<HTMLSpanElement>("#paths-error");

if (!form || !pathsList || !addPathButton || !messageBox || !pathsError) {
    throw new Error("The scenario creation form is missing required elements.");
}

function showMessage(message: string, isSuccess = false): void {
    messageBox!.textContent = message;
    messageBox!.classList.add("visible");
    messageBox!.classList.toggle("success", isSuccess);
}

function clearMessage(): void {
    messageBox!.textContent = "";
    messageBox!.classList.remove("visible", "success");
}

function setFieldError(fieldId: string, message: string): void {
    const field = document.getElementById(fieldId) as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null;
    const error = document.querySelector<HTMLElement>(`[data-error-for="${fieldId}"]`);

    if (field) {
        field.setCustomValidity(message);
        field.classList.toggle("input-invalid", message.length > 0);
    }

    if (error) {
        error.textContent = message;
    }
}

function addPathRow(): void {
    const row = document.createElement("div");
    row.className = "parameter-row path-row";

    const nameLabel = document.createElement("label");
    nameLabel.textContent = "Path name";

    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.placeholder = "Path 1";
    nameInput.className = "path-name";
    nameInput.required = true;
    nameLabel.append(nameInput);

    const bandwidthLabel = document.createElement("label");
    bandwidthLabel.textContent = "Bandwidth (Mbps)";

    const bandwidthInput = document.createElement("input");
    bandwidthInput.type = "number";
    bandwidthInput.min = "0";
    bandwidthInput.step = "any";
    bandwidthInput.value = "100";
    bandwidthInput.className = "path-bandwidth";
    bandwidthInput.required = true;
    bandwidthLabel.append(bandwidthInput);

    const delayLabel = document.createElement("label");
    delayLabel.textContent = "Delay (ms)";

    const delayInput = document.createElement("input");
    delayInput.type = "number";
    delayInput.min = "0";
    delayInput.step = "any";
    delayInput.value = "20";
    delayInput.className = "path-delay";
    delayInput.required = true;
    delayLabel.append(delayInput);

    const jitterLabel = document.createElement("label");
    jitterLabel.textContent = "Jitter (ms)";

    const jitterInput = document.createElement("input");
    jitterInput.type = "number";
    jitterInput.min = "0";
    jitterInput.step = "any";
    jitterInput.value = "2";
    jitterInput.className = "path-jitter";
    jitterInput.required = true;
    jitterLabel.append(jitterInput);

    const packetLossLabel = document.createElement("label");
    packetLossLabel.textContent = "Packet loss (0-1)";

    const packetLossInput = document.createElement("input");
    packetLossInput.type = "number";
    packetLossInput.min = "0";
    packetLossInput.max = "1";
    packetLossInput.step = "any";
    packetLossInput.value = "0";
    packetLossInput.className = "path-packet-loss";
    packetLossInput.required = true;
    packetLossLabel.append(packetLossInput);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-parameter";
    removeButton.textContent = "Remove";
    removeButton.addEventListener("click", () => row.remove());

    row.append(
        nameLabel,
        bandwidthLabel,
        delayLabel,
        jitterLabel,
        packetLossLabel,
        removeButton
    );

    pathsList!.append(row);
    nameInput.focus();
}

function validatePaths(): boolean {
    const rows = pathsList!.querySelectorAll<HTMLDivElement>(".path-row");

    pathsError!.textContent = "";

    if (rows.length === 0) {
        pathsError!.textContent = "At least one network path is required.";
        return false;
    }

    let valid = true;

    for (const row of rows) {
        const nameInput = row.querySelector<HTMLInputElement>(".path-name");
        const bandwidthInput = row.querySelector<HTMLInputElement>(".path-bandwidth");
        const delayInput = row.querySelector<HTMLInputElement>(".path-delay");
        const jitterInput = row.querySelector<HTMLInputElement>(".path-jitter");
        const packetLossInput = row.querySelector<HTMLInputElement>(".path-packet-loss");

        if (!nameInput || !bandwidthInput || !delayInput || !jitterInput || !packetLossInput) {
            valid = false;
            continue;
        }

        const inputs = [
            nameInput,
            bandwidthInput,
            delayInput,
            jitterInput,
            packetLossInput
        ];

        for (const input of inputs) {
            input.setCustomValidity("");
            input.classList.remove("input-invalid");
        }

        if (nameInput.value.trim().length === 0) {
            nameInput.setCustomValidity("Path name is required.");
            nameInput.classList.add("input-invalid");
            valid = false;
        }

        for (const input of [
            bandwidthInput,
            delayInput,
            jitterInput,
            packetLossInput
        ]) {
            if (!Number.isFinite(input.valueAsNumber) || input.valueAsNumber < 0) {
                input.setCustomValidity("Enter a valid non-negative number.");
                input.classList.add("input-invalid");
                valid = false;
            }
        }

        if (packetLossInput.valueAsNumber > 1) {
            packetLossInput.setCustomValidity("Packet loss must be between 0 and 1.");
            packetLossInput.classList.add("input-invalid");
            valid = false;
        }
    }

    if (!valid) {
        pathsError!.textContent = "One or more network paths are invalid.";
    }

    return valid;
}

function validateForm(): boolean {
    clearMessage();
    pathsError!.textContent = "";

    const idInput = document.querySelector<HTMLInputElement>("#scenario-id");
    const nameInput = document.querySelector<HTMLInputElement>("#name");
    const durationInput = document.querySelector<HTMLInputElement>("#duration-seconds");
    const repetitionsInput = document.querySelector<HTMLInputElement>("#repetitions");
    const receiverConsumptionInput = document.querySelector<HTMLInputElement>("#receiver-consumption");

    if (!idInput || !nameInput || !durationInput || !repetitionsInput || !receiverConsumptionInput) {
        showMessage("The form is incomplete. Please reload the page.");
        return false;
    }

    setFieldError(
        "scenario-id",
        scenarioIdPattern.test(idInput.value)
            ? ""
            : "Use lowercase letters, digits and hyphens; start with a letter and do not end with a hyphen."
    );

    setFieldError(
        "name",
        nameInput.value.trim().length > 0 ? "" : "Scenario name is required."
    );

    setFieldError(
        "duration-seconds",
        Number.isFinite(durationInput.valueAsNumber) && durationInput.valueAsNumber >= 0
            ? ""
            : "Duration must be a non-negative number."
    );

    setFieldError(
        "repetitions",
        Number.isSafeInteger(repetitionsInput.valueAsNumber) && repetitionsInput.valueAsNumber >= 1
            ? ""
            : "Repetitions must be a positive integer."
    );

    setFieldError(
        "receiver-consumption",
        Number.isFinite(receiverConsumptionInput.valueAsNumber) &&
        receiverConsumptionInput.valueAsNumber >= 0
            ? ""
            : "Receiver consumption must be a non-negative number."
    );

    validatePaths();

    const valid = form!.checkValidity() && validatePaths();

    if (!valid) {
        form!.reportValidity();
        showMessage("Please correct the highlighted fields before creating the scenario.");
    }

    return valid;
}

function buildScenario(): { id: string; databaseEntry: Record<string, Scenario> } {
    const id = (document.querySelector<HTMLInputElement>("#scenario-id")?.value ?? "").trim();

    const paths: NetworkPath[] = [];

    for (const row of pathsList!.querySelectorAll<HTMLDivElement>(".path-row")) {
        const name = row.querySelector<HTMLInputElement>(".path-name")?.value.trim() ?? "";
        const bandwidth = row.querySelector<HTMLInputElement>(".path-bandwidth")?.valueAsNumber;
        const delay = row.querySelector<HTMLInputElement>(".path-delay")?.valueAsNumber;
        const jitter = row.querySelector<HTMLInputElement>(".path-jitter")?.valueAsNumber;
        const packetLoss = row.querySelector<HTMLInputElement>(".path-packet-loss")?.valueAsNumber;

        paths.push({
            name,
            bandwidthMbps: bandwidth!,
            delayMs: delay!,
            jitterMs: jitter!,
            packetLossPercent: packetLoss!
        });
    }

    const scenario: Scenario = {
        name: document.querySelector<HTMLInputElement>("#name")!.value.trim(),
        description: document.querySelector<HTMLTextAreaElement>("#description")!.value.trim(),
        durationSeconds: document.querySelector<HTMLInputElement>("#duration-seconds")!.valueAsNumber,
        repetitions: document.querySelector<HTMLInputElement>("#repetitions")!.valueAsNumber,
        receiverConsumptionMbps: document.querySelector<HTMLInputElement>("#receiver-consumption")!.valueAsNumber,
        paths
    };

    // The schema describes the entire database, so the new record is wrapped
    // in an object whose property name is the scenario ID.
    return { id, databaseEntry: { [id]: scenario } };
}

addPathButton.addEventListener("click", addPathRow);

form.addEventListener("submit", async (event: SubmitEvent) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    const submitButton = form!.querySelector<HTMLButtonElement>('button[type="submit"]');

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Creating...";
    }

    try {
        const { databaseEntry } = buildScenario();

        const response = await fetch(form!.action, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(databaseEntry)
        });

        if (!response.ok) {
            const responseText = await response.text();
            throw new Error(responseText || `Request failed with status ${response.status}.`);
        }

        window.location.assign(form!.dataset.successUrl!);

    } catch (error) {
        const message = error instanceof Error ? error.message : "An unexpected error occurred.";
        showMessage(`Could not create scenario: ${message}`);

        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = "Create scenario";
        }
    }
});

addPathRow();

export {};
