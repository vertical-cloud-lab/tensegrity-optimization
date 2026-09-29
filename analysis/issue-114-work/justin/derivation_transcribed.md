# Transcription of Justin's handwritten derivation

Source: [work-derivation-2026-09-29.pdf](work-derivation-2026-09-29.pdf), attached to issue #114 on 2026-09-29.
Transcribed as written, including the original notation.

**Free-body diagram.** A top point mass on a spring. On the top mass: F_s up, F_g down. On the bottom of the
spring: F_s down, F_ext down (drawn as arrows at the lower node).

**Work done by spring.**

- W_top = ∫_Δx F_s dx
- W_bottom = -∫_Δx F_s dx. Margin note: "the force is now pointed in the negative direction, so negative
  displacement and positive force must produce positive work."
- W = ∫ F_s dx_top - ∫ F_s dx_bottom
- W = ∫_Δt (F_s V_top - F_s V_bottom) dt
- W = ∫_Δt F_s (V_top - V_bottom) dt

**For approximation:** W = Σ F_s(t) (dX_top(t) - dX_bottom(t))

**F_s(t):** F_s - F_g = m a_top(t), so F_s = F_g + m a_top(t), boxed as **F_s(t) = m (g + a_top(t))**

**dX(t):**

- V(t_n) = V(t_{n-1}) + (1/2)(a_{n-1} + a_n)(t_n - t_{n-1}), "use to make array V(t)"
- dX(t_n) = (1/2)(V(t_{n-1}) + V(t_n))(t_n - t_{n-1}), "use to make array dX(t)"
