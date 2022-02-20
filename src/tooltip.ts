import tippy, { Props } from "tippy.js"

export default (node: HTMLElement, content: string, params?: Props) => {
    node.setAttribute("aria-label", content);
    node.title = "";
    const tip = tippy(node, { content, delay: [100, 0], ...params });
    return {
        update: (newParams: Props): void => tip.setProps({ ...newParams }),
        destroy: (): void => tip.destroy(),
    };
};