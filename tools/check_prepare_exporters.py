#!/usr/bin/env python3
"""Compare two isolated preparations with a batched, runtime-only release preparation.

Uses only locally imported pinned Minecraft files. Run after compile-exporters and copy its
server/, client/ and manifest.json to exporters/. Byte differences are accepted only where
both isolated runs also differ and normalize identically (known exporter noise).
"""
import argparse
import errno
import hashlib
import json
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def link_minecraft(target, link):
    try:
        link.symlink_to(target, target_is_directory=True)
        return 'symlink'
    except OSError as e:
        # Windows can deny symlink creation without Developer Mode/admin (ERROR_PRIVILEGE_NOT_HELD).
        winerror = getattr(e, 'winerror', None)
        if os.name != 'nt' or winerror not in (1314,):
            raise
        result = subprocess.run(
            ['cmd', '/c', 'mklink', '/J', str(link), str(target)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise OSError(
                e.errno,
                f"mklink /J failed: {result.stderr.strip() or result.stdout.strip()}",
                str(link),
                winerror,
            ) from e
        # Verify junction points at the intended target directory.
        resolved = os.path.realpath(link)
        if os.path.normcase(resolved) != os.path.normcase(os.path.realpath(target)):
            unlink_minecraft(link)
            raise OSError(f"junction does not point to target: {link} -> {resolved}")
        return 'junction'


def unlink_minecraft(link):
    if not link.exists() and not link.is_symlink():
        return
    # Junctions/symlinks must be removed as links; never delete the target directory.
    if link.is_symlink():
        link.unlink()
        return
    if os.name == 'nt':
        is_junction = False
        try:
            is_junction = bool(link.stat().st_file_attributes & 0x400)
        except (AttributeError, OSError):
            is_junction = False
        if is_junction:
            os.rmdir(link)
            return
    # If it is a real directory/file, do not treat it as a link.
    if link.is_dir():
        raise OSError(f"refusing to remove real directory as minecraft link: {link}")
    link.unlink()


def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file() and p.suffix != '.log'
            and not {'classes', 'client-classes'} & set(p.relative_to(folder).parts)
            and p.name != 'horizon-resources.json'}


def normalize(path):
    value = json.loads(path.read_text())
    if path.name == 'block-behaviours.json':
        # JVM-assigned lambda class addresses are printed as opaque field values.
        def clean(node):
            if isinstance(node, str):
                return re.sub(r'\$\$Lambda/0x[0-9a-fA-F]+', '$$Lambda/<address>', node)
            if isinstance(node, list):
                return [clean(item) for item in node]
            if isinstance(node, dict):
                return {key: clean(item) for key, item in node.items()}
            return node
        value = clean(value)
    elif path.name == 'creative-inventory.json':
        for tab in value['tabs']:
            if 'tags' in tab:
                tab['tags'] = [sorted(tags) for tags in tab['tags']]
    return value


def verify(folders):
    a, b, batched = [hashes(folder) for folder in folders]
    if a.keys() != b.keys() or a.keys() != batched.keys():
        raise SystemExit('Resource file sets differ')
    known = {'render-definitions.json', 'block-behaviours.json', 'creative-inventory.json'}
    noise = [name for name in a if a[name] != b[name] or a[name] != batched[name]]
    differences = []
    for name in noise:
        if name not in known:
            differences.append(name)
        else:
            x, y, z = [normalize(folder / name) for folder in folders]
            if x != y or x != z:
                differences.append(name)
    manifests = []
    for folder, raw in zip(folders, [a, b, batched]):
        replacements = {raw[name]: f'normalized:{name}' for name in noise}
        def clean(node):
            if isinstance(node, str):
                return replacements.get(node, node)
            if isinstance(node, list):
                return [clean(item) for item in node]
            if isinstance(node, dict):
                return {key: clean(item) for key, item in node.items()}
            return node
        manifests.append(clean(json.loads((folder / 'horizon-resources.json').read_text())))
    if manifests[0] != manifests[1] or manifests[0] != manifests[2]:
        differences.append('horizon-resources.json')
    print(f'Normalized exporter noise: {noise}')
    if differences:
        raise SystemExit(f'Resources differ: {differences}')
    print(f'PASS: all {len(a)} resource files match, with only known noise normalized')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve()
    keep_failed = False
    with tempfile.TemporaryDirectory(prefix='prepare-exporters-') as temporary:
        work = args.work.resolve() if args.work else Path(temporary)
        work.mkdir(parents=True, exist_ok=True)
        # Freeze the tested executable even if a developer rebuilds concurrently.
        frozen = work / binary.name
        shutil.copy2(binary, frozen)
        binary = frozen
        results = []
        times = []
        minecraft_links = []
        try:
            for name in ['isolated-1', 'isolated-2', 'batched']:
                folder = work / name
                folder.mkdir()
                shutil.copyfile(ROOT / 'research-lock.json', folder / 'research-lock.json')
                shutil.copytree(ROOT / 'mods/horizon/src/test/java', folder / 'mods/horizon/src/test/java')
                shutil.copytree(ROOT / 'exporters', folder / 'exporters')
                (folder / '.local').mkdir()
                minecraft_link = folder / '.local/minecraft'
                link_minecraft((ROOT / '.local/minecraft').resolve(), minecraft_link)
                minecraft_links.append(minecraft_link)
                env = dict(os.environ)
                env.pop('HORIZON_PREPARE_ISOLATED', None)
                if name.startswith('isolated'):
                    env['HORIZON_PREPARE_ISOLATED'] = '1'
                else:
                    # An actual runtime-only home: no javac in bin. Java resolves its own libraries.
                    java = Path(shutil.which('java')).resolve()
                    runtime = folder / 'runtime'
                    (runtime / 'bin').mkdir(parents=True)
                    trace = folder / 'java-invocations.txt'
                    if os.name == 'nt':
                        # Windows CreateProcess resolves executable images directly; Rust
                        # horizon-prepare resolves/launches JAVA_HOME/bin/java.exe (not .cmd/.bat).
                        # Build a tiny native shim that records invocations and forwards to real java.
                        java_exe = runtime / 'bin' / 'java.exe'
                        trace_s = str(trace).replace('\\', '\\\\').replace('"', '\\"')
                        real_s = str(java).replace('\\', '\\\\').replace('"', '\\"')
                        shim_rs = runtime / 'bin' / 'java_trace_shim.rs'
                        shim_rs.write_text(
                            '#![windows_subsystem = "console"]\n'
                            'use std::fs::OpenOptions;\n'
                            'use std::io::Write;\n'
                            'use std::process::{Command, exit};\n'
                            'fn main() {\n'
                            '    let args: Vec<String> = std::env::args().skip(1).collect();\n'
                            f'    let trace = "{trace_s}";\n'
                            f'    let real = "{real_s}";\n'
                            '    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(trace) {\n'
                            '        let _ = writeln!(f, "{}", args.join(" "));\n'
                            '    } else {\n'
                            '        eprintln!("java trace shim: failed to write trace: {}", trace);\n'
                            '        exit(127);\n'
                            '    }\n'
                            '    let status = match Command::new(real).args(&args).status() {\n'
                            '        Ok(s) => s,\n'
                            '        Err(e) => {\n'
                            '            eprintln!("java trace shim: failed to exec real java: {}", e);\n'
                            '            exit(127);\n'
                            '        }\n'
                            '    };\n'
                            '    exit(status.code().unwrap_or(1));\n'
                            '}\n',
                            encoding='utf-8',
                        )
                        compile_shim = subprocess.run(
                            ['rustc', '-O', str(shim_rs), '-o', str(java_exe)],
                            capture_output=True,
                            text=True,
                        )
                        if compile_shim.returncode != 0:
                            raise RuntimeError(
                                'failed to compile Windows java trace shim: '
                                + (compile_shim.stderr.strip() or compile_shim.stdout.strip())
                            )
                        try:
                            shim_rs.unlink()
                        except OSError:
                            pass
                    else:
                        wrapper = runtime / 'bin' / java.name
                        wrapper.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> '
                                           + shlex.quote(str(trace)) + '\nexec '
                                           + shlex.quote(str(java)) + ' "$@"\n')
                        wrapper.chmod(0o755)
                    env['JAVA_HOME'] = str(runtime)
                    env['PATH'] = str(runtime / 'bin')
                started = time.monotonic()
                with (work / f'{name}.log').open('w') as log:
                    subprocess.run([str(binary), '--root', str(folder)], cwd=folder, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1200)
                if name == 'batched':
                    if not trace.is_file():
                        raise SystemExit(f'batched Java invocation trace was not created: {trace}')
                    launches = [line for line in trace.read_text(encoding='utf-8', errors='replace').splitlines() if line != '-version']
                    if len(launches) != 5:
                        raise SystemExit(f'Expected 5 exporter/data-generator JVMs, got {len(launches)}: {launches}')
                    print(f'Runtime-only preparation: {len(launches)} JVM launches', flush=True)
                text = (work / f'{name}.log').read_text()
                if 'Compiling ' in text:
                    raise SystemExit(f'{name} unexpectedly needed a compiler')
                resources = next((folder / '.local/horizon-client').iterdir())
                results.append(resources)
                times.append(round(time.monotonic() - started, 2))
                print(f'{name}: {times[-1]}s, prepared', flush=True)
            verify(results)
            print(f'Isolated {times[:2]}s, batched {times[2]}s')
        except BaseException:
            # Preserve the temporary work directory on failure for debugging evidence.
            if args.work is None:
                keep_failed = True
                print(f'Failure: preserving work directory {work}', flush=True)
            raise
        finally:
            # Remove link/junction entries explicitly so temp cleanup never follows them.
            for minecraft_link in minecraft_links:
                try:
                    unlink_minecraft(minecraft_link)
                except OSError:
                    pass
        if keep_failed and args.work is None:
            # Break out before TemporaryDirectory cleanup removes evidence.
            os._exit(1)


if __name__ == '__main__':
    main()
