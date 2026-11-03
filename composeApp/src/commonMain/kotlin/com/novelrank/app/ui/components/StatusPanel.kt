package com.novelrank.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.novelrank.app.presentation.RankUiState
import com.novelrank.app.presentation.failureLabel
import com.novelrank.app.presentation.formatTimestamp
import com.novelrank.app.presentation.statusLabel
import com.novelrank.app.ui.Ink
import com.novelrank.app.ui.Muted
import com.novelrank.app.ui.Warm

@Composable
fun StatusPanel(state: RankUiState, onRefresh: () -> Unit, onReload: () -> Unit, onOpen: (String) -> Unit) {
    val snapshot = state.snapshot
    val warning = state.rankingError != null || snapshot?.status in setOf("partial", "stale", "blocked", "unavailable", "parse_error")
    Surface(color = if (warning) Color(0xFFF5EBD9) else MaterialTheme.colorScheme.primaryContainer,
        shape = RoundedCornerShape(16.dp), modifier = Modifier.fillMaxWidth().testTag("ranking-status")) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            val heading = when {
                state.rankingError != null && snapshot != null -> "刷新失败 · 保留上次结果"
                state.rankingError != null -> "榜单获取失败"
                state.rankingLoading -> if (snapshot == null) "正在获取榜单" else "正在刷新 · 暂时显示上次结果"
                snapshot != null -> statusLabel(snapshot)
                else -> "准备查询"
            }
            Text(heading, color = if (warning) Warm else Ink, fontWeight = FontWeight.SemiBold,
                style = MaterialTheme.typography.titleSmall, modifier = Modifier.testTag("status-label"))
            if (state.rankingLoading) LinearProgressIndicator(Modifier.fillMaxWidth().testTag("ranking-loading"))
            Text(state.rankingError ?: snapshot?.message ?: "首次获取可能需要一些时间，请稍候。", color = Muted,
                style = MaterialTheme.typography.bodySmall)
            if (snapshot != null) {
                Text("${if (snapshot.books.isEmpty()) "尝试时间" else "采集时间"}  ${formatTimestamp(snapshot.fetchedAt)}（本地时间）" +
                    (if (snapshot.fromCache) "  ·  来自缓存" else ""), color = Muted, style = MaterialTheme.typography.labelSmall)
                Text("来源更新时间  ${formatTimestamp(snapshot.sourceUpdatedAt)}", color = Muted, style = MaterialTheme.typography.labelSmall)
                if (snapshot.status == "stale") failureLabel(snapshot.failureReason)?.let {
                    Text("本次刷新：$it", color = Warm, style = MaterialTheme.typography.labelSmall)
                }
                TextButton(onClick = { onOpen(snapshot.sourceUrl) }, modifier = Modifier.testTag("open-source")) { Text("查看原始榜单 ↗") }
            }
            if (!state.rankingLoading && (state.rankingError != null || snapshot?.books?.isEmpty() == true)) {
                Button(onClick = onRefresh, modifier = Modifier.testTag("retry-ranking")) { Text("重试榜单") }
                if (state.rankingError != null) TextButton(onClick = onReload) { Text("重新加载分类目录") }
            }
        }
    }
}

@Composable
fun EmptyPanel(title: String, description: String, action: String? = null, onAction: () -> Unit = {}) {
    Surface(shape = RoundedCornerShape(18.dp), modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium, color = Ink)
            Text(description, style = MaterialTheme.typography.bodyMedium, color = Muted)
            if (action != null) Button(onClick = onAction) { Text(action) }
        }
    }
}
