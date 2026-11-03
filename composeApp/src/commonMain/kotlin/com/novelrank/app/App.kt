package com.novelrank.app

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.HttpRankRepository
import com.novelrank.app.data.createPlatformHttpClient
import com.novelrank.app.data.isWebUrl
import com.novelrank.app.presentation.RankPresenter
import com.novelrank.app.ui.RankActions
import com.novelrank.app.ui.RankScreen
import com.novelrank.app.ui.RankTheme
import com.novelrank.app.ui.components.SettingsDialog
import kotlinx.coroutines.launch

@Composable
fun App(environment: ClientEnvironment) {
    val scope = rememberCoroutineScope()
    val presenter = remember(environment) {
        RankPresenter(
            HttpRankRepository(createPlatformHttpClient()),
            environment,
            scope
        )
    }
    val state by presenter.state.collectAsState()
    var settingsOpen by remember { mutableStateOf(state.baseUrl.isBlank()) }
    val snackbar = remember { SnackbarHostState() }
    val uriHandler = LocalUriHandler.current
    LaunchedEffect(presenter) { presenter.start() }
    DisposableEffect(presenter) { onDispose { presenter.close() } }
    val actions = RankActions(
        source = presenter::selectSource,
        category = presenter::selectCategory,
        board = presenter::selectBoard,
        search = presenter::search,
        refresh = presenter::refresh,
        reload = presenter::reloadCatalog,
        settings = { presenter.clearSettingsError(); settingsOpen = true },
        openUrl = { url ->
            val opened = isWebUrl(url) && runCatching { uriHandler.openUri(url) }.isSuccess
            if (!opened) scope.launch { snackbar.showSnackbar("无法打开来源链接，请检查浏览器设置。") }
        },
    )
    RankTheme {
        Box(Modifier.fillMaxSize().safeDrawingPadding()) {
            RankScreen(state, actions)
            SnackbarHost(snackbar, modifier = Modifier.align(Alignment.BottomCenter))
        }
        if (settingsOpen) SettingsDialog(
            state.baseUrl,
            environment.defaultAddress,
            environment.allowHttp,
            state.settingsError,
            presenter::saveAddress,
            { settingsOpen = false },
            presenter::clearSettingsError
        )
    }
}
