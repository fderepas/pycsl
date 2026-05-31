"""PyCSL mock for Python's urllib.request module."""
_ = 0  # anchor

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

#@ \trusted
#@ ensures \result >= 0
def urlopen(url, data=None, timeout=None, context=None):
    """Mock: opens URL — opaque response object."""
    return 0

#@ \trusted
#@ ensures \result == 0
def install_opener(opener):
    """Mock: installs opener — side-effect only."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def build_opener(*handlers):
    """Mock: builds opener — opaque OpenerDirector."""
    return 0

#@ \trusted
def pathname2url(path, add_scheme=False):
    """Mock: converts pathname to URL — string."""
    return ""

#@ \trusted
def url2pathname(url, require_scheme=False, resolve_host=False):
    """Mock: converts URL to pathname — string."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def getproxies():
    """Mock: returns proxy settings — opaque dict."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlretrieve(url, filename=None, reporthook=None, data=None):
    """Mock: retrieves URL to file — opaque (filename, headers) tuple."""
    return 0

#@ \trusted
#@ ensures \result == 0
def urlcleanup():
    """Mock: cleans up temporary files — side-effect only."""
    return 0

# ---------------------------------------------------------------------------
# Classes (modelled as constructor functions returning opaque ints)
# ---------------------------------------------------------------------------

#@ \trusted
#@ ensures \result >= 0
def Request(url, data=None, headers=None, origin_req_host=None,
            unverifiable=False, method=None):
    """Mock: Request object — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def OpenerDirector():
    """Mock: OpenerDirector — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def BaseHandler():
    """Mock: BaseHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPDefaultErrorHandler():
    """Mock: HTTPDefaultErrorHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPRedirectHandler():
    """Mock: HTTPRedirectHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPCookieProcessor(cookiejar=None):
    """Mock: HTTPCookieProcessor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ProxyHandler(proxies=None):
    """Mock: ProxyHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPPasswordMgr():
    """Mock: HTTPPasswordMgr — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPPasswordMgrWithDefaultRealm():
    """Mock: HTTPPasswordMgrWithDefaultRealm — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPPasswordMgrWithPriorAuth():
    """Mock: HTTPPasswordMgrWithPriorAuth — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def AbstractBasicAuthHandler(password_mgr=None):
    """Mock: AbstractBasicAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPBasicAuthHandler(password_mgr=None):
    """Mock: HTTPBasicAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ProxyBasicAuthHandler(password_mgr=None):
    """Mock: ProxyBasicAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def AbstractDigestAuthHandler(password_mgr=None):
    """Mock: AbstractDigestAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPDigestAuthHandler(password_mgr=None):
    """Mock: HTTPDigestAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ProxyDigestAuthHandler(password_mgr=None):
    """Mock: ProxyDigestAuthHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPHandler():
    """Mock: HTTPHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPSHandler(debuglevel=0, context=None, check_hostname=None):
    """Mock: HTTPSHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FileHandler():
    """Mock: FileHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DataHandler():
    """Mock: DataHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FTPHandler():
    """Mock: FTPHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CacheFTPHandler():
    """Mock: CacheFTPHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def UnknownHandler():
    """Mock: UnknownHandler — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def HTTPErrorProcessor():
    """Mock: HTTPErrorProcessor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def addinfourl():
    """Mock: addinfourl — opaque."""
    return 0
