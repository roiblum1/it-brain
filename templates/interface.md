---
title: <Consumer team> ↔ <provider team> — <what crosses the boundary, as someone would grep for it>
type: interface
area: <provider-side area from teams.json, e.g. trident, cisco-aci>
teams: [<consumer>, <provider>]   # both sides — validate requires at least two teams from teams.json
tags: []
applies_to: []
confidence: hypothesis   # becomes observed/verified only when both teams have checked the contract against reality
last_verified: YYYY-MM-DD
owners: []
source: it-brain-design
---

# <Title>

> One page per seam between two teams. It says who provides what, how to ask for it, how each side checks
> its own half without touching the other's systems, and which symptoms on one side are usually caused on the
> other. Changes need an approval from **every** team in `teams:`.

## Parties

| Side | Team | Systems |
|---|---|---|
| consumer | | |
| provider | | |

## What crosses the boundary

## Who provides what

| Item | Provided by | Requested how | Lead time |
|---|---|---|---|

## How each side checks its half (read-only)

## Symptoms that cross the line

| Symptom (seen by) | Usually on which side | First check |
|---|---|---|

## Escalation

Who to page, in which channel (`teams.json` → `channel`), and what to include (cluster as `<cluster>`, time window, error text).

## Open questions

## History

- YYYY-MM-DD: created
