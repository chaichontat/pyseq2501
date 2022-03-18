export function flash(element: HTMLElement) {
  requestAnimationFrame(() => {
    if (element) {
      element.style.transition = "none";
      element.style.backgroundColor = "rgba(255,62,0,0.3)";

      setTimeout(() => {
        element.style.transition = "background 1s";
        element.style.backgroundColor = "";
      });
    }
  });
}

// Does not call on load. User needs to edit something first to see error.

export function count<T extends string | number>(names: T[]): Record<T, number> {
  return names.reduce((a, b) => ({ ...a, [b]: (a[b] || 0) + 1 }), {} as Record<T, number>); // don't forget to initialize the accumulator
}

export function checkRange(el: HTMLInputElement, minmax: [number, number] = [0, Infinity]): { destroy: () => void } {
  const handleValueChange = () => {
    const n = parseFloat(el.value);
    if (minmax[0] <= n && n <= minmax[1]) {
      el.classList.remove("invalid");
    } else {
      el.classList.add("invalid");
    }
  };

  document.addEventListener("input", handleValueChange);

  return {
    destroy: () => {
      document.removeEventListener("input", handleValueChange);
    },
  };
}

export function notEmpty(el: HTMLInputElement): { update: () => void; destroy: () => void } {
  const handleValueChange = () => {
    if (el.value) {
      el.classList.remove("invalid");
    } else {
      el.classList.add("invalid");
    }
  };
  document.addEventListener("input", handleValueChange);

  return {
    update: handleValueChange,
    destroy: () => {
      document.removeEventListener("input", handleValueChange);
    },
  };
}
