import argparse
import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr

def main():
    parser = argparse.ArgumentParser(description="Git Push Helper")
    parser.add_argument("-m", "--message", type=str, help="Commit message for the changes.")
    parser.add_argument("--no-push", action="store_true", help="Commit changes without pushing.")
    args = parser.parse_args()

    # 1. Stage all changes
    print("Staging all changes...")
    success, _, err = run_command(["git", "add", "."])
    if not success:
        print(f"Error staging changes: {err.strip()}", file=sys.stderr)
        sys.exit(1)
        
    # Check if there are staged changes to commit
    status_result = subprocess.run(["git", "diff", "--quiet", "--cached"])
    has_changes = status_result.returncode != 0
    #working
    if has_changes:
        commit_msg = args.message
        if not commit_msg:
            print("Staged changes detected.")
            try:
                commit_msg = input("Enter commit message for your changes (or press Enter for 'update changes'): ").strip()
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(1)
            if not commit_msg:
                commit_msg = "update changes"
        
        print(f"Committing changes: '{commit_msg}'")
        success, _, err = run_command(["git", "commit", "-m", commit_msg])
        if not success:
            print(f"Error committing changes: {err.strip()}", file=sys.stderr)
            sys.exit(1)
        print("Changes committed successfully.")
    else:
        print("No staged changes to commit.")

    # 2. Push to remote
    if not args.no_push:
        print("Pushing commits to remote repository...")
        # Get current branch name
        branch_success, branch_out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        branch_name = branch_out.strip() if branch_success else "main"
        
        push_success, _, err = run_command(["git", "push", "origin", branch_name])
        if push_success:
            print("Successfully pushed all changes to remote!")
        else:
            print(f"Error pushing to remote: {err.strip()}", file=sys.stderr)
            print("Please check your internet connection, remote configuration, or git credentials.")
            sys.exit(1)
    else:
        print("Skipping push as requested (--no-push).")

if __name__ == "__main__":
    main()
