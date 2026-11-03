package com.novelrank.app

import com.novelrank.app.presentation.*
import kotlinx.datetime.TimeZone
import kotlin.test.*

class DisplayTest {
    @Test fun preservesSourceStatesAndCacheLabel() {
        assertEquals("来源访问受限", statusLabel(sampleSnapshot(status = "blocked")))
        assertEquals("旧快照", statusLabel(sampleSnapshot(status = "stale")))
        assertEquals("部分数据", statusLabel(sampleSnapshot(status = "partial")))
        assertEquals("缓存榜单", statusLabel(sampleSnapshot().copy(fromCache = true)))
        assertEquals("来源页面发生变化", failureLabel("parse_error"))
    }
    @Test fun formatsTimestampInRequestedZoneWithoutInventingMissingTime() {
        assertEquals("11-03 06:00", formatTimestamp("2026-11-03T06:00:00Z", TimeZone.UTC))
        assertEquals("11-03 14:00", formatTimestamp("2026-11-03T06:00:00Z", TimeZone.of("Asia/Shanghai")))
        assertEquals("未提供", formatTimestamp(null))
        assertEquals("未提供", formatTimestamp("not-a-date"))
    }
}
