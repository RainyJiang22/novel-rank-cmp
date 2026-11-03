package com.novelrank.app

import com.novelrank.app.data.isWebUrl
import com.novelrank.app.data.normalizeServiceAddress
import kotlin.test.*

class ServiceAddressTest {
    @Test fun acceptsCloudPrefixAndLocalDebugAddress() {
        assertEquals("https://47.251.189.239/novelrank", normalizeServiceAddress("  https://47.251.189.239/novelrank/  ", false))
        assertEquals("http://10.0.2.2:8000", normalizeServiceAddress("http://10.0.2.2:8000/", true))
        assertEquals("https://example.com/prefix", normalizeServiceAddress("https://example.com/prefix/", true))
        assertEquals("http://[::1]:8000", normalizeServiceAddress("http://[::1]:8000/", true))
    }
    @Test fun rejectsCredentialsFragmentsQueriesAndInvalidHosts() {
        listOf("", "example.com", "ftp://example.com", "http://", "http://a:99999", "http://a:0",
            "https://user:pass@example.com", "https://example.com?token=secret", "https://example.com#part",
            "https://example.com/a b", "https://example.com/../other", "https://example.com/%2e./other").forEach { value ->
            assertFailsWith<IllegalArgumentException>(value) { normalizeServiceAddress(value, true) }
        }
    }
    @Test fun releaseRejectsStoredHttpAndExternalLinksOnlyAllowWeb() {
        assertFailsWith<IllegalArgumentException> { normalizeServiceAddress("http://127.0.0.1:8000", false) }
        assertTrue(isWebUrl("https://www.jjwxc.net/onebook.php?novelid=1"))
        listOf("javascript:alert(1)", "file:///etc/passwd", "intent://test", "http://", "http://a:0", "https://user:pass@example.com").forEach {
            assertFalse(isWebUrl(it))
        }
    }
}
