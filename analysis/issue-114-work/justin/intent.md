# Justin's stated intent (issue #114 comment, 2026-09-29)

Quoted from the issue thread:

> The purpose of this analysis to the find the total work done by the tensegrity inspired strutter on the two
> points meshed by the accelerometers. Hypothetically, the total work done during a drop test should be some
> negative value that represents the total energy lost by the tensegrity inspired object. In other words: it is
> the energy that was down to the object, but the object never did to anything else.
>
> I have provided two python files. "numarical_work" tests my math on by comparing numerical results to a known
> result giving a hypothetical polynomial (a function that is easy to integrate by hand). In
> "implimatation_or_work" I used the data from corny7 and produce graphs of the work.
>
> It is worth mentioning that I have not selected a mass for the upper portion of the devise because I have not
> decided on a good way to approximate the mass of the object as a point. Therefore, a value of one was assumed.
> fortunately, the mass simple scales the result so we can simply say the graph represents the energy lose per
> unit mass.

The two plots in this folder (`corny7_trial1_work.png`, `corny7_trial2_work.png`) are the ones attached to that
comment. "trial 1" and "trial 2" are corny7 drops 1 and 2 (`data[:, 0] == 1` and `== 2`).
