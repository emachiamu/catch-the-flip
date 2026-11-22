# Theory primer: cat qubits, the buffer, and why a bit flip makes noise

This primer is written for a reader who knows the harmonic oscillator, coherent states and
the Lindblad master equation. Tutorials 1 to 3 in `notebooks/` introduce all three, with the
simulation tool dynamiqs, and tutorial 4 introduces the quantum trajectories of section 4. The
challenge is inspired by a recent theory paper (section 8). You do not need it: everything
the challenge asks can be found from the simulations and the data.

Units: throughout the challenge the two-photon dissipation rate $\kappa_2$ is the unit of
rate and $1/\kappa_2$ the unit of time. For a device with $\kappa_2/2\pi = 1\ \mathrm{MHz}$
one time unit is $1/\kappa_2 = 0.16\ \mu\mathrm{s}$, so a segment of $200/\kappa_2$ lasts
$32\ \mu\mathrm{s}$.

## 1. The cat qubit

A dissipative cat qubit stores a qubit in a microwave resonator, the *memory* (mode $a$),
in the two coherent states $|{+\alpha}\rangle$ and $|{-\alpha}\rangle$ with $\alpha$ real.
We call $\bar n = |\alpha|^2$ the cat size. The logical states and operators are

* $|0_L\rangle \approx |{+\alpha}\rangle$, $|1_L\rangle \approx |{-\alpha}\rangle$
  (up to corrections of order $e^{-2\bar n}$, since $\langle \alpha | {-\alpha}\rangle = e^{-2\bar n}$),
* $Z_L \approx \mathrm{sign}$ of the quadrature $x = (a + a^\dagger)/2$: reading $Z_L$ means
  measuring on which side of the origin the field sits,
* $X_L$ = photon-number parity $e^{i\pi a^\dagger a}$: the cat states
  $|\mathcal C_\pm\rangle \propto |\alpha\rangle \pm |{-\alpha}\rangle$ are its eigenstates.

The point of this encoding is the *noise bias*. Single-photon loss ($L = \sqrt{\kappa_1}\,a$)
maps $|\pm\alpha\rangle$ onto themselves ($a|\alpha\rangle = \alpha|\alpha\rangle$) but flips
the parity: it is a **phase flip**, at a rate $\Gamma_X \simeq 2\kappa_1 \bar n$ that grows
linearly with the cat size. Thermal excitation ($a^\dagger$) flips the parity too, so with a
thermal occupation $n_{th}$ the rate becomes
$\Gamma_X \simeq 2\kappa_1\left[(1 + 2n_{th})\,\bar n + n_{th}\right]$; dephasing ($a^\dagger a$)
preserves the parity and does not contribute. A **bit flip**,
$|\alpha\rangle \to |{-\alpha}\rangle$, requires the field to travel across phase space; with
the stabilisation of section 2 it is exponentially suppressed, $\Gamma_Z \propto e^{-c\,\bar n}$,
with $c$ of order 2: between 1.5 and 2.5 at the cat sizes of this challenge,
depending on which noise drives the flips. Conventions used
everywhere in this challenge (for the ensemble average, as given by the master equation):

$$\langle Z_L\rangle(t) = e^{-\Gamma_Z t},\qquad
P(\text{read } {-\alpha} \text{ at } t \mid \text{prepared } {+\alpha}) = \tfrac12\left(1 - e^{-\Gamma_Z t}\right) \approx \tfrac12 \Gamma_Z t .$$

So "the bit-flip time" $T_Z = 1/\Gamma_Z$ is the decay time of $\langle Z_L\rangle$ and the
probability of a flip per unit time is $\Gamma_Z/2$.

A word on letters. A flip is named after the axis along which the state flips. A bit flip
exchanges the two eigenstates of $Z_L$, $|{\pm\alpha}\rangle$: its rate is $\Gamma_Z$, its time
$T_Z$, and it makes $\langle Z_L\rangle$ decay. A phase flip exchanges the two eigenstates of
$X_L$, the cat states $|\mathcal C_\pm\rangle$: its rate is $\Gamma_X$, its time
$T_X = 1/\Gamma_X$, and it makes $\langle X_L\rangle$ decay. The noise bias is the ratio
$T_Z/T_X$. The *operator* that exchanges the eigenstates of $Z_L$ is $X_L$, which is why
undoing a bit flip would take a logical $X$; some papers name the rates after that operator
and write $\Gamma_X$ for the bit-flip rate.

## 2. Two-photon dissipation and the buffer

The cat is held in place by an engineered dissipation that removes photons *in pairs*:

$$\dot\rho = \kappa_2\, \mathcal D[a^2 - \alpha^2]\,\rho,\qquad
\mathcal D[L]\rho = L\rho L^\dagger - \tfrac12\{L^\dagger L, \rho\}.$$

Both $|\pm\alpha\rangle$ are annihilated by $L_2 = a^2 - \alpha^2$: they are dark states of
this dissipator and so is any superposition of them. Any other state is pulled back onto
the manifold spanned by $|\pm\alpha\rangle$, the *code space* of the qubit, at a rate of order
$\kappa_2 \bar n$.

In the device this dissipator is not fundamental. The memory $a$ is coupled to a lossy
*buffer* resonator $b$ by a two-to-one photon exchange, and the buffer is driven:

$$H = g_2\,(a^2 b^\dagger + a^{\dagger 2} b) - \epsilon_d\,(b + b^\dagger),\qquad
\dot\rho = -i[H,\rho] + \kappa_b\,\mathcal D[b]\rho + (\text{memory noise}).$$

When the buffer is lossy enough, with $\kappa_b$ much larger than its coupling to the
memory, $g_2|\alpha|$ (and a fortiori $g_2$), it follows the memory adiabatically:

$$ b \simeq \frac{2i}{\kappa_b}\left(\epsilon_d - g_2 a^2\right) = -\frac{2i g_2}{\kappa_b}\left(a^2 - \alpha^2\right),\qquad \alpha^2 = \frac{\epsilon_d}{g_2}. $$

(Tutorial 3 writes the drive with the opposite sign, $+\epsilon_d(b + b^\dagger)$, hence its
$\alpha^2 = -\epsilon_d/g_2^*$; the physics is the same.)
Eliminating $b$ gives back the two-photon dissipator with $\kappa_2 = 4g_2^2/\kappa_b$. The
field leaking out of the buffer, $\sqrt{\kappa_b}\, b$, is therefore proportional to
$L_2 = a^2 - \alpha^2$ applied to the memory: **the buffer output is a direct witness of how
far the memory is from the code space**. In the code space it is dark: the buffer sits in
vacuum and nothing comes out, even though the drive $\epsilon_d$ is on. The drive is exactly
compensated by the two-photon exchange, as long as $a^2 = \alpha^2$.

In this challenge the nominal model is the eliminated one with jump operators

| channel | jump operator | role |
| --- | --- | --- |
| buffer (monitored) | $\sqrt{\kappa_2}\,(a^2 - \alpha^2)$ | stabilisation; its output is what you record |
| loss | $\sqrt{\kappa_1(1 + n_{th})}\,a$ | phase flips |
| thermal | $\sqrt{\kappa_1 n_{th}}\,a^\dagger$ | phase flips; kicks the memory out of the code space |
| dephasing | $\sqrt{\kappa_\varphi}\,a^\dagger a$ | kicks the memory out of the code space |

and the hidden device of the validation and test sets keeps the buffer as a real mode (finite
$\kappa_b$, monitored channel $i\sqrt{\kappa_b}\,b \simeq \sqrt{\kappa_2}\,(a^2 - \alpha^2)$)
and adds a small Kerr term $-\tfrac K2 a^{\dagger 2} a^2$ to the Hamiltonian (the frequency of the
memory then depends on its photon number). The *type* of these differences is
announced; their values are not.

## 3. A bit flip is an excursion, and excursions shine

Thermal excitation and dephasing kick the memory out of the code space. The two kicks are
the same: a dephasing jump gives $a^\dagger a|\alpha\rangle = \alpha\, a^\dagger|\alpha\rangle$,
the state of a thermal jump, a coherent state with one photon added, whose squared overlap
with $|\alpha\rangle$ is $\bar n/(\bar n + 1)$. Single-photon loss does *not* kick:
$a|\alpha\rangle = \alpha|\alpha\rangle$; it only flips the parity (a phase flip) and, between
its jumps, slowly shrinks the cat, which the stabilisation compensates continuously. The
stabilisation pulls a kicked state back within a time of order $1/(\kappa_2\bar n)$, and
almost always back to the lobe it came from. Very rarely a kick, or a quick succession of
kicks, takes the memory so far from its lobe that the stabilisation brings amplitude to the
other one: that is a bit flip. On its way the field has to pass near the origin of phase
space, the saddle between the two lobes. How a flip unfolds in a single monitored run, and
in which state the memory ends, is what step 1 of the challenge asks you to find out.

While the memory is away from the code space, $a^2 \neq \alpha^2$ and the buffer radiates.
For a state near the origin, $\langle a^2\rangle \approx 0$ and the emission rate is

$$\kappa_b\langle b^\dagger b\rangle \simeq \kappa_2\,\langle (a^{\dagger 2} - \alpha^2)(a^2 - \alpha^2)\rangle \simeq \kappa_2\,\alpha^4 .$$

A flip lasting a time $\tau$ therefore comes with a burst of order $\bar n^2 \kappa_2 \tau$
photons, with a definite phase: during the burst the buffer field is
$b \simeq 2i\epsilon_d/\kappa_b$, the value it would have if the memory were empty, so in a
heterodyne record the burst appears in a known quadrature with a known sign. A kick that
relaxes without flipping also radiates, but much less (the state stays close to its lobe,
$|\langle a^2 - \alpha^2\rangle|$ stays small). The challenge is to tell the two apart from
the record alone.

Bit flips are rare, so a record contains a lot of "no flip" and a little "flip". For the
hackathon the nominal device is deliberately noisy ($\kappa_\varphi/\kappa_2 = 0.02$ instead of
the $10^{-3}$–$10^{-2}$ of real devices, and thermal photons) so that flips are frequent
enough to be simulated and seen; the physics is unchanged.

## 4. Monitoring: unravelings and records

A Lindblad equation describes the *average* evolution. When the output of a channel is
measured, the state conditioned on the record follows a *stochastic* equation, an
*unraveling* of the master equation (tutorial 4 simulates the two below):

* **photon counting** (jump unraveling, `dq.jssesolve`): the record is a list of click
  times; between clicks the state evolves under the no-click non-Hermitian generator, at a
  click it jumps, $|\psi\rangle \to L|\psi\rangle/\|L|\psi\rangle\|$. The click rate is
  $\langle L^\dagger L\rangle$.
* **homodyne / heterodyne** (diffusive unraveling, `dq.dssesolve`): the record is a
  continuous signal $dY = \langle L + L^\dagger\rangle dt + dW$, white noise on top of the
  quadrature of the output field. Heterodyne measures both quadratures ($I$ and $Q$) at the
  price of splitting the signal in two.

Two facts make the datasets of this challenge well defined whatever is done with the other
channels:

1. the statistics of the record of a measured channel does not depend on whether the other
   channels are monitored or not (no-signalling: monitoring them only refines *our*
   conditional knowledge), so we may unravel the unmonitored channels in whatever way is
   convenient for the simulation;
2. a detector of efficiency $\eta$ is a perfect detector preceded by a beam splitter of
   transmission $\eta$: for counting, each photon is registered independently with
   probability $\eta$; for heterodyne, the measured channel is $\sqrt{\eta}\,L$ and the
   lost part $\sqrt{1-\eta}\,L$ is simply not recorded.

What *does* depend on that choice is the conditional state itself. A simulation conditions
the state on the records of *every* channel, including those nobody looks at, so `pneg`, its
readout probability of $-\alpha$ at the end of a segment (section 5), describes a fictitious
observer who watches them all. `simulate.counting_segments` makes that observer count the
photons of the unmonitored channels; `simulate.heterodyne_segments`, whose solver is
diffusive, makes it measure them with homodyne detectors. The buffer records and the labels
have the same statistics either way (fact 1), but the two observers know different things.
Use `pneg` to understand the physics, and say which observer you mean when you do.

## 5. Labels: the Z readout

Each segment starts in $|{+\alpha}\rangle$, runs for $T_{\rm seg}$ with the buffer monitored,
and ends with a **Z readout**: an ideal homodyne measurement of $x = (a + a^\dagger)/2$
thresholded at $0$. The label is $1$ if $x < 0$ was read ($-\alpha$: a flip). For a coherent
state this readout errs with probability $\Phi(-2\alpha)$, with $\Phi$ the standard normal
distribution function: $0.2\%$ at $\bar n = 2$, $0.08\%$ at $\bar n = 2.5$. The
label is a *sample* of the readout: a segment whose conditional state ended in a
superposition of the two lobes is labelled $1$ with the corresponding probability. No
detector can beat the Bayes-optimal classifier $P(\text{label} = 1 \mid \text{record})$, and
because of the readout sampling even that classifier does not reach an AUC of 1.

## 6. Rates from the Liouvillian spectrum

For small Hilbert spaces the fastest way to get $\Gamma_Z$ and $\Gamma_X$ is not to
integrate anything: write the Liouvillian $\mathcal L$ as a $N^2 \times N^2$ matrix and
look at its slowest eigenvalues. The eigenvalue $0$ is the steady state; the eigenvector
that carries $\langle a\rangle$ decays at $\Gamma_Z$, the one that carries the parity at
$\Gamma_X$ (`catchtheflip.rates.spectrum`). This is how the organisers know the flip
probability per segment of every device, including at cat sizes where flips are too rare to
simulate directly.

## 7. What a herald could buy: post-selection, Pauli frames and erasures

**The phase-flip repetition code in brief.** A line of $d$ cat qubits stores one logical
qubit in the span of the two states in which all cats share the same parity, $|\mathcal C_+\rangle^{\otimes d}$
and $|\mathcal C_-\rangle^{\otimes d}$. Every error-correction *cycle* (in the challenge, one
segment) measures the products of the parities of neighbouring cats, the *stabilisers*
$X_i X_{i+1}$. A phase flip changes the parity of one cat, hence the value of the
stabilisers next to it: this pattern is its *syndrome*, from which a *decoder* (here a
majority vote) infers and undoes up to $\lfloor (d-1)/2 \rfloor$ phase flips per cycle. The
*distance* of a code against an error is the smallest number of such errors that changes the
logical state without being detected.

A bit flip of a data cat commutes with every stabiliser: it leaves no syndrome and is a
logical error all by itself. In other words the code has distance $d$ against phase flips
but distance 1 against bit flips. Without heralds the logical bit-flip probability per cycle
is about $d\,p_{\rm flip}$, and the only cure is a bigger cat. A herald, a flag raised by the
buffer output, opens three options.

**Post-selection.** The simplest use of a herald is to throw away the runs in which the
buffer shouted. Keeping a fraction $Y$ of the segments (the *yield*), the flip
probability among the kept segments is $p_{\rm kept}$, and the figure of merit is

$$\rho(Y) = \frac{p_{\rm kept}}{p_{\rm flip}},$$

lower is better, $\rho = 1$ meaning the record carries no information. The leaderboard of
the challenge reports the flip suppression $1 - \rho$ at $Y = 0.7$ (higher is better), on a
file that mixes segments of four cat sizes: the 30 % discarded segments are taken where the
detector is most suspicious, whatever their cat size. A detector must therefore rank a
record of a small cat against a record of a big one. The scale they share is the probability
of a flip given the record *and* the cat size, which combines how often a cat of that size
flips at all (the prior, sections 3 and 6) with what the record adds (the burst).
Post-selection is a legitimate tool for memory experiments and for characterising devices,
not for computing: a computer cannot discard a run.

**Correction by a Pauli frame.** The obvious use of a herald is to read it as the location
of a Pauli $X$ error and to undo it with a logical $X$ (a Pauli-frame update). A missed
flip still costs a logical error; a false alarm applies a wrong update, which is itself a
flip. Per segment and per qubit,

$$p_{\rm eff} = p_{\rm flip}\,(1 - \mathrm{TPR}) + (1 - p_{\rm flip})\,\mathrm{FPR},\qquad
S = \frac{p_{\rm eff}}{p_{\rm flip}} = (1 - \mathrm{TPR}) + \frac{1 - p_{\rm flip}}{p_{\rm flip}}\,\mathrm{FPR},$$

with TPR the fraction of flips caught and FPR the fraction of flip-free segments flagged
(both measured against the readout labels). $S = 1$ is "no gain", $S > 1$ "the correction
hurts". Because $p_{\rm flip}$ is small, false alarms are expensive: FPR must stay well
below $p_{\rm flip}$ for $S$ to drop. Whether $S$ can be made small at all, even by a perfect
detector, depends on what a heralded flip does to the qubit. That is the question of step 4.

**Erasures.** An *erasure* is an error whose location (which qubit, when) is known, while
its effect on the qubit is not: the qubit's state has been replaced by something unknown.
Erasures are much easier to correct than ordinary errors: a code of distance $d$ corrects
up to $\lfloor (d-1)/2 \rfloor$ errors at unknown locations, but up to $d - 1$ erasures,
because knowing where the errors are leaves the decoder only their effect to infer. Codes with
a distance larger than 1 against bit flips exist, for example the thin surface codes such as
the XZZX code, proposed to correct the residual bit flips of cat qubits, or an outer code
built on top of repetition-code logical qubits. They are beyond the scope of this challenge,
but the physics that decides what a herald is worth to them is entirely within it.

**Two numbers to keep apart.** $\rho$ measures how well the record *ranks* segments by their
probability of having flipped; $S$ measures whether flagged segments can be *repaired* by a
logical $X$. They answer different questions; step 4 asks you to compare them, and to
explain the comparison.

## 8. Further reading

**The paper behind the challenge.** Ferrari, Cohen, Savona, Minganti,
[arXiv:2607.01375](https://arxiv.org/abs/2607.01375) (2026), a theory paper by researchers at
EPFL and Alice & Bob, studies the burst of a flipping cat with ensemble methods (past quantum
states and a number-resolved master equation) rather than single monitored runs. We suggest
you read it after the hackathon and compare its results with your own. Its device is quieter than ours ($\kappa_1 = \kappa_\varphi =
0.005$–$0.01\,\kappa_2$, no thermal photons) and its buffer much faster
($\kappa_b = 100\,\kappa_2$); it uses time windows of $3$–$13/\kappa_2$, an ideal photon
counter or one with $\eta = 0.7$ and few dark counts, and an integrated homodyne record of the
buffer.

**Background.**

* Mirrahimi et al., *Dynamically protected cat-qubits*, New J. Phys. 16, 045014 (2014).
* Guillaud & Mirrahimi, *Repetition cat qubits for fault-tolerant quantum computation*, Phys. Rev. X 9, 041053 (2019).
* Lescanne et al., *Exponential suppression of bit-flips in a qubit encoded in an oscillator*, Nat. Phys. 16, 509 (2020).
* Réglade, Bocquet et al., *Quantum control of a cat qubit with bit-flip times exceeding ten seconds*, Nature 629, 778 (2024).
* Wu, Kolkowitz, Puri, Thompson, *Erasure conversion for fault-tolerant quantum computing in alkaline earth Rydberg atom arrays*, Nat. Commun. 13, 4657 (2022): why erasures are cheap to correct.
* Bonilla Ataides, Tuckett, Bartlett, Flammia, Brown, *The XZZX surface code*, Nat. Commun. 12, 2172 (2021).
* Wiseman & Milburn, *Quantum Measurement and Control*, chapter 4 (quantum trajectories: unravelings, homodyne and heterodyne detection).
* dynamiqs documentation, [stochastic solvers](https://www.dynamiqs.org/stable/python_api/index.html).
