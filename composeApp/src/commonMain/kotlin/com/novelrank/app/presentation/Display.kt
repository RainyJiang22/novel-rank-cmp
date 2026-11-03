package com.novelrank.app.presentation

import com.novelrank.app.model.RankingSnapshot
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import kotlin.time.Instant

fun statusLabel(snapshot: RankingSnapshot): String = when (snapshot.status) {
    "ok" -> if (snapshot.fromCache) "缓存榜单" else "已获取榜单"
    "partial" -> "部分数据"
    "stale" -> "旧快照"
    "blocked" -> "来源访问受限"
    "unavailable" -> "来源暂不可用"
    "parse_error" -> "来源页面发生变化"
    else -> "未知来源状态"
}

fun failureLabel(reason: String?): String? = when (reason) {
    "blocked" -> "来源访问受限"
    "unavailable" -> "来源暂不可用"
    "parse_error" -> "来源页面发生变化"
    else -> null
}

@OptIn(kotlin.time.ExperimentalTime::class)
fun formatTimestamp(value: String?, zone: TimeZone = TimeZone.currentSystemDefault()): String =
    value?.let {
        runCatching {
            val local = Instant.parse(it).toLocalDateTime(zone)
            val month = local.monthNumber.toString().padStart(2, '0')
            val day = local.dayOfMonth.toString().padStart(2, '0')
            val hour = local.hour.toString().padStart(2, '0')
            val minute = local.minute.toString().padStart(2, '0')
            "$month-$day $hour:$minute"
        }.getOrNull()
    } ?: "未提供"
