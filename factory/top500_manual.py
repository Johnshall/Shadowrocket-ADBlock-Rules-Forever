# -*- coding: utf-8 -*-

'''
Fetch a fresh global top500 domain list, then (optionally) probe which sites
need proxy vs direct when run from a mainland-China network.

Domain list sources (tried in order):
1. Moz Top 500 CSV  (same format historically used by this project)
   https://moz.com/top-500/download?table=top500Domains
2. Tranco daily top-1m (free, research-oriented Alexa successor)
   https://tranco-list.eu/top-1m.csv.zip

The connectivity scan below should be run in a mainland network environment.
'''

from __future__ import print_function

import csv
import io
import os
import sys
import time
import zipfile
import threading
import tempfile

try:
    from urllib.request import Request, urlopen
except ImportError:  # pragma: no cover - py2
    from urllib2 import Request, urlopen

RESULTANT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultant')
MANUAL_LIST = os.path.join(RESULTANT_DIR, 'top500_manual.list')
MOZ_CSV = os.path.join(RESULTANT_DIR, 'top500Domains.csv')

MOZ_URL = 'https://moz.com/top-500/download?table=top500Domains'
TRANCO_ZIP_URL = 'https://tranco-list.eu/top-1m.csv.zip'

REQUESTS_HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.2',
    'Connection': 'keep-alive',
}


def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def _http_get(url, timeout=60):
    req = Request(url, headers={
        'User-Agent': REQUESTS_HEADER['User-Agent'],
        'Accept': '*/*',
    })
    resp = urlopen(req, timeout=timeout)
    try:
        return resp.read()
    finally:
        try:
            resp.close()
        except Exception:
            pass


def fetch_moz_top500():
    """Return list of domains from Moz Top 500 free CSV. Raises on failure."""
    print('Trying Moz Top 500 ...')
    raw = _http_get(MOZ_URL, timeout=60)
    text = raw.decode('utf-8', errors='replace')
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise RuntimeError('Moz CSV empty')
    # Expect header: Rank, Root Domain, ...
    start = 1 if rows[0] and rows[0][0].strip().lower() in ('rank', '"rank"') else 0
    domains = []
    for row in rows[start:]:
        if len(row) < 2:
            continue
        dom = row[1].strip().strip('"')
        if dom:
            domains.append(dom)
    if len(domains) < 100:
        raise RuntimeError('Moz returned too few domains: %d' % len(domains))
    # Persist CSV for reference (same path as historical workflow)
    with open(MOZ_CSV, 'wb') as f:
        f.write(raw)
    print('Moz OK: %d domains' % len(domains))
    return domains, 'Moz Top 500 (%s)' % MOZ_URL


def fetch_tranco_top500():
    """Return first 500 domains from Tranco daily top-1m zip."""
    print('Trying Tranco top-1m ...')
    raw = _http_get(TRANCO_ZIP_URL, timeout=120)
    tmp = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
    try:
        tmp.write(raw)
        tmp.close()
        with zipfile.ZipFile(tmp.name, 'r') as zf:
            names = zf.namelist()
            if not names:
                raise RuntimeError('Tranco zip empty')
            with zf.open(names[0]) as fh:
                data = fh.read().decode('utf-8', errors='replace')
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

    domains = []
    for line in data.splitlines():
        line = line.strip()
        if not line or ',' not in line:
            continue
        _rank, dom = line.split(',', 1)
        dom = dom.strip().lower()
        if not dom or '.' not in dom:
            continue
        domains.append(dom)
        if len(domains) >= 500:
            break
    if len(domains) < 100:
        raise RuntimeError('Tranco returned too few domains: %d' % len(domains))
    print('Tranco OK: %d domains' % len(domains))
    return domains, 'Tranco daily top-1m first 500 (%s)' % TRANCO_ZIP_URL


def write_manual_list(domains, source_note):
    if not os.path.isdir(RESULTANT_DIR):
        os.makedirs(RESULTANT_DIR)
    with open(MANUAL_LIST, 'w', encoding='utf-8') as f:
        f.write('# top500 proxy list update time: %s\n' % _now())
        f.write('# source: %s\n' % source_note)
        for d in domains:
            f.write(d + '\n')
    print('Wrote %s (%d domains)' % (MANUAL_LIST, len(domains)))


def fetch_top500_list():
    """Fetch top500 domains; Moz first, Tranco fallback."""
    errors = []
    for fetcher in (fetch_moz_top500, fetch_tranco_top500):
        try:
            domains, note = fetcher()
            write_manual_list(domains, note)
            return domains
        except Exception as e:
            msg = '%s failed: %s' % (fetcher.__name__, e)
            print(msg, file=sys.stderr)
            errors.append(msg)
    raise RuntimeError('All top500 sources failed:\n  - ' + '\n  - '.join(errors))


def read_manual_list():
    domains = []
    with open(MANUAL_LIST, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            domains.append(line)
    return domains


# ---- connectivity probe (run from mainland network) ----

domains_proxy = []
domains_direct = []
_domains_lock = threading.Lock()
scaner_thread_num = 0


class DomainScaner(threading.Thread):
    def __init__(self, queue, session_get):
        threading.Thread.__init__(self)
        self.queue = queue
        self.session_get = session_get

    def run(self):
        global scaner_thread_num
        while True:
            with _domains_lock:
                if not self.queue:
                    break
                domain = self.queue.pop(0)

            is_proxy = False
            try:
                self.session_get('http://www.' + domain, timeout=10, headers=REQUESTS_HEADER)
            except BaseException:
                try:
                    self.session_get('http://' + domain, timeout=10, headers=REQUESTS_HEADER)
                except BaseException:
                    is_proxy = True

            if is_proxy:
                domains_proxy.append(domain)
            else:
                domains_direct.append(domain)

            with _domains_lock:
                remain = len(self.queue)
            print('[Domains Remain: %d]\tProxy %s: %s' % (remain, is_proxy, domain))

        scaner_thread_num -= 1


def probe_direct_proxy(domains, workers=10):
    """Classify domains into direct/proxy by HTTP reachability."""
    global scaner_thread_num, domains_proxy, domains_direct
    try:
        import requests  # only needed for mainland probe
    except ImportError:
        raise SystemExit(
            'python package "requests" is required for connectivity probe. '
            'Install it, or set TOP500_SKIP_PROBE=1 to only refresh the ranking list.'
        )
    domains_proxy = []
    domains_direct = []
    queue = list(domains)

    print('top500 probe starting with %d domains, %d workers...\n' % (len(queue), workers))
    scaner_thread_num = 0
    for _ in range(workers):
        DomainScaner(queue, requests.get).start()
        scaner_thread_num += 1

    while scaner_thread_num:
        time.sleep(0.5)

    now_time = _now()
    file_proxy = open(os.path.join(RESULTANT_DIR, 'top500_proxy.list'), 'w', encoding='utf-8')
    file_direct = open(os.path.join(RESULTANT_DIR, 'top500_direct.list'), 'w', encoding='utf-8')
    try:
        file_proxy.write('# top500 proxy list update time: ' + now_time + '\n')
        file_direct.write('# top500 direct list update time: ' + now_time + '\n')

        d_direct = sorted(set(domains_direct))
        d_proxy = sorted(set(domains_proxy))
        for domain in d_direct:
            file_direct.write(domain + '\n')
        for domain in d_proxy:
            file_proxy.write(domain + '\n')
    finally:
        file_proxy.close()
        file_direct.close()

    print('{:-^30}'.format('Done!'))
    print('direct=%d proxy=%d' % (len(d_direct), len(d_proxy)))


def main():
    # Always refresh the ranking list when possible.
    skip_fetch = os.environ.get('TOP500_SKIP_FETCH', '').strip() in ('1', 'true', 'yes')
    skip_probe = os.environ.get('TOP500_SKIP_PROBE', '').strip() in ('1', 'true', 'yes')

    if skip_fetch and os.path.isfile(MANUAL_LIST):
        print('TOP500_SKIP_FETCH set; using existing %s' % MANUAL_LIST)
        domains = read_manual_list()
    else:
        domains = fetch_top500_list()

    if skip_probe:
        print('TOP500_SKIP_PROBE set; skip connectivity classification.')
        return

    print('Get top500 list successfully (%d domains)...\n' % len(domains))
    probe_direct_proxy(domains)


if __name__ == '__main__':
    main()
