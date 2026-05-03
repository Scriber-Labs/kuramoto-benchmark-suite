from scipy.integrate import solve_ivp

def solve_kuramoto(rhs, y0, t_span, t_eval, rtol, atol, max_step):
    return solve_ivp(
        fun=rhs,
        t_span=(0.0, t_span),
        y0=y0,
        method="RK45",
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )