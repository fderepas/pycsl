# The Twelve-Factor App

Originally formulated by Adam Wiggins at Heroku, the twelve factors describe a methodology for building services that deploy cleanly to modern cloud environments. The throughline is the same across all twelve: **remove implicit assumptions that break when the app moves between environments.**

A twelve-factor app can be cloned from version control, run on a developer's laptop, deployed to staging, and promoted to production — all without changing the code, only the configuration.

---

## I. Codebase — one codebase, many deploys

One app, one repository, tracked in version control. Multiple deploys (dev, staging, prod) of the same codebase, never multiple codebases for the same app.

**The trap:** environment-specific forks of the code. The instant prod has code that staging doesn't, "works in staging" stops being meaningful.

---

## II. Dependencies — explicitly declare and isolate

Every dependency is declared in a manifest (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`) and isolated from system-level packages.

**The trap:** relying on a binary that "happens to be installed" on the server. The first time you deploy to a fresh machine, it breaks.

---

## III. Config — store config in the environment

Anything that varies between deploys — database URLs, API keys, feature flags — lives in environment variables, not in the code or in committed config files.

**The trap:** `config.production.yaml` checked into the repo. Now your secrets are in version control history forever, and the config is fused to the codebase.

The litmus test: could you open-source the codebase today without leaking credentials? If not, config is leaking into code.

---

## IV. Backing services — treat them as attached resources

Databases, queues, caches, third-party APIs — all of them are accessed via a URL or connection string from config. Swapping a local Postgres for a managed RDS instance is a config change, not a code change.

**The trap:** hardcoding the assumption that "the database is on localhost" or "the queue is RabbitMQ." Both will eventually be wrong.

---

## V. Build, release, run — strictly separate the stages

**Build:** compile code and assets into an artifact.
**Release:** combine the build artifact with environment config.
**Run:** execute the release.

Each stage is one-way and immutable. You can't edit code in production; you must build a new release.

**The trap:** SSH'ing into production to "just fix one thing." The fix disappears on the next deploy and nobody knows what production is actually running.

---

## VI. Processes — execute the app as stateless processes

Processes hold no local state between requests. Any state that must persist goes to a backing service (database, cache, blob store).

**The trap:** caching session data in process memory. The next request hits a different replica and the session vanishes.

In-process caching of *immutable* or *reconstructible* data is fine — it's caching of authoritative state that breaks horizontal scaling.

---

## VII. Port binding — export services via port binding

The app is self-contained. It binds to a port and serves HTTP (or whatever protocol) directly, without needing to be injected into a host web server like Apache or Tomcat.

**The trap:** apps that only run inside a specific server's plugin architecture. They drag the host along with them everywhere.

---

## VIII. Concurrency — scale out via the process model

Scale by running more processes, not by making one process bigger. Different workload types (web, worker, scheduled) become different process types.

**The trap:** building everything into one giant process and scaling vertically. You hit the ceiling on a single machine and have no way out.

---

## IX. Disposability — fast startup, graceful shutdown

Processes start quickly (seconds, not minutes) and shut down cleanly on SIGTERM: stop accepting new work, finish what's in flight, exit.

**The trap:** long warmup times. They make autoscaling useless — the spike is over by the time the new instance is ready.

The corollary: be crash-tolerant. Anything that breaks if the process dies mid-operation will eventually break, because processes die mid-operation all the time.

---

## X. Dev/prod parity — keep environments as similar as possible

Minimize the gap along three axes: time (deploy soon after writing), personnel (same people write and deploy), and tools (same backing services in dev as in prod).

**The trap:** SQLite in dev and Postgres in prod. They behave differently in subtle ways; the differences only show up in production.

Containers and managed local versions of services (a real local Postgres via Docker, not an in-memory substitute) keep this gap small.

---

## XI. Logs — treat logs as event streams

Logs are an unbuffered stream written to stdout. The app doesn't know or care where they go — collecting, routing, and storing them is the platform's job.

**The trap:** apps that write to log files on disk. Now log rotation, retention, and aggregation are the app's problem, and they don't follow the process when it moves to a new host.

---

## XII. Admin processes — run admin tasks as one-off processes

Database migrations, data fixes, ad-hoc scripts — run them as one-off processes against the same codebase and config as the running app, not as separately deployed tooling.

**The trap:** a separate "scripts" repo that drifts out of sync with the app it operates on. The first time a script runs against an incompatible schema, you have a story to tell.

---

## What the twelve factors are really about

Stripped down, the twelve factors encode three deeper commitments:

1. **The unit of deployment is a self-contained artifact.** It carries its dependencies, makes no assumptions about the host, and reads everything that varies from the environment.
2. **Statelessness is the path to horizontal scale.** State goes to backing services; processes are interchangeable.
3. **Operations is a first-class concern of the code.** Logging, configuration, startup, shutdown, and process model are design decisions, not afterthoughts.

These ideas predate the twelve-factor formulation and outlast it — they're really just an articulation of what cloud-native means. Newer methodologies (containers, Kubernetes, serverless) inherit most of these factors implicitly; the value of the original list is making them explicit.
