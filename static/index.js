function handleTab (evt) {
    console.log(evt);
    let li = evt.target.parentElement;
    document.querySelector(".tabs li.is-active").classList.remove("is-active");
    li.classList.add("is-active");
    document.querySelectorAll(".tab-contents").forEach(el => { el.classList.add("is-sr-only"); });
    switch (li.id) {
        case "tab-selection":
            document.getElementById("selection-contents").classList.remove("is-sr-only");
            break;
        case "tab-replacement":
            document.getElementById("replacement-contents").classList.remove("is-sr-only");
            break;
        case "tab-crossover":
            document.getElementById("crossover-contents").classList.remove("is-sr-only");
            break;
        case "tab-mutation":
            document.getElementById("mutation-contents").classList.remove("is-sr-only");
            break;
        case "tab-stop-criteria":
            document.getElementById("stop-criteria-contents").classList.remove("is-sr-only");
            break;
    }
}

document.querySelectorAll(".tabs li").forEach(tab => {
    tab.addEventListener("click", handleTab);
});

function generateBase () {
    let base = {};
    $('#base-settings input').serializeArray().map(entry => { base[entry.name] = entry.value; });
    return base;
}

function updateHelperDisabled (input) {
    let level = input.closest(".level");
    if (level) {
        level.querySelectorAll(".level-right input").forEach(el => { el.disabled = !input.checked; });
    }
}

document.querySelectorAll("#selection-contents input[type='radio']").forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll("#selection-contents input[type='radio']").forEach(input => {
            updateHelperDisabled(input);
        });
    });
});

document.querySelectorAll("#replacement-contents input[type='radio']").forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll("#replacement-contents input[type='radio']").forEach(input => {
            updateHelperDisabled(input);
        });
    });
});

document.querySelectorAll("#crossover-contents input[type='checkbox']").forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll("#crossover-contents input[type='checkbox']").forEach(input => {
            updateHelperDisabled(input);
        });
    });
});

document.querySelectorAll("#mutation-contents input[type='checkbox']").forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll("#mutation-contents input[type='checkbox']").forEach(input => {
            updateHelperDisabled(input);
        });
    });
});

document.querySelectorAll("#stop-criteria-contents input[type='checkbox']").forEach(input => {
    input.addEventListener("input", () => {
        document.querySelectorAll("#stop-criteria-contents input[type='checkbox']").forEach(input => {
            updateHelperDisabled(input);
        });
    });
});
function generateSelection () {
    let vals = {};
    $('#selection-contents input').serializeArray().map(entry => { vals[entry.name] = entry.value; });
    let selection = {
        "method": vals["method"],
    };
    delete vals.method;
    selection.parameters = vals;
    return selection;
}

function generateReplacement () {
    let vals = {};
    $("#replacement-contents input").serializeArray().map(entry => {
        if (!Number.isNaN(Number(entry.value))) {
            vals[entry.name] = Number(entry.value);
        } else {
            vals[entry.name] = entry.value;
        }
    });
    let replacement = {
        "method": vals["method"],
    };
    delete vals.method;
    replacement.parameters = vals;
    return replacement;
}
