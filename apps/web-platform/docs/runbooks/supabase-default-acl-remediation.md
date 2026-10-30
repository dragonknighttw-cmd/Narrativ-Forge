# Supabase production ACL remediation runbook

Project: Narrativ-Forge (`xrhlefglqwquhvpoevsg`)

## Current verified state (2026-10-30)

Applied through the Supabase migration runner:
- Revoke direct privileges on all existing `public` tables, sequences, and functions from `anon` and `authenticated`.
- Revoke postgres-owned default privileges for future `public` tables, sequences, and function EXECUTE from those client roles.

Post-migration verification:
- `information_schema.role_table_grants`: 0 grants to `anon`/`authenticated` in `public`.
- `information_schema.role_routine_grants`: 0 grants to `anon`/`authenticated` in `public`.
- postgres-owned `pg_default_acl` entries no longer include those client roles.
- Supabase-owned defaults still include those client roles for object types TABLE (`r`), SEQUENCE (`S`), and FUNCTION (`f`).

The active SQL session is `postgres`, and `pg_has_role(current_user, 'supabase_admin', 'MEMBER')` is false. Do not attempt to bypass role ownership, modify protected catalogs, or create SECURITY DEFINER workarounds.

## Required owner-authorized remediation

Run the following only through a Supabase-supported administrative path that has authority to alter defaults for role `supabase_admin` (or after Supabase Support grants/provides the supported procedure):

```sql
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL ON TABLES FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE ALL ON SEQUENCES FROM anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM anon, authenticated;
```

Do not run as the ordinary `postgres` session unless it is a member of `supabase_admin`; PostgreSQL will reject the operation.

## Verification SQL

```sql
SELECT d.defaclrole::regrole AS creator,
       d.defaclnamespace::regnamespace AS schema,
       d.defaclobjtype AS object_type,
       d.defaclacl
FROM pg_default_acl AS d
WHERE d.defaclnamespace = 'public'::regnamespace
ORDER BY 1, 3;
```

For the `supabase_admin` rows, confirm `anon` and `authenticated` are absent from:
- `r` (tables)
- `S` (sequences)
- `f` (functions)

Then rerun:
```sql
SELECT
  (SELECT count(*) FROM information_schema.role_table_grants
   WHERE grantee IN ('anon','authenticated') AND table_schema='public') AS client_table_grants,
  (SELECT count(*) FROM information_schema.role_routine_grants
   WHERE grantee IN ('anon','authenticated') AND specific_schema='public') AS client_function_grants;
```

Expected counts for direct grants remain zero. Test backend API access and authentication flows after the change.

## RLS advisor note

As of the audit, Supabase Advisor reports 43 public tables with RLS enabled and no policies. With no client table grants, these tables are not made accessible by adding broad policies. Review each table's intended access model individually before adding any policy. Do not create blanket `USING (true)` policies.

## Explicitly out of scope

Leaked Password Protection remains excluded per the project's documented Free-plan constraint.