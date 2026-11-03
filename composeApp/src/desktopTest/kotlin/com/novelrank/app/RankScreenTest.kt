package com.novelrank.app

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.unit.dp
import com.novelrank.app.data.normalizeServiceAddress
import com.novelrank.app.presentation.RankUiState
import com.novelrank.app.ui.*
import com.novelrank.app.ui.components.*
import org.junit.Rule
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class RankScreenTest {
    @get:Rule val compose = createComposeRule()
    private fun actions(search: (String) -> Unit = {}) = RankActions({}, {}, {}, search, {}, {}, {}, {})

    @Test fun wideSourceSelectionHasSelectedSemantics() {
        var selected by mutableStateOf("fanqie")
        compose.setContent { RankTheme { Box(Modifier.requiredSize(1100.dp, 800.dp)) {
            SourceSelector(testCatalog.sources, selected, true) { selected = it }
        } } }
        compose.onNodeWithTag("source-fanqie").assertIsSelected()
        compose.onNodeWithTag("source-jinjiang").performClick().assertIsSelected()
        compose.onNodeWithTag("source-fanqie").assertIsNotSelected()
    }

    @Test fun narrowSearchRetainsOriginalRankAndCanBeCleared() {
        var state by mutableStateOf(RankUiState("https://example.com", testCatalog, initialSelection, snapshot = sampleSnapshot()))
        compose.setContent { RankTheme { Box(Modifier.requiredSize(390.dp, 844.dp)) {
            RankScreen(state, actions { state = state.copy(query = it) })
        } } }
        compose.onNodeWithTag("ranking-search").performTextInput("Alice")
        compose.onNodeWithTag("rank-content").performScrollToNode(hasTestTag("book-7"))
        compose.onNodeWithTag("book-7").assertIsDisplayed()
        compose.onNodeWithText("07", useUnmergedTree = true).assertIsDisplayed()
        compose.onNodeWithTag("book-1").assertDoesNotExist()
        compose.onNodeWithTag("rank-content").performScrollToNode(hasTestTag("ranking-search"))
        compose.onNodeWithTag("clear-search").performClick()
        compose.runOnIdle { assertEquals("", state.query) }
    }

    @Test fun blockedStateOffersRetryAndOriginalSource() {
        var retried = false
        var opened = ""
        val state = RankUiState("https://example.com", snapshot = sampleSnapshot(status = "blocked"))
        compose.setContent { RankTheme { StatusPanel(state, { retried = true }, {}, { opened = it }) } }
        compose.onNodeWithText("来源访问受限").assertIsDisplayed()
        compose.onNodeWithTag("retry-ranking").performClick()
        compose.onNodeWithTag("open-source").performClick()
        compose.runOnIdle { assertTrue(retried); assertEquals(state.snapshot!!.sourceUrl, opened) }
    }

    @Test fun failedRefreshClearlyLabelsRetainedData() {
        val state = RankUiState("https://example.com", snapshot = sampleSnapshot(), rankingError = "服务连接失败")
        compose.setContent { RankTheme { StatusPanel(state, {}, {}, {}) } }
        compose.onNodeWithText("刷新失败 · 保留上次结果").assertIsDisplayed()
        compose.onNodeWithText("服务连接失败").assertIsDisplayed()
    }

    @Test fun categoryMenuEmitsSelectedId() {
        var picked = ""
        val state = RankUiState("https://example.com", testCatalog, initialSelection)
        compose.setContent { RankTheme { RankingFilters(state, { picked = it }, {}, {}) } }
        compose.onNodeWithTag("picker-category").performClick()
        compose.onNodeWithTag("option-category-0_748").performClick()
        compose.runOnIdle { assertEquals("0_748", picked) }
    }

    @Test fun addressDialogDoesNotDismissOnInvalidInput() {
        var open by mutableStateOf(true)
        var error by mutableStateOf<String?>(null)
        var saved = ""
        compose.setContent { RankTheme {
            if (open) SettingsDialog("", "https://example.com/novelrank", false, error, onSave = { input ->
                try { saved = normalizeServiceAddress(input, false); true }
                catch (exception: IllegalArgumentException) { error = exception.message; false }
            }, onDismiss = { open = false }, onEdit = { error = null })
        } }
        compose.onNodeWithTag("service-address").performTextInput("http://localhost:8000")
        compose.onNodeWithTag("save-address").performClick()
        compose.onNodeWithTag("settings-error", useUnmergedTree = true).assertIsDisplayed()
        compose.runOnIdle { assertTrue(open) }
        compose.onNodeWithTag("service-address").performTextReplacement("https://example.com/novelrank/")
        compose.onNodeWithTag("save-address").performClick()
        compose.runOnIdle { assertFalse(open); assertEquals("https://example.com/novelrank", saved) }
    }
}
