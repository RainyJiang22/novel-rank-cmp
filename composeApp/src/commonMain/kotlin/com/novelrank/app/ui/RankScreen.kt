package com.novelrank.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.novelrank.app.presentation.RankUiState
import com.novelrank.app.ui.components.BookCard
import com.novelrank.app.ui.components.EmptyPanel
import com.novelrank.app.ui.components.RankingFilters
import com.novelrank.app.ui.components.SourceSelector
import com.novelrank.app.ui.components.StatusPanel

data class RankActions(
    val source: (String) -> Unit, val category: (String) -> Unit, val board: (String) -> Unit,
    val search: (String) -> Unit, val refresh: () -> Unit, val reload: () -> Unit,
    val settings: () -> Unit, val openUrl: (String) -> Unit,
)

@Composable
fun RankScreen(state: RankUiState, actions: RankActions, modifier: Modifier = Modifier) {
    BoxWithConstraints(
        modifier.fillMaxSize().background(Paper),
        contentAlignment = Alignment.TopCenter
    ) {
        val wide = maxWidth >= 960.dp
        Row(
            Modifier.widthIn(max = 1360.dp).fillMaxSize()
                .padding(horizontal = if (wide) 32.dp else 18.dp),
            horizontalArrangement = Arrangement.spacedBy(32.dp)
        ) {
            if (wide) {
                Column(
                    Modifier.width(214.dp).fillMaxHeight().verticalScroll(rememberScrollState())
                        .padding(vertical = 30.dp),
                    verticalArrangement = Arrangement.spacedBy(28.dp)
                ) {
                    Brand()
                    HorizontalDivider(color = Outline)
                    SourceSelector(
                        state.catalog?.sources.orEmpty(),
                        state.selection?.sourceId,
                        true,
                        actions.source
                    )
                    Text(
                        "各站热度各有口径。\n保留原始名次，发现值得读的故事。",
                        color = Muted,
                        style = MaterialTheme.typography.bodySmall
                    )
                    Text(
                        "NOVELRANK / 0.1.0",
                        color = Muted,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
            Column(Modifier.weight(1f).fillMaxHeight()) {
                Row(
                    Modifier.fillMaxWidth()
                        .padding(top = if (wide) 28.dp else 18.dp, bottom = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    if (!wide) Brand() else Text(
                        "小说分类热榜",
                        color = Muted,
                        style = MaterialTheme.typography.labelLarge
                    )
                    Spacer(Modifier.weight(1f))
                    TextButton(
                        onClick = actions.settings,
                        modifier = Modifier.testTag("open-settings")
                    ) { Text("服务设置") }
                }
                RankingContent(state, actions, wide)
            }
        }
    }
}

@Composable
private fun Brand() {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Box(
            Modifier.size(38.dp).background(Ink, RoundedCornerShape(11.dp)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                "榜",
                color = MaterialTheme.colorScheme.onPrimary,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }
        Column {
            Text(
                "小说热榜",
                color = Ink,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                "NOVEL RANK",
                color = Muted,
                style = MaterialTheme.typography.labelSmall,
                letterSpacing = 1.sp
            )
        }
    }
}

@Composable
private fun RankingContent(state: RankUiState, actions: RankActions, wide: Boolean) {
    val listState = rememberLazyListState()
    LaunchedEffect(state.selection, state.baseUrl) { listState.scrollToItem(0) }
    LazyColumn(
        state = listState,
        modifier = Modifier.fillMaxSize().testTag("rank-content"),
        contentPadding = PaddingValues(bottom = 32.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item("intro") {
            Column(
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.padding(top = 8.dp, bottom = 6.dp)
            ) {
                Text(
                    "每一种故事，都有它的热度。", color = Ink, fontSize = if (wide) 30.sp else 24.sp,
                    lineHeight = if (wide) 40.sp else 34.sp, fontWeight = FontWeight.Bold
                )
                Text(
                    "追踪分类前十，找到下一本想读的小说。",
                    color = Muted,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
        if (state.catalogLoading) item("catalog-loading") {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                LinearProgressIndicator(Modifier.fillMaxWidth())
                Text("正在连接服务，获取网站与分类…", color = Muted)
            }
        }
        if (state.catalogError != null) item("catalog-error") {
            EmptyPanel("还没有连接到榜单服务", state.catalogError, "重试连接", actions.reload)
            TextButton(onClick = actions.settings) { Text("修改服务地址") }
        }
        if (state.catalog != null) {
            if (!wide) item("sources") {
                SourceSelector(
                    state.catalog.sources,
                    state.selection?.sourceId,
                    false,
                    actions.source
                )
            }
            item("filters") {
                RankingFilters(
                    state,
                    actions.category,
                    actions.board,
                    actions.search
                )
            }
            item("heading") {
                Row(
                    Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(
                            state.category?.name.orEmpty(),
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            "${state.board?.name.orEmpty()} · ${state.board?.metricLabel.orEmpty()}",
                            color = Muted,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    Button(
                        onClick = actions.refresh, enabled = !state.rankingLoading,
                        modifier = Modifier.testTag("refresh-rankings")
                    ) { Text(if (state.rankingLoading) "获取中…" else "刷新榜单") }
                }
            }
            item("status") { StatusPanel(state, actions.refresh, actions.reload, actions.openUrl) }
            if (state.snapshot?.books?.isNotEmpty() == true) {
                item("count") {
                    Text(
                        if (state.query.isBlank()) "来源前十 · 已获取 ${state.snapshot.books.size} 部作品"
                        else "前十内搜索 · 匹配 ${state.visibleBooks.size} / ${state.snapshot.books.size} 部作品",
                        color = Muted, style = MaterialTheme.typography.labelLarge
                    )
                }
                if (state.visibleBooks.isEmpty()) item("no-matches") {
                    EmptyPanel(
                        "前十作品中没有匹配结果",
                        "试试其他书名或作者关键词；这里仅搜索当前榜单。",
                        "清除筛选"
                    ) { actions.search("") }
                }
                items(state.visibleBooks, key = { "book-${it.id}" }) { book ->
                    BookCard(
                        book,
                        compact = !wide,
                        onOpen = actions.openUrl
                    )
                }
            }
            item("footnote") {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.padding(vertical = 12.dp)
                ) {
                    HorizontalDivider(color = Outline)
                    Text(
                        state.source?.note.orEmpty(),
                        color = Muted,
                        style = MaterialTheme.typography.bodySmall
                    )
                    Text(
                        "榜单来自原站公开页面。缓存有效期 15 分钟，连续刷新仍遵守 60 秒间隔。",
                        color = Muted,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }
        item("bottom") { Spacer(Modifier.height(4.dp)) }
    }
}
