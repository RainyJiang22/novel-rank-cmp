package com.novelrank.app

import com.novelrank.app.data.RankRepository
import com.novelrank.app.data.SettingsStore
import com.novelrank.app.model.*

val testCatalog = Catalog(listOf(
    Source("fanqie", "番茄小说", "https://fanqienovel.com/", "来源说明",
        listOf(Category("1_261", "都市日常", "男频", listOf("reading", "new")),
            Category("0_748", "豪门总裁", "女频", listOf("new"))),
        listOf(Board("reading", "阅读榜", "在读人数"), Board("new", "新书榜", "在读人数"))),
    Source("jinjiang", "晋江文学城", "https://www.jjwxc.net/", "收入排名，金额未公开",
        listOf(Category("ancient-romance", "古代言情", "收入金榜", listOf("gold")),
            Category("modern-romance", "现代言情", "收入金榜", listOf("gold"))),
        listOf(Board("gold", "分类收入金榜", "收入排名（金额未公开）"))),
))
val initialSelection = Selection("fanqie", "1_261", "reading")

fun sampleSnapshot(selection: Selection = initialSelection, status: String = "ok") = RankingSnapshot(
    sourceId = selection.sourceId, categoryId = selection.categoryId, boardId = selection.boardId,
    status = status, message = "测试来源响应", sourceUrl = "https://fanqienovel.com/rank/1_2_261",
    fetchedAt = "2026-11-03T06:00:00Z",
    books = if (status in setOf("ok", "partial", "stale")) (1..10).map {
        Book(it, it.toString(), "测试作品$it", if (it == 7) "Alice" else "作者$it", "https://fanqienovel.com/page/$it", "123人在读", "都市日常")
    } else emptyList(),
)

class MemorySettings(var address: String? = null, var failSave: Boolean = false) : SettingsStore {
    override fun loadAddress() = address
    override fun saveAddress(address: String) {
        if (failSave) error("storage error")
        this.address = address
    }
}

class FakeRepository : RankRepository {
    val catalogCalls = mutableListOf<String>()
    val rankingCalls = mutableListOf<Triple<String, Selection, Boolean>>()
    var onCatalog: suspend (String) -> Catalog = { testCatalog }
    var onRanking: suspend (String, Selection, Boolean) -> RankingSnapshot = { _, selection, _ -> sampleSnapshot(selection) }
    var closed = false
    override suspend fun catalog(baseUrl: String): Catalog {
        catalogCalls += baseUrl
        return onCatalog(baseUrl)
    }
    override suspend fun ranking(baseUrl: String, selection: Selection, refresh: Boolean): RankingSnapshot {
        rankingCalls += Triple(baseUrl, selection, refresh)
        return onRanking(baseUrl, selection, refresh)
    }
    override fun close() { closed = true }
}
