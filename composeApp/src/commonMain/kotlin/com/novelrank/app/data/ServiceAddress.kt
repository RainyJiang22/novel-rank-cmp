package com.novelrank.app.data

import io.ktor.http.Url

fun normalizeServiceAddress(input: String, allowHttp: Boolean): String {
    val raw = input.trim()
    require(raw.isNotEmpty()) { "请输入服务地址。" }
    require(raw.length <= 2048 && raw.none { it.isWhitespace() || it.code < 32 }) { "服务地址包含无效字符。" }
    require(
        Regex(
            "^https?://",
            RegexOption.IGNORE_CASE
        ).containsMatchIn(raw)
    ) { "地址必须以 http:// 或 https:// 开头。" }
    require('?' !in raw && '#' !in raw) { "服务地址不能包含查询参数或 # 片段。" }
    // Ktor supplies localhost when an authority is missing; a user-entered address must include one.
    require(hasValidAuthority(raw)) { "请填写有效的主机与端口。" }
    require(raw.substringAfter("://").substringAfter('/', "").split('/').none {
        it.lowercase().replace("%2e", ".") in setOf(".", "..")
    }) { "服务地址不能包含相对路径。" }
    val url =
        runCatching { Url(raw) }.getOrElse { throw IllegalArgumentException("服务地址格式不正确。") }
    require(url.host.isNotBlank() && url.port in 1..65535) { "请填写有效的主机与端口。" }
    require(url.user == null && url.password == null) { "服务地址不能包含用户名或密码。" }
    require(allowHttp || url.protocol.name == "https") { "当前版本需要 HTTPS 服务地址。" }
    return url.toString().trimEnd('/')
}

fun isWebUrl(value: String): Boolean = runCatching {
    val url = Url(value)
    Regex("^https?://", RegexOption.IGNORE_CASE).containsMatchIn(value) &&
        hasValidAuthority(value) &&
        url.host.isNotBlank() && url.port in 1..65535 && url.user == null && url.password == null &&
        value.none { it.isWhitespace() || it.code < 32 }
}.getOrDefault(false)

private fun hasValidAuthority(value: String): Boolean {
    val authority =
        value.substringAfter("://").substringBefore('/').substringBefore('?').substringBefore('#')
    if (authority.isBlank() || '@' in authority) return false
    // Validate the explicit port before Url treats zero as the protocol's default port.
    if (':' in authority && !authority.endsWith(']')) {
        val port = authority.substringAfterLast(':').toIntOrNull() ?: return false
        if (port !in 1..65535) return false
    }
    return true
}
