#!/usr/bin/env python3

"""Extract URLs from HTML documents."""

import argparse
import re
import sys
import urllib.parse

import bs4
import requests

_TAG_ATTRS = {
    'a': {'href'},
    'applet': {'code', 'archive', 'codebase'},
    'area': {'href'},
    'audio': {'src'},
    'base': {'href'},
    'blockquote': {'cite'},
    'body': {'background'},
    'button': {'formaction'},
    'del': {'cite'},
    'embed': {'src'},
    'form': {'action'},
    'frame': {'longdesc', 'src'},
    'head': {'profile'},
    'html': {'manifest'},
    'iframe': {'longdesc', 'src'},
    'img': {'longdesc', 'src'},
    'input': {'formaction', 'src'},
    'ins': {'cite'},
    'link': {'href'},
    'menuitem': {'icon'},
    'object': {'archive', 'codebase', 'data'},
    'q': {'cite'},
    'script': {'src'},
    'source': {'src'},
    'video': {'src'},
}
"""HTML tags and attributes that can hold URLs.

According to W3Schools, only the listed attributes of the listed tags
(keys) can hold URLs. Both HTML 4.01 and HTML 5 are included.

The data are scraped from w3schools.com on 2015-05-09.

"""

def urlgrep(pattern=None, content=None, filepath=None, url=None, base=None,
            deduplicate=True, session=None):
    """Extract URLs matching a pattern from an HTML document.

    The HTML document is either passed in full as a string (the
    `content` parameter), or is read from a local file (the `filepath`
    parameter), or is retrieved from a remote URL (the `url`
    parameter). Only one of the these three -- the first one in
    `content`, `filepath`, and `url` that is not ``None`` -- is
    used. One of the three must be specified.

    Sometimes we need a base URL to resolve relative URLs. The `url`
    argument or its redirection (if any) is automatically used as base
    when the document is retrieved from `url`. Otherwise, the `base`
    parameter, if specified and not None, is used. If none of the above
    applies, ``http://localhost`` is used as a fallback. Note that the
    HTML ``<base>`` tag within the document may change the base URL, and
    that is respected.

    The `pattern` parameter supplies a regex pattern to match parsed
    URLs. Only matching URLs are returned. If no pattern is specified,
    ``r"^(?!javascript:)"`` is used to exclude the "``javascript:``
    scheme". You may supply an empty string if you want to include
    ``javascript:``.

    Parameters
    ----------
    pattern : str, optional
        Regex pattern to match parsed URLs against. Default is
        ``r"^(?!javascript:)"``.
    content : bytes or str, optional
        An HTML document.
    filepath : str, optional
        Path to a local HTML document.
    url : str, optional
        URL pointing to an HTML document (note that the ``file`` scheme
        is not supported by ``requests``). If no scheme is supplied in
        the URL, use ``http://``.
    base : str, optional
        Base URL used for `content` for `filepath`. If no scheme is
        supplied in the URL, use ``http://`` (for a local path, use
        ``file://``).
    deduplicate : str, optional
        Deduplicate matching URLs and only keep the first occurrence of
        each unique URL. Default is ``True``.
    session : requests.Session, optional
        If not ``None``, make HTTP requests within this session. Default
        is ``None``.

    Returns
    -------
    matching_urls : list
        List of parsed absolute URLs matching the given pattern.

    Raises
    ------
    ValueError
        If content, filepath and url are all None.
    OSError
        If failed to open the specified file.
    requests.exceptions.RequestException
        If requests fail to retrieve the URL specified.

    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches

    urlscheme = re.compile(r"^\w+://")

    base = "localhost" if base is None else base
    if not urlscheme.match(base):
        base = "http://%s" % base

    if content is not None:
        pass
    elif filepath is not None:
        with open(filepath, mode='rb') as fileobj:
            content = fileobj.read()
    elif url is not None:
        if not urlscheme.match(url):
            url = "http://%s" % url
        if session is None:
            request = requests.get(url)
        else:
            request = session.get(url)
        content = request.content
        base = request.url
    else:
        raise ValueError("content, filepath and url cannot all be None")

    regex = (re.compile(pattern) if pattern is not None
             else re.compile(r"^(?!javascript:)"))

    soup = bs4.BeautifulSoup(content, "lxml")

    # base URL might be modified by the HTML <base> tag, which must
    # reside inside <head>
    if soup.head and soup.head.base and "href" in soup.head.base.attrs:
        base = soup.head.base["href"]

    matching_urls = []
    for tag in soup.descendants:
        if tag.name in _TAG_ATTRS:
            for attribute in _TAG_ATTRS[tag.name]:
                if attribute in tag.attrs:
                    parsed_url = urllib.parse.urljoin(base, tag[attribute])
                    if regex.search(parsed_url):
                        matching_urls.append(parsed_url)

    if deduplicate:
        seen = set()
        seen_add = seen.add
        matching_urls = [url for url in matching_urls
                         if not (url in seen or seen_add(url))]

    return matching_urls

def main():
    """CLI interface."""
    description = """Parse URLs from HTML documents. When invoked with
    no URLs or files, read from stdin."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-u", "--url", action="append",
                        help="""URL to an HTML document to be
                        parsed. This option can be specified multiple
                        times on the command line. "http://" is
                        automatically attached if the scheme is left
                        out.""")
    parser.add_argument("-b", "--base",
                        help="""Base URL. Only used for files or
                        stdin. "http://" is automatically attached if
                        the scheme is left out.""")
    parser.add_argument("-p", "--pattern",
                        help="""Regexp to match against.""")
    parser.add_argument("-d", "--preserve-duplicates", action="store_true",
                        help="""Do not deduplicate URLs within a document.""")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="""Print additional information to stderr.""")
    parser.add_argument("filepaths", metavar="FILE", nargs="*",
                        help="""Files to be parsed.""")
    args = parser.parse_args()
    urls = args.url if args.url is not None else []
    filepaths = args.filepaths
    base = args.base
    pattern = args.pattern
    deduplicate = not args.preserve_duplicates
    # verbose if --verbose specified and sources more than one
    verbose = len(urls) + len(filepaths) >= 2 if args.verbose else False

    returncode = 0
    if not urls and not filepaths:
        content = sys.stdin.read()
        matching_urls = urlgrep(pattern=pattern,
                                content=content,
                                base=base,
                                deduplicate=deduplicate)
        print('\n'.join(matching_urls))
        sys.stdout.flush()
    else:
        for url in urls:
            try:
                matching_urls = urlgrep(pattern=pattern,
                                        url=url,
                                        deduplicate=deduplicate)

                if verbose and matching_urls:
                    sys.stderr.write("# from '%s':\n" % url)
                    sys.stderr.flush()

                print('\n'.join(matching_urls))
                sys.stdout.flush()

            except requests.exceptions.RequestException as err:
                sys.stderr.write("error: failed to get '%s'\n" % url)
                sys.stderr.write("error: %s\n" % str(err))
                sys.stderr.flush()
                returncode = 1

        for filepath in filepaths:
            try:
                matching_urls = urlgrep(pattern=pattern,
                                        filepath=filepath,
                                        base=base,
                                        deduplicate=deduplicate)

                if verbose and matching_urls:
                    sys.stderr.write("# from '%s':\n" % filepath)
                    sys.stderr.flush()

                print('\n'.join(matching_urls))
                sys.stdout.flush()

            except OSError as err:
                sys.stderr.write("error: failed to open '%s'\n" % filepath)
                sys.stderr.write("error: %s\n" % str(err))
                sys.stderr.flush()
                returncode = 1

    return returncode
