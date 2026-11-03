package com.novelrank.app.presentation

import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.RankRepository
import com.novelrank.app.data.ServiceException
import com.novelrank.app.data.normalizeServiceAddress
import com.novelrank.app.model.Selection
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** UI-thread state owner. Its child scope is disposed with the Compose screen. */
class RankPresenter(
    private val repository: RankRepository,
    private val environment: ClientEnvironment,
    parentScope: CoroutineScope,
) {
    private val scope =
        CoroutineScope(parentScope.coroutineContext + SupervisorJob(parentScope.coroutineContext[Job]))
    private val loaded = runCatching { environment.store.loadAddress() }
    private val initial = runCatching {
        normalizeServiceAddress(
            loaded.getOrNull() ?: environment.defaultAddress,
            environment.allowHttp
        )
    }
    private val mutableState = MutableStateFlow(
        RankUiState(
            baseUrl = initial.getOrDefault(""),
            settingsError = if (loaded.isFailure) "无法读取本地地址，请重新设置。" else initial.exceptionOrNull()?.message,
        )
    )
    val state = mutableState.asStateFlow()
    private var generation = 0L
    private var catalogJob: Job? = null
    private var rankingJob: Job? = null
    private var started = false
    private var closed = false

    fun start() {
        if (!started && !closed) {
            started = true
            reloadCatalog()
        }
    }

    fun reloadCatalog() {
        if (closed) return
        val baseUrl = state.value.baseUrl
        if (baseUrl.isBlank()) {
            mutableState.value = state.value.copy(catalogError = "请先设置聚合服务地址。")
            return
        }
        val desired = state.value.selection
        val requestId = ++generation
        catalogJob?.cancel()
        rankingJob?.cancel()
        mutableState.value = state.value.copy(
            catalog = null,
            selection = null,
            snapshot = null,
            catalogLoading = true,
            rankingLoading = false,
            catalogError = null,
            rankingError = null,
            query = ""
        )
        catalogJob = scope.launch {
            try {
                val catalog = repository.catalog(baseUrl)
                if (requestId != generation || closed) return@launch
                val selection = chooseSelection(catalog, desired)
                mutableState.value = state.value.copy(
                    catalog = catalog,
                    selection = selection,
                    catalogLoading = false
                )
                requestRanking(refresh = false, keepSnapshot = false)
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                if (requestId == generation && !closed) {
                    mutableState.value = state.value.copy(
                        catalogLoading = false,
                        catalogError = error.userMessage("无法加载网站目录，请检查服务地址。")
                    )
                }
            }
        }
    }

    fun selectSource(id: String) {
        val catalog = state.value.catalog ?: return
        if (catalog.sources.none { it.id == id }) return
        if (state.value.selection?.sourceId == id) return
        changeSelection(chooseSelection(catalog, Selection(id, "", "")))
    }

    fun selectCategory(id: String) {
        val current = state.value.selection ?: return
        val category = state.value.source?.categories?.firstOrNull { it.id == id } ?: return
        val board = current.boardId.takeIf { it in category.boardIds } ?: category.boardIds.first()
        changeSelection(current.copy(categoryId = id, boardId = board))
    }

    fun selectBoard(id: String) {
        val current = state.value.selection ?: return
        if (state.value.category?.boardIds?.contains(id) != true) return
        changeSelection(current.copy(boardId = id))
    }

    private fun changeSelection(selection: Selection) {
        if (closed || state.value.selection == selection) return
        mutableState.value = state.value.copy(selection = selection, query = "")
        requestRanking(refresh = false, keepSnapshot = false)
    }

    fun refresh() {
        if (!closed && !state.value.rankingLoading) requestRanking(
            refresh = true,
            keepSnapshot = true
        )
    }

    fun search(query: String) {
        if (!closed) mutableState.value = state.value.copy(query = query)
    }

    fun saveAddress(input: String): Boolean {
        if (closed) return false
        val address = try {
            normalizeServiceAddress(input, environment.allowHttp)
        } catch (error: IllegalArgumentException) {
            mutableState.value = state.value.copy(settingsError = error.message)
            return false
        }
        try {
            environment.store.saveAddress(address)
        } catch (_: Exception) {
            mutableState.value =
                state.value.copy(settingsError = "地址保存失败，请检查本地存储后重试。")
            return false
        }
        val changed = address != state.value.baseUrl
        mutableState.value = state.value.copy(baseUrl = address, settingsError = null)
        if (changed || state.value.catalog == null) reloadCatalog()
        return true
    }

    fun clearSettingsError() {
        mutableState.value = state.value.copy(settingsError = null)
    }

    private fun requestRanking(refresh: Boolean, keepSnapshot: Boolean) {
        val selection = state.value.selection ?: return
        val baseUrl = state.value.baseUrl
        val requestId = ++generation
        rankingJob?.cancel()
        mutableState.value = state.value.copy(
            rankingLoading = true, rankingError = null,
            snapshot = if (keepSnapshot) state.value.snapshot else null
        )
        rankingJob = scope.launch {
            try {
                val result = repository.ranking(baseUrl, selection, refresh)
                if (requestId == generation && !closed && state.value.selection == selection && state.value.baseUrl == baseUrl) {
                    if (result.selection != selection) throw ServiceException("返回的榜单与当前选择不一致，请重试。")
                    mutableState.value = state.value.copy(snapshot = result, rankingLoading = false)
                }
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                if (requestId == generation && !closed) {
                    mutableState.value = state.value.copy(
                        rankingLoading = false,
                        rankingError = error.userMessage("无法获取榜单，请稍后重试。")
                    )
                }
            }
        }
    }

    fun close() {
        if (closed) return
        closed = true
        generation++
        scope.cancel()
        repository.close()
    }
}

private fun Exception.userMessage(fallback: String) =
    if (this is ServiceException) message ?: fallback else fallback
