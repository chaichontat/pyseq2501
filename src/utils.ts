export function flash(element: HTMLElement) {
    requestAnimationFrame(() => {
        element.style.transition = "none";
        element.style.backgroundColor = "rgba(255,62,0,0.3)";

        setTimeout(() => {
            element.style.transition = "background 1s";
            element.style.backgroundColor = "";
        });
    });
}

// Does not call on load. User needs to edit something first to see error.

export function checkRange(el: HTMLInputElement, min: number = 0, max: number = Infinity): { destroy: () => void } {
    const handleValueChange = (e: InputEvent) => {
        const n = parseFloat(el.value)
        if (min < n && n < max) {
            el.classList.remove("invalid")
        } else {
            el.classList.add("invalid")
        }
    }

    document.addEventListener("input", handleValueChange)

    return {
        destroy: () => {
            document.removeEventListener("input", handleValueChange)
        }
    }
}

export function notEmpty(el: HTMLInputElement): { update: () => void, destroy: () => void } {
    const handleValueChange = (e?: InputEvent) => {
        if (el.value) {
            el.classList.remove("invalid")
        } else {
            el.classList.add("invalid")
        }
    }
    document.addEventListener("input", handleValueChange)

    return {
        update: handleValueChange,
        destroy: () => {
            document.removeEventListener("input", handleValueChange)
        }
    }
}