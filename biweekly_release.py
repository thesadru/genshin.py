import git
import logging

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(name)s | %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

repo = git.Repo()

# Get the last commit message
commit_message = repo.head.commit.message
logger.info(f"Last commit message: {commit_message!r}")

# Is the last commit message a version bump?
if not isinstance(commit_message, str) or "chore(ver)" in commit_message:
    logger.info("Version bump commit found")
    exit()

# Get the current version
current_version = None
with open("pyproject.toml", "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("version = "):
            current_version = line.split('"')[1]
            break

if current_version is None:
    logger.error("Current version not found in pyproject.toml")
    exit()

logger.info(f"Current version: {current_version!r}")

# Get patch version
major, minor, patch = current_version.split(".")
patch = int(patch) + 1
new_version = f"{major}.{minor}.{patch}"  # e.g. 1.7.5
logger.info(f"New version: {new_version!r}")

# Update the version number in pyproject.toml
with open("pyproject.toml", "w") as f:
    for line in lines:
        if line.startswith("version = "):
            f.write(f'version = "{new_version}"\n')
        else:
            f.write(line)
logger.info("Updated version number in pyproject.toml")
