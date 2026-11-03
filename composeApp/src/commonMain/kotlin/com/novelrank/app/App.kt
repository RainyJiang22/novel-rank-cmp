package com.novelrank.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private val Ink = Color(0xFF174D40)
private val Paper = Color(0xFFF6F4ED)

/** Shared bootstrap screen. Live ranking queries will be added in the next phase. */
@Composable
fun App() {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Ink,
            background = Paper,
            surface = Color.White,
            onBackground = Color(0xFF202A25),
        ),
    ) {
        Box(
            Modifier.fillMaxSize().background(Paper).safeDrawingPadding(),
            contentAlignment = Alignment.TopCenter,
        ) {
            Column(
                modifier = Modifier.widthIn(max = 760.dp).fillMaxWidth()
                    .verticalScroll(rememberScrollState()).padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp),
            ) {
                Spacer(Modifier.height(20.dp))
                Text("NOVEL RANK  /  小说热榜", color = Ink, fontWeight = FontWeight.SemiBold)
                Text(
                    "发现每一种故事的热度。",
                    fontSize = 32.sp,
                    lineHeight = 44.sp,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    "一个面向 Android、iOS 与桌面端的小说分类热榜项目。",
                    style = MaterialTheme.typography.bodyLarge,
                    color = Color(0xFF5D6960),
                )
                Surface(shape = RoundedCornerShape(20.dp)) {
                    Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text("首批网站", style = MaterialTheme.typography.titleMedium)
                        listOf("起点中文网", "番茄小说", "七猫中文网", "晋江文学城")
                            .forEachIndexed { index, source ->
                                Row(
                                    Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                ) {
                                    Text("0${index + 1}   $source", fontWeight = FontWeight.Medium)
                                    Text("待接入", color = Color(0xFF778077))
                                }
                                if (index < 3) HorizontalDivider(color = Paper)
                            }
                    }
                }
                Text(
                    "项目初始化 · v0.1.0",
                    color = Ink,
                    style = MaterialTheme.typography.labelLarge,
                )
                Text(
                    "下一步：按网站和分类查询前十榜单，保留来源、热度口径与更新时间。当前尚未接入榜单数据。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF5D6960),
                )
                Spacer(Modifier.height(12.dp))
            }
        }
    }
}
