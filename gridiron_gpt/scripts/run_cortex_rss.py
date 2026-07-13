from pprint import pprint

from gridiron_gpt.pipelines.cortex_rss_pipeline import (
    run_cortex_rss_pipeline,
)


if __name__ == "__main__":
    result = run_cortex_rss_pipeline()
    pprint(result)
