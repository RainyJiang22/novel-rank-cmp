package com.novelrank.app

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import androidx.compose.runtime.remember
import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.DesktopSettingsStore
import com.novelrank.app.data.CLOUD_SERVICE_ADDRESS

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "小说热榜 · NovelRank",
        state = rememberWindowState(width = 1180.dp, height = 860.dp),
    ) {
        val environment = remember { ClientEnvironment(DesktopSettingsStore(), CLOUD_SERVICE_ADDRESS, allowHttp = true) }
        App(environment)
    }
}
