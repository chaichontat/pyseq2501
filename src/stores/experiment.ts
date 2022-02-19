import { Cmds, cmdDefaults } from "./command";
import { Reagent, reagentDefault, ReagentGroup } from "./reagent";

export type NReagent = { uid: number; reagent: Reagent | ReagentGroup };
export type NCmd = { uid: number; cmd: Cmds };


export type NExperiment = {
    name: string,
    flowcell: 0 | 1,
    reagents: NReagent[],
    cmds: NCmd[],
}

export const experimentDefault: NExperiment = {
    name: "",
    flowcell: 0,
    reagents: [{ uid: 0, reagent: { ...reagentDefault } }],
    cmds: [{ uid: 0, cmd: { ...cmdDefaults.pump } }]
}