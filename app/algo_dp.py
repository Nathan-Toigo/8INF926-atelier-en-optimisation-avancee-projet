from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Sequence
import math

@dataclass
class HydroPlantModel:
    elav_coeff: Tuple[float, float, float] = (-1.453e-6, 7.022e-3, 99.98)
    turb_coeff: List[Tuple[float, ...]] = field(default_factory=lambda: [
        (876.5404, -12.3376, -23.7066, 0.0181, 0.5931, -0.5985, -0.0006, -0.0059, 0.0147),
        (568.5323, -6.5275, -25.9285, 0.0123, 0.3086, 0.1932, -0.0004, -0.0025, 0.0009),
        (-2502.4, 9.9767, 178.7178, -0.0138, -0.4584, -4.2689, 3.6178e-4, 0.0054, 0.0340),
        (3347.6, -18.2111, -224.2315, 0.0234, 0.9174, 4.7799, -7.8865e-4, -0.0101, -0.0334),
        (-1452.7, 6.8356, 94.1139, -0.0131, -0.2594, -2.0887, 3.3149e-4, 0.0024, 0.0162),
    ])

    @staticmethod
    def _loss(qi: float) -> float:
        return 0.5e-5 * qi * qi

    def elav(self, qtot: float) -> float:
        a2, a1, a0 = self.elav_coeff
        return a2 * qtot * qtot + a1 * qtot + a0

    def hnet(self, niv_amont: float, qtot: float, qi: float) -> float:
        return niv_amont - self.elav(qtot) - self._loss(qi)

    def power_unit(self, turbine_idx_1based: int, qi: float, niv_amont: float, qtot: float) -> float:
        if qi <= 0:
            return 0.0
        c = self.turb_coeff[turbine_idx_1based - 1]
        h = self.hnet(niv_amont, qtot, qi)
        p = (
            c[0] + c[1]*qi + c[2]*h + c[3]*qi*qi + c[4]*qi*h + c[5]*h*h +
            c[6]*qi*qi*h + c[7]*qi*h*h + c[8]*h*h*h
        )
        return max(0.0, p)

    def power_dispatch(self, q_vec: Sequence[float], niv_amont: float, qtot: float) -> Tuple[List[float], float]:
        p_vec = [self.power_unit(i + 1, q_vec[i], niv_amont, qtot) for i in range(len(q_vec))]
        return p_vec, float(sum(p_vec))


@dataclass
class DPHydroOptimizer:
    model: HydroPlantModel
    dq: int = 5
    qmin: int = 0
    qmax_default: int = 160
    n_turbines: int = 5

    def optimize(self, qtot: float, niv_amont: float, qmax_by_turbine: Optional[List[float]] = None) -> Dict:
        if qmax_by_turbine is None:
            qmax_by_turbine = [self.qmax_default] * self.n_turbines

        qtot_d = int(round(qtot / self.dq) * self.dq)
        qmax_d = [int(math.floor(qm / self.dq) * self.dq) for qm in qmax_by_turbine]

        states = list(range(0, qtot_d + self.dq, self.dq))
        n_states = len(states)

        v = [[float('-inf')] * n_states for _ in range(self.n_turbines + 1)]
        policy = [[0] * n_states for _ in range(self.n_turbines)]

        v[self.n_turbines][0] = 0.0

        for i in range(self.n_turbines - 1, -1, -1):
            for s, q_remain in enumerate(states):
                umax = min(q_remain, qmax_d[i])
                best_val, best_u = float('-inf'), 0
                for u in range(self.qmin, umax + self.dq, self.dq):
                    q_next = q_remain - u
                    s_next = q_next // self.dq
                    reward = self.model.power_unit(i + 1, float(u), float(niv_amont), float(qtot_d))
                    cand = reward + v[i + 1][s_next]
                    if cand > best_val:
                        best_val, best_u = cand, u
                v[i][s] = best_val
                policy[i][s] = best_u

        q_opt = [0.0] * self.n_turbines
        q_remain = qtot_d
        for i in range(self.n_turbines):
            s = q_remain // self.dq
            u = policy[i][s]
            q_opt[i] = float(u)
            q_remain -= u

        p_vec, p_tot = self.model.power_dispatch(q_opt, float(niv_amont), float(qtot_d))
        return {
            'qtot_input': float(qtot),
            'qtot_discretized': float(qtot_d),
            'niv_amont': float(niv_amont),
            'qmax_by_turbine': qmax_by_turbine,
            'q_opt': q_opt,
            'p_opt_by_turbine': p_vec,
            'p_opt_total': p_tot,
            'n_active': int(sum(1 for q in q_opt if q > 0)),
            'value0': v[0][qtot_d // self.dq] if qtot_d // self.dq < n_states else 0.0,
        }

# Global instance for easy API usage
dp_model = HydroPlantModel()
dp_optimizer = DPHydroOptimizer(model=dp_model, dq=5)
