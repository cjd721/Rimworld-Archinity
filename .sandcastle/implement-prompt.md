# TASK

Fix issue {{TASK_ID}}: {{ISSUE_TITLE}}

Pull in the issue using `gh issue view <ID>`. If it has a parent PRD, pull that in too.

Only work on the issue specified.

Work on branch {{BRANCH}}. Make commits and run tests.

# CONTEXT

Here are the last 10 commits:

<recent-commits>

!`git log -n 10 --format="%H%n%ad%n%B---" --date=short`

</recent-commits>

# STANDARDS

Read @CODING_STANDARDS.md before writing anything. It is the implementation brief:
hard constraints, the failures that produce no error message, the verification
commands, and how the red-green loop applies in a codebase that is mostly XML defs.

# EXPLORATION

Explore the repo and fill your context window with relevant information that will allow you to complete the task.

# EXECUTION

Use the red-green loop as `CODING_STANDARDS.md` defines it for this repo.

For def work the match count is the test: record what an xpath matches before you
patch, apply the patch, confirm the count is what you predicted, then move to the
next one. One patch, one confirmation.

Verify with the tools the repo actually has. Never fabricate a harness to satisfy
the loop, and never claim tests were run when they were not. If the change
genuinely warrants test infrastructure that does not exist yet, say so on the
issue rather than adding it unasked.

# FEEDBACK LOOPS

Before committing, run all four verification commands from `CODING_STANDARDS.md`
and include their results. A def change is not done until all four pass.

# COMMIT

Make a git commit. The commit message must:

1. Start with `RALPH:` prefix
2. Include task completed + PRD reference
3. Key decisions made
4. Files changed
5. Blockers or notes for next iteration

Keep it concise.

# THE ISSUE

If the task is not complete, leave a comment on the issue with what was done.

Do not close the issue - this will be done later.

Once complete, output <promise>COMPLETE</promise>.

# FINAL RULES

ONLY WORK ON A SINGLE TASK.
