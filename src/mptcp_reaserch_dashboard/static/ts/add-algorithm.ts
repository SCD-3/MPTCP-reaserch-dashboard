type AlgorithmType = "REFERENCE" | "AUTHORIAL";
type SupportedEnvironment = "OPENINTERNET" | "UML" | "NS3" | "MATHEMATICAL";

interface Algorithm {
    code: string;
    name: string;
    shortName: string;
    type: AlgorithmType;
    description: string;
    isActive: boolean;
    parameters: Record<string, number>;
    supportedEnvironments: SupportedEnvironment[];
}

const algorithmIdPattern = /^[a-z](?:[a-z0-9-]*[a-z0-9])?$/;
const parameterNamePattern = /^[a-zA-Z_][a-zA-Z0-9_]*$/;

const form = document.querySelector<HTMLFormElement>("#algorithm-form");
const parameterList = document.querySelector<HTMLDivElement>("#parameters-list");
const addParameterButton = document.querySelector<HTMLButtonElement>("#add-parameter");
const messageBox = document.querySelector<HTMLDivElement>("#form-message");
const parametersError = document.querySelector<HTMLSpanElement>("#parameters-error");

if (!form || !parameterList || !addParameterButton || !messageBox || !parametersError) {
    throw new Error("The algorithm creation form is missing required elements.");
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

function addParameterRow(): void {
    const row = document.createElement("div");
    row.className = "parameter-row";

    const keyLabel = document.createElement("label");
    keyLabel.textContent = "Parameter name";
    const keyInput = document.createElement("input");
    keyInput.type = "text";
    keyInput.placeholder = "initial_window";
    keyInput.className = "parameter-name";
    keyInput.autocomplete = "off";
    keyLabel.append(keyInput);

    const valueLabel = document.createElement("label");
    valueLabel.textContent = "Numeric value";
    const valueInput = document.createElement("input");
    valueInput.type = "number";
    valueInput.step = "any";
    valueInput.placeholder = "10";
    valueInput.className = "parameter-value";
    valueLabel.append(valueInput);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-parameter";
    removeButton.textContent = "Remove";
    removeButton.addEventListener("click", () => row.remove());

    row.append(keyLabel, valueLabel, removeButton);
    parameterList!.append(row);
    keyInput.focus();
}

function validateForm(): boolean {
    clearMessage();
    parametersError!.textContent = "";

    const idInput = document.querySelector<HTMLInputElement>("#algorithm-id");
    const codeInput = document.querySelector<HTMLInputElement>("#code");
    const nameInput = document.querySelector<HTMLInputElement>("#name");
    const shortNameInput = document.querySelector<HTMLInputElement>("#short-name");
    const descriptionInput = document.querySelector<HTMLTextAreaElement>("#description");

    if (!idInput || !codeInput || !nameInput || !shortNameInput || !descriptionInput) {
        showMessage("The form is incomplete. Please reload the page.");
        return false;
    }

    setFieldError("algorithm-id",
        algorithmIdPattern.test(idInput.value)
            ? ""
            : "Use lowercase letters, digits and hyphens; start with a letter and do not end with a hyphen.");

    setFieldError("code",
        /^[a-z]{3}$/.test(codeInput.value)
            ? ""
            : "Code must contain exactly 3 lowercase letters.");

    setFieldError("name", nameInput.value.trim().length > 0 ? "" : "Name is required.");
    setFieldError("short-name", shortNameInput.value.trim().length > 0 ? "" : "Short name is required.");
    setFieldError("description", descriptionInput.value.trim().length > 0 ? "" : "Description is required.");

    const parameterNames = new Set<string>();
    let parameterError = "";

    for (const row of parameterList!.querySelectorAll<HTMLDivElement>(".parameter-row")) {
        const keyInput = row.querySelector<HTMLInputElement>(".parameter-name");
        const valueInput = row.querySelector<HTMLInputElement>(".parameter-value");

        if (!keyInput || !valueInput) {
            continue;
        }

        const key = keyInput.value.trim();
        const value = valueInput.value.trim();

        keyInput.setCustomValidity("");
        valueInput.setCustomValidity("");
        keyInput.classList.remove("input-invalid");
        valueInput.classList.remove("input-invalid");

        if (!key || !parameterNamePattern.test(key)) {
            keyInput.setCustomValidity("Use a letter or underscore first, followed by letters, digits or underscores.");
            keyInput.classList.add("input-invalid");
            parameterError = "One or more parameter names are invalid.";
        } else if (parameterNames.has(key)) {
            keyInput.setCustomValidity("Parameter names must be unique.");
            keyInput.classList.add("input-invalid");
            parameterError = `Duplicate parameter name: ${key}.`;
        } else {
            parameterNames.add(key);
        }

        if (!value || !Number.isFinite(Number(value))) {
            valueInput.setCustomValidity("Enter a valid finite number.");
            valueInput.classList.add("input-invalid");
            parameterError = "Every parameter must have a valid numeric value.";
        }
    }

    parametersError!.textContent = parameterError;

    const valid = form!.checkValidity();
    if (!valid) {
        form!.reportValidity();
        showMessage("Please correct the highlighted fields before creating the algorithm.");
    }

    return valid;
}

function buildAlgorithm(): { id: string; databaseEntry: Record<string, Algorithm> } {
    const id = (document.querySelector<HTMLInputElement>("#algorithm-id")?.value ?? "").trim();
    const parameters: Record<string, number> = {};

    for (const row of parameterList!.querySelectorAll<HTMLDivElement>(".parameter-row")) {
        const key = row.querySelector<HTMLInputElement>(".parameter-name")?.value.trim();
        const value = row.querySelector<HTMLInputElement>(".parameter-value")?.value.trim();

        if (key && value !== undefined && value !== "") {
            parameters[key] = Number(value);
        }
    }

    const supportedEnvironments = Array.from(
        form!.querySelectorAll<HTMLInputElement>('input[name="supportedEnvironments"]:checked')
    ).map((input) => input.value as SupportedEnvironment);

    const algorithm: Algorithm = {
        code: document.querySelector<HTMLInputElement>("#code")!.value.trim(),
        name: document.querySelector<HTMLInputElement>("#name")!.value.trim(),
        shortName: document.querySelector<HTMLInputElement>("#short-name")!.value.trim(),
        type: document.querySelector<HTMLSelectElement>("#type")!.value as AlgorithmType,
        description: document.querySelector<HTMLTextAreaElement>("#description")!.value.trim(),
        isActive: document.querySelector<HTMLInputElement>("#is-active")!.checked,
        parameters,
        supportedEnvironments
    };

    // The schema describes the entire database, so the new record is wrapped
    // in an object whose property name is the algorithm ID.
    return { id, databaseEntry: { [id]: algorithm } };
}

addParameterButton.addEventListener("click", addParameterRow);

form.addEventListener("submit", async (event: SubmitEvent) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    const submitButton = form.querySelector<HTMLButtonElement>('button[type="submit"]');

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Creating...";
    }

    try {
        const { databaseEntry } = buildAlgorithm();

        const response = await fetch(form.action, {
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

        window.location.assign(form.dataset.successUrl!);

    } catch (error) {
        const message = error instanceof Error ? error.message : "An unexpected error occurred.";
        showMessage(`Could not create algorithm: ${message}`);

        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = "Create algorithm";
        }
    }
});
