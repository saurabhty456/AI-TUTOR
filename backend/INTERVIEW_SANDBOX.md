# Interview SQL sandbox

SQL execution is disabled until `INTERVIEW_SANDBOX_DATABASE_URL` points to a dedicated PostgreSQL sandbox database. Never point it at `DATABASE_URL`, the CodeTutor application database, or another database containing user data. The API rejects a matching host/database/role, but deployment isolation is still required.

Use a dedicated, non-superuser login and a database that contains no application data or extensions:

```sql
CREATE ROLE codetutor_sandbox LOGIN PASSWORD '<unique-long-password>'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
CREATE DATABASE codetutor_interview_sandbox OWNER codetutor_sandbox;
REVOKE ALL ON DATABASE codetutor_interview_sandbox FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE codetutor_interview_sandbox TO codetutor_sandbox;
```

Set `INTERVIEW_SANDBOX_DATABASE_URL` in the backend environment using that login. Keep this variable server-side and use a network policy that permits connections only from the backend. For stronger isolation, run the sandbox on a separate PostgreSQL instance/container with outbound network access disabled.

For each execution the API opens a non-pooled connection, creates temporary fixture tables from server-owned definitions, commits the fixtures, and runs one `SELECT`/`WITH` statement in a read-only transaction with a 2.5 second statement timeout and 500 ms lock timeout. The connection is physically closed after the run, dropping its temporary tables. Writes are rejected by PostgreSQL; DSA answers are never executed.
