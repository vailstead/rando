from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from opsdemo.models import (
    Team,
    Environment,
    Service,
    ServiceDependency,
    Incident,
    IncidentUpdate,
)


class Command(BaseCommand):
    help = "Seed realistic demo data for the ops incident/dependency MCP demo"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Deleting existing demo data..."))
        IncidentUpdate.objects.all().delete()
        Incident.objects.all().delete()
        ServiceDependency.objects.all().delete()
        Service.objects.all().delete()
        Environment.objects.all().delete()
        Team.objects.all().delete()

        self.stdout.write(self.style.NOTICE("Creating teams..."))
        teams = self.create_teams()

        self.stdout.write(self.style.NOTICE("Creating environments..."))
        envs = self.create_environments()

        self.stdout.write(self.style.NOTICE("Creating services..."))
        services = self.create_services(teams)

        self.stdout.write(self.style.NOTICE("Creating dependencies..."))
        self.create_dependencies(services)

        self.stdout.write(self.style.NOTICE("Creating incidents and updates..."))
        self.create_incidents(envs, services)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def create_teams(self):
        team_data = [
            {
                "name": "Platform",
                "manager_name": "Alex Carter",
                "contact_email": "platform@example.local",
                "slack_channel": "#team-platform",
            },
            {
                "name": "Payments",
                "manager_name": "Maya Singh",
                "contact_email": "payments@example.local",
                "slack_channel": "#team-payments",
            },
            {
                "name": "Customer Experience",
                "manager_name": "Jordan Lee",
                "contact_email": "cx@example.local",
                "slack_channel": "#team-cx",
            },
            {
                "name": "Identity",
                "manager_name": "Taylor Brooks",
                "contact_email": "identity@example.local",
                "slack_channel": "#team-identity",
            },
            {
                "name": "Data",
                "manager_name": "Sam Rivera",
                "contact_email": "data@example.local",
                "slack_channel": "#team-data",
            },
        ]

        teams = {}
        for item in team_data:
            team = Team.objects.create(**item)
            teams[team.name] = team
        return teams

    def create_environments(self):
        env_data = [
            {"name": "dev", "criticality": "low"},
            {"name": "staging", "criticality": "medium"},
            {"name": "prod", "criticality": "critical"},
        ]

        envs = {}
        for item in env_data:
            env = Environment.objects.create(**item)
            envs[env.name] = env
        return envs

    def create_services(self, teams):
        service_data = [
            {
                "name": "gateway",
                "description": "External ingress and API routing layer.",
                "owner_team": teams["Platform"],
                "tier": 1,
            },
            {
                "name": "customer-portal",
                "description": "Web frontend used by customers for login and account workflows.",
                "owner_team": teams["Customer Experience"],
                "tier": 1,
            },
            {
                "name": "order-api",
                "description": "Order management API for creation, lookup, and status updates.",
                "owner_team": teams["Customer Experience"],
                "tier": 1,
            },
            {
                "name": "payment-api",
                "description": "Payment authorization and settlement service.",
                "owner_team": teams["Payments"],
                "tier": 1,
            },
            {
                "name": "notification-service",
                "description": "Email and SMS event notification service.",
                "owner_team": teams["Customer Experience"],
                "tier": 2,
            },
            {
                "name": "identity-service",
                "description": "Authentication, token issuance, and session validation.",
                "owner_team": teams["Identity"],
                "tier": 1,
            },
            {
                "name": "reporting-service",
                "description": "Analytics aggregation and operational reporting endpoints.",
                "owner_team": teams["Data"],
                "tier": 2,
            },
            {
                "name": "redis-cache",
                "description": "Shared cache tier for sessions, rate limits, and hot data.",
                "owner_team": teams["Platform"],
                "tier": 1,
            },
            {
                "name": "message-bus",
                "description": "Shared asynchronous event bus.",
                "owner_team": teams["Platform"],
                "tier": 2,
            },
            {
                "name": "postgres-orders",
                "description": "Primary relational datastore for orders and payment metadata.",
                "owner_team": teams["Platform"],
                "tier": 1,
            },
        ]

        services = {}
        for item in service_data:
            service = Service.objects.create(
                repo_url=f"https://git.example.local/{item['name']}",
                runbook_url=f"https://wiki.example.local/runbooks/{item['name']}",
                is_active=True,
                **item,
            )
            services[service.name] = service
        return services

    def create_dependencies(self, services):
        dependencies = [
            ("gateway", "customer-portal", "http", "Gateway routes customer web traffic"),
            ("identity-service", "customer-portal", "identity", "Portal login depends on auth"),
            ("identity-service", "order-api", "identity", "Order API validates customer tokens"),
            ("order-api", "customer-portal", "http", "Portal calls order API"),
            ("payment-api", "order-api", "http", "Order completion depends on payment authorization"),
            ("postgres-orders", "order-api", "database", "Order records stored in postgres"),
            ("postgres-orders", "payment-api", "database", "Payment metadata persisted in postgres"),
            ("redis-cache", "identity-service", "cache", "Session and token cache"),
            ("redis-cache", "order-api", "cache", "Hot order/session data"),
            ("redis-cache", "payment-api", "cache", "Fraud/session lookup cache"),
            ("message-bus", "notification-service", "queue", "Notifications emitted asynchronously"),
            ("order-api", "notification-service", "http", "Order events drive notifications"),
            ("order-api", "reporting-service", "http", "Reporting pulls order aggregates"),
            ("postgres-orders", "reporting-service", "database", "Reporting reads operational data"),
        ]

        for upstream, downstream, dep_type, notes in dependencies:
            ServiceDependency.objects.create(
                upstream_service=services[upstream],
                downstream_service=services[downstream],
                dependency_type=dep_type,
                notes=notes,
            )

    def create_incidents(self, envs, services):
        now = timezone.now()
        prod = envs["prod"]
        staging = envs["staging"]

        incidents = []

        # Story arc 1: identity outage and downstream blast radius
        inc1 = Incident.objects.create(
            service=services["identity-service"],
            environment=prod,
            title="Elevated authentication latency causing login failures",
            summary=(
                "Authentication requests in production are timing out intermittently. "
                "Users are reporting failed logins and expired-session loops."
            ),
            severity="sev1",
            status="resolved",
            started_at=now - timedelta(days=8, hours=3),
            resolved_at=now - timedelta(days=8, hours=1, minutes=20),
            detected_by="synthetic-auth-check",
            commander="Taylor Brooks",
            suspected_cause="Redis-backed session lookup contention",
            customer_impact="Customer logins intermittently failing across the portal.",
            root_cause=(
                "High latency on redis-cache caused token/session lookups in identity-service "
                "to exceed timeout thresholds."
            ),
            affected_users_estimate=4200,
        )
        incidents.append(inc1)

        self.add_updates(
            inc1,
            [
                (-8, -180, "NOC Bot", "Alert fired for auth latency above 2.5s in prod."),
                (-8, -170, "Taylor Brooks", "Investigating elevated token validation latency in identity-service."),
                (-8, -160, "Jordan Lee", "Customer Experience reports spike in login failures from portal users."),
                (-8, -140, "Alex Carter", "redis-cache saturation observed on shared node pool."),
                (-8, -110, "Taylor Brooks", "Traffic shifted and cache pressure reduced. Authentication latency improving."),
                (-8, -80, "Taylor Brooks", "Incident resolved. Root cause points to redis contention impacting session lookups."),
            ],
            now,
        )

        inc2 = Incident.objects.create(
            service=services["customer-portal"],
            environment=prod,
            title="Customers unable to sign in to portal",
            summary=(
                "Portal users are receiving repeated login prompts and occasional 401 responses "
                "despite valid credentials."
            ),
            severity="sev2",
            status="resolved",
            started_at=now - timedelta(days=8, hours=2, minutes=50),
            resolved_at=now - timedelta(days=8, hours=1, minutes=15),
            detected_by="frontend-synthetic-check",
            commander="Jordan Lee",
            suspected_cause="Downstream authentication dependency degradation",
            customer_impact="New and returning users unable to consistently access the portal.",
            root_cause=(
                "Portal failures were downstream symptoms of identity-service authentication latency."
            ),
            affected_users_estimate=3800,
        )
        incidents.append(inc2)

        self.add_updates(
            inc2,
            [
                (-8, -170, "NOC Bot", "Synthetic browser test failing at login step."),
                (-8, -150, "Jordan Lee", "Initial triage suggests auth/session handling issue, not frontend deploy."),
                (-8, -125, "Taylor Brooks", "Identity confirms elevated token validation latency."),
                (-8, -75, "Jordan Lee", "Portal login flow recovered as identity-service stabilized."),
            ],
            now,
        )

        inc3 = Incident.objects.create(
            service=services["order-api"],
            environment=prod,
            title="Intermittent token validation timeouts on order submission",
            summary=(
                "Authenticated order placement requests are timing out during token validation. "
                "Read-only order lookups less affected."
            ),
            severity="sev2",
            status="resolved",
            started_at=now - timedelta(days=8, hours=2, minutes=40),
            resolved_at=now - timedelta(days=8, hours=1, minutes=10),
            detected_by="apm-order-latency-monitor",
            commander="Jordan Lee",
            suspected_cause="Identity dependency latency during token validation",
            customer_impact="Some customers unable to complete order submission.",
            root_cause="Order API dependency on identity-service caused downstream request failures.",
            affected_users_estimate=1200,
        )
        incidents.append(inc3)

        self.add_updates(
            inc3,
            [
                (-8, -160, "APM Bot", "P95 latency spike on POST /orders in production."),
                (-8, -145, "Jordan Lee", "Correlating with auth validation failures from identity-service."),
                (-8, -100, "Jordan Lee", "Write path recovered once auth latencies dropped."),
            ],
            now,
        )

        # Story arc 2: redis degradation affecting multiple services
        inc4 = Incident.objects.create(
            service=services["redis-cache"],
            environment=prod,
            title="Shared cache cluster saturation causing elevated latency",
            summary=(
                "Redis cache cluster in prod experienced sustained CPU and memory pressure, "
                "leading to timeouts and degraded response times for dependent services."
            ),
            severity="sev1",
            status="resolved",
            started_at=now - timedelta(days=15, hours=4),
            resolved_at=now - timedelta(days=15, hours=2, minutes=10),
            detected_by="infra-cache-monitor",
            commander="Alex Carter",
            suspected_cause="Hot key concentration and uneven shard pressure",
            customer_impact="Several customer-facing services experienced latency and timeout symptoms.",
            root_cause=(
                "Uneven key distribution and sustained session traffic created hot shards in the shared cache cluster."
            ),
            affected_users_estimate=5100,
        )
        incidents.append(inc4)

        self.add_updates(
            inc4,
            [
                (-15, -240, "Infra Bot", "Redis cluster CPU above 95% across two primary nodes."),
                (-15, -225, "Alex Carter", "Investigating cache saturation and connection backlog."),
                (-15, -205, "Taylor Brooks", "Identity-service seeing increased cache lookup latency."),
                (-15, -195, "Maya Singh", "payment-api reporting intermittent timeout errors on fraud/session lookups."),
                (-15, -150, "Alex Carter", "Mitigation in progress: traffic shedding and shard rebalance."),
                (-15, -130, "Alex Carter", "Cache latency returning to normal. Monitoring dependent services."),
            ],
            now,
        )

        inc5 = Incident.objects.create(
            service=services["payment-api"],
            environment=prod,
            title="Intermittent payment authorization timeouts",
            summary=(
                "Payment authorization requests are intermittently timing out in production, "
                "especially during high request concurrency."
            ),
            severity="sev2",
            status="resolved",
            started_at=now - timedelta(days=15, hours=3, minutes=40),
            resolved_at=now - timedelta(days=15, hours=2),
            detected_by="payment-apm",
            commander="Maya Singh",
            suspected_cause="Shared cache dependency latency",
            customer_impact="Some checkouts failed during payment authorization.",
            root_cause="Payment API experienced downstream cache lookup delays during redis saturation.",
            affected_users_estimate=900,
        )
        incidents.append(inc5)

        self.add_updates(
            inc5,
            [
                (-15, -220, "APM Bot", "P95 on authorize-payment exceeded 4s."),
                (-15, -210, "Maya Singh", "No code changes observed. Investigating shared dependencies."),
                (-15, -180, "Alex Carter", "redis-cache incident likely driving payment latency."),
                (-15, -120, "Maya Singh", "Payment success rates improving following cache mitigation."),
            ],
            now,
        )

        inc6 = Incident.objects.create(
            service=services["notification-service"],
            environment=prod,
            title="Delayed order confirmation notifications",
            summary=(
                "Order confirmation notifications are delayed or missing for a subset of completed orders."
            ),
            severity="sev3",
            status="resolved",
            started_at=now - timedelta(days=15, hours=3, minutes=10),
            resolved_at=now - timedelta(days=15, hours=1, minutes=45),
            detected_by="support-escalation",
            commander="Jordan Lee",
            suspected_cause="Upstream event backlog from degraded dependencies",
            customer_impact="Customers received delayed email and SMS confirmations.",
            root_cause=(
                "Notification delays were secondary effects of upstream order/payment slowness during cache degradation."
            ),
            affected_users_estimate=600,
        )
        incidents.append(inc6)

        self.add_updates(
            inc6,
            [
                (-15, -190, "Support Lead", "Increase in tickets for missing confirmation emails."),
                (-15, -175, "Jordan Lee", "Queue consumption healthy; upstream order completion appears delayed."),
                (-15, -115, "Jordan Lee", "Notification flow normalizing as upstream services recover."),
            ],
            now,
        )

        # Story arc 3: noisy reporting service
        reporting_specs = [
            {
                "days": 28,
                "severity": "sev3",
                "status": "resolved",
                "title": "Reporting dashboard latency spike during business hours",
                "summary": "Operational reporting endpoints exceeded latency thresholds for 35 minutes.",
                "suspected_cause": "Heavy aggregate queries against shared order dataset",
                "root_cause": "Inefficient aggregation query plan during peak load.",
                "impact": "Internal reporting users experienced slow dashboards.",
                "users": 120,
            },
            {
                "days": 21,
                "severity": "sev4",
                "status": "resolved",
                "title": "Delayed refresh of hourly reporting dataset",
                "summary": "Hourly analytics refresh lagged behind expected schedule.",
                "suspected_cause": "Backlog in reporting pipeline",
                "root_cause": "Long-running extract job delayed downstream reporting refresh.",
                "impact": "Internal metrics stale for about 90 minutes.",
                "users": 60,
            },
            {
                "days": 12,
                "severity": "sev3",
                "status": "resolved",
                "title": "Reporting API elevated error rate on large date-range queries",
                "summary": "Large date-range report generation intermittently returned 500 errors.",
                "suspected_cause": "Memory pressure under large query execution",
                "root_cause": "Reporting worker exceeded memory limits on oversized date-range aggregation.",
                "impact": "Analysts had intermittent failures for large report exports.",
                "users": 85,
            },
            {
                "days": 2,
                "severity": "sev3",
                "status": "investigating",
                "title": "Reporting service intermittent timeouts on export endpoint",
                "summary": "CSV export endpoint is intermittently timing out for larger result sets.",
                "suspected_cause": "Recurring large-query performance issue",
                "root_cause": "",
                "impact": "Internal users intermittently unable to export reports.",
                "users": 45,
            },
        ]

        for spec in reporting_specs:
            incident = Incident.objects.create(
                service=services["reporting-service"],
                environment=prod,
                title=spec["title"],
                summary=spec["summary"],
                severity=spec["severity"],
                status=spec["status"],
                started_at=now - timedelta(days=spec["days"], hours=2),
                resolved_at=None if spec["status"] == "investigating" else now - timedelta(days=spec["days"], hours=1),
                detected_by="reporting-monitor",
                commander="Sam Rivera",
                suspected_cause=spec["suspected_cause"],
                customer_impact=spec["impact"],
                root_cause=spec["root_cause"],
                affected_users_estimate=spec["users"],
            )
            incidents.append(incident)

            self.add_updates(
                incident,
                [
                    (-spec["days"], -120, "Monitoring Bot", f"Alert triggered for reporting-service: {spec['title']}"),
                    (-spec["days"], -90, "Sam Rivera", "Initial triage underway. Reviewing query patterns and resource usage."),
                    (-spec["days"], -60, "Sam Rivera", "Issue isolated to reporting workloads with larger dataset scans."),
                ],
                now,
            )

        # Additional realistic noise
        extra_incidents = [
            {
                "service": "gateway",
                "env": prod,
                "days": 6,
                "severity": "sev3",
                "status": "resolved",
                "title": "Elevated 502 responses from gateway",
                "summary": "Short burst of 502s observed at the edge during backend pool instability.",
                "detected_by": "edge-monitor",
                "commander": "Alex Carter",
                "suspected_cause": "Upstream backend connection churn",
                "impact": "Brief increase in failed customer requests.",
                "root_cause": "Connection pool churn during backend recovery window.",
                "users": 700,
                "updates": [
                    ("Edge Bot", "Spike in 502 rate detected at gateway."),
                    ("Alex Carter", "Investigating upstream connection resets."),
                    ("Alex Carter", "Error rate normalized after backend pool stabilized."),
                ],
            },
            {
                "service": "payment-api",
                "env": staging,
                "days": 4,
                "severity": "sev4",
                "status": "resolved",
                "title": "Staging payment sandbox token expiry mismatch",
                "summary": "Staging payment sandbox produced invalid token expiry values for test transactions.",
                "detected_by": "qa-suite",
                "commander": "Maya Singh",
                "suspected_cause": "Sandbox configuration mismatch",
                "impact": "QA team unable to validate some payment flows in staging.",
                "root_cause": "Incorrect sandbox token lifetime configuration.",
                "users": 12,
                "updates": [
                    ("QA Bot", "Automated payment suite failed in staging."),
                    ("Maya Singh", "Issue limited to staging sandbox config."),
                    ("Maya Singh", "Configuration corrected and tests passing."),
                ],
            },
            {
                "service": "order-api",
                "env": prod,
                "days": 1,
                "severity": "sev2",
                "status": "open",
                "title": "Order lookup latency elevated for recent orders",
                "summary": "Order detail lookups for newly created orders are slower than baseline in prod.",
                "detected_by": "apm-order-read-monitor",
                "commander": "Jordan Lee",
                "suspected_cause": "Database query plan regression or cache miss pattern",
                "impact": "Some customers experience slow order-history page loads.",
                "root_cause": "",
                "users": 540,
                "updates": [
                    ("APM Bot", "Read latency above threshold on GET /orders/{id}."),
                    ("Jordan Lee", "Investigating cache hit rate and query timings."),
                    ("Alex Carter", "No platform incident currently open; likely service-local performance issue."),
                ],
            },
            {
                "service": "message-bus",
                "env": prod,
                "days": 10,
                "severity": "sev3",
                "status": "resolved",
                "title": "Transient event bus consumer lag",
                "summary": "Consumer lag increased for several partitions, delaying asynchronous workflows.",
                "detected_by": "queue-monitor",
                "commander": "Alex Carter",
                "suspected_cause": "Broker rebalance event",
                "impact": "Asynchronous notifications and secondary processing delayed.",
                "root_cause": "Short broker rebalance event temporarily slowed consumer throughput.",
                "users": 300,
                "updates": [
                    ("Queue Bot", "Consumer lag exceeded threshold for 12 partitions."),
                    ("Alex Carter", "Broker rebalance observed; monitoring recovery."),
                    ("Alex Carter", "Lag returned to normal. No data loss detected."),
                ],
            },
            {
                "service": "customer-portal",
                "env": prod,
                "days": 18,
                "severity": "sev3",
                "status": "resolved",
                "title": "Portal session timeout banner displayed incorrectly",
                "summary": "Users briefly saw timeout warnings even while active in their session.",
                "detected_by": "support-escalation",
                "commander": "Jordan Lee",
                "suspected_cause": "Frontend handling of auth refresh timing",
                "impact": "Confusing but mostly non-blocking user experience issue.",
                "root_cause": "Frontend timeout warning threshold was too aggressive.",
                "users": 1100,
                "updates": [
                    ("Support Lead", "Multiple users reported premature timeout warnings."),
                    ("Jordan Lee", "Issue appears limited to banner logic, not actual session invalidation."),
                    ("Jordan Lee", "Warning threshold adjusted and user reports stopped."),
                ],
            },
        ]

        for item in extra_incidents:
            incident = Incident.objects.create(
                service=services[item["service"]],
                environment=item["env"],
                title=item["title"],
                summary=item["summary"],
                severity=item["severity"],
                status=item["status"],
                started_at=now - timedelta(days=item["days"], hours=2),
                resolved_at=None if item["status"] == "open" else now - timedelta(days=item["days"], hours=1),
                detected_by=item["detected_by"],
                commander=item["commander"],
                suspected_cause=item["suspected_cause"],
                customer_impact=item["impact"],
                root_cause=item["root_cause"],
                affected_users_estimate=item["users"],
            )
            incidents.append(incident)

            self.add_updates(
                incident,
                [
                    (-item["days"], -120, item["updates"][0][0], item["updates"][0][1]),
                    (-item["days"], -85, item["updates"][1][0], item["updates"][1][1]),
                    (-item["days"], -50, item["updates"][2][0], item["updates"][2][1]),
                ],
                now,
            )

    def add_updates(self, incident, update_specs, now):
        """
        update_specs format:
        [
            (days_ago, minutes_offset, author, message),
            ...
        ]

        Example:
            (-8, -180, "Bot", "message")
        Means:
            now - 8 days - 180 minutes
        """
        for days_ago, minutes_offset, author, message in update_specs:
            created_at = now + timedelta(days=days_ago, minutes=minutes_offset)
            IncidentUpdate.objects.create(
                incident=incident,
                created_at=created_at,
                author=author,
                message=message,
            )
