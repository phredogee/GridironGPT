# GridironGPT Architecture Notes

## Current Command Path

The main user-facing command is currently an alias:

```bash
gaskd='cd $PROJECT_ROOT && LLM_PROVIDER=deepseek GRIDIRON_LLM=deepseek python -m gridiron_gpt.cli ask'

## Active Runtime Path
gaskd
↓
python -m gridiron_gpt.cli ask
↓
gridiron_gpt/cli -> ../cli
↓
cli/ask.py
↓
gridiron_gpt.core.advisor -> ../core/advisor.py
↓
gridiron_gpt.core.llm -> ../core/llm.py

## Confirmed Active Files
cli/ask.py
cli/__main__.py
cli/draft.py
cli/espn.py
core/advisor.py
core/llm.py
data/index/gridiron.index
data/index/gridiron_docs.json
gridiron_gpt/__init__.py
gridiron_gpt/__main__.py

## Active Supporting Areas
draft/
data_ingest/
validators/
data/

## Legacy/Needs Review
modules/
semantic/
src/
project_gridiron_gpt/
phred/
cli_modules/
interface/
pipelines/

## Trainging Camp Upgrade Rule
cli/
core/
data_ingest/
draft/
data/
