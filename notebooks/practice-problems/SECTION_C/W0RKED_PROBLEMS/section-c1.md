# C.1:  Numerical Methods with Bézout's Identity & Coprime Sampling 

The `kuramoto-benchmark-suite` codebase uses coprime sampling to reduce memory from $\mathcal{O}(MN)$ to 
$\mathcal{O}(M+N)$. The following problems build intuition for the mathematical foundation.

## Problem 16: Bézout's Identity by Hand
[**Goal:** Compute Bézout's coefficients manually.
]()**Setup:** Bézout's identity states that $\forall a,b \in \mathbb{Z} \, \exists \, x,y\in\mathbb{Z}$ such that: $$ax+by=\gcd{(a,b)} \, .$$
**Tasks:**
- [x] a) Use the extended Euclidean algorithm to find $\gcd{7,11}$ and a pair of Bézout coefficients $(x,y)$.
- [x] b) Verify your answer to part a.
- [x] c) Use the extended Euclidean algorithm to find $\gcd{(6,9)}$ and a pair of Bézout coefficients $(x,y)$.
- [x] d) **Code reference:** Open `../../../src/kuramoto/solvers/coprime.py` and locate the `extended_gcd` function. Trace through the recursive calls for inputs $(7,11)$ and verify your hand calculation matches.

**Answers for hand-written problems:**
- a) $$7\underbrace{(-3)}_{x} + 11\underbrace{(2)}_{y}=\underbrace{1}_{\gcd{(7,11)}}$$
- b) $$7(-3)+11(2)=-21 + 22 = 1 \, ✔️$$
- c) $$6\underbrace{(-1)}_x + 9\underbrace{(1)}_y = \underbrace{3}_{\gcd{(6,9)}}$$
- d) Exploring `../solvers/coprime.py`
    - [x] Trace through the recursive calls for inputs $(7,11)$ of the `extended_gcd` function located in 
    `../src/kuramoto/solvers/coprime.py` and verify all steps of your hand calculations (written as Bezout identitties) 
    from parts a) and c). Make sure to color-cod output using the color scheme specified below:
    - $(m,n)$ - #00a6ff  (`COLOR_PALLETTE["electric_blue"]`)
    - $\gcd{(m,n)}$ - #28d728 (`COLOR_PALETTE["bright_green"]`)
    - Bezout's coefficients, $x$ and $y$ - #ff00c3 (`COLOR_PALLETTE["bright_magenta"]`)

## Problem 17: Chinese Remainder Theorem (CRT) Reconstruction
**Goal:** Understand how two coprime samplers reconstruct the full signal.
**Setup:** Suppose you have two samplers:
  1. Sampler A records every $N=11$-th step.
  2. Sampler B records every $M=7$-th step.

  - **Lemma:** Since $\gcd{(7,11)}=1$, we can reconstruct any time index $t\in[0,76]$ from the pair of remainders
  $(t\mod{7}, t\mod{11}$).

**Tasks:**
  1. Suppose Sampler A observes the signal at local index $k_n=5$ (i.e., $t\equiv 5(\mod{11})$) and Sampler B observes the
  signal at local index $k_m=3$ (i.e., $t\equiv3(\mod{7})$). Use the Bézout coefficients from Problem 16 to reconstruct 
  $t$.
  2. Verify:
     - $t\mod{11}=5$
     - $t\mod{7}=3$
  3. Code reference: Look at `coprime_reconstruct_frequency` in `../solvers/coprime.py`. The formula is 
    $$k_\text{true} = (k_m\cdot b \cdot N + k_n \cdot a \cdot M)\mod{(M\cdot N)}$$
    where $(g,a,b) = \operatorname{extended_gcd}(M,N)$.

### Answers to handwritten problems
a)
- **Step 1:** Key insight $$\begin{align*} b\cdot N & \equiv 1\mod{M} \\ b\cdot M & \equiv 0 \mod{M}\end{align*}$$ 
      and $$\begin{align*} a\cdot M & \equiv 1\mod{N} \\ b\cdot N &\equiv 0\mod{N}\end{align*}$$
- **Step 2:** "Each term isolates one remainder." $$\begin{align*} \text{term}_1 &= k_m(b\cdot N) = 3(2\cdot11)&=66 
  \\ \text{term}_2 &= k_n(a\cdot M) = 5(-3\cdot 7)&=-105\end{align*}$$
- **Step 3:** $$\begin{align*}k_\text{true}&=(\text{term}_1 + \text{term}_2)\mod{(M\cdot N)} \\ 
   &= (66+(-105))\mod{77} \\ &= -39 \mod{77} \\ &= 38 \end{align*}$$

  $$\boxed{k_\text{true}=38}$$

b)
 i. Show that $38\mod{11}=5$:
  $$k_n=38-(11\cdot q)$$
  $$q=\left\lfloor\frac{38}{11}\right\rfloor=\lfloor 3.4545 \rfloor=3$$
  $$k_n=38-(11\cdot 3) = 38 - 33 = 5\, ✅ $$
 ii. Show that $38\mod{7}=3$:
  $$k_m=38-(7\cdot q)$$
  $$q=\left\lfloor\frac{38}{7}\right\rfloor=\lfloor 5.4286\rfloor=5$$
  $$k_m = 38 - (7\cdot5)=38-35=3 \, ✅$$

c) Exploring `../solvers/coprime.py`:
    - [ ] Trace through `coprime_reconstruct_frequency` for inputs $M=7$, $N=11$, $k_n=5$, and $k_m=3$ and verify your 
    hand calculations from parts a) and b). Make sure to color-code output using the color scheme specified below:
        - $(M,N)$ - #00a6ff (`COLOR_PALETTE["electric_blue"]`)
        - $(k_m, k_n)$ - `COLOR_PALETTE["coral_orange"]`
        - $k_\text{true}$ - `COLOR_PALETTE["vivid_pink"]'`
        - $(a,b)$ - `COLOR_PALETTE["brigh_green"]`
