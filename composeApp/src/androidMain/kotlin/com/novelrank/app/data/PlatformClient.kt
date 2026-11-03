package com.novelrank.app.data

import io.ktor.client.HttpClient
import io.ktor.client.engine.okhttp.OkHttp

actual fun createPlatformHttpClient(): HttpClient = rankHttpClient(OkHttp.create())
