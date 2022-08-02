from prometheus_client import Counter

METRIC_NAME_PREFIX = "bpl_"

reward_requests_total = Counter(
    name=f"{METRIC_NAME_PREFIX}reward_http_requests_total",
    documentation="Total /reward http requests by response status, response template, and retailer slug.",
    labelnames=("retailer_slug", "response_status", "response_template"),
)
