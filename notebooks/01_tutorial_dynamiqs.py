# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "dynamiqs==0.3.7",
#     "jax>=0.4.30",
#     "marimo>=0.25",
#     "matplotlib>=3.8",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Tutorial 1: `dynamiqs`

    In this tutorial, you will learn how to use the software package `dynamiqs`.
    Many more tutorials and documentation can be found on the `dynamiqs` [website](https://www.dynamiqs.org).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | These notebooks are marimo notebooks

    If you come from Jupyter, four rules differ ([marimo for Jupyter users](https://docs.marimo.io/guides/coming_from/jupyter/)):

    - **Reactive execution.** When you run a cell, marimo also runs every cell that uses a variable it defines. The order of the cells on the page does not matter.
    - **One definition per variable.** A global variable can be defined in one cell only. Names that start with an underscore (`_fig`, `_ax`, `_k`) are local to their cell, and several cells can reuse them.
    - **Output.** A cell displays its last expression: end a plotting cell with the figure (`_fig`, `plt.gcf()`). `print` output appears below the cell.
    - **Plain Python files.** A notebook is a `.py` file and stores no outputs. Open it with `marimo edit notebooks/01_tutorial_dynamiqs.py`, run it as a script with `python notebooks/01_tutorial_dynamiqs.py`, or save it with its outputs with `marimo export html notebooks/01_tutorial_dynamiqs.py -o tutorial_01.html`.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is `dynamiqs`?

    `dynamiqs` allows the high-performance simulation of quantum systems with `JAX`, a GPU-oriented library developed by Google.

    In contrast to other existing simulation packages, `dynamiqs` offers the following advantages:
    - **Differentiable:**

      The quantum solvers are fully differentiable. This is extremely helpful when dealing with optimal control, parameter estimation, experiment fitting, etc.
    - **GPU Accelerated:**

      Thanks to `JAX`, `dynamiqs` allows to transition seamlessly between CPU, GPU and TPU simulations, and run batches of simulations at once. This is very powerful when sweeping parameters.
    - **Built on `JAX`:**

      `dynamiqs` benefits from the JAX ecosystem, that is built for both high-performance numerical computing and machine learning. This makes it also easy to extend the functionalities of `dynamiqs`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We begin with some basic imports and some plotting functions that we will later use.
    """)
    return


@app.cell
def _():
    import io

    import dynamiqs as dq
    import jax
    import jax.numpy as jnp # the JAX version of numpy
    from matplotlib import pyplot as plt

    return dq, io, jax, jnp, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Setting a computing device:** If we have multiple computing devices available, such as CPU, GPU, or TPU, we can choose which one should be used by `dynamiqs`.
    We can see the availability of devices by calling:
    """)
    return


@app.cell
def _(jax):
    jax.devices()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If multiple devices are available, we can set the device used for `dynamiqs` calculations using `dq.set_device(device, index)` where `device` is one of `cpu`, `gpu` or `tpu`, and `index` is an integer (in case of multiple GPU devices, for example, defaults to 0).

    Here, we will use a regular cpu:
    """)
    return


@app.cell
def _(dq):
    dq.set_device('cpu')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Precision:** We can set the default floating point precision used in `dynamiqs`. There are two options available:
    - 'single' sets default precision to float32 and complex64 (default setting),
    - 'double' sets default precision to float64 and complex128.

    It is important to know that for most GPUs the `single` precision is the native precision and a higher precision will slow down computations considerably.

    Here, we use the default setting:
    """)
    return


@app.cell
def _(dq):
    dq.set_precision('single')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 1. Simulating a harmonic oscillator

    In this first section, we begin with a simple simulation of a quantum harmonic oscillator. We initialize the system in a coherent state $\lvert\alpha\rangle$, and then evolve it in time with Hamiltonian $H = \omega \hat{a}^\dagger \hat{a}$. This will show a simple rotation in phase space of the coherent state.

    Let us initialize the system, the operators and the scope of the simulation.
    """)
    return


@app.cell
def _(dq, jnp):
    # parameters
    n = 32  # number of Fock states
    omega = 1.0  # detuning
    T = jnp.pi / omega  # time of evolution

    # operators
    a = dq.destroy(n)  # annihilation operator
    H = omega * dq.dag(a) @ a  # Hamiltonian

    # initial state and save time
    psi0 = dq.coherent(n, 2.0)  # coherent state
    t_save = jnp.linspace(0, T, 50)
    return H, T, a, n, omega, psi0, t_save


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice that we use the `@` for matrix-matrix multiplication of two Jax arrays (`dq.dag(a)` and `a`) here. (The `*` operator is an element-wise operator by default)

    Then, we can run `dq.sesolve` which will solve the Schrödinger equation.
    """)
    return


@app.cell
def _(H, dq, psi0, t_save):
    # solve Schrodinger equation
    result = dq.sesolve(H, psi0, t_save)
    print(result)
    return (result,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In a few tens of milliseconds, we get our full time evolution, with the evolved state at each time step. Let us plot these states in phase space for multiple times.
    """)
    return


@app.cell
def _(dq, plt, result):
    dq.plot.wigner_mosaic(result.states, cross = True)
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We can also generate a GIF to visualize the evolution of the state.
    """)
    return


@app.cell
def _(dq, io, mo, result):
    _gif = dq.plot.wigner_gif(result.states, gif_duration = 2, fps = 25)
    mo.image(io.BytesIO(_gif.data))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As expected, the coherent state rotates in phase space. We get a simple harmonic oscillator with frequency $\omega$. After some time $T = \pi / \omega$, the state has rotated by an angle $\pi$ in phase space.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The oscillator is losing photons!

    Let us now assume that our oscillator is losing photons. We can model this by adding a dissipation term $\kappa \mathcal{D}[a]$ to the problem. The corresponding equation to solve is now the Lindblad master equation, a generalization of the Schrödinger equation for open quantum systems. Photons will thus be lost at rate $\kappa$ to the environment.

    In dynamiqs, we simply need to define this jump operator, and we can then integrate the master equation as before using `dq.mesolve`.
    """)
    return


@app.cell
def _(H, a, dq, jnp, psi0, t_save):
    # define the jump operator
    kappa = 0.5
    jump_ops = [jnp.sqrt(kappa) * a]

    # solve the Lindblad master equation with dynamiqs.mesolve
    result_lossy = dq.mesolve(H, jump_ops, psi0, t_save)
    return jump_ops, kappa, result_lossy


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Again, let us plot the states in phase space for multiple times.
    """)
    return


@app.cell
def _(dq, plt, result_lossy):
    dq.plot.wigner_mosaic(result_lossy.states, cross = True)
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compared to our previous simulation, the state now spirals towards the center of phase space and has a reduced amplitude at the final time. We will check this by computing the total number of photons in the oscillator against time. To do so, we will provide an additional argument to `dynamiqs.mesolve`, which is the observable we want to measure.
    """)
    return


@app.cell
def _(H, T, a, dq, jnp, jump_ops, plt, psi0):
    # observable to measure (number of photons)
    exp_ops = [dq.dag(a) @ a]

    # run dynamiqs.mesolve with a finer time grid
    t_fine = jnp.linspace(0, T, 200)
    result_loss = dq.mesolve(H, jump_ops, psi0, t_fine, exp_ops=exp_ops)

    # also run dynamiqs.sesolve without dissipation for comparison
    result_noloss = dq.sesolve(H, psi0, t_fine, exp_ops=exp_ops)

    # plot the observable against time
    _fig, _ax = plt.subplots(1, 1, figsize=(5, 3))
    _ax.plot(t_fine, result_loss.expects[0].real, label=r"$\kappa > 0$")
    _ax.plot(t_fine, result_noloss.expects[0].real, label=r"$\kappa = 0$")
    _ax.set_ylim((0, 4.2))
    _ax.set_xlim((0, T))
    _ax.set_xlabel(r"Time $t$", fontsize=12)
    _ax.set_ylabel(r"Number of photons", fontsize=12)
    _ax.legend(fontsize=12, frameon=False)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Gradients!
    One cool thing about `dynamiqs` is the ability to compute gradients. Suppose that in the above example, we want to compute the gradient of the number of photons in the final state at time $T, \overline{n} = \mathrm{Tr}[\hat{a}^\dagger \hat{a} \hat{\rho}(T)]$, with respect to the frequency $\omega$, the decay rate $\kappa$ and the initial coherent state amplitude $\alpha_0$.
    """)
    return


@app.cell
def _(dq, jax, jnp, kappa, n, omega):
    # parameters
    alpha0 = 1.0    # initial coherent state amplitude
    T_rev = 2 * jnp.pi  # total evolution time (one full revolution)

    def population(omega, kappa, alpha0):
        """Return the oscillator population after time evolution."""
        # initialize operators, initial state and saving times
        a = dq.destroy(n)
        H = omega * dq.dag(a) @ a
        jump_ops = [jnp.sqrt(kappa) * a]
        psi0 = dq.coherent(n, alpha0)
        tsave = jnp.linspace(0, T_rev, 101)

        # run simulation
        result = dq.mesolve(H, jump_ops, psi0, tsave)

        return dq.expect(dq.number(n), result.states[-1]).real

    # compute gradient with respect to omega, kappa and alpha
    grad_population = jax.grad(population, argnums=(0, 1, 2))
    grads = grad_population(omega, kappa, alpha0)
    print(f'Gradient w.r.t. omega : {grads[0]:.4f}')
    print(f'Gradient w.r.t. kappa : {grads[1]:.4f}')
    print(f'Gradient w.r.t. alpha0: {grads[2]:.4f}')
    return (T_rev,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Batching!

    One cool thing about the fact that `dynamiqs` is using `JAX` is that it allows to run many independent simulations concurrently, also called **batching**.
    This can dramatically speedup simulations, especially on GPUs. Importantly, this does not use any for-loops under the hood and is therefore much more efficient.

    For example, we can sweep over the parameters $\omega$, $\kappa$ and $\alpha_0$:
    """)
    return


@app.cell
def _(T_rev, a, dq, jnp, n):
    omegas = jnp.linspace(0.5, 1.5, 10)
    kappas = jnp.linspace(0.1, 1.0, 8)
    alpha0s = jnp.linspace(0.5, 1.5, 5)

    H_batch = omegas[:, None, None] * dq.dag(a) @ a
    jump_ops_batch = [jnp.sqrt(kappas)[:, None, None] * a]
    psi0_batch = dq.coherent(n, alpha0s)

    tsave = jnp.linspace(0, T_rev, 101)

    result_batch = dq.mesolve(H_batch, jump_ops_batch, psi0_batch, tsave)
    print(result_batch.states.shape)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We see that the resulting time-evolved density matrix has now more dimensions, associated with the sweeps of the different parameters.
    """)
    return


if __name__ == "__main__":
    app.run()
