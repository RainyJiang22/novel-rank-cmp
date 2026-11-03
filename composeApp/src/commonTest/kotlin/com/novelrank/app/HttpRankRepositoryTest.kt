package com.novelrank.app

import com.novelrank.app.data.*
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.test.*

class HttpRankRepositoryTest {
    private val headers = headersOf(HttpHeaders.ContentType, "application/json; charset=utf-8")

    @Test fun preservesProxyPrefixAndEncodesWholeSelection() = runTest {
        val engine = MockEngine { request ->
            assertEquals("application/json", request.headers[HttpHeaders.Accept])
            when (request.url.encodedPath) {
                "/novelrank/api/v1/catalog" -> respond(Json.encodeToString(testCatalog), headers = headers)
                "/novelrank/api/v1/rankings" -> {
                    assertEquals("fanqie", request.url.parameters["source"])
                    assertEquals("1_261", request.url.parameters["category"])
                    assertEquals("reading", request.url.parameters["board"])
                    assertEquals("true", request.url.parameters["refresh"])
                    respond(Json.encodeToString(sampleSnapshot()), headers = headers)
                }
                else -> error("Unexpected endpoint")
            }
        }
        val repository = HttpRankRepository(rankHttpClient(engine))
        try {
            assertEquals(testCatalog, repository.catalog("https://example.com/novelrank"))
            assertEquals(10, repository.ranking("https://example.com/novelrank", initialSelection, true).books.size)
        } finally { repository.close() }
    }

    @Test fun decodesAllBusinessStatusesAndNullMetadata() = runTest {
        for (status in listOf("ok", "partial", "stale", "blocked", "unavailable", "parse_error")) {
            val sample = sampleSnapshot(status = status).let { snapshot ->
                if (status == "partial") snapshot.copy(books = listOf(snapshot.books.first().copy(title = null, author = null, metadataStatus = "partial")))
                else snapshot
            }
            val body = Json.encodeToString(sample).replaceFirst("{", "{\"futureField\":true,")
            val repository = HttpRankRepository(rankHttpClient(MockEngine { respond(body, headers = headers) }))
            try { assertEquals(sample, repository.ranking("https://example.com", initialSelection, false)) }
            finally { repository.close() }
        }
    }

    @Test fun rejectsWrongIdentityRankOrderAndFakeEmptySuccess() = runTest {
        val sample = sampleSnapshot()
        val cases = listOf(sample.copy(sourceId = "jinjiang"), sample.copy(books = emptyList()), sample.copy(status = "new_unknown_status"),
            sample.copy(books = sample.books.reversed()), sample.copy(books = listOf(sample.books[0], sample.books[0])),
            sample.copy(sourceUrl = "javascript:alert(1)"))
        for (value in cases) {
            val repository = HttpRankRepository(rankHttpClient(MockEngine { respond(Json.encodeToString(value), headers = headers) }))
            try { assertFailsWith<ServiceException> { repository.ranking("https://example.com", initialSelection, false) } }
            finally { repository.close() }
        }
    }

    @Test fun validatesCatalogAndInvalidJson() = runTest {
        val badCatalog = testCatalog.copy(sources = listOf(testCatalog.sources.first().copy(
            categories = listOf(testCatalog.sources.first().categories.first().copy(boardIds = listOf("unknown"))))))
        for (body in listOf("<html>error</html>", "{\"sources\":[]}", Json.encodeToString(badCatalog))) {
            val repository = HttpRankRepository(rankHttpClient(MockEngine { respond(body, headers = headers) }))
            try { assertFailsWith<ServiceException> { repository.catalog("https://example.com") } }
            finally { repository.close() }
        }
    }

    @Test fun httpErrorsNeverBecomeSuccessfulEmptyRankingsAndRedirectsStop() = runTest {
        for (code in listOf(400, 401, 403, 422, 500, 503, 302)) {
            var requests = 0
            val repository = HttpRankRepository(rankHttpClient(MockEngine {
                requests++
                respond("private backend error", HttpStatusCode.fromValue(code), headersOf(HttpHeaders.Location, "https://other.test/"))
            }))
            try {
                val failure = assertFailsWith<ServiceException> { repository.catalog("https://example.com") }
                assertFalse(failure.message.orEmpty().contains("private backend"))
                assertEquals(1, requests)
            } finally { repository.close() }
        }
    }

    @Test fun cancellationPropagatesAndNetworkErrorsAreReadable() = runTest {
        val cancelled = HttpRankRepository(rankHttpClient(MockEngine { throw CancellationException("cancel") }))
        try { assertFailsWith<CancellationException> { cancelled.catalog("https://example.com") } }
        finally { cancelled.close() }
        val offline = HttpRankRepository(rankHttpClient(MockEngine { error("sensitive local diagnostic") }))
        try {
            val error = assertFailsWith<ServiceException> { offline.catalog("https://example.com") }
            assertEquals("无法连接服务，请检查服务地址和网络。", error.message)
        } finally { offline.close() }
    }
}
