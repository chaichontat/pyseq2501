import tippy, { Props } from "tippy.js"

export default (node: HTMLElement, content: string, params?: Props) => {
    node.setAttribute("aria-label", content);
    node.title = "";
    const tip = tippy(node, { content, ...params });
    return {
        update: (newParams: Props): void => tip.setProps({ content, ...newParams }),
        destroy: (): void => tip.destroy(),
    };
};