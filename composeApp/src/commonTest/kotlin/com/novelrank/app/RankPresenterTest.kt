package com.novelrank.app

import com.novelrank.app.data.*
import com.novelrank.app.presentation.RankPresenter
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

@OptIn(ExperimentalCoroutinesApi::class)
class RankPresenterTest {
    private fun environment(store: MemorySettings = MemorySettings()) = ClientEnvironment(store, "https://example.com/novelrank", true)

    @Test fun startupSelectionRepairSearchAndRefresh() = runTest {
        val repository = FakeRepository()
        val presenter = RankPresenter(repository, environment(), this)
        try {
            presenter.start(); presenter.start(); advanceUntilIdle()
            assertEquals(1, repository.catalogCalls.size)
            assertEquals(initialSelection, presenter.state.value.selection)
            presenter.search("alice")
            assertEquals(listOf(7), presenter.state.value.visibleBooks.map { it.rank })
            presenter.selectCategory("0_748"); advanceUntilIdle()
            assertEquals("new", presenter.state.value.selection?.boardId)
            assertEquals("", presenter.state.value.query)
            presenter.selectBoard("reading")
            assertEquals("new", presenter.state.value.selection?.boardId)
            presenter.selectSource("jinjiang"); advanceUntilIdle()
            presenter.selectCategory("modern-romance"); advanceUntilIdle()
            assertEquals("gold", presenter.state.value.selection?.boardId)
            presenter.refresh(); advanceUntilIdle()
            assertTrue(repository.rankingCalls.last().third)
        } finally { presenter.close() }
        assertTrue(repository.closed)
    }

    @Test fun lateRankingCannotOverwriteANewSelectionEvenIfCancellationIsIgnored() = runTest {
        val pending = CompletableDeferred<Unit>()
        val repository = FakeRepository().apply {
            onRanking = { _, selection, _ ->
                if (selection == initialSelection) withContext(NonCancellable) { pending.await() }
                sampleSnapshot(selection)
            }
        }
        val presenter = RankPresenter(repository, environment(), this)
        try {
            presenter.start(); runCurrent()
            assertTrue(presenter.state.value.rankingLoading)
            presenter.selectSource("jinjiang"); runCurrent()
            assertEquals("jinjiang", presenter.state.value.snapshot?.sourceId)
            pending.complete(Unit); advanceUntilIdle()
            assertEquals("jinjiang", presenter.state.value.snapshot?.sourceId)
        } finally { pending.complete(Unit); presenter.close() }
    }

    @Test fun addressChangeInvalidatesLateCatalogAndPersistsAcrossPresenterRecreation() = runTest {
        val pending = CompletableDeferred<Unit>()
        val store = MemorySettings("https://old.test")
        val repository = FakeRepository().apply {
            onCatalog = { base ->
                if (base == "https://old.test") withContext(NonCancellable) { pending.await() }
                testCatalog
            }
        }
        val presenter = RankPresenter(repository, environment(store), this)
        try {
            presenter.start(); runCurrent()
            assertTrue(presenter.saveAddress("https://new.test/prefix/")); runCurrent()
            pending.complete(Unit); advanceUntilIdle()
            assertEquals("https://new.test/prefix", presenter.state.value.baseUrl)
            assertEquals(listOf("https://new.test/prefix"), repository.rankingCalls.map { it.first })
        } finally { pending.complete(Unit); presenter.close() }
        val next = RankPresenter(FakeRepository(), environment(store), this)
        assertEquals("https://new.test/prefix", next.state.value.baseUrl)
        next.close()
    }

    @Test fun failedRefreshPreservesLastDataAndShowsSeparateError() = runTest {
        val repository = FakeRepository()
        val presenter = RankPresenter(repository, environment(), this)
        try {
            presenter.start(); advanceUntilIdle()
            val old = presenter.state.value.snapshot
            repository.onRanking = { _, _, _ -> throw ServiceException("服务连接失败") }
            presenter.refresh(); advanceUntilIdle()
            assertEquals(old, presenter.state.value.snapshot)
            assertEquals("服务连接失败", presenter.state.value.rankingError)
            assertFalse(presenter.state.value.rankingLoading)
        } finally { presenter.close() }
    }

    @Test fun settingsValidationAndStorageFailureKeepExistingConnection() = runTest {
        val store = MemorySettings()
        val repository = FakeRepository()
        val presenter = RankPresenter(repository, environment(store), this)
        try {
            presenter.start(); advanceUntilIdle()
            assertFalse(presenter.saveAddress("not a url"))
            assertNotNull(presenter.state.value.settingsError)
            store.failSave = true
            assertFalse(presenter.saveAddress("https://another.test"))
            assertEquals("https://example.com/novelrank", presenter.state.value.baseUrl)
            assertEquals(1, repository.catalogCalls.size)
        } finally { presenter.close() }
    }

    @Test fun catalogFailureCanRetryAndUnsupportedResponseIdentityIsRejected() = runTest {
        val repository = FakeRepository().apply { onCatalog = { throw ServiceException("无法连接") } }
        val presenter = RankPresenter(repository, environment(), this)
        try {
            presenter.start(); advanceUntilIdle()
            assertEquals("无法连接", presenter.state.value.catalogError)
            assertNull(presenter.state.value.snapshot)
            repository.onCatalog = { testCatalog }
            repository.onRanking = { _, _, _ -> sampleSnapshot().copy(categoryId = "wrong") }
            presenter.reloadCatalog(); advanceUntilIdle()
            assertNotNull(presenter.state.value.rankingError)
            assertNull(presenter.state.value.snapshot)
        } finally { presenter.close() }
    }

    @Test fun releaseDoesNotReuseDebugHttpAndClosingCancelsRequests() = runTest {
        val repository = FakeRepository()
        val presenter = RankPresenter(repository, ClientEnvironment(MemorySettings("http://localhost:8000"), CLOUD_SERVICE_ADDRESS, false), this)
        presenter.start(); advanceUntilIdle()
        assertTrue(repository.catalogCalls.isEmpty())
        assertNotNull(presenter.state.value.catalogError)
        presenter.close()
        var cancelled = false
        val delayed = FakeRepository().apply { onCatalog = { try { awaitCancellation() } finally { cancelled = true } } }
        val active = RankPresenter(delayed, environment(), this)
        active.start(); runCurrent(); active.close(); runCurrent()
        assertTrue(cancelled)
        assertTrue(delayed.closed)
    }
}
