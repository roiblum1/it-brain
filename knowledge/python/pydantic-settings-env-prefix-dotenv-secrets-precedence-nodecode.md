---
title: pydantic-settings — BaseSettings with env_prefix INVENTORY_, .env file, secrets_dir, nested __ delimiter, list env vars JSON-decoded (SettingsError) unless NoDecode, precedence init > env > .env > secrets > default, SecretStr
type: knowledge
area: python
tags: [pydantic-settings, basesettings, settingsconfigdict, env-prefix, dotenv, secrets-dir, nodecode, settingserror, secretstr, server-scan, configuration]
applies_to: [pydantic-2, pydantic-settings-2]
confidence: observed
last_verified: 2026-11-02
owners: [ocp]
source: pydantic/pydantic-settings docs/index.md (d90133c), team-redbull/server-scan:backend/app/config/settings.py (08d284c); reproduced with pydantic-settings 2.15.0
---

# pydantic-settings: how configuration gets loaded

server-scan loads all of its configuration this way (`team-redbull/server-scan:backend/app/config/settings.py`);
the variable list is `knowledge/server-scan/server-scan-configuration-env-vars-reference.md`. The behaviour below was
reproduced with **pydantic-settings 2.15.0** (server-scan's pin).

## server-scan's setup

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INVENTORY_",     # field mongo_db  ← env INVENTORY_MONGO_DB
        env_file=".env",              # optional file, read if present
        env_file_encoding="utf-8",
        extra="ignore",              # unrelated keys in .env don't break start-up
    )
    port: int = 8080
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:5173"])
    ome_password: SecretStr = SecretStr("")      # every credential is SecretStr
```

Settings are built once (`lru_cache`) and injected through FastAPI dependencies, never read with `os.environ`
elsewhere — so tests override them with `dependency_overrides`.

## Precedence (highest first)

1. CLI arguments (only if `cli_parse_args` is on)
2. arguments passed to `Settings(...)`
3. environment variables
4. the dotenv file
5. the secrets directory (one file per field, file name = variable name)
6. field defaults

Reproduced: env `INVENTORY_PORT=7000` beat `.env`'s `INVENTORY_PORT=9000`; with the env var removed, the `.env`
value won; `Settings(port=1)` beat both. On Kubernetes this means: **an env var from the Deployment always beats a
baked-in `.env`** — check the pod's env first when a setting "won't change".

## Names

- Matching is **case-insensitive** by default: `inventory_mongo_db` set in the environment was picked up.
  `case_sensitive=True` changes that (not on Windows env vars).
- Nested models: with `env_nested_delimiter="__"`, `INVENTORY_OME__TIMEOUT=30` sets `ome.timeout` (reproduced; server-scan
  does not use nesting at `08d284c`).
- Secrets dir: `secrets_dir="/run/secrets"` reads e.g. `/run/secrets/inventory_api_token` into field `api_token`
  (reproduced; the file name includes the prefix). Mounting a Kubernetes Secret as files there keeps values out
  of `env` / `oc describe`.

## Lists and dicts from env vars — the `SettingsError` trap

Complex fields (`list`, `dict`, nested models) are **JSON-decoded** from the env var:

| Field | Env value | Result |
|---|---|---|
| `origins: list[str]` | `'["a","b"]'` | `['a', 'b']` |
| `origins: list[str]` | `a,b` | `SettingsError: error parsing value for field "origins" from source "EnvSettingsSource"` — start-up fails |
| `hosts: Annotated[list[str], NoDecode]` | `a,b` | no JSON decoding: the raw string reaches validation → `Input should be a valid list [type=list_type]` **unless** a `mode="before"` validator splits it |

server-scan does the second correctly: `NoDecode` + a `before` validator `_split_csv` (`"a,b"` → `["a", "b"]`) so
operators can write comma-separated values (`knowledge/python/pydantic-validators-field-model-before-after-wrap.md`).

## Secrets

- Declare every credential as `SecretStr`: it prints and serializes as `**********`
  (`knowledge/python/pydantic-serialization-model-dump-json-mode-alias-secretstr.md`).
- Unwrap with `.get_secret_value()` only where the value is used; never log `settings.model_dump()` with
  `SecretStr` unwrapped, never write an example `.env` with real values into the brain (`<REDACTED>`).
- A `SecretStr` default of `SecretStr("")` means "not configured" — validate that production has it set (server-scan
  does this in `model_validator(mode="after")` checks).

## Related

Temporal workers must not read settings inside workflow code (non-deterministic):
`knowledge/temporal/temporal-python-sdk-rules-that-cost-us-time.md`.

## History

- 2026-11-02: created
