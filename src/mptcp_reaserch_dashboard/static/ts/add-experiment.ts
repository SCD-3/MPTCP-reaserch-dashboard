type ExperimentStatus =
    | "DRAFT"
    | "PLANNED"
    | "QUEUED"
    | "RUNNING"
    | "COMPLETED"
    | "FAILED"
    | "CANCELLED";

interface Experiment {
    name: string;
    scenarioId: string;
    environmentId: string;
    algorithmIds: string[];
    repetitions: number;
    status: ExperimentStatus;
}

const experimentIdPattern = /^[a-z](?:[a-z0-9-]*[a-z0-9])?$/;

const form = document.querySelector<HTMLFormElement>("#experiment-form");
const algorithmsList = document.querySelector<HTMLDivElement>("#algorithms-list");
const addAlgorithmButton = document.querySelector<HTMLButtonElement>("#add-algorithm");
const messageBox = document.querySelector<HTMLDivElement>("#form-message");
const algorithmsError = document.querySelector<HTMLSpanElement>("#algorithms-error");

if (!form || !algorithmsList || !addAlgorithmButton || !messageBox || !algorithmsError) {
    throw new Error("The experiment creation form is missing required elements.");
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
    const field = document.getElementById(fieldId) as
        HTMLInputElement | HTMLSelectElement | null;

    const error = document.querySelector<HTMLElement>(
        `[data-error-for="${fieldId}"]`
    );

    if (field) {
        field.setCustomValidity(message);
        field.classList.toggle("input-invalid", message.length > 0);
    }

    if (error) {
        error.textContent = message;
    }
}

function addAlgorithmRow(): void {
    const row = document.createElement("div");
    row.className = "parameter-row";

    const label = document.createElement("label");
    label.textContent = "Algorithm ID";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "algorithm-001";
    input.className = "algorithm-id";
    input.autocomplete = "off";

    label.append(input);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-parameter";
    removeButton.textContent = "Remove";

    removeButton.addEventListener("click", () => {
        row.remove();
    });

    row.append(label, removeButton);

    algorithmsList!.append(row);

    input.focus();
}

function validateForm(): boolean {
    clearMessage();
    algorithmsError!.textContent = "";

    const idInput = document.querySelector<HTMLInputElement>("#experiment-id");
    const nameInput = document.querySelector<HTMLInputElement>("#name");
    const scenarioInput = document.querySelector<HTMLInputElement>("#scenario-id");
    const environmentInput = document.querySelector<HTMLInputElement>("#environment-id");
    const repetitionsInput = document.querySelector<HTMLInputElement>("#repetitions");

    if (!idInput || !nameInput || !scenarioInput || !environmentInput || !repetitionsInput) {
        showMessage("The form is incomplete. Please reload the page.");
        return false;
    }

    setFieldError(
        "experiment-id",
        experimentIdPattern.test(idInput.value)
            ? ""
            : "Use lowercase letters, digits and hyphens; start with a letter and do not end with a hyphen."
    );

    setFieldError(
        "name",
        nameInput.value.trim().length > 0
            ? ""
            : "Name is required."
    );

    setFieldError(
        "scenario-id",
        experimentIdPattern.test(scenarioInput.value)
            ? ""
            : "Enter a valid scenario ID."
    );

    setFieldError(
        "environment-id",
        experimentIdPattern.test(environmentInput.value)
            ? ""
            : "Enter a valid environment ID."
    );

    const repetitions = Number(repetitionsInput.value);

    setFieldError(
        "repetitions",
        Number.isSafeInteger(repetitions) && repetitions >= 1
            ? ""
            : "Repetitions must be a positive integer."
    );

    const algorithmIds = new Set<string>();
    let algorithmError = "";

    const rows = algorithmsList!.querySelectorAll<HTMLDivElement>(".parameter-row");

    if (rows.length === 0) {
        algorithmError = "At least one algorithm is required.";
    }

    for (const row of rows) {
        const input = row.querySelector<HTMLInputElement>(".algorithm-id");

        if (!input) {
            continue;
        }

        const id = input.value.trim();

        input.setCustomValidity("");
        input.classList.remove("input-invalid");

        if (!experimentIdPattern.test(id)) {
            input.setCustomValidity("Enter a valid algorithm ID.");
            input.classList.add("input-invalid");

            algorithmError = "One or more algorithm IDs are invalid.";
        } else if (algorithmIds.has(id)) {
            input.setCustomValidity("Algorithm IDs must be unique.");
            input.classList.add("input-invalid");

            algorithmError = `Duplicate algorithm ID: ${id}.`;
        } else {
            algorithmIds.add(id);
        }
    }

    algorithmsError!.textContent = algorithmError;

    const valid = form!.checkValidity() && algorithmError.length === 0;

    if (!valid) {
        form!.reportValidity();
        showMessage("Please correct the highlighted fields before creating the experiment.");
    }

    return valid;
}

function buildExperiment(): {
    id: string;
    databaseEntry: Record<string, Experiment>;
} {
    const id = (
        document.querySelector<HTMLInputElement>("#experiment-id")?.value ?? ""
    ).trim();

    const algorithmIds = Array.from(
        algorithmsList!.querySelectorAll<HTMLInputElement>(".algorithm-id")
    ).map(input => input.value.trim());

    const experiment: Experiment = {
        name: document.querySelector<HTMLInputElement>("#name")!.value.trim(),

        scenarioId: document.querySelector<HTMLInputElement>("#scenario-id")!.value.trim(),

        environmentId: document.querySelector<HTMLInputElement>("#environment-id")!.value.trim(),

        algorithmIds,

        repetitions: Number(
            document.querySelector<HTMLInputElement>("#repetitions")!.value
        ),

        status: document.querySelector<HTMLSelectElement>("#status")!.value as ExperimentStatus
    };

    // The schema describes the entire database.
    // Wrap the new experiment using its ID as the property name.
    return {
        id,
        databaseEntry: {
            [id]: experiment
        }
    };
}

addAlgorithmButton.addEventListener("click", addAlgorithmRow);

form.addEventListener("submit", async (event: SubmitEvent) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    const submitButton = form!.querySelector<HTMLButtonElement>(
        'button[type="submit"]'
    );

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Creating...";
    }

    try {
        const { databaseEntry } = buildExperiment();

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

            throw new Error(
                responseText || `Request failed with status ${response.status}.`
            );
        }

        window.location.assign(form!.dataset.successUrl!);

    } catch (error) {
        const message = error instanceof Error
            ? error.message
            : "An unexpected error occurred.";

        showMessage(`Could not create experiment: ${message}`);

        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = "Create experiment";
        }
    }
});

export {};