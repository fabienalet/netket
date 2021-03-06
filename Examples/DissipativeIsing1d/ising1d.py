# Copyright 2018 The Simons Foundation, Inc. - All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import netket as nk
import numpy as np

rg = nk.utils.RandomEngine(seed=1234)

# 1D Lattice
L = 10
gp = 0.3
Vp = 2.0

g = nk.graph.Hypercube(length=L, n_dim=1, pbc=False)

# Hilbert space of spins on the graph
hi = nk.hilbert.Spin(s=0.5, graph=g)


# Defining the Ising hamiltonian (with sign problem here)
# Using local operators
sx = [[0, 1], [1, 0]]
sy = [[0, -1j], [1j, 0]]
sz = [[1, 0], [0, -1]]

sigmam = [[0, 0], [1, 0]]

# The hamiltonian
ha = nk.operator.LocalOperator(hi)

# List of dissipative jump operators
j_ops = []

# Observables
obs_sx = nk.operator.LocalOperator(hi)
obs_sy = nk.operator.LocalOperator(hi)
obs_sz = nk.operator.LocalOperator(hi)

for i in range(L):
    ha += (gp / 2.0) * nk.operator.LocalOperator(hi, sx, [i])
    ha += (Vp / 4.0) * nk.operator.LocalOperator(hi,
                                                 np.kron(sz, sz), [i, (i + 1) % L])

    # sigma_{-} dissipation on every site
    j_ops.append(nk.operator.LocalOperator(hi, sigmam, [i]))

    obs_sx += nk.operator.LocalOperator(hi, sx, [i])
    obs_sy += nk.operator.LocalOperator(hi, sy, [i])
    obs_sz += nk.operator.LocalOperator(hi, sz, [i])


#  Create the liouvillian
lind = nk.operator.LocalLiouvillian(ha, j_ops)

# RBM Spin Machine
ma = nk.machine.NdmSpinPhase(hilbert=hi, alpha=1, beta=1)
ma.init_random_parameters(seed=1234, sigma=0.001)

# Metropolis Local Sampling
sa = nk.sampler.MetropolisLocal(machine=ma)
# Sampler for the diagonal of the density matrix, to compute observables
sa_obs = nk.sampler.MetropolisLocal(machine=ma.diagonal())

# Optimizer
op = nk.optimizer.Sgd(0.01)
sr = nk.optimizer.SR(diag_shift=0.01, use_iterative=True)

ss = nk.SteadyState(lind, sa, op, 2000, sampler_obs=sa_obs, n_samples_obs=500)
ss.add_observable(obs_sx, "Sx")
ss.add_observable(obs_sy, "Sy")
ss.add_observable(obs_sz, "Sz")


ss.run(output_prefix="test", n_iter=200)
