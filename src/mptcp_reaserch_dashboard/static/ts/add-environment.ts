type EnvironmentType =
    | "OPENINTERNET"
    | "UML"
    | "NS3"
    | "MATHEMATICAL";

interface Environment {
    name: string;
    type: EnvironmentType;
    description: string;
    version: string;
    isActive: boolean;
    configuration: Record<string, string>;
}

const environmentIdPattern = /^[a-z](?:[a-z0-9-]*[a-z0-9])?$/;
const configurationNamePattern = /^[a-zA-Z_][a-zA-Z0-9_]*$/;

const form = document.querySelector<HTMLFormElement>("#environment-form");
const configurationList = document.querySelector<HTMLDivElement>("#configuration-list");
const addConfigurationButton = document.querySelector<HTMLButtonElement>("#add-configuration");
const messageBox = document.querySelector<HTMLDivElement>("#form-message");
const configurationError = document.querySelector<HTMLSpanElement>("#configuration-error");

if (!form || !configurationList || !addConfigurationButton || !messageBox || !configurationError) {
    throw new Error("The environment creation form is missing required elements.");
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
        HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null;

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

function addConfigurationRow(): void {
    const row = document.createElement("div");
    row.className = "parameter-row";

    const keyLabel = document.createElement("label");
    keyLabel.textContent = "Configuration key";

    const keyInput = document.createElement("input");
    keyInput.type = "text";
    keyInput.placeholder = "simulation_time";
    keyInput.className = "configuration-name";
    keyInput.autocomplete = "off";

    keyLabel.append(keyInput);

    const valueLabel = document.createElement("label");
    valueLabel.textContent = "Configuration value";

    const valueInput = document.createElement("input");
    valueInput.type = "text";
    valueInput.placeholder = "120";
    valueInput.className = "configuration-value";

    valueLabel.append(valueInput);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-parameter";
    removeButton.textContent = "Remove";

    removeButton.addEventListener("click", () => {
        row.remove();
    });

    row.append(keyLabel, valueLabel, removeButton);

    configurationList!.append(row);

    keyInput.focus();
}

function validateForm(): boolean {
    clearMessage();
    configurationError!.textContent = "";

    const idInput = document.querySelector<HTMLInputElement>("#environment-id");
    const nameInput = document.querySelector<HTMLInputElement>("#name");
    const versionInput = document.querySelector<HTMLInputElement>("#version");

    if (!idInput || !nameInput || !versionInput) {
        showMessage("The form is incomplete. Please reload the page.");
        return false;
    }

    setFieldError(
        "environment-id",
        environmentIdPattern.test(idInput.value)
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
        "version",
        versionInput.value.trim().length > 0
            ? ""
            : "Version is required."
    );

    const configurationNames = new Set<string>();
    let configurationErrorMessage = "";

    for (const row of configurationList!.querySelectorAll<HTMLDivElement>(".parameter-row")) {
        const keyInput = row.querySelector<HTMLInputElement>(".configuration-name");
        const valueInput = row.querySelector<HTMLInputElement>(".configuration-value");

        if (!keyInput || !valueInput) {
            continue;
        }

        const key = keyInput.value.trim();

        keyInput.setCustomValidity("");
        valueInput.setCustomValidity("");

        keyInput.classList.remove("input-invalid");
        valueInput.classList.remove("input-invalid");

        if (!key || !configurationNamePattern.test(key)) {
            keyInput.setCustomValidity(
                "Use a letter or underscore first, followed by letters, digits or underscores."
            );

            keyInput.classList.add("input-invalid");

            configurationErrorMessage = "One or more configuration keys are invalid.";
        } else if (configurationNames.has(key)) {
            keyInput.setCustomValidity(
                "Configuration keys must be unique."
            );

            keyInput.classList.add("input-invalid");

            configurationErrorMessage = `Duplicate configuration key: ${key}.`;
        } else {
            configurationNames.add(key);
        }

        // Configuration values are strings, so empty values are allowed.
    }

    configurationError!.textContent = configurationErrorMessage;

    const valid = form!.checkValidity();

    if (!valid) {
        form!.reportValidity();
        showMessage("Please correct the highlighted fields before creating the environment.");
    }

    return valid;
}

function buildEnvironment(): {
    id: string;
    databaseEntry: Record<string, Environment>;
} {
    const id = (
        document.querySelector<HTMLInputElement>("#environment-id")?.value ?? ""
    ).trim();

    const configuration: Record<string, string> = {};

    for (const row of configurationList!.querySelectorAll<HTMLDivElement>(".parameter-row")) {
        const key = row.querySelector<HTMLInputElement>(".configuration-name")?.value.trim();
        const value = row.querySelector<HTMLInputElement>(".configuration-value")?.value ?? "";

        if (key) {
            configuration[key] = value;
        }
    }

    const environment: Environment = {
        name: document.querySelector<HTMLInputElement>("#name")!.value.trim(),

        type: document.querySelector<HTMLSelectElement>("#type")!.value as EnvironmentType,

        description: document.querySelector<HTMLTextAreaElement>("#description")!.value.trim(),

        version: document.querySelector<HTMLInputElement>("#version")!.value.trim(),

        isActive: document.querySelector<HTMLInputElement>("#is-active")!.checked,

        configuration
    };

    // The schema describes the entire database.
    // Therefore, wrap the new environment using its ID as the property name.
    return {
        id,
        databaseEntry: {
            [id]: environment
        }
    };
}

addConfigurationButton.addEventListener("click", addConfigurationRow);

form.addEventListener("submit", async (event: SubmitEvent) => {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    const submitButton = form.querySelector<HTMLButtonElement>(
        'button[type="submit"]'
    );

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Creating...";
    }

    try {
        const { databaseEntry } = buildEnvironment();

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

            throw new Error(
                responseText || `Request failed with status ${response.status}.`
            );
        }

        window.location.assign(form.dataset.successUrl!);

    } catch (error) {
        const message = error instanceof Error
            ? error.message
            : "An unexpected error occurred.";

        showMessage(`Could not create environment: ${message}`);

        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = "Create environment";
        }
    }
});

export {} // weird