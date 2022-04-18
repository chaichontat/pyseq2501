import type { Cmd } from "./command";
import { cmdDefaults } from "./command";
import type { Reagent, ReagentGroup } from "./reagent";
import { reagentDefault } from "./reagent";

export type NReagent = { uid: number; reagent: Reagent | ReagentGroup };
export type NCmd = { uid: number; cmd: Cmd };

export type Experiment = {
  name: string;
  path: string;
  fc: boolean;
  reagents: (Reagent | ReagentGroup)[];
  cmds: Cmd[];
};

export type NExperiment = {
  name: string;
  path: string;
  fc: boolean;
  reagents: NReagent[];
  cmds: NCmd[];
};

export function genExperimentDefault(max_uid: number): NExperiment {
  return {
    name: "",
    path: ".",
    fc: false,
    reagents: [{ uid: max_uid + 1, reagent: { ...reagentDefault } }],
    cmds: [{ uid: max_uid + 2, cmd: { ...cmdDefaults.pump } }],
  };
}

export function fromExperiment(e: Experiment, max_uid: number): NExperiment {
  return {
    name: e.name,
    fc: e.fc,
    path: e.path,
    reagents: e.reagents.map((reagent) => ({ uid: ++max_uid, reagent })),
    cmds: e.cmds.map((cmd) => ({ uid: ++max_uid, cmd })),
  };
}

export function toExperiment(ne: NExperiment): Experiment {
  return {
    name: ne.name,
    fc: ne.fc,
    path: ne.path,
    reagents: ne.reagents.map((nr: NReagent) => nr.reagent),
    cmds: ne.cmds.map((nc: NCmd) => nc.cmd),
  };
}
