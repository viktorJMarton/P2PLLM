# Governance and publication

The project intent is open source. A project code/documentation license has NOT been chosen or granted by this planning package. Model and vendor SDK licenses must be checked separately. Do not publish a repository, accept third-party license terms, or silently select a legal license for the owner.

Owner decisions still needed before public release: license; maintainer authority; RFC acceptance process; public hosting account; code-of-conduct/contribution policy. Routine technical work may proceed without these publication choices.

## Existing authority and local autonomy
The owner's 2026-10-22 standing instruction authorizes source/documentation
commits and GitHub pushes to the appropriate development branch at every
successful sprint closure. This explicitly permits updating this existing
repository despite the general publication restriction above. It does not
authorize creating a new public repository, choosing a license, force-pushing,
merging the default branch, publishing releases or accepting additional terms.
Follow the closure procedure in docs/operations/department-workflow.md; record
and verify the remote commit before claiming closure. A push failure is an
explicit pending closure, not success. Do not ask again for this same scope.

The owner has authorized parallel development agents and routine local coding,
testing, pinned dependency/toolchain setup, documentation and local commits.
Respect current host delegation limits. Do not ask for that same authorization
again on every handoff or iteration. Agents may choose reversible implementation
details within accepted contracts and produce concrete proposals for broader
changes. An unavailable reviewer blocks approval/merge, not unrelated coding.

The owner explicitly approved Android SDK license acceptance in this session for
Command-line Tools16.0, SDK35, Build Tools35.0.0 and NDK27.0.12077973. WORK-0012
records the exact packages/license. This is not blanket acceptance of future
third-party terms or a grant of a project publication license. Preserve scoped
approvals across agent handoffs; a new scope requires a concrete owner decision.

The owner additionally approved SDK Platform-Tools license acceptance on
2026-10-22 for physical-phone benchmarking. Windows Platform-Tools37.0.1 is pinned
in config/development-windows.json; this extends the previous four-package scope
only by Platform-Tools and does not authorize unrelated SDK licenses/packages.

The [3-iteration/5-question journal meeting rule](docs/operations/agent-meetings.md)
is also an owner requirement. Real responses are required for shared decisions;
waiting alone grants no authority. Local journal meetings do not change the
independent-review, security or release decision requirements.

Proposal lifecycle: draft -> evidence gathering -> review -> accepted/rejected/superseded. Security claims require qualified review; changing model/privacy boundaries requires explicit ADR and migration plan. Agents may open local review artifacts and draft PR text; actual external posting follows session authorization and available repository permissions.
