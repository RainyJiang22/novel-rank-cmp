package com.novelrank.app

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.toComposeImageBitmap
import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.DesktopSettingsStore
import com.novelrank.app.data.CLOUD_SERVICE_ADDRESS
import java.awt.Taskbar
import javax.imageio.ImageIO

fun main() = application {
    val icon = remember {
        val stream =
            checkNotNull(Thread.currentThread().contextClassLoader.getResourceAsStream("icons/app-icon.png"))
        val image = checkNotNull(stream.use { ImageIO.read(it) })
        if (Taskbar.isTaskbarSupported()) {
            val taskbar = Taskbar.getTaskbar()
            if (taskbar.isSupported(Taskbar.Feature.ICON_IMAGE)) taskbar.iconImage = image
        }
        BitmapPainter(image.toComposeImageBitmap())
    }
    Window(
        onCloseRequest = ::exitApplication,
        title = "小说热榜 · NovelRank",
        icon = icon,
        state = rememberWindowState(width = 1180.dp, height = 860.dp),
    ) {
        val environment = remember {
            ClientEnvironment(
                DesktopSettingsStore(),
                CLOUD_SERVICE_ADDRESS,
                allowHttp = true
            )
        }
        App(environment)
    }
}
