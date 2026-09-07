# GridironGPT DFS Commands

This file tracks commands specific to DFS Capstone development. Do not add commands here unless they are specific to the DFS branch/workflow.

## Branch

```bash
git switch dfs-capstone
```

Return to the season-long core:

```bash
git switch main
```

## Current development rule

Before DFS work:

```bash
git status
```

Confirm that DFS development is occurring on `dfs-capstone` before making Capstone-specific changes.

## Testing

Use the existing GridironGPT test suite as the regression boundary while DFS-specific tests are added.

Exact DFS test commands will be documented here once the package/test paths are established.
