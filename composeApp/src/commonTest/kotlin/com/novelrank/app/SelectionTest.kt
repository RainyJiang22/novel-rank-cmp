package com.novelrank.app

import com.novelrank.app.model.Selection
import com.novelrank.app.presentation.RankUiState
import com.novelrank.app.presentation.chooseSelection
import kotlin.test.*

class SelectionTest {
    @Test fun usesPreferredSelectionThenValidFallbacks() {
        assertEquals(initialSelection, chooseSelection(testCatalog))
        assertEquals(Selection("qimao", "203", "category-click"), chooseSelection(testCatalog, Selection("qimao", "203", "reading")))
        assertEquals(initialSelection, chooseSelection(testCatalog, Selection("removed", "removed", "removed")))
        val singleSource = testCatalog.copy(sources = listOf(testCatalog.sources.last()))
        assertEquals("qimao", chooseSelection(singleSource).sourceId)
    }
    @Test fun searchFiltersOnlyCurrentBooksAndKeepsRanks() {
        val state = RankUiState("https://example.com", snapshot = sampleSnapshot(), query = "  ALICE ")
        assertEquals(listOf(7), state.visibleBooks.map { it.rank })
        assertEquals(10, state.copy(query = " ").visibleBooks.size)
        assertTrue(state.copy(query = "没有的作品").visibleBooks.isEmpty())
        val missing = sampleSnapshot().copy(books = listOf(sampleSnapshot().books.first().copy(title = null, author = null)))
        assertTrue(state.copy(snapshot = missing, query = "作者").visibleBooks.isEmpty())
    }
}
