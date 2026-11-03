package com.novelrank.app.model

import kotlinx.serialization.Serializable

@Serializable
data class Catalog(val sources: List<Source>)

@Serializable
data class Source(
    val id: String,
    val name: String,
    val homeUrl: String,
    val note: String,
    val categories: List<Category>,
    val boards: List<Board>,
)

@Serializable
data class Category(val id: String, val name: String, val group: String, val boardIds: List<String>)

@Serializable
data class Board(val id: String, val name: String, val metricLabel: String)

@Serializable
data class Book(
    val rank: Int,
    val id: String,
    val title: String?,
    val author: String?,
    val url: String,
    val metric: String? = null,
    val genre: String? = null,
    val metadataStatus: String = "complete",
)

@Serializable
data class RankingSnapshot(
    val sourceId: String,
    val categoryId: String,
    val boardId: String,
    val status: String,
    val message: String,
    val sourceUrl: String,
    val fetchedAt: String,
    val sourceUpdatedAt: String? = null,
    val fromCache: Boolean = false,
    val failureReason: String? = null,
    val books: List<Book>,
) {
    val selection: Selection get() = Selection(sourceId, categoryId, boardId)
}

data class Selection(val sourceId: String, val categoryId: String, val boardId: String)
