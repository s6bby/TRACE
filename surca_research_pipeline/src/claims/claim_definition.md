# Claim Definition

This is the starting definition for claim extraction in TRACE.

The goal is to keep this simple enough to use in the first prototype.

## Working definition

A claim is a checkable statement in the model response.

For this project, a claim should:

- say something specific about the student, their behavior, their supports, or a recommendation
- be concrete enough that we could try to check it against the IEP or BIP
- stand on its own as one unit of meaning

In short:

> A claim is one statement from the model that could be checked against the source documents.

## What counts as a claim

These count as claims:

- "The student shows aggression during transitions."
- "A BIP is in place."
- "The student receives OT services."
- "The behavior appears escape-maintained."
- "The student may need closer supervision."

Why these count:

- they make a concrete statement
- they point to something that could be supported, inferred, or unsupported

## What does not count as a claim

These do not count as claims by themselves:

- "This is important to remember."
- "The student may need support."
- "The documents should be reviewed carefully."
- "Overall, this plan seems appropriate."

Why these do not count:

- they are too vague
- they are not easy to verify against the documents
- they are more like advice or filler than a checkable statement

## First claim types

For the first prototype, claims should be grouped into simple types:

- `behavior`
- `function`
- `service`
- `accommodation`
- `safety`
- `staffing_or_support`
- `recommendation`
- `other`

These do not need to be perfect yet. The point is just to keep the claims organized.

## How the first prototype should treat claims

The first version should stay simple.

It should:

1. split the response into sentence or bullet-sized units
2. keep only units that look like checkable statements
3. assign each kept unit a basic claim type
4. save the result in structured JSON

The first version does not need to decide yet whether a claim is supported or unsupported. It only needs to identify the claim units cleanly.

## Examples for the prototype

Response text:

"The student becomes aggressive during transitions. He receives OT services. A break card is available when he is frustrated."

Possible extracted claims:

1. "The student becomes aggressive during transitions."
2. "He receives OT services."
3. "A break card is available when he is frustrated."

Possible claim types:

1. `behavior`
2. `service`
3. `accommodation`

## What to watch out for

The first extractor will probably over-extract some things and miss others.

Main risks:

- combining two claims into one long sentence
- keeping vague recommendation language that is not really checkable
- missing claims that are phrased indirectly
- treating explanation text as a factual claim

That is okay for the first prototype. The point right now is to get a clean first pass that we can test and improve.
