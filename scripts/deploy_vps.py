"""
Deploy FreedomWalletBot to VPS via SFTP/SSH with password auth.
Usage: python scripts/deploy_vps.py
"""
import os
import paramiko
import stat
from pathlib import Path

# ── VPS Config ──────────────────────────────────────────────
VPS_HOST = "103.69.190.75"
VPS_USER = "administrator"
VPS_PASS = "2HiiyvOWXacxGz"
VPS_PORT = 22
REMOTE_PATH = "/home/administrator/FreedomWalletBot"

# ── Local project root ───────────────────────────────────────
LOCAL_ROOT = Path(__file__).parent.parent.resolve()

# ── Files/folders to EXCLUDE from upload ────────────────────
EXCLUDE_DIRS  = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache", "logs", "data"}
EXCLUDE_FILES = {".env", "google_service_account.json", "*.pyc", "*.db", "*.log"}

def should_exclude(path: Path) -> bool:
    if path.name in EXCLUDE_DIRS or path.name in EXCLUDE_FILES:
        return True
    if path.suffix in {".pyc", ".db", ".log"}:
        return True
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False

def ensure_remote_dir(sftp, remote_dir: str):
    """Recursively create remote directory."""
    parts = remote_dir.split("/")
    current = ""
    for part in parts:
        if not part:
            current = "/"
            continue
        current = f"{current}/{part}" if current != "/" else f"/{part}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)

def upload_dir(sftp, local_dir: Path, remote_dir: str, indent=0):
    """Recursively upload a directory via SFTP."""
    ensure_remote_dir(sftp, remote_dir)
    for item in sorted(local_dir.iterdir()):
        rel = item.relative_to(LOCAL_ROOT)
        if should_exclude(rel):
            print(f"{'  '*indent}  ⏭  skip: {rel}")
            continue
        remote_item = f"{remote_dir}/{item.name}"
        if item.is_dir():
            print(f"{'  '*indent}📁 {item.name}/")
            upload_dir(sftp, item, remote_item, indent + 1)
        else:
            try:
                sftp.put(str(item), remote_item)
                print(f"{'  '*indent}  ✅ {item.name}")
            except Exception as e:
                print(f"{'  '*indent}  ❌ {item.name} — {e}")

def run_ssh(ssh, cmd: str) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    return code, out, err

def main():
    print(f"\n🚀 Deploying FreedomWalletBot to {VPS_HOST}")
    print(f"   Local: {LOCAL_ROOT}")
    print(f"   Remote: {REMOTE_PATH}\n")

    # ── Connect ──────────────────────────────────────────────
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("📡 Connecting to VPS...")
    try:
        ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("   ✅ SSH connected!\n")
    except Exception as e:
        print(f"   ❌ SSH connection failed: {e}")
        return

    sftp = ssh.open_sftp()

    # ── Stop bot on VPS ──────────────────────────────────────
    print("⏸  Stopping bot on VPS...")
    code, out, err = run_ssh(ssh, "pkill -f 'python.*main.py' 2>/dev/null; sleep 2; echo done")
    print(f"   → {out or 'no process killed'}\n")

    # ── Backup remote .env and db ────────────────────────────
    print("💾 Backing up .env and database on VPS...")
    run_ssh(ssh, f"cp {REMOTE_PATH}/.env {REMOTE_PATH}/.env.bak 2>/dev/null || true")
    run_ssh(ssh, f"cp {REMOTE_PATH}/data/bot.db {REMOTE_PATH}/data/bot.db.bak 2>/dev/null || true")
    print("   ✅ Backup done\n")

    # ── Ensure remote base dir ───────────────────────────────
    ensure_remote_dir(sftp, REMOTE_PATH)

    # ── Upload files ─────────────────────────────────────────
    print(f"📤 Uploading files to {REMOTE_PATH}...")
    upload_dir(sftp, LOCAL_ROOT, REMOTE_PATH)

    sftp.close()
    print("\n✅ File upload complete!\n")

    # ── Install / update dependencies ────────────────────────
    print("📦 Installing dependencies on VPS...")
    code, out, err = run_ssh(ssh, f"cd {REMOTE_PATH} && pip install -r requirements.txt -q 2>&1 | tail -5")
    print(f"   {out}")
    if err:
        print(f"   ⚠️  {err}\n")

    # ── Check if .env exists on VPS ──────────────────────────
    code, out, _ = run_ssh(ssh, f"test -f {REMOTE_PATH}/.env && echo EXISTS || echo MISSING")
    if out == "MISSING":
        print("⚠️  WARNING: .env file is MISSING on VPS!")
        print(f"   Copy your local .env manually:")
        print(f"   scp .env {VPS_USER}@{VPS_HOST}:{REMOTE_PATH}/.env\n")
    else:
        print("   ✅ .env exists on VPS\n")

    # ── Start bot on VPS ─────────────────────────────────────
    print("▶️  Starting bot on VPS...")
    run_ssh(ssh, f"cd {REMOTE_PATH} && nohup python main.py > logs/bot_stdout.log 2>&1 &")
    import time; time.sleep(3)

    code, out, err = run_ssh(ssh, "pgrep -a python | grep main.py")
    if out:
        print(f"   ✅ Bot is running: {out}")
    else:
        print("   ❌ Bot did not start! Check logs:")
        code, out, _ = run_ssh(ssh, f"tail -20 {REMOTE_PATH}/logs/bot_stdout.log 2>/dev/null || tail -20 {REMOTE_PATH}/data/logs/bot.log 2>/dev/null")
        print(out)

    ssh.close()
    print("\n🎉 Deployment complete!\n")
    print(f"   Monitor logs: ssh {VPS_USER}@{VPS_HOST} 'tail -f {REMOTE_PATH}/logs/bot_stdout.log'")

if __name__ == "__main__":
    main()
