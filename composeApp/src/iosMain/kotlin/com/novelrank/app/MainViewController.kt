package com.novelrank.app

import androidx.compose.ui.window.ComposeUIViewController
import androidx.compose.runtime.remember
import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.IosSettingsStore
import com.novelrank.app.data.CLOUD_SERVICE_ADDRESS

fun MainViewController(allowHttp: Boolean) = ComposeUIViewController {
    val environment = remember { ClientEnvironment(IosSettingsStore(), CLOUD_SERVICE_ADDRESS, allowHttp = allowHttp) }
    App(environment)
}
