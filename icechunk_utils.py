"""
Helpers for opening Icechunk repositories on Source Cooperative using
temporary credentials managed by the source-coop CLI.
"""

import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import icechunk

SOURCE_COOP_CLI = "/home/jovyan/.cargo/bin/source-coop"
_DEFAULT_CREDS_CACHE = "/home/jovyan/.cache/source-coop/credentials/_default.json"


def get_source_credentials(creds_cache: str = _DEFAULT_CREDS_CACHE):
    """
    Refresh and return Source Cooperative temporary credentials.

    Calls the source-coop CLI to ensure the cached token is up to date,
    then reads the credentials from the cache file.

    Returns
    -------
    source_creds : dict
        Keys: aws_access_key_id, aws_secret_access_key, aws_session_token,
        region_name, endpoint_url.
    expiration : datetime
        Token expiration as a timezone-aware UTC datetime.
    """
    subprocess.run(
        [SOURCE_COOP_CLI, "creds"],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    with Path(creds_cache).open() as f:
        cached = json.load(f)

    expiration = datetime.fromisoformat(cached["expiration"])

    source_creds = {
        "aws_access_key_id": cached["access_key_id"],
        "aws_secret_access_key": cached["secret_access_key"],
        "aws_session_token": cached["session_token"],
        "region_name": "us-east-1",
        "endpoint_url": "https://data.source.coop",
    }

    return source_creds, expiration


def open_source_icechunk_repo(
    bucket: str,
    prefix: str,
    config=None,
    min_minutes_left: int = 15,
    create_if_missing: bool = True,
    verbose: bool = True,
    check_expiration: bool = True,
):
    """
    Open or create an Icechunk repo on Source Cooperative.

    Refreshes credentials via the source-coop CLI before opening.

    Parameters
    ----------
    bucket
        Source Cooperative bucket name (e.g. "ocean-icechunks").
    prefix
        Key prefix inside the bucket for the Icechunk repository.
    config
        Optional icechunk.RepositoryConfig (e.g. with VirtualChunkContainers).
    min_minutes_left
        If the token has fewer than this many minutes remaining and
        check_expiration=True, returns (None, None, None, time_left).
    create_if_missing
        Create the repository if it does not already exist.
    verbose
        Print status messages.
    check_expiration
        Raise a clean stop instead of a cryptic error when the token is expired.

    Returns
    -------
    repo : icechunk.Repository or None
    storage : icechunk storage object or None
    source_creds : dict or None
    time_left : timedelta
    """
    source_creds, expiration = get_source_credentials()

    now = datetime.now(timezone.utc)
    time_left = expiration - now

    if check_expiration and time_left < timedelta(minutes=0):
        print(
            f"Stopping cleanly. Source credentials expired. "
            f"Run: {SOURCE_COOP_CLI} login --duration 1d --port 8400"
        )
        return None, None, None, time_left

    storage = icechunk.s3_storage(
        bucket=bucket,
        prefix=prefix,
        region=source_creds["region_name"],
        endpoint_url=source_creds["endpoint_url"],
        force_path_style=True,
        access_key_id=source_creds["aws_access_key_id"],
        secret_access_key=source_creds["aws_secret_access_key"],
        session_token=source_creds["aws_session_token"],
    )

    if create_if_missing:
        try:
            repo = icechunk.Repository.create(storage, config)
            if verbose:
                print("Created new Icechunk repo")
        except Exception:
            repo = icechunk.Repository.open(storage, config=config)
            if verbose:
                print("Opened existing Icechunk repo")
    else:
        repo = icechunk.Repository.open(storage, config=config)
        if verbose:
            print("Opened existing Icechunk repo")

    if verbose:
        print(f"Time remaining on token: {time_left}")

    return repo, storage, source_creds, time_left


def wait_for_fresh_repo(
    bucket: str,
    prefix: str,
    config=None,
    min_minutes_left: int = 15,
    verbose: bool = True,
):
    """
    Open the Icechunk repo, prompting for a token refresh if needed.

    Loops until the token has at least min_minutes_left remaining, or the
    user chooses to stop. Useful before starting a long write loop.

    Returns
    -------
    repo, storage, source_creds, time_left
        Returns (None, None, None, time_left) if the user stops.
    """
    while True:
        repo, storage, source_creds, time_left = open_source_icechunk_repo(
            bucket=bucket,
            prefix=prefix,
            config=config,
            min_minutes_left=min_minutes_left,
            create_if_missing=True,
            check_expiration=True,
            verbose=False,
        )

        if time_left >= timedelta(minutes=min_minutes_left):
            if verbose:
                print(f"Token okay. Time remaining: {time_left}")
            return repo, storage, source_creds, time_left

        print(
            f"Source credentials expire in about {time_left}. "
            f"Refresh with: {SOURCE_COOP_CLI} login --duration 1d --port 8400"
        )

        try:
            answer = input("Enter y after refreshing the token, or n to stop: ").strip().lower()
        except KeyboardInterrupt:
            print("Input interrupted. Stopping cleanly.")
            return None, None, None, time_left

        if answer == "y":
            continue
        if answer == "n":
            print("Stopping. Resume with start_index set to the last committed file.")
            return None, None, None, time_left

        print("Please enter y or n.")
