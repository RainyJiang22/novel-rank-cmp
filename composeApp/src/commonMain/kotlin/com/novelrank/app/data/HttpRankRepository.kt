package com.novelrank.app.data

import com.novelrank.app.model.Catalog
import com.novelrank.app.model.RankingSnapshot
import com.novelrank.app.model.Selection
import io.ktor.client.HttpClient
import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.plugins.HttpRequestTimeoutException
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.request.accept
import io.ktor.client.request.get
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import kotlinx.coroutines.CancellationException
import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.Json

fun rankHttpClient(engine: HttpClientEngine): HttpClient = HttpClient(engine) {
    followRedirects = false
    expectSuccess = false
    install(HttpTimeout) {
        requestTimeoutMillis = 50_000
        connectTimeoutMillis = 10_000
        socketTimeoutMillis = 50_000
    }
}

class HttpRankRepository(private val client: HttpClient) : RankRepository {
    private val json = Json { ignoreUnknownKeys = true }

    override suspend fun catalog(baseUrl: String): Catalog = guarded {
        json.decodeFromString<Catalog>(request("$baseUrl/api/v1/catalog")).also { catalog ->
            require(catalog.sources.isNotEmpty())
            require(catalog.sources.map { it.id }.distinct().size == catalog.sources.size)
            catalog.sources.forEach { source ->
                require(source.id.isNotBlank() && source.name.isNotBlank() && isWebUrl(source.homeUrl))
                require(source.categories.isNotEmpty() && source.boards.isNotEmpty())
                require(source.categories.map { it.id }.distinct().size == source.categories.size)
                require(source.boards.map { it.id }.distinct().size == source.boards.size)
                source.boards.forEach { require(it.id.isNotBlank() && it.name.isNotBlank()) }
                source.categories.forEach { category ->
                    require(category.id.isNotBlank() && category.name.isNotBlank() && category.boardIds.isNotEmpty())
                    require(category.boardIds.all { id -> source.boards.any { it.id == id } })
                }
            }
        }
    }

    override suspend fun ranking(
        baseUrl: String,
        selection: Selection,
        refresh: Boolean
    ): RankingSnapshot = guarded {
        val params = mapOf(
            "source" to selection.sourceId, "category" to selection.categoryId,
            "board" to selection.boardId, "refresh" to refresh.toString()
        )
        json.decodeFromString<RankingSnapshot>(request("$baseUrl/api/v1/rankings", params))
            .also { result ->
                require(result.selection == selection && isWebUrl(result.sourceUrl))
                require(
                    result.status in setOf(
                        "ok",
                        "partial",
                        "stale",
                        "blocked",
                        "unavailable",
                        "parse_error"
                    )
                )
                require(result.books.size <= 10 && result.fetchedAt.isNotBlank())
                require(result.books.map { it.rank } == (1..result.books.size).toList())
                require(result.books.map { it.id }.distinct().size == result.books.size)
                require(result.books.all { it.id.isNotBlank() && isWebUrl(it.url) })
                when (result.status) {
                    "ok" -> require(result.books.size == 10)
                    "partial", "stale" -> require(result.books.isNotEmpty())
                    else -> require(result.books.isEmpty())
                }
            }
    }

    private suspend fun request(url: String, params: Map<String, String> = emptyMap()): String {
        val response = client.get(url) {
            accept(ContentType.Application.Json)
            url { params.forEach { (key, value) -> parameters.append(key, value) } }
        }
        if (response.status != HttpStatusCode.OK) {
            throw ServiceException(
                when (response.status.value) {
                    400, 422 -> "服务不接受当前分类组合，请重新加载目录。"
                    401, 403 -> "无法访问聚合服务，请检查服务权限。"
                    in 300..399 -> "服务地址发生跳转，请在设置中填写最终地址。"
                    in 500..599 -> "聚合服务暂时出错，请稍后重试。"
                    else -> "服务返回 HTTP ${response.status.value}，请检查服务地址。"
                }
            )
        }
        return response.bodyAsText().also { require(it.length <= 1_048_576) }
    }

    private suspend fun <T> guarded(block: suspend () -> T): T = try {
        block()
    } catch (error: CancellationException) {
        throw error
    } catch (error: ServiceException) {
        throw error
    } catch (_: HttpRequestTimeoutException) {
        throw ServiceException("连接服务超时，请稍后重试。")
    } catch (_: SerializationException) {
        throw ServiceException("服务响应格式不兼容，请检查服务版本。")
    } catch (_: IllegalArgumentException) {
        throw ServiceException("服务返回的数据与当前分类不一致或格式不完整。")
    } catch (_: Exception) {
        throw ServiceException("无法连接服务，请检查服务地址和网络。")
    }

    override fun close() = client.close()
}
