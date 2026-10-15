# Initial Owner Bootstrap

Use this only for the very first account in a new Narrativ Forge database. The script uses the application's existing PBKDF2 password hasher and creates the user plus their owner membership in one database transaction.

## Safety checks

- The script refuses to run if **any** user already exists.
- It requires an existing organization; specify the organization explicitly if there is more than one.
- The password is requested with terminal echo disabled, must be at least 12 characters, and is never printed.
- The script does not reset passwords or modify existing accounts.
- Never paste `DATABASE_URL`, database passwords, or the new owner password into chat, GitHub issues, or source files.

## Run on your own computer

1. Clone or pull the latest repository, then open PowerShell in `web-platform/backend`.
2. Install the backend dependencies in a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
3. Set `DATABASE_URL` in your local shell to the connection string for the intended Supabase project. Get it from the trusted provider dashboard; do not use a connection string for a different project. Do not commit it or share it in chat.
4. Run the bootstrap script:
   ```powershell
   python -m scripts.bootstrap_owner --organization-slug legacy-workspace
   ```
   If the intended organization has a different slug, use its actual slug or pass `--organization-id <id>`.
5. Enter the Owner email and a new strong password when prompted. The password does not appear on screen.
6. After the script reports success, open the deployed Narrativ Forge frontend and test login. Confirm that the account has the Owner role.

If the script refuses because a user already exists, stop and use the normal owner-controlled invitation/recovery process instead. Do not delete users or disable security checks to force bootstrap.

## Important deployment note

The script writes directly to the database only when run manually from your own machine. It is not part of the Render startup command and will not run during deployment. The backend and frontend Render services do not need to be redeployed merely to create the initial database account.
