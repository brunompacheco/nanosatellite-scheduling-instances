from pathlib import Path
from tqdm import tqdm

import json
import pickle
import numpy as np

from problem import get_model


if __name__ == '__main__':
    instances_fps = list(Path('new-instances').glob('97_*.json'))

    dst_dir = Path('new-instances')

    try:
        solutions_fpaths = dst_dir.glob('*_sols.npz')
        solutions = [fp.name[:-len('_sols.npz')] for fp in solutions_fpaths]

        instances_fps = [f for f in instances_fps if f.name[:-len('.json')] not in solutions]
    except FileNotFoundError:
        pass

    for fpath in tqdm(instances_fps):
        instance_name = fpath.name[:-len('.json')]

        with open(fpath) as f:
            instance = json.load(f)

        jobs = list(range(instance['jobs']))

        model = get_model(instance, coupling=True, new_ineq=False, timeout=60)
        model.setParam('PoolSearchMode', 2)
        model.setParam('PoolSolutions', 500)
        model.update()

        model.optimize()

        objs = list()
        sols = list()
        for i in range(model.SolCount):
            model.Params.SolutionNumber = i
            objs.append(model.PoolObjVal)
            # sol = np.array([v.xn for v in model.getVars() if 'x(' in v.VarName])
            sol = np.array([v.xn for v in model.getVars() if ('x(' in v.VarName) or ('phi(' in v.VarName)])
            # sol = np.array([v.xn for v in model.getVars()])
            sols.append(sol)
        model.Params.SolutionNumber = 0

        sols = np.array(sols)
        objs = np.array(objs)

        np.savez(dst_dir/(instance_name + '_sols.npz'), sols, objs)
