package com.novelrank.app.presentation

import com.novelrank.app.model.Book
import com.novelrank.app.model.Catalog
import com.novelrank.app.model.RankingSnapshot
import com.novelrank.app.model.Selection

fun chooseSelection(catalog: Catalog, desired: Selection? = null): Selection {
    val source = catalog.sources.firstOrNull { it.id == desired?.sourceId }
        ?: catalog.sources.firstOrNull { it.id == "fanqie" }
        ?: catalog.sources.first()
    val category = source.categories.firstOrNull { it.id == desired?.categoryId }
        ?: source.categories.firstOrNull { source.id == "fanqie" && it.id == "1_261" }
        ?: source.categories.first()
    val board = category.boardIds.firstOrNull { it == desired?.boardId } ?: category.boardIds.first()
    return Selection(source.id, category.id, board)
}

data class RankUiState(
    val baseUrl: String,
    val catalog: Catalog? = null,
    val selection: Selection? = null,
    val catalogLoading: Boolean = false,
    val rankingLoading: Boolean = false,
    val snapshot: RankingSnapshot? = null,
    val catalogError: String? = null,
    val rankingError: String? = null,
    val settingsError: String? = null,
    val query: String = "",
) {
    val source get() = catalog?.sources?.firstOrNull { it.id == selection?.sourceId }
    val category get() = source?.categories?.firstOrNull { it.id == selection?.categoryId }
    val board get() = source?.boards?.firstOrNull { it.id == selection?.boardId }
    val visibleBooks: List<Book> get() {
        val keyword = query.trim()
        return snapshot?.books.orEmpty().filter {
            keyword.isEmpty() || it.title.orEmpty().contains(keyword, ignoreCase = true) ||
                it.author.orEmpty().contains(keyword, ignoreCase = true)
        }
    }
}
