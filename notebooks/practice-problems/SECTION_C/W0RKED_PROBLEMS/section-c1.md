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
- [ ] d) **Code reference:** Open `../../../src/kuramoto/solvers/coprime.py` and locate the `extended_gcd` function. Trace through the recursive calls for inputs $(7,11)$ and verify your hand calculation matches.

**Answers for hand-written problems:**
- a) $$7\underbrace{(-3)}_{x} + 11\underbrace{(2)}_{y}=\underbrace{1}_{\gcd{(7,11)}}$$
- b) $$7(-3)+11(2)=-21 + 22 = 1 \, ✔️$$
- c) $$6\underbrace{(-1)}_x + 9\underbrace{(1)}_y = \underbrace{3}_{\gcd{(6,9)}}$$
- d) Exploring `../solvers/coprime.py`
    - [ ] Trace through the recursive calls for inputs $(7,11)$ of the `extended_gcd` function located in 
    `../src/kuramoto/solvers/coprime.py` and verify all steps of your hand calculations (written as Bezout identitties) 
    from parts a) and c). Make sure to color-cod output using the color scheme specified below:
    - $(m,n)$ - #00a6ff
    - $\gcd{(m,n)$ - #28d728
    - Bezout's coefficients, $x$ and $y$ - #ff00c3
