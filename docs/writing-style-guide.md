# Writing and slide style guide

Every rule here comes from review feedback on real course material, mostly from
Holden Bunker's walkthrough of the Week 1 content
([annotated review](course-review/holden-week1-review/README.md), recorded 2026-08-14)
and Sterling Baird's comments on the same video. Where a rule has a "before", the
before is text that actually shipped.

This guide governs **student-facing** material: slide decks, Canvas pages and
assignments, quiz questions, homework and lab sheets, website tutorials, and the
student template repo. It does not govern internal notes, context files, or commit
messages, though following it there costs nothing.

Read this before writing or editing any of that material.

---

## 1. Never use en dashes or em dashes

**This is the single most repeated piece of feedback on this course's content, and
it is not a matter of taste.** Do not use `—` (em dash) or `–` (en dash) in any
student-facing text. Not in slide titles, not in bullets, not in Canvas
descriptions, not in quiz stems, not in tutorial prose.

They are the clearest single tell that text was machine-written, and this course
asks students not to hand in machine-written work. The material has to hold itself
to that standard first.

Rewrite instead. An em dash is almost always one of four things, and each has a
plain replacement:

| The dash was doing this | Use instead |
| --- | --- |
| Joining two independent clauses | A period. Two sentences. |
| Introducing an explanation or list | A colon |
| Setting off an aside | Commas, parentheses, or delete the aside |
| Separating a label from its value | A colon |

Before and after, from L1:

> **Before:** Once you can see a stress concentration, you can't unsee it — this course rewires how you look at objects.
>
> **After:** Once you can see a stress concentration, you can't unsee it. This course rewires how you look at objects.

> **Before:** The first engaged thread of a bolt — where the crack starts.
>
> **After:** The first engaged thread of a bolt is where the crack starts.

> **Before:** Slides are PowerPoint decks on OneDrive — open a deck and click Present before reading it.
>
> **After:** Slides are PowerPoint decks on OneDrive. Open a deck and click Present before reading it.

**Ranges** are the one place a dash is tempting for a real reason. Use "to" in
prose ("weeks 2 to 3", "1.25 to 2") and a plain hyphen where the range is a label
in a table cell or a short axis annotation ("1-5", "Ch. 3-4"). Do not reach for an
en dash to make a range look typeset.

**Hyphens are fine.** `well-characterized`, `free-body diagram`, `pre-class` are
all correct and unaffected by this rule. The rule is about `—` and `–` only.

**Checking your work.** `python scripts/check_style.py` flags every en dash and em
dash in student-facing paths and exits non-zero if it finds any. Run it before you
commit. It also flags the phrases in section 2.

---

## 2. Do not sound pretentious, and do not sound like AI slop

The reviewer's instruction, verbatim: *"run through every single one of your
sentences as to whether or not it sounds pretentious for people who already know
what they're doing."* And: *"Talk like you're just explaining something, not like
you're trying to give them a talk about why I should invest in your
cryptocurrency."*

The audience is juniors and seniors who have already passed statics and mechanics
of materials. Writing that oversells is worse than writing that is plain, because
they can tell.

### The specific patterns to avoid

**a) The grandiose claim about the material's own value.** If a sentence is
selling the content rather than delivering it, cut the sentence.

> **Before:** Seven steps turn a messy real-world problem into a defensible answer, and they earn points on every assignment.
>
> **After:** This is how we want you to solve problems in this class. You get points for each step.

> **Before:** Every phase hands the next one a physical artifact. That is what makes the project hard to fake.
>
> **After:** Each phase builds on the one before it.

**b) The dramatic rhetorical title.** A slide title should state the message of
the slide as a plain sentence. It should not be a slogan.

> **Before:** Why steel survives what chalk can't: ductility.
>
> **After:** Steel yields before it separates, so it fails on the shear plane instead of the tension plane.

> **Before:** Predict before you twist: at what angle will the chalk snap?
>
> **After:** Chalk is brittle, so it breaks on the plane of maximum tension.

**c) "Predict first" framing used as a slogan.** Asking students to predict is
good teaching. Announcing that you are asking them to predict is filler. Ask the
question and stop.

> **Before:** Predict first: tens of MPa, or hundreds?
>
> **After:** (delete, and let the question slide stand on its own)

**d) Invented jargon for ordinary things.** Call it what it is.

> **Before:** The stress element is the bookkeeping device: same point, same state, different numbers at every angle.
>
> **After:** A stress element is a way to draw the stresses at one point so you can see how they change with angle.

**e) Faux-profound one-liners bolted onto the end of a slide.** "Two frames, one
state." "It's everywhere." "The 6.7 is carrying all of it." If the line does not
add information, delete it.

**f) Padding that tells students what they already know.**

> **Before:** Five minutes of recall: every analysis this semester still opens with a free body and ΣF = ΣM = 0.
>
> **After:** Every analysis this semester starts with a free-body diagram.

The reviewer on that one: *"they know that."*

### A test you can actually apply

Read the sentence out loud as if you were standing in front of the class saying it
to a room of seniors. If you would not say it that way out loud, do not write it
that way on the slide. Most pretentious sentences are ones nobody would ever say.

---

## 3. Never write as if students intend to cheat

Cut any sentence whose purpose is to explain why the assignment is
cheat-resistant. It insults the honest majority, and it does not stop anyone.

> **Before:** This project makes you answer it about something you chose, took apart, and measured yourself, which is exactly why it cannot be outsourced to a chatbot or to last year's team.
>
> **After:** You will answer it about a product you chose, took apart, and measured yourself.

Say what students do. Do not say what they cannot get away with.

---

## 4. Show, do not tell: every slide needs a visual

The reviewer's rule, verbatim: *"If every slide does not have a picture on it, you
failed in some way or another."* And on a slide that listed places stress
concentrations appear: *"We're not seeing it, we're reading it. And that's not how
people visualize."*

Prose describing a physical thing is nearly always worse than an image of that
thing. This is the Jean-luc Doumont point the deck builders already cite, applied
consistently:

- A bulleted list of stress-concentration locations should be **photographs** of a
  bolt thread, a keyway corner, a weld toe, and a diving-board taper.
- A worked example about a 6 mm eyebolt holding a 150 kg engine should carry a
  **drawing of the eyebolt with the engine hanging off it**, generated with
  matplotlib into `scripts/ppt/figures-shared/` like every other course figure.
- A question slide that names a physical setup ("an 800 N rider stands on a
  170 mm crank") needs a **sketch of the crank and spindle**. The reviewer, on
  that exact slide: *"I need pictures."*

Where a real photograph does not exist yet, generate a labelled diagram rather
than shipping a text-only slide. Do not invent a photograph or link one you have
not verified.

**Memes are allowed and encouraged** where they land, specifically on the safety
factor slide and the A0 onboarding slide. Keep them appropriate for BYU.

---

## 5. Set equations with an equation editor, never as typed text

Equations rendered as ordinary run-on text are the most common formatting
complaint in the review. Two separate instances were called out by name.

> **Before (L1 slide 6, as plain text):** `A = πd²/4 = 28.3 mm² · P = 150 × 9.81 = 1.47 kN`
>
> **Before (L2 slide 8, as plain text):** `C = (σx+σy)/2 · R = √[((σx−σy)/2)² + τxy²] · σ1,2 = C ± R · τmax = R`

Both are unreadable, and both run several distinct equations together on one line
separated by middle dots.

**In PowerPoint:** use the equation editor, which stores OMML
(`<m:oMathPara>`). `scripts/ppt/omml.py` builds OMML from a LaTeX-like string so
deck specs can declare equations as data. Use `{"equation": "..."}` in a spec body
rather than typing a Unicode approximation into a text run.

**In markdown** (homework, labs, tutorials, solution guides): use LaTeX in `$...$`
or `$$...$$`.

**One equation per line.** Never join equations with `·`.

**Every equation gets a name and a purpose.** The reviewer: *"on these slides it
should be readily apparent what equations are used for and where they come from,
and in this one it's not readily apparent."*

**Each deck ends with an equation summary slide** listing the equations introduced
in that lecture, what each is for, and when it applies. Students come back to the
decks looking for the equation they need for homework, and that is the slide they
are looking for.

---

## 6. Define a term before you require it

The reviewer hit this three separate times on one phrase, "three distinct machine
elements", which the project brief required before anything defined it.

> *"I need that to be strictly defined before you say 'buy one product that holds
> more than three machine elements'. You've got to be more specific."*

The definition existed. It was 400 words further down the page.

**Rule:** the first time a term appears in a document or a deck, its definition is
already visible, on the same screen or an earlier one. If you are about to write a
requirement that uses a term of art, either define it inline or move the
definition above the requirement. This applies to slide order as much as to page
order.

---

## 7. Always use an "appear" transition when the answer is on the same slide that asks the question

> *"If you're mentioning that it's a brittle failure, and you're asking it as a
> question, the answer should not be on the same slide as that question."*

The chalk slide asked "at what angle will the chalk snap?" and then answered it in
the closing line of the same slide. Ensure there is an "appear" animation so that it requires a click to show the answer.

Corollary: do not hand students the equation they are supposed to retrieve. The
crank-spindle question slide printed `τmax = 16T/(πd³)` in the prompt. That
belongs on the solution slide that follows.

---

## 8. No unexplained acronyms

`MoM` shipped on an L1 slide meaning "mechanics of materials". The reviewer, who
teaches this material: *"I don't know what MoM is. Don't use acronyms in slides
like this."*

Write it out. If an acronym is genuinely worth introducing (FBD, FEA, LO), expand
it on first use and then use it consistently.

---

## 9. Pre-class material is read alone, at a desk, before class

Every lecture deck in this course is **flipped**: students step through it on
their own or with peers before the class meeting. Do not write pre-class slides as if the reader
is standing in the classroom holding the demo.

> **Before (on a deck read the night before):** Twist steadily until it snaps. Look at the surface: what angle did you actually get?
>
> **After:** In class we will twist a piece of chalk until it breaks. Before then, predict what the broken surface will look like and why.

Sterling, on exactly this slide: *"these slides are part of the flipped classroom,
to be watched and gone through before class, so it's weird that it's talking about
the chalk activity as if they're in the middle of doing it."*

The same rule applies to "tomorrow's lab" and "today" phrasing. Anchor to named
days and dates, because a student may read the deck on any of several days.

---

## 10. State what is required as a requirement, and what is optional as optional

> *"This feels like it's more like a directive rather than saying it's something
> that you can do. I don't know that we're requiring people to download the
> PowerPoint."*

If it is required, say "you must". If it is a recommendation, say "we recommend".
Do not write a bare imperative for something optional, and do not soften something
that is actually mandatory.

Related: **never write "today", "tomorrow", "this week", or "is released today"**
in material with a persistent URL. Canvas pages and slide decks outlive the day
they were written.

> **Before:** Assignment 0 (GitHub + @claude onboarding) is released today, due Friday, Sep 11.
>
> **After:** Assignment 0 (GitHub and @claude onboarding) opens Wed Sep 2 and is due Fri Sep 11 at 5:00 pm.

---

## 11. Reference a document by linking it

> *"If you're going to mention the oral defense, you should have a link to it in
> Canvas."*

The project page mentioned `oral-defense-rubric.md` as a bare code span. A student
reading it on Canvas has no way to open that file, and the repo it lives in is
private. Either link to the Canvas copy, or publish the file to the public site
and link that. Naming a file the reader cannot open is worse than not mentioning
it.

Similarly, if a page refers to a sheet or form students have to use (the
product-selection criteria sheet, for instance), **put a screenshot of it on the
page**.

---

## 12. Put the important thing first

> *"They don't really care about this. This maybe goes at the very end. ... This is
> very important, you should have this be briefed [early]."*

Order sections by what the reader needs, not by what is logically prior. On the
project page, the grade weighting and the four phases matter on first read;
learning-outcome mappings and administrative provenance do not, and they belong at
the bottom.

**Sections that exist for repo bookkeeping should not render to students at all.**
Mark them so the Canvas sync drops them.

---

## 13. Render images at an appropriate size on Canvas pages

> *"I love this, this is great. These pictures should be way smaller, though."*

This was specifically referring to a Canvas page. A photograph that fills the viewport pushes everything else off screen and makes
the page feel padded. Scale figures so the reader can see the figure and the text
that explains it at the same time. Photographs of a whole product rarely need more
than half the text width. By contrast, on SLIDES, there's a tendency to make images and videos too small. In some cases, it's best to make the image or video fill the entire slide
and then have the "message title" be in white font text with a black 0% or 50% transparent background

**Always credit the source of an image.** The reviewer called this out
approvingly: *"I'm really happy that you put in where it came from. That's really
good."* Keep doing it.

This should **always** be in the speaker notes. **Sometimes** in the slides, especially if the source is more than just some generic Google image. Keep the
citation/caption very short (which means you don't need to make the font size ridiculously small), and always de-emphasize it from the content by making it a 50% gray font. These text boxes 
should be placed close to the item itself.

---

## 14. PowerPoint sections: leave `slide-graveyard` alone

The course decks carry a section named `slide-graveyard`. It holds backup and
retired slides, it is managed by hand by the instructor, and **automation must not
write into it**.

Three rules:

1. Build new content into the default section, never into `slide-graveyard`.
2. Anything placed in `slide-graveyard` must be **hidden** (`show="0"` on the
   `<p:sld>` element), so it cannot appear in presentation mode.
3. **Every slide a script adds must be listed in the section map**, not just in
   the slide list. Those are two independent lists in a `.pptx`, and PowerPoint
   draws a slide no section claims under the section that *precedes* it. Because
   the graveyard is last, an unlisted slide is a slide in the bin.

Rule 3 is the one that bit. `build_deck_from_spec.py` wrote only the slide list,
so on 36 of the 40 lecture decks the map still said "Default Section holds two
slides" while the deck had grown to a dozen. Every slide after the second was
unlisted, and PowerPoint drew all of them inside `slide-graveyard`. Nothing was
misfiled: the map was simply years behind the deck.

Each deck now ends with a `slide-graveyard` section holding exactly one hidden
marker slide titled "Slide Graveyard". The marker is what gives the section
something to hold, since an empty section is invisible in the slide panel and
easy to delete by accident. Park backup slides after it, hidden.

`python scripts/ppt/check_sections.py deck.pptx` reports any deck where the
graveyard holds unhidden slides, where slides are in no section at all, or where
the default section is nearly empty.
`python scripts/ppt/normalize_sections.py --live --all` repairs published decks;
the builders call `normalize_sections.normalize()` before saving, so a rebuild
cannot reintroduce the drift.

---

## 15. Get the engineering right

Style never outranks correctness, and two genuine technical errors surfaced in one
50-minute review. Both were in figures, which is where they hide.

- **Stress-element shear arrows must satisfy moment equilibrium.** The L2 element
  drew all four shear arrows producing a clockwise couple, which cannot be in
  equilibrium. With the top arrow pointing in `+x` and the bottom in `-x`, the
  right face must point `+y` and the left face `-y`.
- **Mohr's circle is drawn on axes through the origin, showing all four
  quadrants.** Plot σ on the horizontal axis and τ on the vertical, draw both axis
  lines through the origin, and choose limits that show negative σ. The L2 figure
  showed only the two right-hand quadrants.

When a figure encodes a sign convention or an axis convention, have someone who
teaches the topic look at the rendered image, not the code that generated it.

---

## 16. Fix the pattern, not the instance

Every phrasing tic flagged once in review turned out to be in several other
places. The review called out "Predict before you twist" on one L2 slide. That
construction is in **20 places across 6 deck specs and 7 website tutorials**:
`L1`, `L2`, `L12`, `L15`, `L17`, `L29`, and the photoelasticity, chalk-tootsie,
bolted-joint, solidworks-model-exploration, beam-bending-kit, and gear-teardown
tutorials. "The stress element is the bookkeeping device" is in two decks. `MoM`
is in 14 places.

So the last step of any style fix is `grep -rn` for the phrase across the repo,
and fixing every hit. Fixing only the instance you were shown leaves the reviewer
to find the same thing again next week, which is the most expensive way to run a
review.

The same applies in reverse when you are asked to apply a general principle: a
note about one lecture ("this slide needs a picture") is a note about all forty.

---

## 17. What not to over-correct

Plain does not mean flat, and this guide is not a licence to strip the course of
voice. The same review that produced every rule above was unprompted-positive
about the project phase timeline, the machine-element photographs with their
sources recorded, the torsion-failure video, and the concrete tables. The
objection to the Week 1 check-in was the absence of visuals, not the writing.

Keep: concrete numbers, real objects, worked examples, a specific everyday hook,
humour that actually lands, and a stated point of view about engineering
practice. Cut only the sentence that tells the student how meaningful that point
of view is.

One thing the review asked us to **add** rather than remove: the course needs a
welcome. The first item in the first module should sound like a person greeting
a class. The landing page stays as the module list, but arriving at a wall of
requirements with no greeting is its own kind of tone problem.

---

## Quick checklist

Before committing student-facing material:

- [ ] No `—` and no `–` anywhere
- [ ] Every sentence survives being read aloud to a room of seniors
- [ ] No sentence explains why the work is hard to fake or to outsource
- [ ] Every slide has a visual
- [ ] Every equation is set with the equation editor or LaTeX, one per line, named
- [ ] Every term is defined before it is required
- [ ] No answer shares a slide with its question
- [ ] No unexplained acronyms
- [ ] Nothing assumes the reader is in the classroom, and nothing says "today"
- [ ] Every document named is also linked
- [ ] `python scripts/check_style.py` passes

- [ ] The phrasing you just fixed was grepped for across the whole repo

---

## Appendix: the review in its own words

Linked timestamps into the source recording, for cases this guide does not
cover. Prefer these over an inference from the rules above. The full annotated
walkthrough, with screenshots, is
[`docs/course-review/holden-week1-review/README.md`](course-review/holden-week1-review/README.md).

| Time | Quote |
| --- | --- |
| [01:08](https://youtu.be/Hjyb577sgQo?t=68) | "This feels like it's more like a directive rather than saying it's something that you can do." |
| [01:50](https://youtu.be/Hjyb577sgQo?t=110) | "Just to make it be more human. Em dashes are pretty cringe, so maybe try to avoid them in general." |
| [03:49](https://youtu.be/Hjyb577sgQo?t=229) | "Yeah, this statement sounds like AI slop." |
| [04:20](https://youtu.be/Hjyb577sgQo?t=260) | "Text is worse than showing pictures of something. So if you need to find a picture, go search for a picture." |
| [05:54](https://youtu.be/Hjyb577sgQo?t=354) | "A factor of safety is not a number that measures what you don't know. That's not true. A factor of safety is us assuming there are unknowns that we cannot quantify that we will account for." |
| [08:07](https://youtu.be/Hjyb577sgQo?t=487) | "If every slide does not have a picture on it, you failed in some way or another." |
| [10:22](https://youtu.be/Hjyb577sgQo?t=622) | "Saying 'where does the answer break' is pretentious." |
| [14:20](https://youtu.be/Hjyb577sgQo?t=860) | "Run through every single of your sentences as to whether or not it sounds pretentious." |
| [14:55](https://youtu.be/Hjyb577sgQo?t=895) | "Don't use acronyms. Just don't use acronyms, really, in slides like this." |
| [16:08](https://youtu.be/Hjyb577sgQo?t=968) | "You should just say perform analysis on it. Don't say 'and prove you understand why it does not break.'" |
| [18:56](https://youtu.be/Hjyb577sgQo?t=1136) | "We should never be writing stuff assuming that people are intending to cheat." |
| [19:55](https://youtu.be/Hjyb577sgQo?t=1195) | "If you're going to mention a machine element, you have to define it before talking about it. That's always true." |
| [20:19](https://youtu.be/Hjyb577sgQo?t=1219) | "I am happy that you put in where it came from. That's really good." |
| [28:41](https://youtu.be/Hjyb577sgQo?t=1721) | "You need to put the equations in LaTeX, because we like LaTeX." |
| [29:00](https://youtu.be/Hjyb577sgQo?t=1740) | "People should be able to come look at this slide when they're looking for equations to be using... maybe we should have an equation slide at the end that summarizes all the equations." |
| [32:02](https://youtu.be/Hjyb577sgQo?t=1922) | "Talk like you're just explaining something, not like you're trying to give them a talk about why I should invest into your cryptocurrency." |

Three items from the review are course-design changes rather than writing, and
belong to whoever owns the check-ins: more questions per check-in
([33:39](https://youtu.be/Hjyb577sgQo?t=2019)), multiple attempts allowed, and
check-ins due at 12:00 noon just before class rather than the evening before
([02:19](https://youtu.be/Hjyb577sgQo?t=139), confirmed in Sterling's comment).
