import tippy from "tippy.js"

export default (node: HTMLElement, content: string) => {
    node.setAttribute("aria-label", content);
    node.title = "";
    const tip = tippy(node, { content, delay: [100, 0] });
    return {
        update: (newmsg: string): void => tip.setContent(newmsg),
        destroy: (): void => tip.destroy(),
    };
};