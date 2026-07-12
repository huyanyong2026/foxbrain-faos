import hashlib
import json
import os
import tarfile
import time
import urllib.request
from pathlib import Path


REPOSITORY = "mssql/server"
TAG = "2019-latest"
REFERENCE = "mcr.microsoft.com/mssql/server:2019-latest"
BASE = "https://mcr.microsoft.com/v2/{}".format(REPOSITORY)
ROOT = Path(os.environ.get("OCI_WORK_DIR", "artifacts/mssql-2019-oci"))
OUTPUT = Path(os.environ.get("OCI_OUTPUT", "artifacts/mssql-server-2019-latest-oci.tar"))
ACCEPT = "application/vnd.docker.distribution.manifest.v2+json"


def fetch(url, accept=None):
    headers = {"Accept": accept} if accept else {}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as response:
        return response.read()


def download_blob(descriptor):
    digest = descriptor["digest"]
    algorithm, value = digest.split(":", 1)
    if algorithm != "sha256":
        raise RuntimeError("Unsupported digest {}".format(digest))
    target = ROOT / "blobs" / algorithm / value
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size == int(descriptor["size"]):
        if hashlib.sha256(target.read_bytes()).hexdigest() == value:
            print("cached", digest, target.stat().st_size, flush=True)
            return
    partial = target.with_suffix(".part")
    expected_size = int(descriptor["size"])
    attempts = 0
    while (partial.stat().st_size if partial.exists() else 0) < expected_size:
        current = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": "bytes={}-".format(current)} if current else {}
        request = urllib.request.Request(BASE + "/blobs/" + digest, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                if current and getattr(response, "status", 200) != 206:
                    partial.unlink(missing_ok=True)
                    current = 0
                mode = "ab" if current else "wb"
                with partial.open(mode) as output:
                    while output.tell() < expected_size:
                        chunk = response.read(min(1024 * 1024, expected_size - output.tell()))
                        if not chunk:
                            break
                        output.write(chunk)
                        print("download", digest, output.tell(), expected_size, flush=True)
            attempts = 0
        except (TimeoutError, OSError) as exc:
            attempts += 1
            if attempts > 100:
                raise RuntimeError("Too many download interruptions for {}".format(digest)) from exc
            print("resume", digest, current, attempts, flush=True)
            time.sleep(min(attempts, 5))
    if partial.stat().st_size != expected_size:
        raise RuntimeError("Size mismatch for {}".format(digest))
    digest_actual = hashlib.sha256(partial.read_bytes()).hexdigest()
    if digest_actual != value:
        raise RuntimeError("Digest mismatch for {}".format(digest))
    partial.replace(target)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest_bytes = fetch(BASE + "/manifests/" + TAG, ACCEPT)
    manifest = json.loads(manifest_bytes)
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    manifest_path = ROOT / "blobs" / "sha256" / manifest_digest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_bytes)
    for descriptor in [manifest["config"], *manifest["layers"]]:
        download_blob(descriptor)
    (ROOT / "oci-layout").write_text(json.dumps({"imageLayoutVersion": "1.0.0"}), encoding="utf-8")
    index = {
        "schemaVersion": 2,
        "manifests": [{
            "mediaType": manifest.get("mediaType", ACCEPT),
            "digest": "sha256:" + manifest_digest,
            "size": len(manifest_bytes),
            "annotations": {"org.opencontainers.image.ref.name": REFERENCE},
            "platform": {"architecture": "amd64", "os": "linux"},
        }],
    }
    (ROOT / "index.json").write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(OUTPUT, "w") as archive:
        archive.add(ROOT / "oci-layout", arcname="oci-layout")
        archive.add(ROOT / "index.json", arcname="index.json")
        archive.add(ROOT / "blobs", arcname="blobs")
    print("created", OUTPUT, OUTPUT.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
