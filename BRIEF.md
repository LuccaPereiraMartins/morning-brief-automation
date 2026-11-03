# Forward Deployed Engineer – Take-Home Task

## The scenario

You have just joined the firm as a Forward Deployed Engineer. You sit with a trading pod but report to the central AI
Team. On your first morning, two PMs send you requests:

- **Tom**, a PM in the **Rates** pod: `data/requests/rates_pm_request.md`
- **Sara**, a PM in the **EM** pod: `data/requests/em_pm_request.md`

**Pick one request**: the pod you would rather work in. The interview will follow up on the same pod and request.

Like most desk requests, yours is loosely defined. Some of it is valuable. Some of it should be built differently
from how it is asked for, and some of it should not be built at all. Your job is to work out which is which, build the
valuable part properly, and leave something the firm could run, audit and reuse.

## The data pack

```
data/
  requests/         the two PM requests
  research/         overnight broker and internal research
  market_data/      end-of-day closes and FX rates
  positions/        positions for each pod's book, and DV01 limits
  entitlements.yaml users, their books and their research licences
  platform/         the firm's standards for AI applications ("the paved road") and the audit event schema
```

Read `data/README.md` for units and conventions. All data is synthetic. It is realistic, so it is imperfect.

## What we'd like you to do

### Part 1 – Scope the request (max 1 page)

Write the reply you would send the PM. Cover:

- what you will build first, and what "done" looks like for them;
- what you will not build, or will build differently, and why. Say it the way you would to a PM;
- the questions you need answered;
- how you will know whether it has saved them time or improved their decisions.

### Part 2 – Build it

Build the first version you scoped in Part 1, following `data/platform/PAVED_ROAD.md`. We are looking for something
small that works and that you would be comfortable putting in front of a PM, not a large feature list. It should:

- produce the output for the PM **and** for the other user named in their request, and show where and why the
  two differ;
- use an LLM where it adds value, behind a single interface, with any provider. If you have no API access, a
  stubbed model behind the same interface is acceptable; say so;
- record an audit trail matching the schema provided;
- include an evaluation set and runner that checks the things that matter for this use case, plus tests;
- include a Dockerfile and a CI configuration (it doesn't need to run anywhere).

### Part 3 – Reuse and graduation (max 1 page)

- Which part of what you built should be a shared capability for every pod, and which part should stay with your
  pod? How would the other pod use the shared part?
- What would a pod developer need in order to extend this without you?
- What is missing before this could graduate to Technology ownership?

### Part 4 – How you used AI tools

We expect you to use AI coding tools. Give at least three examples of something they suggested that you changed or
rejected, and why. A few of your key prompts or transcript excerpts are welcome but optional.

## What to send us

- A git repository (zip or link) with a README explaining how to run it in a few commands.
- Your Part 1, 3 and 4 write-ups (Markdown or PDF).
- Sample output for both users, and the output of your evaluation run.

## Time

Please spend **no more than 4 hours**. We won't reward going beyond that, and we are not looking for polish. If time
is short, a smaller build with a strong Part 1 is better than a larger build with a weak one. Python is preferred.

You may use any LLM provider. Please don't include API keys or other credentials in your submission.

## What happens next

We'll ask you to walk us through your submission in a 60-minute session. We'll then give you some new data and follow-up
questions from the same PM, and ask you to work through them with your solution, live with us. Please have your
solution running on your machine for the call. You can use AI tools during the session, as you would at work.

If anything in the brief is unclear, make a reasonable assumption and write it down. Turning unclear requests into
clear ones is a large part of the job.
