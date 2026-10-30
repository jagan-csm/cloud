def explain_incident(kind, service, facts=None):
    facts = facts or {}
    explanations = {
        "high_latency": "Observed fact: response latency exceeded the configured threshold. Possible causes include a slow downstream service, database delay, or resource contention.",
        "payment_timeout": "Observed fact: the payment request timed out. Possible causes include a slow payment dependency, network delay, or an intentionally simulated timeout.",
        "service_unavailable": "Observed fact: a service returned an unavailable response. Check its health endpoint and related logs.",
        "high_error_rate": "Observed fact: the observed error rate exceeded the configured threshold. Inspect representative traces and error logs to narrow down the cause.",
    }
    return {"service": service, "kind": kind, "facts": facts, "explanation": explanations.get(kind, "Review the metrics, trace spans, and related logs. Cause is not confirmed."), "is_rule_based": True}
